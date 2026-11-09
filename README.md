# GPT娘与鲸鱼娘表情动作库

**在线浏览：[ladyk.asia/expressions](https://ladyk.asia/expressions/)**

社区非官方 AI 生成角色素材库，包含静态姿态、头像与短循环 GIF。

当前收录 **181 个主素材**：单人静态 77、双人静态 69、GIF 34、头像 1。GIF 另附原始六帧 PNG 与源图。

打开 [gallery.html](gallery.html) 查看图库，完整索引见 [catalog.json](catalog.json)。下载整个仓库后可离线浏览。

## 许可与来源

- 自写组帧工具使用 MIT，见 [LICENSE](LICENSE)。
- 发布者对本项目生成素材中有权许可的部分提供 CC BY 4.0；第三方角色设计、参考图和商标权利不在授权范围内，见 [ASSET-LICENSE.md](ASSET-LICENSE.md)。
- **没有确认全库不存在版权问题，也不承诺所有素材均可无条件商用。** AI 生成及开源许可不会消除第三方权利。
- 鲸鱼娘造型参考 [社区资源库](https://treapgogo.github.io/deepseek-whale-girl/)。其[许可说明](https://github.com/TreapGoGo/deepseek-whale-girl#代码内容与素材许可)明确将角色设定图排除在代码 MIT 之外；参考图的再次使用授权尚未完全核实。第三方原图不随本库复制。
- GPT娘是白发紫瞳龙角的社区拟人方向；本库生成母版与动作由 AI 制作。早期造型调研查看过 [gpt-pet](https://github.com/weit0529/gpt-pet)，该项目注明图片来源于 B 站社区作者；此链接不是对该上游图片授权的保证。
- 本库不代表 OpenAI、DeepSeek 或任何上游作者官方立场。若权利人提出异议，请通过仓库 Issue 提供具体文件和权利依据，维护者核查后处理。

## 制作与质量

新画面由内置 imagegen 生成静态源图，Pillow 仅裁帧、可选整帧配准和 GIF 编码；不是直接生成视频。GIF 已做完整解码与关键帧检查，**实际播放流畅度和无缝循环尚未验收**。静态图透明合成也未作全库验收。边距偏紧及衣饰细线漂移可能存在。

运行工具示例：`python tools/build-character-gif-sheet.py path/to/six-frame-source --output animation.gif`。需要 Pillow；源目录内须有 3×2 方格源图 `sheet.png`。

## 更新

计划每两天同步本地新增的已归档主素材。自动同步需要维护电脑在线、任务可运行及有效 GitHub 登录；实际成功发布以提交记录为准。

不包含失败候选、第三方参考原图、账号凭证、私密运营记录或本机路径。
