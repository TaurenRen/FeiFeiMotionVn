# FeiFeiMotionVn

> 用代码拍宣传片：一支片就是一个网页，配乐自己写谱，不满意就指着画面让它改。
> Windows 上开箱即用 —— 28 项能力逐条验过，跨平台缺陷全部修好，附三道验收门。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tested on](https://img.shields.io/badge/tested-Windows%2011%20%C2%B7%20Node%2022.22.2-blue)]()
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-installable-green)](SKILL.md)

![标题帧](evidence/screenshots/title-2.2s.png)

---

## 它是什么

跟 agent 说一句「给我的产品做个 30 秒发布片」，它会读你的产品、给你三个方向挑、写完整支片子、自己写谱配乐，然后在浏览器里打开一个编辑器等你。

- **画面是代码写的** —— GSAP / Canvas / Three / SVG 随便用，每一帧只由代码和时间决定。没有私有格式，片子带走就能跑。
- **配乐是现场演的** —— 写一份 ABC 谱，谱里标好场景，程序按标记对齐画面演奏出来；画面上每个东西落地的那一帧配一个音效。全在本机，不调收费接口。
- **可以在画面上留评论** —— 浏览器里按 `C` 点一下，写「这里换成蓝色」，agent 收到的是**时间点 + 场景 + 你点中的元素 + 源码行**，它先把那一帧放大看一眼，再只改那一处。
- **交付前会被挑错** —— 渲染前查结构/字体/裁切/对比度，渲染后查单帧闪烁、静止段、硬切与运动曲线。三道门不过就不让出片。

这台机器上交付的那支 26.9 秒 1080p 片子（画面、配乐、音效全部由它生成，渲了 42 秒）：

[`evidence/films/film-windows-test.mp4`](evidence/films/film-windows-test.mp4) · [`evidence/films/film-windows-test.gif`](evidence/films/film-windows-test.gif)

---

## 28 项能力，Windows 11 上的实测结果

| 能力 | 结果 |
|---|---|
| 环境体检 | ✅ 4/4（Node / FFmpeg+ffprobe / mp4·mov·webm·gif / Chrome） |
| 12 个起步模板（发布会 / 动态文字 / 财经图表 / 白板 / 3B1B / Kurzgesagt / 口播包装 / 界面 3D…） | ✅ |
| 抓产品素材（网页 / 本地工程）：截图、logo、SVG、品牌色、字体 | ✅ 缺失项如实上报，不画灰方块冒充 |
| 浏览器编辑器 + **按 C 指着画面改** | ✅ 评论自带 `00:00.00 · 场景 title`，收件箱闭环走通 |
| 看你点的那一帧（整帧 + 点击处 2x 特写） | ✅ |
| 作曲模式（ABC 谱 + 场景标记对齐） | ✅ 314 音符 / 5 声部，6 个标记落点偏差 ≤0.4% |
| 23 种音效 / 12 类兜底配乐 | ✅ |
| 渲染前自检 | ✅ 一次抓出 8 个真问题 |
| 渲染 1080p30 | ✅ 26.9 秒片 → 35–42 秒渲完 |
| 成片自检（单帧闪烁 / 静止段 / 硬切 / 运动曲线） | ✅ 第一版被判「像幻灯片」，改到 mean 0.85、10 硬切才过 |
| 分享包（≤10MB GIF + 发帖文案）/ 分享页（播放器 + source.zip） | ✅ |
| 换画幅（1920×1080 → 1080×1920，自动留重排任务） | ✅ |
| 色板对照 + 对比度检查 / 27 款随附字体 / 经验库 | ✅ |
| 新建项目 / 换画幅副本 / 演示片 | 🔧 **在本机静默失败，本仓库已修** |
| 真乐器采样包 | 🔧 需 7-Zip（`.7z` 包，Windows 自带 tar 无 LZMA）；不装就用合成音色，不影响出片 |
| 口播 | 🔧 用你自己的录音：`--audio 配音.wav --text 稿子.txt --asr off` |

逐条证据（每条命令的原始输出 + 界面截图 + 成片 + 录屏）：[`TEST-REPORT.md`](TEST-REPORT.md)。

---

## 三行开始

```powershell
git clone https://github.com/TaurenRen/FeiFeiMotionVn.git ; cd FeiFeiMotionVn
node engine\cli\om.js doctor        # 应该 4 个 ✓，不需要装任何东西

`engine/` 就是本仓库自带的渲染内核（已经打好 Windows 补丁），克隆下来即可用。
```

然后照流程走：`grab` → `new` → `studio` → `inbox --wait` → `check` → `render` → `qa`。

验收别靠眼睛扫输出：

```powershell
python scripts\qc_gate.py engine my-film --render
# GATE 1 doctor → GATE 2 check → GATE 3 qa → PASS cuts=10 mean motion=0.85/s
```

`patches/` 记的是**改动本身**：`apply.ps1` 能把同样的修复打到一份干净的上游 v0.3.1 上（优先 `git apply`，对不上就走拷贝兜底，打完自己跑一个 `om new` 数文件个数——少于 33 个就算失败）。`engine/` 是打完的结果，日常用不到 `patches/`。

---

## 里面有什么

```
SKILL.md                操作手册（装成 agent skill 直接可用：npx skills add TaurenRen/FeiFeiMotionVn）
engine/                 渲染内核：cli（om 命令）/ studio（编辑器）/ runtime / 12 模板 / 字体 / 样片
patches/
  0001-windows.patch    跨平台修复本身（5 个文件 / 178 行）
  apply.ps1             把修复打到一份干净的上游上 + 冒烟验证
  files/                打好补丁的成品文件（git 不可用时的兜底）
scripts/
  qc_gate.py            三道验收门（doctor → check → qa），不合格就拦住不让渲染
  score_build.py        按小节数生成 ABC 谱，杜绝配乐「速度弯折」
  sync_score.py         把 .abc 同步进 index.html 的 om-score
  splice_script.py      把动画脚本同步进 index.html（这支片迭代 5 版全靠它）
  drive_studio.mjs      用 CDP 驱动编辑器走完「按 C → 点画面 → 写评论 → 发送」
  sync_github.py        不走 git push 的推送（本机 HTTPS 通道被拦，改走 Git Data API）
tools/
  rebrand.py            把上游引擎改名成 FeiFeiMotionVn 的那一次批量替换（可复现）
evidence/
  logs/                 30 份原始输出
  screenshots/          编辑器界面、关键帧、色板对照
  films/                成片 mp4 / gif、编辑器操作录屏
```

---

## 修了什么

1. **`fs.cpSync(…,{recursive:true})` 在 Windows + Node 22 上直接打死进程**（stdout/stderr 全空，退出码 127），而单文件 `cpSync` 正常。结果是新建项目复制到一半就没了、CLI 还报成功。改成手写 `mkdir + copyFile` 遍历（`cli/lib/fsx.js`）。
2. **`.7z` 解不开**：只调 `bsdtar`（Windows 上没这个名字，等价的 `tar.exe` 又没有 LZMA）。改成 `7z → 7za → 7-Zip 安装路径 → bsdtar → tar`，失败时说清"装个 7-Zip 再跑一次"。
3. **口播在 Windows 上是死路**：虚拟环境的解释器路径写死成 `bin/python`（Windows 是 `Scripts\python.exe`），打印的安装命令也是 POSIX 的。按平台拼路径与命令，并明确 `--asr off` 可以完全不用 ASR。

---

## 两个最值钱的结论

**配乐的小节算术。** 引擎会把速度在场景标记之间「弯」过去：小节数错了它不报错，只把那段放慢 25%、50%。4/4 一小节在解析器里是 **4 个单位**（裸音符 0.5 / `X/` 0.25 / `X8` 4 / `z8` 4 整小节）——把 `z4` 当整小节休止就会整体错位。第一版谱因此被弯 −50%，第二版整曲跑成 34.17 秒（片长 26.4）。`scripts/score_build.py` 就是为了让它不可能再错：按小节数生成，凑不满 4 个单位就不写文件。

**「像幻灯片」是可以量化的。** 成片自检给出的每秒运动量，第一版是 **0.15、零硬切**，直说 "reads as slides"；把相机推拉到 1.26、加一道横穿的光扫、34 颗浮尘、六处硬切 + 闪白之后是 **0.85、10 个硬切、平均镜头 2.4 秒**。它量的不是审美，是"有没有人愿意看下去"。

---

## 依赖与致谢

- 本项目自带渲染内核（`engine/`），它来自一个 MIT 许可的上游引擎，本发行版做了重命名与跨平台改造。
  MIT 要求副本随源码保留版权声明，所以原始出处放在 [`NOTICE`](NOTICE) —— 产品命名是本项目的，法律上的出处在那份声明里。
- 动画库 [GSAP](https://gsap.com)（GSAP Standard License）；随附字体为 SIL OFL 1.1；真乐器采样为 CC0/CC-BY，由引擎在 `samples build` 时从原处下载。
- 本仓库的修复、脚本、文档与验收门为 MIT，见 [LICENSE](LICENSE)。

---

MIT · 补丁、脚本、流程随意用。
