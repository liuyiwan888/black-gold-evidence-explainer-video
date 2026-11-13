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
python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo liuyiwan888/black-gold-evidence-explainer-video --path skill
```

安装后按 `black-gold-evidence-explainer-video` 调用，并提供主题或文案及希望使用的素材。ChatCut 工作流见 [`execution.md`](skill/references/execution.md)。

## 文件

- [`skill/SKILL.md`](skill/SKILL.md)：制作流程和验收要求
- [`skill/references/style.md`](skill/references/style.md)：画面、章节、动效和声音规范
- [`ANALYSIS.md`](ANALYSIS.md)：参考视频的结构与拆解记录

Skill 提供制作规范，不附带参考视频本身。新主题的事实、来源和素材需重新准备与核对。
