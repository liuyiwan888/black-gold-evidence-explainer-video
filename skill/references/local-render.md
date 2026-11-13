# 独立运行的基础渲染器

## 依赖和运行

需要 Python 3.10+、FFmpeg（含 ffprobe，放在 PATH）与中文字体。Windows 自动选微软雅黑；Linux 查找 Noto Sans CJK；其他字体通过 `--font` 指定。进入安装后的 Skill 目录：

```shell
python -m pip install -r requirements.txt
python scripts/render.py examples/demo.json --out output/demo.mp4
```

默认会将各镜头的旁白文本发送到 Edge 在线语音服务合成，联网使用，无需本包配置密钥；服务可用性取决于网络和服务方。默认声音 `zh-CN-YunxiNeural`，用 `--voice` 更换。使用前向用户说明文本会发送到在线语音服务。每镜头提供 `audio` 路径时，直接使用录音而不调用在线语音。合成失败会报错，不会生成假装完成的静音版本。

可加 `--bgm music.mp3`，音乐按 10% 音量混入。未指定音乐时只有旁白；完整制作时另行准备用户选择或可用的配乐。基础导出为 576×1024、30 fps、H.264/AAC，与参考原片尺寸相同。

## 文案转为镜头 JSON

顶层是 `scenes` 数组。每镜头填写 `title`、`narration`、`chapter`、`chapterNumber`、`source` 和 `kind`。按语义分镜，不把长文全塞进一个画面。每镜头时长从真实音频测量，不截断音频。

| kind | 额外字段 | 效果 |
| --- | --- | --- |
| title | headline, detail | 大字论点与解释逐层出现 |
| timeline | items: [{label,text}]，最多 4 项 | 竖向时间线节点按序点亮 |
| relationship | items: [{label}]，最多 3 项；target | 三方卡片连线到中心结论 |
| bars | items: [{label,value}]，最多 4 项；unit | 从真实数值按比例增长的非负柱状图 |
| evidence | image；highlight 可选 [x,y,w,h] | 原图等比缩放，关键位置金框；位置用 0–1 比例 |

`image`、`audio` 路径相对于 JSON 文件。使用前确认字卡、节点、标题不过长，不适合此布局的内容拆分或修改渲染代码。条形图只接受非负数；负数比较另做坐标轴。不要以演示数据替代用户真实数据。

基础字幕按标点和字数近似分配时间，不能声称逐字精确同步。交付正式成片前依据实际音频修正对齐，必要时在剪辑器导入精确字幕。渲染器输出 MP4 和实际镜头时间 JSON，中间音频/分镜保留在输出目录用于继续编辑。

这套程序可验证基础风格能实际渲染。参考片的实拍蒙太奇、来源资料获取、复杂网页高亮与细致节奏，仍需制作代理结合文案补充；安装程序不代表这些创作已经完成。
