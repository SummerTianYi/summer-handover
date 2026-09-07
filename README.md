# Summer Handover — 零上下文交接系统

**任何人（或任何 agent）随时接管任何人的工作，且不破坏已完成的工作。**

这是一套装进任何仓库的协作操作系统，面向多 agent / 多人 / 异构环境并行开发。源自一个真实的 103 工具桌面 agent 项目（三方 agent 接力 + 白纸门禁三轮验证），抽离为通用系统。

## 它防什么

| 灾难 | 机制 |
|---|---|
| 三个 agent 三套架构，互相读不懂 | 宪法层：`AGENTS.md` 目录骨架 + 接口契约，Day 0 只决定一次 |
| 新人/新 agent 考古三天还重造轮子 | 状态层：`HANDOFF.md` 领地表 + 冻结区 + 每人交接卡 |
| 互相覆盖、环境炸裂（works on my machine） | 防护层：追加式归属 + 环境契约 + 三平台 CI 矩阵 |
| 文档说谎、状态过期 | 验证层：`check_handover.py` 机械守卫（进 CI）+ 白纸门禁（接管时跑） |

## 快速开始

```bash
# 在你的项目仓库根目录
python /path/to/zero-context-handover/scripts/bootstrap.py --preset sprint --owners alice,bob,cary
# 然后按打印出的 Day-0 清单填写，30 分钟立约仪式，买整个项目的秩序
```

三档预设：**sprint**（比赛/短跑）/ **standard**（数周-数月）/ **full**（长周期多 agent，含十题白纸全卷门禁）。方法论、教训与执行流程见 [`skills/zero-context-handover/SKILL.md`](skills/zero-context-handover/SKILL.md)。

## 作为 skill 使用

把 `skills/zero-context-handover/` 装进你的 agent skill 目录（如 `~/.agents/skills/`），agent 收到"给这个仓库装交接系统"类指令时自动按 SKILL.md 执行；或手动跑 bootstrap。

## 比赛/团队现场 Prompt（复制粘贴即用）

三段现成 prompt（Day-0 装配 / 队友首次 clone / 每日开工）见 [`skills/zero-context-handover/templates/PROMPTS.md`](skills/zero-context-handover/templates/PROMPTS.md)——队员不需要知道 zero-context-handover 的存在，系统装配后完全活在比赛仓库里。

## 安装与运行逻辑（一句话装好）

```bash
git clone https://github.com/SummerTianYi/zero-context-handover
python zero-context-handover/scripts/install.py   # 装进本机所有 agent 的技能目录
```

之后对本机任何 agent 说一句"**给这个仓库装零上下文交接系统**"即可；没有 skill 发现机制的 agent 直接读 `SKILL.md` 照做，效果相同。

**运行逻辑（重要）**：本系统**不是常驻监视器**，没有任何后台进程。它是"三个时刻的工具 + 一个永不下班的哨兵"——装配（bootstrap，一次）、体检（`python check_handover.py`，提交前后随手跑）、门禁（交接/接管时跑考卷）；而"一直在检查"的角色由 **GitHub Actions** 承担：每次 push 自动三平台矩阵跑守卫，红灯绿灯人人可见。仓库状态三层查看：本地 `python check_handover.py`、远端 CI 页、系统健康 `--selftest`。

**队友零配置**：系统全部实体（守卫/冻结器/模板）bootstrap 时已复制进项目仓库——队友 clone 项目、跑 setup、提交前跑一条守卫命令即可，不需要装本 skill，甚至不需要用 agent。

## 实战出身

- 验证场：洛天依桌面 agent 项目（Godot 角色三任 agent 接力 + 103 工具联网能力），白纸门禁三轮各抓出 4/3/8 处文档腐化并当场修复；
- 目标场景：数学建模竞赛式三人三机三 agent 异构并行（Windows/macOS/Linux、模型与 skill 配置互不相同）。

## 边界

它防破坏不防平庸：弱模型在规则内依然会写烂代码；它是协作层操作系统，不替代测试纪律。宪法没有警察——CI 是唯一强制执行者，检查尽量进 CI。

## License

MIT
