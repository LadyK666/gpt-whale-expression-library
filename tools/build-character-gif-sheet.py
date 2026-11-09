"""Assemble a generated 3x2 keyframe sheet; never draw or matte character art."""
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageChops


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', type=Path)
    parser.add_argument('--output', default='whale-wave-blink.gif')
    parser.add_argument('--durations', type=int, nargs=6,
                        default=[520, 160, 180, 140, 180, 320])
    parser.add_argument('--x-shifts', type=int, nargs=6, default=[0] * 6,
                        help='Nonnegative integer registration offsets; original crops are retained')
    parser.add_argument('--accent-palette-roi', type=int, nargs=4,
                        help='Optional source-sheet box supplying 16 reserved palette colors; no art is altered')
    args = parser.parse_args()
    folder = args.folder.resolve()
    sheet_path = folder / 'sheet.png'
    sheet = Image.open(sheet_path)
    sheet.load()
    width, height = sheet.size
    if width % 3 or height % 2 or width // 3 != height // 2:
        raise ValueError(f'Expected exact 3x2 square cells, received {sheet.size}')
    if sheet.mode == 'RGBA' and sheet.getchannel('A').getextrema()[0] != 255:
        raise ValueError('Opaque-background workflow requires opaque source')
    cell = width // 3
    sheet = sheet.convert('RGB')
    frame_folder = folder / 'frames'
    frame_folder.mkdir(exist_ok=True)
    if args.accent_palette_roi:
        left, top, right, bottom = args.accent_palette_roi
        if not (0 <= left < right <= width and 0 <= top < bottom <= height):
            raise ValueError('Accent palette ROI must be inside the source sheet')
        base = sheet.quantize(colors=240, method=Image.Quantize.MEDIANCUT)
        accent = sheet.crop((left, top, right, bottom)).quantize(colors=16, method=Image.Quantize.MEDIANCUT)
        palette = Image.new('P', (1, 1))
        palette.putpalette(base.getpalette()[:240 * 3] + accent.getpalette()[:16 * 3])
    else:
        palette = sheet.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    frames, records, encoded_records = [], [], []
    for index in range(6):
        x, y = index % 3 * cell, index // 3 * cell
        box = (x, y, x + cell, y + cell)
        frame = sheet.crop(box)
        path = frame_folder / f'frame-{index + 1:02}.png'
        frame.save(path)
        records.append({'file': str(path), 'crop_box': box, 'sha256': sha256(path)})
        shift = args.x_shifts[index]
        if not 0 <= shift < cell:
            raise ValueError('Registration shift must be nonnegative and smaller than one cell')
        if any(args.x_shifts):
            registered_folder = folder / 'registered-frames'
            registered_folder.mkdir(exist_ok=True)
            if shift:
                registered = frame.copy()
                registered.paste(frame.crop((0, 0, cell - shift, cell)), (shift, 0))
                # Extend only the existing left background edge; no character extraction/redrawing.
                edge = frame.crop((0, 0, 1, cell)).resize((shift, cell), Image.Resampling.NEAREST)
                registered.paste(edge, (0, 0))
                frame = registered
            encoded_path = registered_folder / path.name
            frame.save(encoded_path)
        else:
            encoded_path = path
        encoded_records.append({'file': str(encoded_path), 'sha256': sha256(encoded_path),
                                'translation_xy': [shift, 0]})
        frames.append(frame.quantize(palette=palette, dither=Image.Dither.NONE))
    durations = args.durations
    output = folder / args.output
    frames[0].save(output, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, disposal=2, optimize=False)
    decoded, measured = [], []
    with Image.open(output) as gif:
        loop = gif.info.get('loop')
        for index in range(gif.n_frames):
            gif.seek(index)
            gif.load()
            frame = gif.convert('RGB')
            decoded.append(frame.copy())
            measured.append({'index': index, 'duration_ms': gif.info.get('duration'),
                             'decoded_sha256': hashlib.sha256(frame.tobytes()).hexdigest()})
    distinct = len({r['decoded_sha256'] for r in measured})
    if len(decoded) != 6 or distinct < 2 or loop != 0:
        raise ValueError('GIF frame-count, distinct-frame, or loop check failed')
    if [r['duration_ms'] for r in measured] != durations:
        raise ValueError('GIF timing changed during encoding')
    total_pixels = cell * cell
    changes = []
    for index, frame in enumerate(decoded):
        delta = ImageChops.difference(frame, decoded[(index + 1) % len(decoded)])
        changed = sum(1 for pixel in delta.getdata() if max(pixel) > 8)
        changes.append(round(changed / total_pixels, 6))
    qa = {'created_at': datetime.now().astimezone().isoformat(),
          'source': str(sheet_path), 'source_sha256': sha256(sheet_path),
          'output': str(output), 'output_sha256': sha256(output),
          'dimensions': [cell, cell], 'frame_count': len(decoded),
          'distinct_decoded_frames': distinct, 'duration_ms': sum(durations),
          'loop': loop, 'full_decode': 'passed', 'opaque_background': True,
          'frames': measured, 'source_frames': records,
          'encoded_frames': encoded_records, 'registration_x_shifts': args.x_shifts,
          'palette': {'method': 'shared median-cut', 'colors': 256,
                      'accent_roi': args.accent_palette_roi,
                      'reserved_accent_colors': 16 if args.accent_palette_roi else 0},
          'adjacent_changed_pixel_fraction_including_seam': changes,
          'assembly': ('Exact equal-cell crops, integer horizontal registration with source-edge background padding, shared palette, GIF encoding; no drawn art, matting or interpolation'
                       if any(args.x_shifts) else
                       'Exact equal-cell crops, shared palette, GIF encoding; no drawn art, matting, interpolation or registration'),
          'visual_review': 'pending', 'playback_verified': False}
    (folder / 'qa.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: qa[k] for k in ['output', 'dimensions', 'frame_count', 'distinct_decoded_frames', 'duration_ms', 'full_decode']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
