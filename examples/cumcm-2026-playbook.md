# 零上下文交接系统 — 比赛现场使用手册（备份）

> 生成：2026-09-08 ｜ 系统版本：zero-context-handover v3 ｜ 比赛主仓：https://github.com/SummerTianYi/cumcm-2026 （已预装配，守卫绿）

## 一、三条现场 Prompt（复制粘贴即用，[ ] 处替换实际值）

### A. 队长专用：开赛首日更新（一次）

```
比赛题目已公布：[粘贴题目]。在 cumcm-2026 仓库中：
更新 AGENTS.md 的项目一句话与接口契约、HANDOFF.md 的北极星/里程碑/领地表（按真题重划三人分工）、
requirements.lock（锁依赖版本）；改完跑 python check_handover.py 到绿，推送。
```

### B. 队友专用：首次 clone 后发给自己的 agent（每人一次）

```
克隆 https://github.com/SummerTianYi/cumcm-2026 并进入目录。你是 [alice/brin/cary] 的全新 agent，
此前没有本仓库任何上下文。依次读 AGENTS.md（宪法）、HANDOFF.md（领地表+冻结区）、
CARDS/[你的名字].md（你的前任交接卡）；然后运行 setup（Windows 跑 setup.ps1，Mac 跑 setup.sh），
再运行 python check_handover.py，必须输出 HANDOVER_GUARD_OK。
完成后向我汇报三问：①我的 workstream 和下一步 ②哪些产出是冻结的 ③怎么运行和验证。
铁律：领地外只读；HANDOFF 冻结区和 FROZEN.lock 里的文件不许改；
每次提交前守卫必须绿、更新 CARDS/[你的名字].md、commit 末尾加 (你的agent名)。
```

### C. 每日开工（每次新会话贴一次）

```
开工。读 AGENTS.md + HANDOFF.md + CARDS/[你的名字].md，跑 python check_handover.py 确认绿，
然后继续 HANDOFF 领地表里你的下一步。领地外只读；冻结区不许动；遇到异常或需要改别人产出时，
停下向我报告，不要自行重构。
```

## 二、操作清单（按时间顺序）

| 时刻 | 谁做 | 什么 |
|---|---|---|
| 现在（一次性） | 所有者 | GitHub 上 cumcm-2026 → Settings → Collaborators → 邀请三位队友（私有仓不加人 clone 会被拒） |
| 现在（一次性） | 所有者 | 决定三人的代号（现为 alice/brin/cary，对应 CARDS/ 下三个文件名；要改就连文件一起改） |
| 开赛首日 | 队长 agent | 跑 Prompt A（更新占位内容 → 守卫绿 → 推送） |
| 每人进场时 | 队友 agent | 跑 Prompt B（克隆自检三问汇报） |
| 每天开工 | 每人 agent | 跑 Prompt C |
| 有人掉线/换手 | 接手者 agent | 跑 docs/TAKEOVER_EXAM.md 三问快卷；full 档交接跑十题全卷 |

## 三、系统是什么（30 秒版）

零后台、零常驻。三个时刻的工具：装配（已做完）/ 体检（`python check_handover.py`，提交前后随手跑）/ 门禁（交接跑考卷）。"永不下班的哨兵"是 GitHub Actions：每次 push 自动在 ubuntu/macos/windows 三平台跑守卫，红灯绿灯仓库页可见。守卫查六件事：宪法必填文件、接口路径、环境契约、冻结哈希（跨平台防误报）、绝对路径禁令、meta 行数与 UTF-8。

## 四、注意事项与应急

1. **私有仓协作权限**：队友必须先接受 GitHub 协作者邀请，否则 clone 被拒。
2. **守卫红灯怎么办**：读报错行——required_files/interface/env/frozen/path_ban/meta/day0 六类，每条都指明具体文件；修好后重跑至绿再提交。CI 红同理。
3. **冻结产出要改**：不许直接改。走 `python scripts/freeze.py <文件> "<新备注>"` 重新声明（自动留审计 FROZEN.history.log），并在交接卡写明原因。
4. **macOS CI 分钟数**：私有仓 macOS 按 10 倍计费；额度紧张就删 handover.yml 矩阵里的 macos-latest 行（省 90%，守卫逻辑不变）。
5. **换机器**：clone 后跑 setup 脚本 + `python check_handover.py --selftest`（一条命令证明环境健康）。
6. **相关仓库**：系统与文档 https://github.com/SummerTianYi/zero-context-handover （开源，含 SKILL.md 方法论与血泪教训）；比赛主仓 https://github.com/SummerTianYi/cumcm-2026
7. **安全边界**：系统防"信息断层/状态漂移/互相破坏"，不防弱模型的烂代码；测试纪律照旧。
