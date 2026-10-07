# Reliability Interview – Calculating Nines and Designing for Failure

**Source:** Interview / System Design
**Level:** T2 / Intermediate
**Role:** Interviewer, Candidate (2–5 years backend engineer)
**Estimated Words:** ~506

---

## Background

### 故事 Prompt 及故事

**Prompt**

请根据以下系统设计知识点生成一个中文技术故事，用于后续英语教学。

知识点：[1.1 可靠性]

故事形式：一段面试场景对话，对话双方是面试官和候选人。

技术要求：T2难度（方案对比级），适合2-5年经验后端工程师。

故事冲突：围绕面试中的常见追问展开——[如何量化可靠性？几个9是怎么算出来的？]

【必须覆盖的核心概念】：

- 硬件/软件/人为故障类型
- 容错基本手段（冗余、重试）
- 几个9的可用性换算

要求：故事简短，纯对话形式，字数350字。确保对话中自然包含以上所有核心概念。

**故事**

面试官在白板上写下"99.99%"，转身问道："简历上写了订单系统四个九的SLA。先说说，这个数字怎么算出来的？"

"一年8760个小时，99.99%允许故障52分钟。99.9%是8.76小时——差一个9，差了十倍。"

"那你们去年实际花了多少分钟？"

"两次故障，18分钟。一次是数据库主库磁盘坏道，从库自动切主，中断3分钟。做了RAID 10加主从复制，冗余到位，恢复很快。"

"3分钟确实不错。第二次呢？"

"第二次不是硬件问题。配置中心改了支付回调URL，两个服务读到不同缓存版本，下游超时15分钟。这是人为变更引发的故障，冗余根本防不住。"

"那这种人为故障怎么防？"

"事后我们加了两道防线：所有配置变更必须走预发环境验证，再灰度发布。硬件故障靠冗余，软件和人为故障就得靠流程——重试、校验、发布审批，每一道都是容错手段。"

面试官点点头："最后一个问题。产品经理想把SLA提到99.999%，全年故障不超过5分钟。你评估一下？"

"五个九要多活架构，成本至少翻一倍。我建议支付链路做五个九，订单查询保持四个九。不是所有服务都值得花这个钱——分级管理，把钱花在刀刃上。"

面试官在笔记上划了一道线。

### 核心概念覆盖说明

- **故障类型（硬件/软件/人为）**：通过磁盘坏道（硬件）和配置错误（人为/软件）两个真实案例自然区分。
- **容错基本手段（冗余、重试）**：硬件故障通过 RAID 10 + 主从复制（冗余）应对；人为故障通过灰度发布和校验（流程 + 重试）应对。
- **几个9的可用性换算**：开篇直接计算 99.99% 与 99.9% 的故障时间差异，结尾引入 99.999% 的成本权衡。

### 文章技术干点

这次面试问答精准地拆解了高可用性（SLA）的四个递进层次：**量化定义、故障分类、纵深防御、成本权衡**，体现了从理论到实践的完整闭环。

#### 1. 可用性的数学与业务含义

- **四个九的计算**：`365 × 24 × 60 × (1 - 0.9999) ≈ 52.56` 分钟，这是全年允许的总宕机时长。每一个"9"意味着停机时间缩短一个数量级，也意味着系统复杂度和成本指数级上升。
- **价值**：SLA 不是空洞的口号，而是精确到分钟的设计约束。所有架构决策必须倒推是否满足这个停机预算。

#### 2. 故障模式分析：硬件 vs 人为

**事件一：硬件故障（磁盘损坏）——3 分钟恢复**

- **冗余设计**：
  - 磁盘级：RAID 10 提供单盘容错。
  - 数据库级：主从复制 + 自动故障转移，从库检测到主库异常后接管写入，切换约 3 分钟。
- **可观测性驱动恢复**：监控系统持续追踪**复制延迟**和**磁盘健康指标**。当主库写入延迟飙升，秒级告警触发，运维在用户感知前已介入。这是"快速发现"支撑"快速恢复"的典范。

**事件二：人为失误（配置不同步）——15 分钟恢复**

- **根因**：配置中心更新了支付回调 URL，但多个服务在同一时刻读取到新旧不同版本，造成调用链断裂。
- **教训**：冗余对物理故障有效，但对逻辑/人为错误完全无效。这是一个纯粹的流程缺陷——变更缺少校验与灰度机制。

#### 3. 纵深防御：流程与代码双重兜底

针对人为失误，候选人提出了三道防线：

- **第一道：预发强制校验**。任何配置变更必须先经过 Staging 环境验证，形成硬性流程节点，阻断未验证的变更流入生产。
- **第二道：金丝雀发布**。即使通过预发，变更也只在极小比例流量上先验证，监控错误率，确认无误再全量。这是用最小爆炸半径换取快速回滚的机会。
- **第三道：代码层容错**。为下游调用引入**指数退避重试**。当下游服务因配置错误等瞬断时，调用端通过逐渐拉长的等待间隔自动重试，避免瞬时失败雪崩为全链路不可用。

核心总结：**硬件故障靠冗余，软件/人为故障靠流程与容错代码**。

#### 4. 五九级可用性的务实评估

面对"五个九"（年停机 < 5 分钟）的需求，候选人提出**分层投资**策略：

- **架构前提**：五九级需要**多活架构**，至少跨三个可用区做**同步复制**，任何单点故障都不影响服务。这意味着基础设施成本翻倍不止。
- **成本收益分析**：并非所有链路都需要五九。建议将**支付链（核心收单）**设为五九，直接保护收入；而**订单查询链**保持四九即可，非核心查询的短期不可用不影响交易，只是体验稍降。
- **核心理念**：可用性是一种资源，必须分配到真正驱动业务价值的链路上，而非盲目追求最高级别的统一标准。

**总结**：这次面试展现的不是理论背诵，而是对"可用性如何落地"的完整工程认知——从分钟级精确量化，到区分故障根因并施以不同防护，再到在高昂成本面前做出理性的分层取舍。

### 解释什么是 SLA

**SLA** 是 **Service Level Agreement（服务等级协议）** 的缩写。它是服务提供方与客户之间就服务质量达成的正式承诺，通常用可量化的指标来定义，例如可用性、响应时间、错误率等，并明确了未达标时的补偿机制。

在这段面试对话中，核心讨论的 SLA 指标是**系统可用性**。

#### 1. 可用性 SLA 的量化方式

可用性通常用"几个九"来描述，代表一年中系统正常运行的时间百分比。计算基础是一年的总时间（365 天 × 24 小时 × 60 分钟 = 525,600 分钟）。

| SLA 级别 | 允许的年宕机时间 | 常见场景 |
|---|---|---|
| 99% | 约 5,256 分钟（3.65 天） | 内部工具、非关键服务 |
| 99.9% | 约 525.6 分钟（8.76 小时） | 一般的 SaaS 服务 |
| 99.99% | 约 52.56 分钟 | 核心业务、支付、交易系统 |
| 99.999% | 约 5.26 分钟 | 电信级、金融核心、生命攸关系统 |

对话中候选人精确掌握了这个换算："四个九意味着全年最多 52 分钟停机，而 99.9% 则放宽到近一个工作日"，这体现了 SLA 的严格性——每增加一个九，容忍的不可用时间就缩短一个数量级。

#### 2. SLA 的构成要素（对话中的体现）

一个完整的 SLA 不仅仅是百分比数字，通常包含：

- **指标定义**：如何计算（例如排除计划内维护与否）。
- **测量周期**：月度、季度还是年度。
- **故障响应**：从发现到恢复的时限。
- **补救措施**：未达标时的服务信用或赔偿。

在面试中，候选人通过真实事件展示了 SLA 的落地：

- 硬件故障（磁盘损坏）依靠冗余和自动切换在 3 分钟内恢复，体现了**高可用架构**对 SLA 的支撑。
- 人为事故（配置不同步）导致 15 分钟中断，暴露了**流程控制**的缺失，后续通过金丝雀发布、预发校验等流程加固来保障 SLA。

#### 3. SLA 的代价：五九决策

当被问到"五九"需求时，候选人指出**五个九需要跨多个可用区的多活架构和同步复制，基础设施成本翻倍**。因此他建议分层：支付链路保五九，查询服务保四九。这说明 SLA 不是越高越好，而是一项需要根据业务价值进行**成本收益权衡**的工程决策——把可靠性预算精准投到直接保护收入的核心链路上。

### 如何监控 replication lag？

监控 **replication lag（复制延迟）** 的核心思路是：持续比较主库已经写入的日志位置，与从库已经执行到的日志位置之间的差距，并将这个差距量化成时间或字节数。

#### 1. 直接查看从库状态（最基础）

在从库上执行：

```sql
SHOW SLAVE STATUS\G
```

关注两个关键字段：

- **`Seconds_Behind_Master`**：从库 SQL 线程落后主库的秒数。值为 0 表示基本无延迟（但可能不精确，尤其在大事务或低负载时）。
- **`Relay_Log_File` / `Exec_Master_Log_Pos`** 与 **`Master_Log_File` / `Read_Master_Log_Pos`** 的对比：直观反映 I/O 线程拉取到的位置与 SQL 线程执行到的位置的差异。

**局限性**：`Seconds_Behind_Master` 可能显示为 0 而实际存在延迟（例如主库几乎没有写入时），且受服务器时间误差影响。

#### 2. 使用 pt-heartbeat（精确时间戳方式）

这是 Percona Toolkit 中的工具，是生产环境更可靠的手段。

**原理**：

1. 在主库上创建一张心跳表（如 `percona.heartbeat`），`pt-heartbeat` 以固定频率（如每秒）更新一条记录，写入当前主库的精确时间戳。
2. 这条更新通过 binlog 复制到从库。
3. 在从库上运行 `pt-heartbeat --monitor`，它会读取心跳表中的时间戳，并与从库当前系统时间比较，计算出精确的延迟秒数（误差可控制在毫秒级）。

**优点**：

- 即使主库完全空闲也能检测延迟（因为心跳一直在更新）。
- 不受主从服务器时钟偏差影响。
- 可以输出为监控系统可消费的格式（如 Nagios、Zabbix）。

#### 3. 基于 GTID 的监控

如果使用 GTID（全局事务标识）复制，可以对比主从的 `gtid_executed` 集合。

- 主库：`SELECT @@global.gtid_executed;`
- 从库：`SELECT @@global.gtid_executed;` 以及 `SELECT GTID_SUBSET('主库gtid', '从库gtid');`

如果从库缺少某些 GTID，说明存在延迟或未应用的事务。这种方式能精确定位缺失了哪些事务，但计算"时间延迟"仍需辅助手段。

#### 4. 监控系统集成与告警

无论使用哪种数据源，都需要将延迟指标纳入监控系统：

- **Prometheus + Grafana**：通过 `mysqld_exporter` 或 `pt-heartbeat` 自定义导出器，将 `Seconds_Behind_Master` 或心跳延迟暴露为 Prometheus 指标，并设置 Grafana 看板和告警规则。
- **告警阈值**：通常设置警告（如延迟 > 10 秒）和严重（延迟 > 60 秒）两级，根据业务容忍度调整。
- **自动暂停迁移**：如候选人所述，在进行大表变更（如回填数据）时，每批次后检查从库延迟，若延迟过高则暂停写入，让从库追赶。

#### 5. 对话中的实际应用

候选人强调监控栈持续追踪**复制延迟**和磁盘健康。当主库磁盘故障导致写入延迟飙升时，监控系统秒级告警，运维在用户感知前就介入处理，将故障恢复时间压缩到 3 分钟。这就是"可观测性驱动快速恢复"的具体体现——如果没有对 replication lag 的持续监控，故障可能会蔓延成大面积服务中断。

**一句话总结**：监控复制延迟，就是用工具持续测量主从之间的数据差距，并把它变成可告警、可追溯的指标，从而在数据不一致或故障切换时快速响应。

---

## Role and Scenario

- **Interviewer:** 考察候选人对系统可靠性的理解，从可用性量化计算追问真实故障案例，再上升到架构成本权衡。
- **Candidate:** 2–5 年经验后端工程师，负责订单系统可靠性设计，能用具体故障数据和生产经验回答追问。
- **Scene:** 面试。面试官从简历上的"99.99% SLA"切入，逐步追问可用性计算、故障恢复细节、硬件冗余与人为故障的对比，以及五个九的成本与架构决策。

---

## Technical Key Points

### 1. Quantifying Availability — The Nines

| SLA | Annual Downtime Allowed |
|---|---|
| 99.9% (three nines) | ~8.76 hours |
| 99.99% (four nines) | ~52 minutes |
| 99.999% (five nines) | ~5 minutes |

- **Calculation basis:** 8,760 hours per year.
- **Key rule:** Every additional nine reduces the acceptable downtime by a factor of ten.
- **Production reality:** Meeting four nines demands deliberate redundancy and strict operational discipline, not just arithmetic.

### 2. Failure Types and Matching Defences

| Failure Type | Example | Defence Strategy |
|---|---|---|
| Hardware | Disk failure on primary database | RAID 10 (disk-level redundancy) + master-slave replication (database-level failover) |
| Software / Human | Config change causing inconsistent cached callback URLs | Staging validation, canary deployment, retry with exponential backoff |

- **Key insight:** Redundancy protects against hardware faults but offers no protection against human-triggered process failures.
- **Observability:** Monitoring replication lag and disk health enables sub-minute detection; without it, a three-minute blip could become a much longer outage.

### 3. Fault Tolerance Mechanisms

- **Redundancy:** RAID 10, master-slave replication, multi-active architecture across availability zones.
- **Process controls:** Staging validation, canary deployment, release approval gates.
- **Retries:** Exponential backoff on downstream calls to prevent transient failures from cascading into full outages.

### 4. Tiered Reliability — Cost vs. Revenue

- Five nines requires multi-active architecture with synchronous replication across at least three AZs — infrastructure cost more than doubles.
- **Tiered approach:** Payment pipeline at five nines; order query service at four nines.
- **Principle:** Spend the reliability budget where it directly protects revenue.

---

## Dialogue (~506 words)

**Interviewer:**

Your resume says the order system achieved 99.99% SLA. Let's start with the basics—how do you actually calculate that number?

**Candidate:**

Take 8,760 hours in a year. Four nines means at most 52 minutes of total downtime annually. If you drop to 99.9%, that jumps to about 8.76 hours—nearly a full working day. Every additional nine reduces the acceptable downtime by a factor of ten. The arithmetic is straightforward, but meeting that target in production demands deliberate redundancy and strict operational discipline.

**Interviewer:**

So how many minutes did your system actually lose last year? Walk me through the real incidents.

**Candidate:**

Two incidents, 18 minutes total. The first was a disk failure on the primary database. The secondary node detected it and took over in about three minutes. We had RAID 10 for disk-level redundancy and master-slave replication for database-level failover, so the switch was nearly seamless.

**Interviewer:**

Three minutes is impressive. How did you even notice the failure that quickly?

**Candidate:**

Our monitoring stack continuously tracks replication lag and disk health metrics. When the primary's write latency spiked, alerts fired within seconds. Without that observability layer, we might have only discovered the failure when users started complaining—which would have turned a three-minute blip into a much longer outage.

**Interviewer:**

And the second incident?

**Candidate:**

That one was entirely human-triggered. Someone updated the payment callback URL format in the config center, but two services picked up different cached versions. One kept calling the old URL, the other expected the new one. Downstream services began timing out, and it took us 15 minutes to trace the root cause and roll back. Redundancy offered no protection whatsoever—it was a pure process failure.

**Interviewer:**

So how do you guard against those kinds of failures?

**Candidate:**

We added two mandatory process layers. First, every config change must pass staging validation before it touches production. Second, we require canary deployment—rolling the change out to a small traffic percentage and monitoring error rates before full release. On the code side, we also introduced retry mechanisms with exponential backoff for downstream calls, so transient failures don't cascade into full outages. The key takeaway: hardware faults need redundancy, but software and human faults need process controls, validation gates, and graceful retries.

**Interviewer:**

One last question. The product manager wants 99.999%—just five minutes of downtime per year. How would you assess that request?

**Candidate:**

Five nines demands a multi-active architecture with synchronous replication across at least three availability zones. That more than doubles the infrastructure bill. I'd recommend a tiered approach: keep the payment pipeline at five nines, but leave the order query service at four nines. Not every service justifies that level of investment. Spend the reliability budget where it directly protects revenue.

---

## Vocabulary (25 Terms)

| Vocabulary | Pronunciation (IPA) | Chinese Meaning |
|---|---|---|
| SLA (Service Level Agreement) | /ˌes el ˈeɪ/ | 服务等级协议 |
| downtime | /ˈdaʊntaɪm/ | 故障停机时间 |
| disk failure | /dɪsk ˈfeɪljər/ | 磁盘故障 |
| primary database | /ˈpraɪməri ˈdeɪtəbeɪs/ | 主数据库 |
| secondary node | /ˈsekəndəri noʊd/ | 从节点 |
| failover | /ˈfeɪloʊvər/ | 故障切换 |
| RAID 10 | /reɪd ten/ | 磁盘阵列10 |
| master-slave replication | /ˈmæstər sleɪv ˌreplɪˈkeɪʃən/ | 主从复制 |
| replication lag | /ˌreplɪˈkeɪʃən læɡ/ | 复制延迟 |
| monitoring stack | /ˈmɒnɪtərɪŋ stæk/ | 监控技术栈 |
| write latency | /raɪt ˈleɪtənsi/ | 写入延迟 |
| observability | /əbˌzɜːrvəˈbɪləti/ | 可观测性 |
| config center | /ˈkɒnfɪɡ ˈsentər/ | 配置中心 |
| callback URL | /ˈkɔːlbæk ˌjuː ɑːr ˈel/ | 回调地址 |
| downstream | /ˌdaʊnˈstriːm/ | 下游的 |
| timeout | /ˈtaɪmaʊt/ | 超时 |
| root cause | /ruːt kɔːz/ | 根因 |
| roll back | /roʊl bæk/ | 回滚 |
| staging validation | /ˈsteɪdʒɪŋ ˌvælɪˈdeɪʃən/ | 预发环境验证 |
| canary deployment | /kəˈneəri dɪˈplɔɪmənt/ | 金丝雀部署 |
| exponential backoff | /ˌekspəˈnenʃəl ˈbækɒf/ | 指数退避 |
| fault tolerance | /fɔːlt ˈtɒlərəns/ | 容错 |
| five nines | /faɪv naɪnz/ | 五个九 (99.999%) |
| multi-active architecture | /ˈmʌlti ˈæktɪv ˈɑːrkɪtektʃər/ | 多活架构 |
| synchronous replication | /ˈsɪŋkrənəs ˌreplɪˈkeɪʃən/ | 同步复制 |

---

## Sentence Patterns

| Function | English Pattern | Use Case |
|---|---|---|
| 计算可用性 | *"X nines means at most Y minutes of total downtime annually."* | 解释 SLA 量化标准 |
| 对比不同等级 | *"Every additional nine reduces the acceptable downtime by a factor of ten."* | 对比不同 SLA 级别的差异 |
| 描述故障接管 | *"The secondary node took over in about X minutes."* | 描述主从切换过程 |
| 强调监控价值 | *"Without that observability layer, we might have only discovered the failure when users started complaining."* | 说明监控对快速发现故障的作用 |
| 区分故障类型 | *"Hardware faults need redundancy, but software and human faults need process controls, validation gates, and graceful retries."* | 分类讨论故障应对策略 |
| 成本权衡 | *"That more than doubles the infrastructure bill. I'd recommend a tiered approach."* | 架构决策中的成本与优先级讨论 |

---

## Reading Comprehension

1. **How does the candidate compute the allowed downtime for 99.99% SLA?**

   **Answer:** Based on 8,760 hours/year, 99.99% allows at most 52 minutes of annual downtime. Each additional nine cuts the allowed time by a factor of ten.

2. **What were the two real incidents the candidate described, and why couldn't redundancy help the second one?**

   **Answer:** A disk failure recovered in 3 minutes via RAID 10 and master-slave replication. The second incident was a config change error causing two services to read different cached callback URLs. Redundancy couldn't prevent this human-triggered failure.

3. **How did monitoring help reduce the impact of the disk failure?**

   **Answer:** Monitoring continuously tracked replication lag and disk health. Alerts on write latency spikes allowed the team to respond within seconds, preventing a much longer outage.

4. **What process improvements did the candidate implement to prevent configuration-related outages?**

   **Answer:** Mandatory staging validation and canary deployment for all config changes, plus retries with exponential backoff on downstream calls to prevent cascading failures.

5. **Why does the candidate propose a tiered reliability strategy instead of upgrading everything to five nines?**

   **Answer:** Five nines requires costly multi-active, synchronous replication. A tiered approach invests in critical paths (e.g., payment) while keeping less critical services at four nines, optimizing cost against revenue risk.

---

*Word count (dialogue): ~506 words*
*Level: Intermediate / T2*
