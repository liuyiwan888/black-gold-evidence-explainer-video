# 黑金证据式解说视频 Skill

将主题或文案制作成竖屏纪实解说视频，使用章节导航、资料截图、时间线、关系图、数据卡、旁白和逐句字幕。

安装后，Codex 会按 Skill 的制作流程调用当前会话中可用的剪辑与渲染工具。生成视频仍需要可用的渲染环境和必要素材；TTS、生成式画面/配乐可能需要登录、额度或确认。Skill 本身不捆绑模型、账户额度或参考视频素材。

## 安装到 Codex

在 Codex 中将本仓库链接交给 Skill 安装器：

```text
https://github.com/liuyiwan888/black-gold-evidence-explainer-video
```

也可在 Windows PowerShell 运行：

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo liuyiwan888/black-gold-evidence-explainer-video --path skill --name black-gold-evidence-explainer-video --ref codex/20261113-video11-style
```

安装后按 `black-gold-evidence-explainer-video` 调用，并提供主题或文案及希望使用的素材。ChatCut 工作流见 [`execution.md`](skill/references/execution.md)。

## 文件

- [`skill/SKILL.md`](skill/SKILL.md)：制作流程和验收要求
- [`skill/references/style.md`](skill/references/style.md)：画面、章节、动效和声音规范
- [`ANALYSIS.md`](ANALYSIS.md)：参考视频的结构与拆解记录

Skill 提供制作规范，不附带参考视频本身。新主题的事实、来源和素材需重新准备与核对。

## 实际运行基础样片

本包现在含 Python 渲染器，不必先连接 ChatCut。需要 Python 3.10+、FFmpeg 和中文字体：

```shell
cd skill
python -m pip install -r requirements.txt
python scripts/render.py examples/demo.json --out output/demo.mp4
```

默认将旁白文本发送到 Edge 在线语音服务合成；可为每镜头提供本地录音替代。程序包含字卡、时间线、关系图、柱状图、资料截图高亮、字幕与旁白导出。[完整输入与使用说明](skill/references/local-render.md)。

基础模板可以实际出片，但不保证任意文案自动达到参考片全部细节。新闻素材获取、实拍蒙太奇、复杂动效、精确声画同步仍需按题材制作。请先查看样片再判断是否满足预期。

[下载实际渲染的 34 秒有声样片](https://github.com/liuyiwan888/black-gold-evidence-explainer-video/releases/download/v0.2.0/demo.mp4)。已检查 H.264/AAC、576×1024、音频非静音，并完成全片解码检查。样片包含标题、时间线和关系图；资料截图及柱状图接口尚未做样片验证。
