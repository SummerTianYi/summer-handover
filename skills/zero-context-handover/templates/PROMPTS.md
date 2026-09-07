# 团队 Prompt 模板（比赛现场直接复制粘贴）

> 三段对应三个时刻。方括号 [ ] 处替换成你们的实际值（仓库地址/人名/文件名）。

## A. 队长专用：Day-0 装配（比赛仓库建好后，只跑一次）

```text
我们是三人数学建模比赛队（alice 建模 / brin 求解 / cary 论文），比赛仓库是 [仓库地址]。
请按顺序执行：
1. 克隆 https://github.com/SummerTianYi/summer-handover 到任意临时目录（仅本次装配用）。
2. 在我们的比赛仓库根目录执行：
   python <临时目录>/skills/zero-context-handover/scripts/bootstrap.py --preset sprint --owners alice,brin,cary
3. 按打印出的 Day-0 清单逐项填写：AGENTS.md（项目一句话+接口契约）、HANDOFF.md（北极星+领地表）、
   CARDS/alice.md、CARDS/brin.md、CARDS/cary.md、requirements.lock（锁定我们的依赖版本）。
4. 全部填完后删除所有 TODO-DAY0 标记，运行 python check_handover.py，
   必须输出 HANDOVER_GUARD_OK 才算完成；红了就把报错项修掉再跑。
5. 把 <临时目录>/skills/zero-context-handover/templates/ci-snippet.yml 复制为
   .github/workflows/handover.yml，随其余文件一起提交推送（commit 信息结尾加 handover-init）。
完成后向我汇报：装配了哪些文件、守卫是否绿、CI 是否通过。
```

## B. 队友专用：首次 clone 后发给自己的 agent（每人一次）

```text
你是本仓库的新任 agent，此前你没有任何本项目的上下文。按顺序执行：
1. 读 AGENTS.md（宪法：接口契约+协作规则）→ HANDOFF.md（领地表+冻结区）→ CARDS/<你的名字>.md。
2. 运行 setup.sh（mac/linux）或 setup.ps1（windows），然后运行 python check_handover.py，
   必须输出 HANDOVER_GUARD_OK。
3. 向我汇报三问：我的 workstream 是什么、哪些产出是冻结的、我的下一步是什么。
   任何一问答不出来，直接告诉我交接卡哪里没写清楚，不要猜。
4. 记住三条铁律：领地外只读；冻结区（HANDOFF §2 + FROZEN.lock）不许重构；
   每次提交前跑 python check_handover.py 并更新 CARDS/<你的名字>.md，commit 末尾加你的 agent 名。
```

## C. 每日开工（可反复使用，每次新会话都贴一次）

```text
开工。读 AGENTS.md + HANDOFF.md + CARDS/<你的名字>.md，跑 python check_handover.py 确认绿，
然后继续 HANDOFF 领地表里你的下一步。领地外只读；冻结区不许动；遇到异常或需要改别人产出时，
停下向我报告，不要自行重构。
```

## 备注

- 队友**不需要**接触 summer-handover 仓库，也**不需要**安装任何 skill——系统实体在比赛仓库里，clone 即得。
- 换人/交接时：新 agent 先跑 B 中第 1-3 步（三问快卷），全对再动手；完整十题考卷在 `docs/TAKEOVER_EXAM.md`（full 档用）。
