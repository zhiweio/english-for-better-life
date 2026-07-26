这份预习材料**不用 material 原文**，概念全部用自己的话复述。每个概念的「用自己的话理解」提供**中英双语**（英文按 **B2**）。长句练习的重点是**嵌套从句**——定语从句、状语从句、非限制性从句叠在一起练。

---

## 课前 3 分钟：今天讲什么

**话题：** 可维护性——接手一个 3000 行、无测试的遗留订单系统，该重写还是重构？怎么切流、怎么保住隐性知识、怎么安全地拆大类？

**三条主线（material 技术干点）：**

```
① 切换风险 → ② 隐性知识 → ③ 渐进式重构
```

**故事线：**

```
主张重写 → 追问怎么切流 → 追问测试与隐性知识 → 追问只能重构怎么办 → 安全网 + 渐进提取
```

| 策略 | 核心手段 | 关键数字 |
| --- | --- | --- |
| 新老切换 | Feature flag + canary（按 user ID） | 并行 2 周 · 先 5% 内部用户 |
| 重写质量 | TDD + CI 80% coverage | 复盘半年 bug / postmortem |
| 被迫重构 | 先集成测试安全网 → 再 Extract | 目标：拆成 ~12 个小模块 |

| 重写值得 | 必须重构 |
| --- | --- |
| 紧耦合大类补测比从头 TDD 更难 | 业务不能停、不能承担并行双系统成本 |
| 团队能保障切换与测试纪律 | 核心逻辑还能在安全网下逐步拆开 |

**规律：** 不是判「重写」或「重构」死刑——用**可灰度、可回滚、可沉淀**的手段选演进路径；没有安全网，每次提取都是赌博。

---

## 概念 1：遗留系统与技术债务——重写还是重构

### 用自己的话理解（中英双语）

**中文：**

面试开场的情境很典型：订单系统一个类 3000 行，十几二十个方法缠在一起，没有单元测试，每次改需求都要加班救火。候选人主张在特定条件下**重写**，但面试官逼的是：你评估过风险吗？凭什么更划算？

这里的关键不是站队，而是**技术债务已经侵蚀了可维护性**——耦合高、缺测试、改一处动全身，继续硬改的成本会指数上升。重写的好处是可以在新代码里从第一天就按 TDD 和模块化来；重构的好处是不用双系统并行、业务不停。

选型要看三件事：旧代码补测试的难度、切换期间能否承受并行维护成本、团队有没有把历史故障沉淀成测试的纪律。候选人没有说「永远重写」，而是准备了两套方案：重写走切流，重构走安全网。

**English (B2):**

The interview starts with a painfully familiar legacy order system: one class with about 3,000 lines, a dozen tightly coupled methods, no unit tests, and every requirement change turning into late-night bug fixes. The candidate argues for a **rewrite under certain conditions**, but the interviewer pushes back on risk — **why** should that be cheaper or safer than refactoring?

The real issue is **technical debt that has already eaten maintainability**. High coupling and missing tests mean a small change can ripple unpredictably, **which** makes continued patching increasingly expensive. A rewrite lets the team apply TDD and modular design from day one; refactoring avoids running two production systems in parallel and keeps the business running on one codebase.

The choice depends on three factors: how hard it is **to retrofit tests onto the old class**, whether the organisation can afford parallel maintenance during cutover, and whether the team will systematically turn past incidents into mandatory tests. The candidate does not claim rewrite is always right — **instead**, rewrite comes with a cutover plan, **whereas** refactor comes with a safety net.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| legacy system | 遗留系统 | A legacy system is code **that** still runs in production **but** is hard **to change safely**. |
| technical debt | 技术债务 | Technical debt is the cost **that** accumulates **when** shortcuts make future changes slower. |
| tight coupling | 紧耦合 | Tight coupling means methods **that** depend on each other **in ways** **that** are hard **to isolate**. |
| maintainability | 可维护性 | Maintainability drops **when** a class grows **without** tests **that** guard its behaviour. |
| cutover | 切换 | Cutover is the moment **when** traffic moves from the old system **to** the new one. |
| retrofit tests | 补写测试 | Retrofitting tests onto old code is harder **than** writing them first in a greenfield rewrite. |

### 嵌套从句练习：说为什么债务逼你选型

**Layer 1：**
> Technical debt makes every change riskier **because** the class has no tests.

**Layer 2 — 加定语从句：**
> A 3,000-line class **that** has no unit tests is a codebase **where** every change feels like gambling.

**Layer 3 — 加对比从句：**
> **Although** rewriting sounds drastic, adding tests to a tightly coupled legacy class is often harder **than** starting fresh with TDD, **which** is why the candidate prefers rewrite **only when** the team can also manage cutover risk.

**Layer 4 — 完整嵌套版：**
> **When** maintainability has been eroded by technical debt — **meaning** a monolithic class **that** couples order logic, tax rules, and ID generation **without** a safety net — the team must choose between a rewrite **that** enforces tests from day one **and** a refactor **that** builds integration coverage **before** any extraction, **each of which** carries different risks **that** the interviewer forces the candidate **to explain**.

**中文对照：** 当技术债务已经侵蚀可维护性——也就是一个把订单逻辑、税费规则和 ID 生成耦在一起、又没有安全网的大类——团队必须在「从头重写并强制测试」和「先补集成覆盖再提取」之间选型，而面试官逼候选人把各自的风险说清楚。

---

## 概念 2：新老系统切换——特性开关与金丝雀

### 用自己的话理解（中英双语）

**中文：**

面试官第一个追问很现实：重写期间旧系统还在跑，新老怎么切？并行多久？延期了业务怎么交代？

候选人答的是组合拳：**特性开关**把路由逻辑外置，出问题翻开关立刻回退，不用重新部署；**金丝雀**按 user ID 导流，先 5% 内部员工验证下单和查询，再逐步拉到 100%；两套系统**并行两周**。并行期间旧系统**冻结功能**，只修紧急 Bug，把维护成本压到最低。

这三层各自解决一个问题：开关管回滚速度，金丝雀管爆炸半径，冻结管并行成本。整体思路是切换必须**可灰度、可监控、可回滚**——不是 Big Bang 一刀切。

**English (B2):**

The first follow-up question is brutally practical: **while** the rewrite is still in progress, the old system keeps serving real orders — **so how** do you cut over, **how long** do you run both sides, and **what** do you tell the business **if** the rewrite slips?

The candidate answers with a layered plan. A **feature flag** externalises routing between old and new code, **which** allows an instant rollback **without** redeploying. A **canary deployment** routes traffic by user ID, starting with about 5% internal users **who** validate order creation and queries **before** the rollout reaches 100%. Both systems run in parallel for roughly two weeks. During that window, the old system is **frozen for new features** and receives only emergency bug fixes, **which** keeps parallel maintenance costs under control.

Each layer solves a different fear: the flag controls rollback speed, the canary limits blast radius, and the freeze limits ongoing change on the legacy side. The overall message is that cutover must be **gradual, observable, and reversible** — not a single high-stakes switch.

### 切换策略对照表（复述）

| 手段 | 解决什么 | 候选人怎么做 |
| --- | --- | --- |
| Feature flag | 瞬间回滚 | 翻开关切回旧系统，业务无感 |
| Canary | 控制爆炸半径 | 按 user ID，5% 内部 → 100% |
| 冻结旧系统 | 压低并行维护成本 | 只修紧急 Bug，不加新功能 |
| 并行窗口 | 给验证留时间 | 约 2 周 |

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| feature flag | 特性开关 | A feature flag is a switch **that** routes traffic **without** redeploying code. |
| canary deployment | 灰度发布 | Canary deployment sends traffic to a small group **who** test the new system first. |
| fallback | 回退 | Fallback means sending users back **to** the old system **when** the new one fails. |
| blast radius | 爆炸半径 | A canary keeps the blast radius small **if** the release is bad. |
| parallel run | 并行运行 | During a parallel run, two systems serve production **while** cutover is validated. |
| ramp up | 逐步放量 | We ramp up traffic **after** internal users **who** hit critical paths report success. |

### 嵌套从句练习：解释切流方案

**Layer 2：**
> We route traffic through a feature flag **that** lets us fall back immediately.

**Layer 3：**
> **When** we cut over, we use a canary deployment **that** starts with 5% internal users, **so that** we can catch failures **before** they affect every customer.

**Layer 4 — 完整嵌套版：**
> **Although** rewriting takes months, production cannot stop, **which** is why we run both systems in parallel for about two weeks **while** a feature flag routes traffic by user ID through a canary **that** begins at 5% internal users — **a setup that** lets us flip back to the legacy system instantly **if** order creation breaks, **whereas** freezing new features on the old side keeps maintenance costs **that** the business worries about under control.

**中文对照：** 虽说重写要几个月，生产不能停，所以大约两周内双系统并行，用特性开关按 user ID 走金丝雀、先从 5% 内部用户开始——这样下单一旦出问题可以立刻切回遗留系统；同时旧系统冻结新功能，把业务担心的维护成本压住。

### 嵌套从句练习：说回滚

**Layer 4：**
> **If** the new system mishandles a critical path, we flip the feature flag **so that** all traffic returns to the legacy codebase **before** most users notice — **a rollback strategy that** depends on routing logic **that** was never hard-coded into either service.

**中文对照：** 若新系统搞砸了关键路径，我们就翻特性开关，让流量在大多数用户察觉之前回到遗留代码——这套回滚策略的前提是路由逻辑从未写死在任一服务里。

---

## 概念 3：隐性知识迁移——把历史故障变成测试

### 用自己的话理解（中英双语）

**中文：**

第二个追问更尖：没有测试所以重构危险——但重写就能自动有覆盖吗？旧代码里那些补丁、边界条件，是线上流血换来的**隐性知识**，重写时怎么不丢？

候选人先承认：重写本身不保证测试质量。但他指出，给 3000 行紧耦合大类**retrofit 测试**比 greenfield 上 TDD 难得多。重写的纪律是：从第一天 TDD，CI 卡 80% coverage；隐性知识靠**系统性复盘**——翻过去半年 bug 修复记录和事故 postmortem，每个场景都变成新代码里的**强制测试用例**。

这比靠老人记忆或零散文档靠谱：知识沉淀成可执行的测试，而不是 oral tradition。不完美，但比往烂代码上硬补测试更系统。

**English (B2):**

The second challenge is sharper: you said missing tests make refactoring dangerous — **but** does a rewrite automatically give you coverage? The legacy code embeds **implicit knowledge** in bug fixes and edge-case patches **that** were paid for in production pain. **How** do you carry that forward?

The candidate admits rewrite does not guarantee test quality by itself. However, **retrofitting tests onto** a 3,000-line tightly coupled class is much harder **than** practising TDD on a greenfield module. For the rewrite, the discipline is TDD from day one plus an 80% coverage gate in CI. For implicit knowledge, the team **systematically reviews** six months of bug-fix history and incident postmortems, **and** turns every identified scenario into a **mandatory test case** in the new codebase.

That approach is more reliable **than** hoping senior engineers remember every wart: knowledge becomes executable tests **rather than** oral tradition. It is not perfect, **but** it is more systematic **than** bolting tests onto code **that** was never designed **to be testable**.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| implicit knowledge | 隐性知识 | Implicit knowledge is behaviour **that** lives in patches **rather than** in docs. |
| incident postmortem | 事故复盘 | A postmortem is a review **that** records **what** failed and **why**. |
| mandatory test case | 强制测试用例 | Each postmortem scenario becomes a test **that** CI must not let regress. |
| TDD | 测试驱动开发 | TDD means writing a failing test **before** you write production code. |
| coverage gate | 覆盖率门禁 | A coverage gate blocks merges **that** drop below 80%. |
| greenfield | 从零新建 | A greenfield rewrite lets you design modules **that** are easy **to test**. |

### 嵌套从句练习：对比补测 vs TDD

**Layer 2：**
> Adding tests to old code is harder **than** starting fresh with TDD.

**Layer 3：**
> **Because** the legacy class couples many responsibilities, retrofitting unit tests is harder **than** writing them first in a rewrite **where** each module has a clear boundary.

**Layer 4 — 完整嵌套版：**
> **Although** rewriting does not automatically produce good tests, a greenfield module **that** follows TDD from day one is easier **to cover** **than** a 3,000-line class **whose** private methods share hidden state — **which** is why the candidate pairs TDD with a CI gate **that** rejects code **whose** coverage falls below 80%.

**中文对照：** 虽说重写不会自动带来好测试，但按 TDD 从零写的模块比那个私有方法共享隐藏状态的 3000 行类更容易覆盖——所以候选人把 TDD 和「覆盖率低于 80% 就拒合并」的 CI 门禁绑在一起。

### 嵌套从句练习：说隐性知识怎么沉淀

**Layer 4：**
> **To transfer** implicit knowledge **that** was buried in years of hotfixes, we reviewed bug records and postmortems **from** the last six months, **and** we turned every scenario **that** had hurt production into a mandatory test **that** the new service must pass **before** we trust the rewrite.

**中文对照：** 要把藏在多年热修复里的隐性知识迁过来，我们复盘了最近六个月的 bug 记录和事故复盘，把每个曾在生产上造成伤害的场景都变成新服务必须通过的强制测试，之后才敢信任这次重写。

---

## 概念 4：渐进式重构——安全网与模块化拆分

### 用自己的话理解（中英双语）

**中文：**

第三个追问：如果只能重构、不能重写，从哪开始？怎么拆 3000 行大类还不影响业务？

候选人两步走，绝不跳步：

**第一步，建安全网**——不动核心逻辑，先写覆盖关键路径的**集成测试**，只断言外部行为不变。这是后续所有手术的门禁。

**第二步，渐进提取**——在安全网保护下，找出最独立、最内聚的私有方法（订单号、税费计算等纯函数），用 IDE 的 Extract Class / Extract Method 抽到工具类或领域服务。每抽一次就跑全量测试，绿了才合并。

目标是把这个大类拆成十几个职责单一、可独立测试的小模块——体现**抽象/分层**和**模块化**：改一处不再牵动全局。整个过程是小步、可逆的微创，不是一次性开胸手术。候选人总结：**没有安全网，每次提取都是赌博**。

**English (B2):**

The third question assumes management says **no rewrite**: **where** do you start, and **how** do you break apart a 3,000-line class **without** disturbing the business?

The candidate insists on two steps **in strict order**.

**First, build a safety net** — do not touch core logic yet. Write **integration tests** **that** cover critical paths and assert only external behaviour. That suite becomes the gate **for** every later change.

**Second, extract incrementally** — under that protection, identify the most self-contained private methods, such as order-number generation or tax calculation, **which** behave like pure functions. Move them into utility classes or domain services using IDE refactorings such as Extract Method or Extract Class. After each extraction, run the full test suite; merge only **when** it stays green.

The end goal is modularization: roughly a dozen small modules **that** each own one concern and carry their own tests — **which** embodies layering and reduces coupling **so that** a local change no longer shakes the entire order flow. The process is a series of small, reversible steps, not one high-stakes surgery. **Without** the safety net, every extraction is a gamble.

### 重构三步对照表（复述）

| 步骤 | 做什么 | 为什么 |
| --- | --- | --- |
| 1. 安全网 | 集成测试覆盖关键路径 | 保证外部行为不变，后续改动有门禁 |
| 2. 提取 | 独立私有方法 → 工具类/领域服务 | 降耦合，大类变小 |
| 3. 小步合并 | 每次提取后跑全量测试 | 可逆、低风险，业务无感 |

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| safety net | 安全网 | A safety net is a test suite **that** guards external behaviour **while** internals change. |
| integration test | 集成测试 | Integration tests check paths **that** real users depend on. |
| critical path | 关键路径 | A critical path is a flow **that** must keep working **during** refactor. |
| extract | 提取 | We extract a method **that** has no hidden dependencies. |
| domain service | 领域服务 | A domain service holds logic **that** belongs to one business rule. |
| reversible | 可逆的 | Refactoring should stay reversible **until** tests prove the change is safe. |
| modularization | 模块化 | Modularization splits a god class into units **that** can be tested alone. |

### 嵌套从句练习：说为什么要先补测试

**Layer 2：**
> I would build a safety net **before** I touch core logic.

**Layer 3：**
> **Before** I extract anything, I would write integration tests **that** cover critical paths, **so that** external behaviour stays unchanged **while** the class shrinks.

**Layer 4 — 完整嵌套版：**
> **Although** the 3,000-line class looks tempting **to rewrite** in one shot, a safer refactor starts with integration tests **that** describe what customers must still see, **because** without that safety net every extraction becomes a gamble **that** could break production orders **that** depend on behaviour **the team no longer fully understands**.

**中文对照：** 虽说那个 3000 行类让人想一口气重写，更稳的重构先从集成测试开始——写清客户必须仍能看见的行为；没有这层安全网，每次提取都可能搞砸团队已不完全理解的生产订单行为。

### 嵌套从句练习：说渐进提取

**Layer 4：**
> **After** the safety net is green, I extract self-contained methods — such as tax calculation **that** does not reach into unrelated state — into domain services **that** own one concern, **and** I merge only **when** the full test suite passes, **which** lets the god class shrink **without** the business feeling a disruptive release.

**中文对照：** 安全网全绿之后，我把互不牵扯状态的自包含方法（比如税费计算）提取到只管一件事的服务里，只有全量测试通过才合并——这样上帝类慢慢变小，业务却感觉不到 disruptive 发布。

---

## 课堂对话套路（B2 + 嵌套从句）

### 套路 1：老师问"重写期间怎么切换"

> **When** we rewrite a system **that** still serves live orders, we run both versions in parallel for about two weeks **while** a feature flag routes traffic by user ID through a canary **that** starts at 5% internal users. **If** order creation breaks, we flip the flag **so that** traffic falls back to the legacy service **before** most customers notice — **a cutover plan that** is gradual, observable, and reversible.

---

### 套路 2：老师问"并行期间旧系统谁维护"

> During the parallel window, we **freeze new features** on the old system **and** allow only emergency bug fixes, **which** answers the business concern **that** a slipping rewrite would double maintenance forever. **Although** two codebases exist, we deliberately limit change on the legacy side **so that** engineers focus on the rewrite **rather than** feeding two product roadmaps.

---

### 套路 3：老师问"重写能保证测试吗 / 隐性知识怎么办"

> Rewriting does not magically create tests, **but** starting fresh with TDD is easier **than** retrofitting coverage onto a tightly coupled god class. **To preserve** implicit knowledge **that** lives in old bug fixes, we reviewed six months of incidents and turned every painful scenario into a mandatory test **that** CI enforces — **which** is more reliable **than** hoping engineers remember every edge case.

---

### 套路 4：老师问"只能重构你从哪开始"

> I would not touch core logic first. Instead, I would build a safety net of integration tests **that** lock external behaviour, **and then** I would extract self-contained methods into smaller modules, running the full suite after each step. **Without** that net, every extraction is a gamble; **with** it, refactoring becomes a series of small, reversible changes **that** the business never feels.

---

### 套路 5：老师问"模块化有什么好处"

> Modularization splits a 3,000-line class into focused units **that** each own one responsibility and carry their own tests, **which** reduces coupling **so that** a tax-rule change no longer risks order-ID generation. **That** is the maintainability payoff **that** pays down technical debt **without** requiring a risky big-bang rewrite.

---

### 套路 6：课上主动说话

| 你想做什么 | 嵌套从句版 |
| --- | --- |
| 确认理解 | So the safety net has **to** come **before** extraction, **because** integration tests guard behaviour **that** unit tests inside a god class cannot easily reach, **right**? |
| 请老师举例 | Could you give an example of implicit knowledge **that** was saved **only because** a postmortem became a test case? |
| 表示同意 | That makes sense — a feature flag gives rollback **that** does not depend on redeploying **when** the canary finds a bug. |
| 提出疑问 | **But** wouldn't two weeks of parallel run still be expensive **if** the rewrite slips by months? |
| 追问重构 | **When** you extract a method, how do you know **which** private functions are safe **to** move first? |
| 对比选型 | Is rewrite still worth it **when** management refuses **to** fund dual-system maintenance **during** cutover? |

---

## 常用句式：嵌套从句版（改写，非原文）

| 功能 | 嵌套从句句式 |
| --- | --- |
| 说切流 | **When** both systems run in parallel, we route traffic through a feature flag **that** supports canary rollout by user ID. |
| 说回滚 | **If** the new path fails, we flip the flag **so that** users return to the legacy system **before** the incident spreads. |
| 压并行成本 | We freeze features on the old system **so that** maintenance stays limited **to** emergencies **while** the rewrite continues. |
| 说隐性知识 | We turned postmortems into tests **that** CI must pass, **which** preserves knowledge **that** used to live only in patches. |
| 对比补测难度 | Retrofitting tests onto coupled legacy code is harder **than** practising TDD on modules **that** were designed **to be testable**. |
| 说安全网 | I would build integration tests **that** cover critical paths **before** I extract anything **that** could change behaviour. |
| 说渐进提取 | After each extraction, I run the full suite **and** merge only **when** external behaviour **that** customers rely on stays green. |
| 总结重构 | **Without** a safety net, refactoring is gambling; **with** it, each step is a reversible change **that** shrinks technical debt. |

---

## 老师可能追问 — 嵌套从句回答

| 老师问 | 你可以答 |
| --- | --- |
| Rewrite vs refactor? | Rewrite makes sense **when** retrofitting tests onto a god class is harder **than** greenfield TDD, **whereas** refactor is mandatory **when** the business cannot fund parallel production systems **during** cutover. |
| How long parallel? | About two weeks, **during which** a canary validates critical paths **before** we ramp to 100%. |
| What is a feature flag? | It is a runtime switch **that** routes traffic **without** redeploying, **which** makes rollback fast **if** the new code fails. |
| Why 5% internal first? | Internal users hit real flows **that** matter, **but** the blast radius stays small **if** something breaks. |
| Why not rewrite without tests? | **Because** implicit knowledge **that** lived in old bug fixes would disappear, **which** is why postmortems become mandatory tests. |
| What is TDD here? | We write failing tests first, **then** code, **and** CI blocks merges **whose** coverage drops below 80%. |
| Safety net vs unit tests? | Integration tests guard behaviour **that** customers see, **which** matters more **than** testing private methods **that** may move during extraction. |
| What to extract first? | Start with self-contained logic such as tax calculation **that** does not share hidden state with unrelated methods. |
| End goal of refactor? | Split the god class into small modules **that** each have independent tests, **so that** future changes stay local. |
| Why is safety net non-negotiable? | **Without** it, every extraction is a gamble **that** could break orders **that** production still depends on. |

---

## 跟读练习：五段 B2 嵌套从句（课前朗读 2 遍）

**Part 1 — 技术债务与选型**

> **When** a legacy order system becomes a 3,000-line class **that** has no unit tests, technical debt erodes maintainability **so that** every requirement change feels risky. The team must then choose between a rewrite **that** enforces TDD from day one **and** a refactor **that** builds a safety net **before** any structural change — **each path** carrying risks **that** a good interviewer will force you **to quantify**.

**Part 2 — 切换与回滚**

> **Although** rewriting takes time, production orders cannot pause, **which** is why we run old and new systems in parallel **while** a feature flag drives a canary rollout by user ID, starting with about 5% internal users. **If** creation or query paths fail, we flip the flag **so that** traffic returns to the legacy stack immediately, **whereas** freezing new work on the old system keeps parallel maintenance **from** growing without bound.

**Part 3 — 隐性知识**

> Rewriting does not automatically produce trustworthy tests, **but** retrofitting coverage onto tightly coupled legacy code is often harder **than** writing tests first in a cleaner design. **To preserve** implicit knowledge **that** was paid for in production incidents, we review bug history and postmortems **and** turn every painful scenario into a mandatory case **that** CI must not let regress.

**Part 4 — 安全网与提取**

> **If** management forbids a rewrite, I still would not touch core logic on day one. I would lock external behaviour with integration tests **that** cover critical paths, **and then** I would extract self-contained methods into focused modules, merging only **when** the full suite stays green — **a sequence in which** the safety net must come first **because** without it every extraction gambles with live orders.

**Part 5 — 模块化与总结**

> The end state is modularization: a dozen small units **that** each own one concern and ship their own tests, **which** pays down coupling **so that** local changes stop shaking the entire order flow. **Whether** you rewrite or refactor, the mature mindset is the same — choose a path **that** is gradual, observable, and reversible, **and** turn historical pain into tests **that** future engineers cannot accidentally delete.

---

## 附录：嵌套从句工具箱

| 从句类型 | 常用引导词 | 练法 |
| --- | --- | --- |
| **定语从句（限定）** | that, which, who, whose, where | 修饰名词：*a flag **that** routes traffic* |
| **定语从句（非限定）** | , which / , who | 补充信息：*…two weeks, **which** limits risk* |
| **时间 / 条件状语** | when, if, before, after, while | ***While** both systems run, …* |
| **原因 / 结果状语** | because, since, so that | *…tests first **so that** behaviour stays locked* |
| **对比 / 让步状语** | although, whereas, while | ***Although** rewrite sounds fast, cutover risk is real* |
| **嵌套技巧** | 从句套从句 | 主句 → 定语从句里再套 that/when/which |

**拆句口诀：** 先找主句主干 → 标出每个 that/which/when/because 引导的从句 → 从外往里读 → 再试着合并回去。

---

**课前最少记：** 3000 行无测试大类 · 并行 2 周 · 5% 内部 canary · feature flag 瞬间回滚 · TDD + 80% CI · 半年 bug/postmortem → 强制用例 · 先集成测试安全网再 Extract · 目标 ~12 小模块 · *Without a safety net, every extraction is a gamble.*
