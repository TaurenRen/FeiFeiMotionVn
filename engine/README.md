# engine · FeiFeiMotionVn 的渲染内核

这个目录是 **FeiFeiMotionVn 的发行版内核**，不是给直接读的文档 —— 用法、流程、验收闸门都在仓库根：

- [`../README.md`](../README.md) —— 项目是什么、28 项能力矩阵、怎么开始
- [`../SKILL.md`](../SKILL.md) —— agent 操作手册（装机、写谱、指着改、三道门）
- [`../TEST-REPORT.md`](../TEST-REPORT.md) —— 每条命令的原始输出与证据

## 直接用它

```
node cli/om.js doctor                  # 环境体检
node cli/om.js templates               # 12 个起步模板
node cli/om.js new my-film --template keynote-ui
node cli/om.js studio my-film          # 编辑器：按 C 点画面留评论
node cli/om.js inbox my-film --wait    # agent 侧接单
node cli/om.js check my-film           # 渲染前自检
node cli/om.js render my-film          # 出片
node cli/om.js qa my-film              # 成片自检
```

## 结构

```
cli/          om 命令行：新建、编辑器、收件箱、配乐、口播、检查、渲染、导出
runtime/      OM.* 小工具与逐帧渲染引擎
studio/       浏览器里的编辑器
templates/    12 个起步模板
fonts/        随附开源字体（Noto Sans SC 四档字重、Inter var、Cormorant…）
examples/     样片（om demo 打开的那支）
skills/feifei-motion/   引擎自带的导演方法、运动语言库、示范谱、经验库
test/         测试
```

许可：MIT。上游来源与版权声明见仓库根 [`../NOTICE`](../NOTICE)。
