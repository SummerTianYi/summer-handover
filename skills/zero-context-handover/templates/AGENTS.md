# AGENTS.md — 项目宪法（模板，Day 0 填写方括号内容后删除本行）

> 本文件是所有参与本仓库的 agent 与人类必须遵守的宪法。任何 agent（无论宿主/模型/skill 配置）进场第一件事：读本文件 → `HANDOFF.md` → 自己的 `CARDS/<owner>.md` 前任内容。

## 项目一句话

TODO-DAY0: 填写后删除本行
[项目名：做什么，为谁，成功标准一句话。]

## 目录骨架（只决定一次，新增顶层目录需全员同意）

```
data/        只进不改的原始数据（大数据不进 git，校验清单见 data/MANIFEST.md）
src/         代码（按 owner 分子目录：src/<owner>/…）
out/         所有生成物（out/figures/、out/tables/，带 MANIFEST 校验和）
docs/        文档（HANDOFF.md、CARDS/ 放根目录或此处，团队自定）
tests/       测试
```

## 接口契约（防架构分裂的核心，Day 0 定死）

TODO-DAY0: 逐条确认后删除本行

- 代码读数据只从 `[data/ 路径]`，schema 见 `[docs/schema.md]`；
- 生成物只落 `[out/ 子路径]`，论文/汇报只引用这些路径；
- 跨 owner 调用只走 `[约定的函数签名/CLI 入口]`，不 import 对方内部模块；
- [其他接口约定。]

## 命名与环境契约

- 命名：[文件/变量/分支命名规范]；
- 语言版本：[Python 3.x（锁文件 requirements.lock / pyproject）/ 其他]；
- 一键安装：`setup.sh`（mac/linux）/ `setup.ps1`（windows），新机器 clone 后先跑它；
- **路径禁令**：代码与配置中禁止出现任何绝对路径与平台专属写法，一律 `pathlib` / 相对路径；个人机器的路径只允许出现在文档的"本机备忘"区；
- **agent 无关性**：不得依赖任何个人本地的 skill/工具/字体/数据；需要的逻辑必须落成仓库内脚本；commit message 末尾带身份标签（见 CONTRIBUTIONS.md）。

## 协作规则

1. **冻结区**（HANDOFF.md）：标记 ✅ 的产出不许重构/覆盖；要改先跑其测试，最小修复；推翻重来需 owner 同意。
2. **领地**：领地表内自主，领地外只读（可提建议）；共享文件按块分块提交，不夹带他人未完成改动。
3. **交接卡**：每次 push 前更新 `CARDS/<owner>.md`（干了什么/怎么跑/下一步/坑）。
4. **守卫**：`python check_handover.py` 本地绿了再 commit；CI 会再拦一次，红了不许合。
5. **接管**：接管他人 workstream 前先跑三问门禁（见 SKILL 或 HANDOFF 门禁节），答不出就把对方交接卡补清楚，不许猜。
6. **归属**：CONTRIBUTIONS.md 只追加不覆盖；每个 agent 注册身份，commit 带标签。
