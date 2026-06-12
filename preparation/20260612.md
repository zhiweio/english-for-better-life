## **Section 1: 传统数据质量工具：Deequ**

**英文原文**

> **1. Traditional Data Quality Tool: Deequ**
>
> - **Definition**: An open-source library based on Spark DataFrames that allows declarative definition of quality checks (e.g., `amount >= 0`, `order_id is not null`), easily embedded in pipelines.
> - **Strengths**: Reliable, controllable, version-manageable, suitable as a quality gate in production environments.
> - **Pain point**: Every rule must be handwritten manually, which is time-consuming and can only validate known issues, remaining completely passive against unknown data problems.

**参考译文**

> **1. 传统数据质量工具：Deequ**
>
> - **定义**：一个基于 Spark DataFrames 的开源库，允许用声明式方式定义质量检查（如 `amount >= 0`、`order_id is not null`），管线嵌入方便。
> - **优势**：可靠、可控、可版本化管理，适合作为生产环境的质量门禁。
> - **痛点**：每条规则都需人工手写，耗时且只能校验已知问题，对未知数据问题完全被动。

| 词汇 / 短语 | 含义 | 口译提示 |
|---|---|---|
| **open-source library** | 开源库 | 固定搭配，library 译"库"而非"图书馆" |
| **Spark DataFrames** | Spark 数据框 | 保留 Spark，DataFrame 可译"数据框"或保留英文 |
| **declarative definition** | 声明式定义 | 编程范式术语，declarative = 声明式（vs imperative 命令式） |
| **quality checks** | 质量检查 | check 此处作名词，= 检查项 |
| **amount >= 0** | 金额大于等于零 | 口译时读出符号或描述含义均可 |
| **order_id is not null** | 订单 ID 非空 | null 译"空值" |
| **embedded in pipelines** | 嵌入管线 | pipeline 数据语境译"管线"或"流水线" |
| **reliable, controllable** | 可靠、可控 | 形容词成对出现，口译保持节奏 |
| **version-manageable** | 可版本化管理 | 或译"可版本控制"，manageable = 可管理的 |
| **quality gate** | 质量门禁 | 指进入下一阶段的准入门槛 |
| **production environments** | 生产环境 | 区别于 dev / test / staging |
| **handwritten manually** | 人工手写 | 强调 manual，口译可加重"手工" |
| **time-consuming** | 耗时的 | 常作形容词用 |
| **validate known issues** | 校验已知问题 | validate = 验证、校验 |
| **remain completely passive** | 完全被动 | remain + 形容词 = 保持某种状态 |
| **unknown data problems** | 未知数据问题 | unknown = 未知的，与 known 相对 |

**长句拆解**

> **原句**：Every rule must be handwritten manually, which is time-consuming and can only validate known issues, remaining completely passive against unknown data problems.
>
> **结构**：主句 + 非限定定语从句 + 现在分词短语（表伴随结果）
>
> **口译版本**：每条规则都得人工手写，这既耗时，又只能校验那些已知的问题；面对未知的数据问题，它完全是被动的，束手无策。
>
> **提示**：三个修饰成分 stacked，口译时用"这既…又…"拆分前半，再用"面对…"引出后半，避免一口气太长。

---

## **Section 2: AI 驱动的数据质量平台**

**英文原文**

> **2. AI-Driven Data Quality Platform**
>
> - **Capability**: Not just executing rules, but **automatically discovering rules**. It autonomously recommends validation rules through data profiling, statistical distribution analysis, and anomaly detection.
> - **Actual effect in the dialogue**: When trialled on the historical order table, it quickly discovered a serious data integrity problem—"negative amounts"—that existing checks had missed.
> - **Output**: Not only flags anomalies, but also generates diagnostic SQL snippets, suggested quality constraints, and attaches a confidence score to each recommended rule.

**参考译文**

> **2. AI 驱动的数据质量平台**
>
> - **能力**：不只是执行规则，而是**自动发现规则**。它通过数据画像、统计分布分析、异常检测，自主推荐验证规则。
> - **对话中的实际效果**：在历史订单表上试用时，快速发现了"负金额"这种现有检查都遗漏了的严重数据完整性问题。
> - **输出**：不仅标记异常，还生成诊断 SQL 片段、建议的质量约束，并附上每条推荐规则的置信度分数。

| 词汇 / 短语 | 含义 | 口译提示 |
|---|---|---|
| **AI-driven** | AI 驱动的 | driven = 由…驱动，常见组合 |
| **automatically discovering rules** | 自动发现规则 | 与 executing rules 形成对比 |
| **data profiling** | 数据画像 | profiling = 画像、剖析，数据术语 |
| **statistical distribution analysis** | 统计分布分析 | 三个词 stacked，口译可稍作停顿 |
| **anomaly detection** | 异常检测 | anomaly = 异常、反常 |
| **autonomously recommends** | 自主推荐 | autonomously = 自主地、自动地 |
| **validation rules** | 验证规则 | validate 的名词形式 |
| **trialled on** | 在…上试用 | trial 作动词 = 试用、试验 |
| **historical order table** | 历史订单表 | 指存量数据表 |
| **negative amounts** | 负金额 | 指金额为负数，业务上通常非法 |
| **data integrity problem** | 数据完整性问题 | integrity = 完整性（数据质量核心维度） |
| **existing checks** | 现有检查 | 指已有的规则校验 |
| **had missed** | 遗漏了 | miss = 错过、遗漏 |
| **flags anomalies** | 标记异常 | flag = 做标记（动词） |
| **diagnostic SQL snippets** | 诊断 SQL 片段 | diagnostic = 诊断的，snippet = 片段 |
| **suggested quality constraints** | 建议的质量约束 | constraint = 约束、限制 |
| **confidence score** | 置信度分数 | 统计/ML 术语，confidence = 置信度 |
| **recommended rule** | 推荐规则 | 指 AI 推荐的候选规则 |

**长句拆解**

> **原句**：When trialled on the historical order table, it quickly discovered a serious data integrity problem—"negative amounts"—that existing checks had missed.
>
> **结构**：When 分词短语 + 主句 + 插入语（同位语）+ 定语从句
>
> **口译版本**：在历史订单表上试用的时候，它很快发现了一个严重的数据完整性问题——也就是"负金额"——这个问题是现有检查都遗漏掉的。
>
> **提示**：破折号插入语口译时用"也就是…"或"即…"过渡，定语从句 that…had missed 可独立成句，避免头重脚轻。

---

## **Section 3: 混合架构：AI 当侦探，Deequ 当守卫**

**英文原文**

> **3. Hybrid Architecture: AI as Detective, Deequ as Guard**
>
> This is the core design of the entire solution:
>
> - **AI (exploration / detective)**: Performs large-scale scanning of historical snapshots in an offline environment, discovering unknown, hidden data problems and generating a candidate rule library.
> - **Deequ (execution / guard)**: After manual review, confirmed stable rules are hardened into hard-coded Deequ checks, embedded in production ETL pipelines and executed on schedule.
> - **Division of labour logic**: AI is responsible for speed and breadth (rapid discovery), while Deequ is responsible for reliability and stability (long-term execution).

**参考译文**

> **3. 混合架构：AI 当侦探，Deequ 当守卫**
>
> 这是整个方案的核心设计：
>
> - **AI（探索/侦探）**：在离线环境对历史快照进行大规模扫描，发现未知的、隐蔽的数据问题，生成候选规则库。
> - **Deequ（执行/守卫）**：经过人工审核后，将确认的稳定规则固化为硬编码的 Deequ 校验，嵌入生产 ETL 管线，按计划执行。
> - **分工逻辑**：AI 负责速度与广度（快速发现），Deequ 负责可靠与稳定（长期执行）。

| 词汇 / 短语 | 含义 | 口译提示 |
|---|---|---|
| **hybrid architecture** | 混合架构 | hybrid = 混合的，常指两种技术结合 |
| **core design** | 核心设计 | 指方案的核心理念 |
| **exploration / detective** | 探索/侦探 | 比喻用法，口译保留形象感 |
| **large-scale scanning** | 大规模扫描 | 指对大量数据的批量分析 |
| **historical snapshots** | 历史快照 | snapshot = 快照，指某一时刻的数据镜像 |
| **offline environment** | 离线环境 | 区别于 online / production |
| **hidden data problems** | 隐蔽的数据问题 | hidden = 隐蔽的、隐藏的 |
| **candidate rule library** | 候选规则库 | candidate = 候选的，待确认的 |
| **manual review** | 人工审核 | review = 审查、审核 |
| **confirmed stable rules** | 确认的稳定规则 | confirmed = 经确认的，stable = 稳定的 |
| **hardened into** | 固化为 | harden = 硬化、固化，技术语境指"确定下来" |
| **hard-coded** | 硬编码的 | 与 configurable / dynamic 相对 |
| **embedded in** | 嵌入 | 指集成到现有系统中 |
| **production ETL pipelines** | 生产 ETL 管线 | 强调 production 环境 |
| **executed on schedule** | 按计划执行 | on schedule = 按计划、准时 |
| **division of labour logic** | 分工逻辑 | division of labour = 分工 |
| **speed and breadth** | 速度与广度 | breadth = 广度，与 depth 深度相对 |
| **rapid discovery** | 快速发现 | rapid = 快速的 |
| **reliability and stability** | 可靠与稳定 | 成对出现，口译保持对称 |
| **long-term execution** | 长期执行 | 强调持续性 |

**长句拆解**

> **原句**：After manual review, confirmed stable rules are hardened into hard-coded Deequ checks, embedded in production ETL pipelines and executed on schedule.
>
> **结构**：After 介词短语 + 主句 + 两个过去分词短语（并列，表被动）
>
> **口译版本**：经过人工审核之后，那些确认稳定的规则会被固化成硬编码的 Deequ 校验项，嵌入到生产的 ETL 管线里，并按计划执行。
>
> **提示**：三个被动动作 stacked，口译时用"被…并…"串联，或拆成"先…再…最后…"体现时间顺序。

---

## **Section 4: AI 规则的局限性及人工审查的必要性**

**英文原文**

> **4. Limitations of AI Rules & Necessity of Manual Review**
>
> - **Limitations**: AI-recommended rules may be "too noisy" (high false-positive rate) or detached from business context (e.g., certain anomalies that are technically abnormal but business-permitted).
> - **Review process**: Every candidate rule must be assessed by the data owner for coverage, false-positive rate, and business meaning. Only after passing can it be hardened into a Deequ check. This ensures automation does not sacrifice reliability.

**参考译文**

> **4. AI 规则的局限性及人工审查的必要性**
>
> - **局限性**：AI 推荐的规则可能"太吵"（误报率高）或脱离业务上下文（如某些虽然异常但业务上允许的情况）。
> - **审查流程**：每条候选规则必须由数据负责人评估其覆盖率、误报率、业务含义，通过后才能固化为 Deequ 校验。这保证了自动化不牺牲可靠性。

| 词汇 / 短语 | 含义 | 口译提示 |
|---|---|---|
| **too noisy** | 太吵 | 比喻用法，指误报太多，口译可保留引号或解释 |
| **high false-positive rate** | 高误报率 | false positive = 假阳性、误报 |
| **detached from business context** | 脱离业务上下文 | detached = 脱离的、分离的 |
| **technically abnormal** | 技术上异常 | technically = 从技术角度看 |
| **business-permitted** | 业务上允许的 | 指业务规则允许的特殊情况 |
| **candidate rule** | 候选规则 | 待审核的推荐规则 |
| **data owner** | 数据负责人 | 指对数据质量负责的人 |
| **assessed for** | 评估其… | assess = 评估、评定 |
| **coverage** | 覆盖率 | 指规则覆盖的数据范围 |
| **false-positive rate** | 误报率 | 再次出现，核心指标 |
| **business meaning** | 业务含义 | 指规则在业务上的合理性 |
| **passing** | 通过（审核） | 指审核通过 |
| **hardened into a Deequ check** | 固化为 Deequ 校验 | 同前文 hardened into |
| **sacrifice reliability** | 牺牲可靠性 | sacrifice = 牺牲，reliability = 可靠性 |

**长句拆解**

> **原句**：Every candidate rule must be assessed by the data owner for coverage, false-positive rate, and business meaning, only after passing can it be hardened into a Deequ check.
>
> **结构**：主句（被动）+ 三个并列评估维度 + 倒装句（only after…can…）
>
> **口译版本**：每条候选规则都必须由数据负责人来评估——看它的覆盖率、误报率，还有业务含义——只有通过了，才能被固化成 Deequ 的校验项。
>
> **提示**：only after…can 倒装口译时不必保留倒装，按中文语序"只有…才能…"自然处理。三个并列维度用破折号或"看它的…"来拆解。

---

## **Section 5: 管线集成与 CI 化**

**英文原文**

> **5. Pipeline Integration & CI-isation**
>
> - **Proposal**: Integrate the final confirmed Deequ rules into the **CI pipeline**. This is the critical step in engineering data quality, ensuring that every ETL change or data landing triggers automatic quality checks. Failures block or alert, achieving a "data gate".
> - **Documentation**: Every rule must record the covered scenario, false-positive rate, and business rationale, forming an auditable quality asset.

**参考译文**

> **5. 管线集成与 CI 化**
>
> - **提案**：将最终确认的 Deequ 规则集成到 **CI 管道** 中。这是数据质量工程化的关键一步，确保每次 ETL 变更或数据落地时，质量检查自动运行，不通过则阻断或告警，实现"数据门禁"。
> - **文档化**：每条规则需记录覆盖场景、误报率、业务理由，形成可审计的质量资产。

| 词汇 / 短语 | 含义 | 口译提示 |
|---|---|---|
| **pipeline integration** | 管线集成 | 指与现有数据管线整合 |
| **CI-isation** | CI 化 | 非标准造词，指纳入 CI 流程，口译可译"持续集成化" |
| **CI pipeline** | CI 管道 / 持续集成管道 | CI = Continuous Integration |
| **critical step** | 关键一步 | critical = 关键的、至关重要的 |
| **engineering data quality** | 数据质量工程化 | engineering 此处作动词用 = 工程化 |
| **ETL change** | ETL 变更 | 指 ETL 代码或逻辑的改动 |
| **data landing** | 数据落地 | 指数据到达、写入目标系统 |
| **triggers automatic quality checks** | 触发自动质量检查 | trigger = 触发 |
| **failures block or alert** | 不通过则阻断或告警 | failure = 检查失败的情况 |
| **data gate** | 数据门禁 | 同前文 quality gate |
| **documentation** | 文档化 | 指形成文档记录 |
| **covered scenario** | 覆盖场景 | 指规则适用的业务场景 |
| **business rationale** | 业务理由 / 业务依据 | rationale = 根本原因、依据 |
| **auditable quality asset** | 可审计的质量资产 | auditable = 可审计的，asset = 资产 |

**长句拆解**

> **原句**：This is the critical step in engineering data quality, ensuring that every ETL change or data landing triggers automatic quality checks.
>
> **结构**：主句 + 现在分词短语（ensuring that…）
>
> **口译版本**：这是把数据质量真正工程化的关键一步，它能确保每次 ETL 发生变更，或者新数据落地的时候，质量检查都会自动触发。
>
> **提示**：engineering 作动名词用，口译时补全为"把…工程化"或"让…实现工程化"。every ETL change or data landing 两个并列主语，口译时用"或者"分隔，避免混淆。

---

## **Section 6: 实施路径：分阶段推进**

**英文原文**

> **6. Implementation Path: Phased Rollout**
>
> 1. **Offline exploration**: Set up the AI tool in a non-production environment, run scanning against the order table snapshot, and generate a candidate rule catalogue.
> 2. **Joint review**: Review recommended anomalies and rules together with the analytics team, filtering out valuable, low-noise items.
> 3. **Hard-coded deployment**: Translate passed rules into Deequ code and formally incorporate them into production Spark ETL jobs.

**参考译文**

> **6. 实施路径：分阶段推进**
>
> 1. **离线探索**：在非生产环境搭建 AI 工具，对订单表快照运行扫描，生成候选规则目录。
> 2. **联合评审**：与分析团队一起审查推荐的异常和规则，筛选出有价值、低噪音的部分。
> 3. **硬编码部署**：将通过的规则翻译成 Deequ 代码，正式纳入生产 Spark ETL 作业。

| 词汇 / 短语 | 含义 | 口译提示 |
|---|---|---|
| **phased rollout** | 分阶段推进 / 分阶段推出 | phased = 分阶段的，rollout = 推出实施 |
| **offline exploration** | 离线探索 | 指在非生产环境试验 |
| **non-production environment** | 非生产环境 | 即 dev / test / staging |
| **set up** | 搭建 | 指安装配置工具 |
| **run scanning against** | 对…运行扫描 | against = 针对 |
| **order table snapshot** | 订单表快照 | 同前文 historical snapshot |
| **candidate rule catalogue** | 候选规则目录 | catalogue = 目录、清单 |
| **joint review** | 联合评审 | joint = 联合的、共同的 |
| **analytics team** | 分析团队 | 指数据分析师团队 |
| **recommended anomalies** | 推荐的异常 | 指 AI 检测出的异常项 |
| **filtering out** | 筛选出 | filter out = 过滤出、筛选出 |
| **valuable, low-noise items** | 有价值、低噪音的部分 | 指高价值且误报少的规则 |
| **hard-coded deployment** | 硬编码部署 | 指固化后正式部署 |
| **translate…into** | 把…翻译成… | 此处指代码转换 |
| **formally incorporate** | 正式纳入 | incorporate = 纳入、整合 |
| **production Spark ETL jobs** | 生产 Spark ETL 作业 | job 数据语境译"作业" |

**长句拆解**

> **原句**：Set up the AI tool in a non-production environment, run scanning against the order table snapshot, and generate a candidate rule catalogue.
>
> **结构**：三个并列祈使句
>
> **口译版本**：先在非生产环境里把 AI 工具搭起来，然后针对订单表的快照跑一遍扫描，最后生成一份候选规则的目录。
>
> **提示**：三个动作链，口译时用"先…然后…最后…"体现时序，避免平铺直叙。

---

## **总结段**

**英文原文**

> **Summary**: The core value of this discussion is that **AI was not allowed to directly "go on duty" to execute critical tasks, but was placed in the "discovery" phase—a front-end link more suited to it**. AI is used to rapidly break through the blind spots of human-written rules, and then a mature rule engine is used as the final quality safety net. This finds a pragmatic balance between efficiency and stability.

**参考译文**

> **总结**：这次讨论的核心价值在于，**没有让 AI 直接"上岗"执行关键任务，而是将其安放在"发现"这个更适合它的前置环节**。利用 AI 快速突破人工规则的认知盲区，再用成熟的规则引擎做最终的质量兜底，在效率与稳定之间找到了一个务实的平衡点。

| 词汇 / 短语 | 含义 | 口译提示 |
|---|---|---|
| **go on duty** | 上岗 | 比喻用法，保留引号 |
| **front-end link** | 前置环节 | 指流程中的前端步骤 |
| **break through blind spots** | 突破盲区 | blind spot = 盲区、盲点 |
| **human-written rules** | 人工编写的规则 | 同 handwritten rules |
| **cognitive blind spots** | 认知盲区 | cognitive = 认知的 |
| **mature rule engine** | 成熟的规则引擎 | mature = 成熟的 |
| **final quality safety net** | 最终的质量兜底 | safety net = 安全网，口译可意译"兜底" |
| **pragmatic balance** | 务实的平衡 | pragmatic = 务实的、实用的 |
| **efficiency and stability** | 效率与稳定 | 核心权衡维度 |

**长句拆解**

> **原句**：AI was not allowed to directly "go on duty" to execute critical tasks, but was placed in the "discovery" phase—a front-end link more suited to it.
>
> **结构**：被动语态 + but 转折 + 插入语（同位语）
>
> **口译版本**：没有让 AI 直接去"上岗"执行那些关键任务，而是把它放在了"发现"这个阶段——这是一个更前置、也更适合它的环节。
>
> **提示**：两个被动语态 stacked，口译时转为主动"没有让…而是把…"，更符合中文。破折号插入语用"也就是…"或"这是…"来过渡。

---

## **附录：口译高频衔接词与句型速查**

| 英文表达 | 口译推荐译法 | 适用场景 |
|---|---|---|
| From the outset | 从一开始 / 起初 | 时间起点 |
| Not just… but… | 不只是…而是… | 递进强调 |
| This is the core design | 这是核心设计 | 引出重点 |
| Division of labour logic | 分工逻辑 | 解释架构 |
| Only after… can… | 只有…才能… | 条件强调 |
| Ensuring that… | 确保… | 目的说明 |
| Phased rollout | 分阶段推进 | 实施计划 |
| The core value lies in… | 核心价值在于… | 总结观点 |
| Find a pragmatic balance | 找到务实的平衡 | 评价方案 |
| Break through blind spots | 突破盲区 | 描述 AI 价值 |

---

以上语料按原文 6 个 section + 总结段完整对应，词汇和句子都保留了原文措辞。课堂上如果老师突然跳到某一段，你可以直接定位到对应 section，不会没词儿。