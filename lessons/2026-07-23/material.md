# 【中级】Maintainability Interview: Rewrite vs Refactor — Taming a Legacy Order System

**技术等级：** T2 · **英语等级：** 中 · **字数：** ~500

**Source:** Interview / System Design  
**Level:** T2 / Intermediate  
**Role:** Interviewer, Candidate (2–5 years backend engineer)  
**Estimated Words:** ~488

---

## 故事 Prompt 及故事

```jsx
请根据以下系统设计知识点生成一个中文技术故事，用于后续英语教学。

知识点：[**1.3 可维护性**]
故事形式：一段面试场景对话，对话双方是面试官和候选人。
技术要求：T2难度（方案对比级），适合2-5年经验后端工程师。
故事冲突设定：
候选人所在团队接手了一个遗留订单系统——代码耦合严重，一个类 3000 行，没有单元测试，每次改需求都要加班修 Bug。他主张"重写整个模块"。面试官追问：凭什么重写比重构更划算？你评估过风险吗？

面试官追问链（必须严格遵循）：
1. "你说重写比重构快。但重写期间，旧系统还在线上跑着业务——新老系统怎么切换？你打算并行运行多久？如果重写进度延误，旧系统的维护成本还在，你怎么跟业务方交代？"
2. "你说没有单元测试所以重构风险大。但重写出来的新代码，你就能保证有测试覆盖吗？旧系统虽然没有测试，但那些 Bug 修复逻辑是血泪经验——重写时你打算怎么把这些隐性知识迁移过来？"
3. "如果你被要求只能重构不能重写，你会从哪开始？怎么在不影响业务的前提下逐步拆解那个 3000 行的大类？重构的安全网怎么建——先补测试还是先做结构拆分？"

【必须覆盖的核心概念】（来自核心层）：
 - 抽象/分层设计
 - 模块化的好处
 - 技术债务对可维护性的侵蚀

【可选延伸概念】（来自扩展层，T2 可不强制要求）：
- 代码整洁度、文档对可维护性的影响

候选人的回答要求：
- 给出重构 vs 重写的明确选型条件（什么情况下重写值得，什么情况下必须重构）
- 提出至少一种降低重构风险的手段（如灰度切流、特性开关、测试补齐）
- 说明从哪开始重构以及为什么

要求：故事简短，纯对话形式，字数350字。
生成完故事后，请用1-2句话说明你是如何通过追问实现方案对比深度的。
```

---

## Background

### 文章技术干点

这段面试对话触及了软件工程中一个经典难题：**如何安全地替换或改造一个正在运行的核心系统**。候选人并非空谈理论，而是给出了具体、可落地的工程方案，其技术深度体现在对切换风险、隐性知识迁移和遗留系统安全重构这三个核心挑战的应对上。

---

### 1. 系统切换：特性标志与金丝雀部署的组合拳

面试官的担忧很现实：新系统上线有风险，旧系统并行有成本。候选人用一套多层次的切换策略来解决：

- **特性标志（Feature Flag）**：将新旧系统的路由逻辑外置到一个开关中，而不是写死在代码里。这提供了**瞬间回滚**的能力——一旦新系统出问题，修改标志即可将所有流量切回旧系统，无需重新部署，业务零感知。
- **金丝雀部署（Canary Deployment）**：采用按 `user ID` 进行白名单导流。先从 **5% 的内部员工**开始，验证后再逐步扩大到全量。这实现了分阶段验证，让爆炸半径始终可控。
- **冻结旧系统**：并行期间，旧系统只修复严重 Bug，不再开发新功能。这直接回应了面试官关于维护成本的质疑——通过行政和技术手段，主动将维护成本降至最低。

---

### 2. 隐性知识迁移：将历史故障转化为强制测试

面试官的第二个问题更尖锐：**旧代码里那些线上踩过坑、打过硬补丁的隐式逻辑，如何确保在重写时不会丢失？**

候选人的应对方式很务实：

- **承认差异**：他坦诚"重写不能自动保证测试质量"，但明确指出，给一个耦合度高的大类补充测试，比从头写新代码时遵循 TDD 要难得多。
- **追溯故障经验**：他通过复盘过去半年的 **Bug 修复记录和事故复盘报告**，将那些用血泪教训换来的业务规则和边界条件显性化。
- **固化为测试用例**：将每一个历史故障场景，直接转化为新代码里的**强制性单元测试**。这比单纯靠开发者的记忆或文档传承要可靠得多，形成了一套可执行的知识沉淀机制。

---

### 3. 渐进式重构：以"安全网"为前提的模块化拆分

当被问到"如果被迫重构，你会怎么做"时，候选人给出了一套风险极低的渐进式重构策略：

- **第一步：建立测试安全网**

  他明确表示，**绝对不会直接动核心逻辑**。第一步是补写覆盖关键业务路径的集成测试。这份测试套件不关心代码内部怎么改，只保证**外部行为不变**，为后续所有修改提供了可靠的门禁。

- **第二步：自我分离与模块化**

  在安全网的保护下，他开始识别 `3000行大杂烩类` 中最独立、最内聚的私有方法（如生成订单号、税费计算等纯函数）。然后，通过重构工具（如 IDE 的 `Extract Class` 或 `Extract Method`），**自动地、安全地**将它们移入独立的工具类或领域服务中。

- **第三步：小步快跑**

  每次只做一个微小的迁移，然后立即运行测试。全绿则合并代码到主干。这个过程是可逆、低风险的"微创手术"，而非一次性的"高风险大手术"。通过无数次这样的微操作，臃肿的单体类最终会自然演化为多个专注、可独立测试的小模块。

---

**总结**：这次面试展现了处理遗留系统的成熟工程思维：不是简单地判"重写"或"重构"死刑，而是根据具体的业务风险和团队能力，选择一条用**可灰度、可监控、可回滚**的手段保障的演进路径，并制定出将历史经验固化为测试用例的实操方法。

---

## 角色及场景

**Interviewer (面试官):** 考察候选人对可维护性和技术债务治理的理解，重点追问重写与重构的决策依据、风险控制和渐进式重构策略。

**Candidate (候选人):** 2-5年经验后端工程师，曾接手一个3000行类的遗留订单系统，主张在特定条件下重写，并能清晰阐述重构的备选方案。

**场景:** 面试。候选人面对一个代码严重耦合、缺乏单元测试的遗留系统，提出"重写整个模块"。面试官通过三轮追问，逼出候选人对新老系统切换、隐性知识迁移和渐进式重构的完整思考。

---

## 面试对话 (中级，正文约 488 词)

**Interviewer:**

You said rewriting is faster than refactoring. But during the rewrite, the old system is still running in production. **How do you switch between the old and new systems? How long would you run them in parallel?** If the rewrite **slips**, the old system still incurs maintenance costs—how do you explain that to the business side?

**Candidate:**

We plan to use a feature flag to control the **cutover**. Both systems run in parallel for two weeks, with traffic routed by user ID via a canary deployment. We start with 5% internal users, verify that order creation and queries work correctly, then gradually ramp up to 100%. If the new system has issues, we flip the flag and immediately fall back to the old system—zero business impact. During the parallel run, the old system only receives emergency bug fixes, no new features, so the maintenance cost is manageable.

**Interviewer:**

Alright. You also said refactoring is risky because there are no unit tests. But rewriting doesn't automatically guarantee test coverage either. The old system may lack tests, but those bug fixes embedded in it are **hard-won** experience. **How do you plan to transfer that implicit knowledge into the rewrite?**

**Candidate:**

I admit rewriting doesn't guarantee test quality by itself. But adding tests to a 3,000-line class with a dozen tightly coupled methods is harder than starting fresh. **During the rewrite, we enforce TDD from day one**—write the test first, then the code, and set an 80% coverage gate in CI. For implicit knowledge, we **systematically reviewed the last six months of bug fix records and incident postmortems. Every one of those scenarios becomes a mandatory test case** in the new code. It's not perfect, but it's more systematic than retrofitting tests onto the old codebase.

**Interviewer:**

Fair. But **if you were forced to refactor instead of rewrite, where would you begin? How would you break down that 3,000-line class without disrupting the business?**

**Candidate:**

I'd start with two things. First, I wouldn't touch any core logic. Instead, I'd build a test safety net—integration tests covering the critical paths, ensuring external behavior stays unchanged. Second, I'd identify the most self-contained private methods inside that class—like order number generation or tax calculation—and extract them into dedicated utility classes or domain services. After each extraction, I run the full test suite. If it passes, I merge. This way, the class shrinks step by step under the protection of the safety net, and the business never feels a thing. The end goal is to split the core order class into a dozen small, focused modules, each with its own independent tests.

**Interviewer:**

That's a clear roadmap. **So you essentially create a safety net first, then extract and modularize incrementally**.

**Candidate:**

Exactly. The safety net is non-negotiable. Without it, every extraction is a gamble. With it, refactoring becomes a series of small, safe, reversible steps rather than one high-stakes surgery.

---

## 词汇表 (25个高频技术词汇)

| **Vocabulary** | **Pronunciation (IPA)** | **Chinese Meaning** |
| --- | --- | --- |
| legacy system | /ˈleɡəsi ˈsɪstəm/ | 遗留系统 |
| refactoring | /ˌriːˈfæktərɪŋ/ | 重构 |
| rewrite | /ˈriːraɪt/ | 重写 |
| feature flag | /ˈfiːtʃər flæɡ/ | 特性开关 |
| canary deployment | /kəˈneəri dɪˈplɔɪmənt/ | 灰度发布 |
| fallback | /ˈfɔːlbæk/ | 回退/降级 |
| unit test | /ˈjuːnɪt test/ | 单元测试 |
| TDD (Test-Driven Development) | /ˌtiː diː ˈdiː/ | 测试驱动开发 |
| coverage | /ˈkʌvərɪdʒ/ | 覆盖率 |
| CI (Continuous Integration) | /ˌsiː ˈaɪ/ | 持续集成 |
| implicit knowledge | /ɪmˈplɪsɪt ˈnɒlɪdʒ/ | 隐性知识 |
| bug fix | /bʌɡ fɪks/ | Bug修复 |
| incident postmortem | /ˈɪnsɪdənt pəʊstˈmɔːtəm/ | 事故复盘 |
| integration test | /ˌɪntɪˈɡreɪʃən test/ | 集成测试 |
| critical path | /ˈkrɪtɪkəl pæθ/ | 关键路径 |
| extract | /ɪkˈstrækt/ | 提取（方法/类） |
| utility class | /juːˈtɪləti klæs/ | 工具类 |
| domain service | /dəˈmeɪn ˈsɜːrvɪs/ | 领域服务 |
| modularization | /ˌmɒdjʊləraɪˈzeɪʃən/ | 模块化 |
| coupling | /ˈkʌplɪŋ/ | 耦合 |
| tight coupling | /taɪt ˈkʌplɪŋ/ | 紧耦合 |
| technical debt | /ˈteknɪkəl det/ | 技术债务 |
| safety net | /ˈseɪfti net/ | 安全网 |
| test suite | /test swiːt/ | 测试套件 |
| reversible | /rɪˈvɜːrsəbəl/ | 可逆的 |

---

## 句式提炼

| **功能** | **英文句式** | **适用场景** |
| --- | --- | --- |
| 描述灰度切流方案 | *"We route traffic by user ID via a canary deployment, starting with X% internal users and gradually ramping up."* | 解释新老系统切换策略 |
| 快速回退 | *"If the new system has issues, we flip the flag and immediately fall back to the old system—zero business impact."* | 说明特性开关的回退能力 |
| 隐性知识迁移 | *"We systematically reviewed bug fix records and incident postmortems, and every scenario became a mandatory test case."* | 解释如何将经验转化为测试 |
| 对比测试难度 | *"Adding tests to a tightly coupled class is harder than starting fresh with TDD."* | 对比重写与重构的测试成本 |
| 建立测试安全网 | *"I'd build a test safety net—integration tests covering the critical paths—before touching any core logic."* | 描述重构的第一步 |
| 渐进式提取 | *"I'd identify self-contained methods and extract them into dedicated classes, running the full test suite after each extraction."* | 描述逐步拆解大类的过程 |

---

## 阅读理解题

1. How does the candidate plan to switch between the old and new systems during the rewrite?

   **Answer:** By using a feature flag and canary deployment, routing traffic by user ID, starting with 5% internal users, and gradually ramping up to 100%. If issues occur, the flag is flipped to fall back immediately.

2. Why does the candidate believe rewriting with TDD is more effective than adding tests to the old codebase?

   **Answer:** Because adding tests to a 3,000-line tightly coupled class is extremely difficult, while starting fresh with TDD and an 80% CI coverage gate is more systematic. Implicit knowledge from past bug fixes is converted into mandatory test cases.

3. How does the candidate plan to transfer implicit knowledge from the old system into the rewrite?

   **Answer:** By systematically reviewing the last six months of bug fix records and incident postmortems, and making every identified scenario a mandatory test case in the new code.

4. What are the first two steps the candidate would take if forced to refactor instead of rewrite?

   **Answer:** First, build a test safety net with integration tests covering critical paths. Second, identify self-contained methods and extract them into dedicated utility classes or domain services, running the full test suite after each extraction.

5. What is the end goal of the incremental refactoring approach described by the candidate?

   **Answer:** To split the core order class into a dozen small, focused modules, each with its own independent tests, achieving modularization without disrupting the business.

---

*Word count (dialogue): ~488 words*  
*Level: Intermediate / T2*
