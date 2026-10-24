---
name: feifeimotionvn
description: 用代码做产品宣传片 / 数据解说 / 口播包装并在 Windows 上真正交付：装引擎与跨平台补丁、抓产品素材、写 ABC 谱配乐、在编辑器里指着画面改、过三道验收门、导出与换画幅。当用户要做发布片或代码生成视频、或遇到 om new 静默失败、配乐速度怪异、成片被评「像幻灯片」、口播在 Windows 上起不来时使用。
---

# FeiFeiMotionVn · 用代码拍片并在 Windows 上交付

一支片 = 一个 `index.html`；画面用 GSAP / Canvas / Three / SVG 写，每帧只由代码和时间决定；
配乐写 ABC 谱由本机演奏；浏览器编辑器里按 `C` 点画面留评论，agent 只改那一处。

28 项能力在 Windows 11 + Node 22.22.2 + Chrome 155 + FFmpeg 上逐条验过：22 项开箱可用，
3 项（新建 / 换画幅 / 演示片）原版静默失败需打补丁，1 项缺系统组件（7-Zip），1 项要换路径（口播）。
交付实测：26.9 秒 1080p30 成片，渲 35–42 秒。

仓库：`github.com/TaurenRen/feifei-motion-win`（本 skill 就在仓库根，可直接 `npx skills add`）。

---

## 一、开工前：先确认这件事值得用这套工具

| 需求 | 用什么 |
|---|---|
| 30 秒产品发布片、数据解说、口播包装、界面 3D 空间导览 | ✅ 本 skill |
| 需要真人出镜 / 实拍素材 | ⛔ 它不生成真人实拍。用你自己的素材，它只负责合成包装 |
| 需要"听懂"音乐好坏 | ⛔ 它听不见。频谱/能量曲线它能查，最后一耳朵必须是人 |
| 长视频（>3 分钟）叙事 | ⚠️ 更适合 Remotion 工程化；强项在 15–60 秒的发布片节奏 |

---

## 二、装机：两步，别跳

```
git clone https://github.com/TaurenRen/feifei-motion-win.git ; cd feifei-motion-win
node engine\cli\om.js doctor        # 必须 4/4
```

`engine/` 是仓库自带的渲染内核，Windows 补丁已经打在里面——**不需要再装别的引擎**。
skill 单独装（`npx skills add`）时只带手册和 scripts，跑之前仍要 clone 这个仓库拿 `engine/`。
`om doctor` 认的是你机器上已有的 Chrome 与 FFmpeg，不另下渲染器。**四个 ✓ 缺一个就不要往下走。**

### 必须打的补丁（否则静默失败）

| 缺陷 | 症状 | 修法 |
|---|---|---|
| `fs.cpSync(…,{recursive:true})` 在 Windows + Node 22 上打死进程（exit 127，零输出） | `om new` 报 `created`，但目录里只有 `index.html`；随后 `om check` 报 13 个 `missing-file` | 换成 `cli/lib/fsx.js` 的 `cpTree()`（mkdir + copyFile 手写遍历）。**新建 / 换画幅 / 演示片全走这条** |
| `.7z` 采样包解不开 | `om samples build` 报 `needs bsdtar`，实际是 Windows 的 `tar.exe` 没有 LZMA | 补丁加了 `7z → 7za → 7-Zip 路径 → bsdtar → tar` 回退；**仍要装 7-Zip 才能真正建成** |
| 虚拟环境解释器写死 `bin/python` | `om voice` 在 Windows 永远找不到解释器 | 补丁按平台给 `Scripts\python.exe` 与对应安装命令 |

**验证补丁生效**（不要只信 `created` 那一行）：

```powershell
node engine\cli\om.js new t --template kinetic-type
(Get-ChildItem -Recurse t -File).Count      # 必须是 33，不是 1
node engine\cli\om.js check t              # 必须 0 errors
```

---

## 三、九步流程与每步的硬纪律

### 1. 读产品、抓素材（`om grab`）

```powershell
node engine\cli\om.js grab https://产品官网 ../proj      # 网页：2x 整页截图、logo 候选、品牌色、字体
node engine\cli\om.js grab D:\本地工程\ ../proj          # 本地：README 图、截图、媒体、样式表里的颜色
```

- **纪律**：抓完必须打开 `materials.md` 逐行看。它会如实写「no logo or icon file found」「no screenshots」——那不是失败，是让你别画灰方块冒充产品。
- 网络注意：GitHub 页面在部分网络下浏览器打不开（`ERR_CONNECTION_TIMED_OUT`），换官网或本地工程模式。

### 2. 选方向、定画幅

12 个模板见 `om templates`。别按"好看"选，按**它在说什么**选：`keynote-ui`（一个东西一屏）、`kinetic-type`（字是演员）、`finance-chart`（先轴后数据）、`ui-space`（界面分层飞出）、`object-3d`（影棚里的实物）。

### 3. 写节奏单（`treatment.md`）——没写完不许开工

3 秒内要有钩子，中段一次爆发，最响那一下前面先停一拍。**场景切点先落成小节线**，再谈画面。

### 4. 写片（一个 `index.html`）

合同三件套，缺一个编辑器就残：

```html
<html data-composition-variables='[{"id":"title","type":"string","label":"标题","default":"…"}]'>
<div id="film" data-composition-id="film" data-width="1920" data-height="1080">
  <h1 data-om-id="title" data-var-text="title">…</h1>
<script>tl.addLabel('scene:title', 0) …</script>
```

- `data-composition-variables` → 编辑器右栏的变量面板（文本框/数字/颜色）
- `data-om-id` → 评论能点中它
- `addLabel('scene:xxx')` → 场景条 + 配乐的 section + 成片自检的镜头划分

**不要写 `data-duration`**（除非你确定时间轴与它一致）：写了会报 `cut-off`；不写则片子长度 = 时间轴长度，改了 timing 变量自动跟着变。

### 5. 直接改值（`om set` / 编辑器）

`om vars` 看全部变量，`om set title="…" count=42 proj/`。编辑器里改的是同一份默认值，改完显示 `已保存 · 第 N 版`。

### 6. 配乐：作曲模式（本 skill 最有价值的纪律）

**结论先说：小节数必须精确，否则引擎会把速度弯过去，而它不报错。**

实测：4/4 的一小节在解析器里 = **4 个单位**，其中
`裸音符 0.5 · X/ 0.25 · X2 1 · X4 2 · X8 4 · z8 4（整小节休止）`。
把 `z4` 当"一小节休止"（它只有半小节）就会整体错位——第一版谱被弯 **−50%**，第二版整曲跑到 34.17 秒（片长 26.4）。

做法：**别手数小节，用 `scripts/score_build.py`**。

```powershell
python scripts\score_build.py            # 校验每个声部每小节 == 4 单位，不合格就不写文件
python scripts\sync_score.py <项目>       # 把 .abc 同步进 index.html 的 om-score
node engine\cli\om.js sound <项目>
```

`om sound` 的报告必须看这三行，任何一行不对就回去改小节：

```
fit      marks on the picture: title 0.00s · claim 4.80s · doctor 7.20s …   ← 标记全落点
tempo    title→claim 100.0 bpm (-0.0%) · …   ← 任何一段弯曲 >8% 就是小节数错了
energy   title -16.2 · claim -19.0 · … · numbers -15.1   ← 应逐级抬升、停顿处下沉、drop 最高
```

场景 ↔ 谱的接线：`!mark:claim!` ↔ 时间轴 label `scene:claim`。
音效写在动画落地那一行：`tl.fromTo('.card', {…}, {…}, OM.sfx('thud', B(23.2)))`。

### 7. 指着画面改（这是它区别于 Remotion 的地方）

```powershell
node engine\cli\om.js studio <项目>          # 你：按 C → 点画面 → 写评论 → 发送
node engine\cli\om.js inbox <项目> --wait    # agent：接下一条（自动 claim）
node engine\cli\om.js look <id> <项目>       # 存整帧 + 点击处 2x 特写，先看再改
…改代码…
node engine\cli\om.js done <id> <项目> --note "把数字从 104px 放大到 156px"
```

评论到手时自带 `00:00.00 · 场景 title` 和目标元素，**不要**凭标题猜用户在看哪儿——`om look` 存在的意义就是先看。

**`om undo` 只有一步**，语义是"恢复上一份快照"，没有 redo。改大改之前先 commit 或复制一份。
（实测中一次 `om undo` 把刚做的两处修改一起抹掉了，所以这条写进纪律。）

### 8. 三道验收门（别靠眼睛扫输出）

```powershell
python scripts\qc_gate.py engine <项目> --render
```

| 门 | 查什么 | 拦什么 |
|---|---|---|
| `om doctor` | 机器能不能渲 | 缺 FFmpeg / 编码器 / Chrome |
| `om check` | 渲染前的结构问题 | `missing-file` · `cut-off` · `stale-sound` · `low-contrast(<4.5:1)` · `layout-motion`（动画 width/height/top/left）· `font-not-shipped` · `history-dependent`（直接 seek 与播放不一致） |
| `om qa` | 成片到底动不动 | 单帧闪烁 · **开场 5 秒平**（前 5 秒最强一秒 <2）· **整片 barely moves**（每秒运动均值 <0.85） |

`om qa` 的 `still for ≥1 s` **不是失败项**——原文是「fine for a reading hold or an end card」。这是选择题：打开那几秒自己看，是"读者需要读"还是"画面死了"。

实测数据：卡片式淡入淡出 = mean **0.15**、0 硬切（判死）；加相机推 + 光扫 + 浮尘 + 六处硬切 = mean **0.85**、10 硬切、平均镜头 2.4s（通过）。

### 9. 交付

```powershell
node engine\cli\om.js render   <项目>                      # out/film-vN.mp4
node engine\cli\om.js render   <项目> --transparent        # ProRes 4444 带 alpha，给剪映/Premiere
node engine\cli\om.js fork     <项目> <新目录> --size 1080x1920   # 竖屏副本 + 收件箱里的重排任务
node engine\cli\om.js share    <项目>                      # ≤10MB GIF + share.md 发帖文案
node engine\cli\om.js export html <项目>                   # 播放器 + source.zip 的分享页
```

---

## 四、翻车点速查

| 现象 | 真因 | 处理 |
|---|---|---|
| `om new` 说 created，项目却跑不起来 | `cpSync` 在 Windows 打死进程 | 打补丁 + `(Get-ChildItem -Recurse).Count == 33` 自查 |
| `om check` 报一堆 `missing-file` | 同上（vendor 没复制完） | 同上 |
| 配乐某段忽快忽慢 | 该段小节数与画面不符，速度被弯 | 看 `tempo` 那行的百分比，改小节数 |
| 整曲比片长/短 | 同上 | 用 `score_build.py` 生成，别手数 |
| 成片被评「像幻灯片」 | 只有淡入淡出，没有镜头运动与硬切 | 相机推 + 背景永不停（光扫/浮尘/网格）+ 切点用硬切 + 闪白 |
| `om check` 报 `history-dependent` | 用 `fromTo` 做闪烁类效果，直接 seek 与播放不一致 | 改 `set` + `to` |
| 中文变糊 / 字重不对 | 只随附 500/900 两档，CSS 写 600 会跳到 900 | 只用实际存在的字重；`om fonts` 看清单 |
| 文字贴底被播放器挡 | 字幕/浮层太靠下 | 浮层字 ≥26px、字幕 ≥44px，且离底边留出控制条高度 |
| `om voice` 起不来 | Windows 没有 `say`；Kokoro 要 Python 3.12 + 325MB 模型 | 用 `--audio 你的录音 --text 稿子 --asr off`（靠静音切句，不需要 whisper） |
| 真乐器包建不完 | `.7z` 需要 7-Zip | 装 7-Zip 再跑 `om samples build`；装不上就用合成音色，不影响出片 |

---

## 五、成本与性能（本机实测）

| 项 | 数值 |
|---|---|
| 1080p30 / 26.9s 成片渲染 | 35.4s（无粒子）→ 42.1s（34 粒子 + 光扫） |
| 默认并发 | 最多 8 个 Chrome（`--workers n` 可调） |
| 成片体积 | 10.3MB（H.264 + AAC stereo） |
| 分享 GIF | 8.4MB（640px / 15fps / 开头 10s + 片尾） |
| 配乐生成 | 26.4s 的谱 → 6.4s 渲成，−14.0 LUFS / peak −1.5 dBFS |
| 配乐依赖与费用 | 全部本机生成，不调任何收费接口 |

---

## 六、交付前最后三问

1. **每一句、每一个数字，是产品的真实素材还是我编的？** `om check` 的 `no-real-material` 警告就是在问这个。
2. **三道门都过了吗？** 特别是"开场 5 秒"——第一秒不动，后面再好也没人看。
3. **我听过了吗？** 它听不见。混音、音效是否盖住口播、段落间有没有抢拍，只能靠耳朵。
