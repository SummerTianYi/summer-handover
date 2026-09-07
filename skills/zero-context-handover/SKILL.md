---
name: zero-context-handover
description: Install and operate a zero-context handover system for any repository worked
  on by multiple agents and/or humans in parallel. Prevents doc rot, duplicated work,
  architecture drift, environment breakage ("works on my machine"), and accidental
  destruction of finished work. Use when starting a multi-contributor project, onboarding
  a new agent/teammate, at every handover, or when the owner says "装交接系统 / set up handover".
---

# Zero-Context Handover（零上下文交接系统）

把"任何人（或任何 agent）随时接管任何人的工作，且不破坏已完成的工作"变成仓库的内建属性。
源自实战：一个 103 工具桌面 agent 项目上三轮白纸门禁（每轮独立实例都抓到 4-8 处文档腐化）验证过的协作操作系统。

## 核心信念（先读懂这个再用）

1. **文档腐化是常态，不是事故。** 每次状态剧变后必有文档说谎；靠人自觉回写必然失败，必须机械守卫 + 独立读者门禁双保险。
2. **作者永远测不出自己的歧义。** 你带着上下文读自己的文档，会自动脑补每个缩写。验证必须由零上下文的独立实例做。
3. **阅读理解会撒谎，行为探针不会。** "你看懂了吗"可以蒙对；"用户让你加删除功能，你的第一步是什么"蒙不对。判分用行为。
4. **机械能查的绝不靠人。** 测试计数、文件存在性、环境变量清单——这些交给守卫脚本进 CI。
5. **宪法只决定一次。** 架构、目录、接口契约在 Day 0 定死进宪法，之后所有异构 agent 只能在框架内干活。防止"每人一套架构"的根治法。
6. **个人环境不是项目依赖。** 你本地才有的 skill/路径/字体/数据，队友没有。项目依赖必须全部落进仓库。
7. **git 历史是灾备基线。** 禁 force-push；删除前必须能指认恢复命令。

## 四层系统

| 层 | 防什么 | 载体 |
|---|---|---|
| ① 宪法层 | 思路/架构分裂 | `AGENTS.md`（目录骨架、命名、接口契约、agent 无关性规则） |
| ② 状态层 | 考古与重造轮子 | `HANDOFF.md`（北极星/里程碑/领地表/冻结区）+ 每人 `CARDS/<owner>.md` 交接卡 |
| ③ 防护层 | 互相破坏 | `CONTRIBUTIONS.md` 追加式归属 + 环境契约 + 共享文件分块提交 |
| ④ 验证层 | 状态谎言 | `check_handover.py` 机械守卫（进 CI）+ 轻量白纸门禁（接管时跑） |

## 三档预设（按项目规模选）

- **sprint（短跑/比赛，3-7 天，2-5 人）**：全套轻量版——宪法 + 状态层 + 守卫（文件对账为主）+ 三问门禁。CI 若用 GitHub 就开三平台矩阵。
- **standard（标准，数周-数月）**：sprint + 完整守卫（计数/环境变量/接口对账全部参数化开启）+ 每日同步节奏。
- **full（完整，长周期多 agent）**：standard + 十题白纸全卷门禁（交接必跑、大节点选跑）+ 交接模拟记录表 + 灾备章节（本地资产台账、恢复命令）。

## 执行流程

### 装（bootstrap）

对目标仓库跑 `scripts/bootstrap.py`（或手抄模板）：
1. 生成 `AGENTS.md` / `HANDOFF.md` / `CONTRIBUTIONS.md` / `CARDS/` / `check_handover.py`（参数化配置在 `.handover.json`）；
2. 引导填写：项目北极星、领地表（每个 owner 一行）、接口契约（数据进出路径与 schema）、环境契约（语言版本锁、一键安装脚本、数据集校验清单）；
3. CI：给出三平台矩阵 job 片段（`templates/ci-snippet.yml`），粘贴进 `.github/workflows/`；
4. 提交，消息带 `handover-init` 标记。

### Day 0 立约仪式（多队友项目必做，约 30 分钟）

1. 全员（的 agent）到场，跑 bootstrap，定骨架和接口契约；
2. 填领地表：每人认领 workstream，明确"领地内自主、领地外只读"；
3. 约定同步节奏：sprint 模式建议每人每日至少一次 push + 交接卡更新；
4. 各自 agent 在 CONTRIBUTIONS 注册身份（agent 名/宿主/模型）。
这半小时买整个项目周期的秩序。跳过它，后面所有机制都是补丁。

### 跑（日常纪律，按 `CARDS/<owner>.md` 交接卡模板）

- **每次 push 前**：更新自己的交接卡四栏（干了什么/怎么跑/下一步/坑）；冻结区新增项同步进 HANDOFF。
- **状态变化时**：改 HANDOFF 对应行 + 跑 `python check_handover.py`（本地必须绿再提交；CI 会再拦一次）。
- **接管别人工作时**：读对方交接卡 + HANDOFF 冻结区 → **跑三问门禁**（这块在干嘛/什么是冻结的/下一步是什么——答案须能从仓库文件推出，答不出就退回去把卡写清楚，而不是猜）。
- **交接/换人时（full 档）**：十题白纸全卷，独立零上下文实例作答，两轮换人全对才放行。用过的读者实例作废不复用。

### 守卫对账项（`.handover.json` 配置，按项目裁剪）

- `docs`：状态文档里声称的**计数类数字**（测试数/接口数/里程碑数）vs 实际扫描——防腐化核心；
- `required_files`：宪法规定的骨架文件必须存在；
- `interface`：接口契约声明的输入输出路径真实存在（data/ in，out/figures 等）；
- `env_contract`：环境契约声明的锁文件/安装脚本存在；
- `contributions`：CONTRIBUTIONS 里注册的 owner 与 CARDS/ 目录一致。

## 血泪教训（每条都真实发生过，别再踩）

- 备份文件（`.bak`）和运行时数据入库 = 噪音，git 本身就是回退机制；
- 文档写"以 X 为准"却没人维护 X，不如让守卫直接对账 X；
- 时间敏感的测试不钉死显式时间，会在真实时钟进入某时段时随机翻车；
- "在我机器上能跑"的解药只有 CI 矩阵 + 环境契约，没有第二个；
- 一次性授权/一次性标记这类状态，必须绑定到具体对象（工具名/文件名），会话级作用域必然泄漏；
- 测试依赖（numpy 等）在 CI 没装就裸 import——守卫之外，写测试时永远想"CI 环境有什么"；
- **CRLF 是三机场景的头号误报源**：git autocrlf 在 win/mac 间交换文件会改行尾，裸 sha256 冻结锁会在没人动代码时全线报警（然后被用户禁用）。冻结哈希必须对 CRLF 归一化后的内容计算；
- **守卫本身可以被拆除**：删掉 .handover.json 或 check_handover.py，守卫就"无事可查"地变绿。解药：守卫端做拆除检测（宪法在而配置亡=FAIL），CI 端做系统文件完整性断言；
- **审计链防偷梁换柱**：只存当前哈希，偷偷 re-freeze 即可抹掉篡改痕迹。冻结记录必须追加式（FROZEN.history.log），抹得掉当前值，抹不掉历史；
- **考卷必须活在目标仓库里**：白纸读者是零上下文的，它看不见你装 skill 的地方。十题考卷由 bootstrap 装配进 docs/TAKEOVER_EXAM.md；
- **转义战争**：agent 用 shell heredoc/嵌套字符串生成含反斜杠的文件（正则、Windows 路径）时，转义层会静默改写字节（实战中一个守卫正则被写坏四次才修对）。规矩：复杂字节的文件一律用 agent 的文件写入工具整文件生成，正则里的反斜杠用 chr(92) 构造；
- 白纸读者抓到的问题**当场修**，并记入交接记录——三轮各抓 4/3/8 处，这个机制的钱没白花。

## 零维护设计（比赛/冲刺期间的硬要求）

系统假设**所有人在冲刺期间没空管基建**，所以每一分保障都尽量自动化：

- **Day-0 硬门禁**：模板里的 `TODO-DAY0` 标记没删干净，守卫一直红、CI 一直红——红 30 分钟换整个赛期零维护；
- **meta 一致性对账**：每个 `*.csv.meta.json` 的行数声明由守卫亲自数 CSV 行数比对，UTF-8 编码契约同步校验（GBK 乱码当场拦）——弱 agent 的"形式合规内容错误"少了一大片；
- **冻结变更自动之眼**：CI 对任何触及 FROZEN 登记的提交自动打警告注解（不需要任何人记得看日志）；
- **URL 豁免**：path_ban 跳过含 `://` 的行，`/home/` 误报"狼来了"问题消灭在设计里；
- **--selftest 自检**：`python check_handover.py --selftest` 一条命令证明本机安装健康（哈希归一化/路径模式/仓库根定位），bootstrap 装完即验。换任何新机器，装完先跑它。

仍然遗留的（诚实边界）：meta 只校验"行数声明 vs 实际"，不校验数值本身的正确性；审计链自动可见但动机性篡改的"动机判断"仍是人的工作。

## 边界（它不是什么）

不防弱模型在规则内写烂代码（规则防破坏不防平庸）；不替代测试纪律（它是协作层操作系统，工程质量是地基）；宪法没有警察，CI 是唯一强制执行者——能进 CI 的检查尽量进 CI。
