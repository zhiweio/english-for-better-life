这份预习材料**不用 material 原文**，概念全部用自己的话复述。每个概念的「用自己的话理解」提供**中英双语**（英文按 **B2**）。长句练习的重点是**嵌套从句**——定语从句、状语从句、非限制性从句叠在一起练。

---

## 课前 3 分钟：今天讲什么

**话题：** 系统可靠性——服务能稳定运行多久、出故障怎么办、要不要追求"五个九"。

**四层框架（material 技术干点）：**

```
① 量化定义 → ② 故障分类 → ③ 纵深防御 → ④ 成本权衡
```

**故事线：**

```
几个9怎么算 → 去年两次故障 → 硬件靠冗余+监控 / 人为靠三道防线 → 五个九太贵，分级投入
```

| 说法 | 全年最多停机 | 常见场景 |
|---|---|---|
| 两个九 (99%) | ~3.65 天 | 内部工具 |
| 三个九 (99.9%) | ~8.76 小时 | 一般 SaaS |
| 四个九 (99.99%) | ~52 分钟 | 支付、交易 |
| 五个九 (99.999%) | ~5 分钟 | 金融核心 |

**规律：** 每多一个 9，允许停机时间缩小十倍；SLA 是精确到分钟的设计约束，不是口号。

---

## 概念 1：几个9是什么意思

### 用自己的话理解（中英双语）

**中文：**

SLA（服务等级协议）说的是：服务提供方和客户之间，就服务质量签的一份正式承诺——可用性、响应时间、错误率等，没达标还可能要赔偿。面试里聊的核心指标是**系统可用性**。

算法不复杂：`365 × 24 × 60 × (1 - 0.9999) ≈ 52.56` 分钟，就是四个九全年允许的总宕机时长。三个九是 8.76 小时，差一个9就是十倍。

但 SLA 不只是个百分比。完整 SLA 还包括：指标怎么算、按年还是按月量、故障多久必须恢复、没达标怎么补偿。候选人用真实故障证明 SLA 能落地——磁盘故障 3 分钟恢复靠架构，配置事故 15 分钟暴露流程漏洞。

真正难的是：所有架构决策都要倒推——会不会超出这个停机预算？否则数字只是写在纸上的目标。

**English (B2):**

An SLA, or Service Level Agreement, is a formal commitment **between a service provider and its customers** **that** defines measurable quality targets — such as availability, response time, and error rate — **and** often specifies compensation **when** those targets are not met. In this interview, the main SLA metric under discussion is **system availability**.

The calculation is straightforward: `365 × 24 × 60 × (1 - 0.9999) ≈ 52.56` minutes, **which** is the total downtime budget for four nines in a year. Three nines allows roughly 8.76 hours — **a gap that** shows how much stricter each additional nine becomes.

However, a real SLA is more than a percentage. It typically includes **how** the metric is measured, **what** counting period applies, **how quickly** failures must be resolved, and **what** remedies exist **when** the target is missed. The candidate demonstrates SLA in practice: a disk failure **that** was recovered in 3 minutes shows what architecture can deliver, **whereas** a 15-minute config outage exposes **where** process controls were missing.

The hard part is this: **every architecture decision must be checked against the downtime budget**, otherwise the SLA is just a number on paper **that** the team will never actually meet.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
|---|---|---|
| SLA | 服务等级协议 | An SLA is a formal promise **that** defines how reliable a service must be. |
| downtime budget | 停机预算 | The downtime budget is the total time **that** you are allowed to lose per year. |
| measurement period | 测量周期 | The SLA states the period **during which** availability is measured. |
| remedy / compensation | 补救 / 赔偿 | The SLA may include remedies **that** apply when targets are missed. |
| availability | 可用性 | Availability is a measure **which** shows how often the system works. |
| factor of ten | 十倍 | Each nine reduces downtime by a factor of ten, **which** is easy to forget. |

### 嵌套从句练习：算几个9

**Layer 0 — 主句：**
> Four nines allows about 52 minutes of downtime per year.

**Layer 1 — 加定语从句 (that/which)：**
> Four nines is an SLA **that** allows about 52 minutes of downtime per year.

**Layer 2 — 加状语从句 (when/although)：**
> **When** we talk about four nines, we mean an SLA **that** allows about 52 minutes of downtime per year.

**Layer 3 — 嵌套完整版（定语从句 + 对比从句 + 非限制性从句）：**
> **When** we talk about four nines, we mean an SLA **that** allows about 52 minutes of downtime per year, **whereas** three nines allows about 8.76 hours, **which means** each extra nine makes the allowed downtime ten times smaller.

**Layer 4 — 再加一层（生产难点）：**
> **Although** the calculation is simple, reaching four nines in production is hard **because** you need redundancy and monitoring systems **that** can detect failures **before** users notice them.

**中文对照：** 虽说计算很简单，但在生产环境达到四个九很难，因为你需要冗余和监控系统，能在用户察觉之前就发现故障。

---

## 概念 2：三种故障，三种办法

### 用自己的话理解（中英双语）

**中文：**

生产环境的故障大致分三类，应对思路完全不同：

**硬件故障**——磁盘物理损坏。冗余分两层：磁盘级 RAID 10 扛单盘故障；数据库级主从复制 + 自动 failover，从库检测到主库异常后约 3 分钟接管。监控持续追踪 replication lag 和磁盘健康，写入延迟一飙升就秒级告警——这是"快速发现"撑住"快速恢复"。

**人为故障**——配置中心更新了支付回调 URL，多个服务同时读到新旧不同版本，调用链断裂。冗余对物理故障有用，对逻辑/流程错误完全无效。15 分钟才定位根因并回滚，说明变更缺少校验和灰度。

核心结论：硬件问题用冗余 + 可观测性挡；人的失误用流程挡。

**English (B2):**

**Hardware failures** — such as a physically damaged disk — are addressed through redundancy **that** works at two levels. At the disk level, RAID 10 tolerates a single disk failure; at the database level, master-slave replication with automatic failover allows the secondary node **to take over writes within about three minutes** **when** the primary becomes unhealthy.

What makes the 3-minute recovery possible is observability: the monitoring stack continuously tracks **replication lag** and disk health metrics, **so that** when write latency on the primary spikes, alerts fire within seconds — **a pattern in which** fast detection supports fast recovery **before** users are affected.

**Human failures** — such as a config update **that** leaves different services reading different cached versions of a payment callback URL — break the call chain in a way **that** redundancy cannot fix. It took about 15 minutes **to find the root cause and roll back**, **which** exposed a pure process gap: changes were released **without** staging validation or canary controls.

The key lesson: **hardware faults need redundancy and observability, whereas human-triggered faults need process controls**.

### 两个案例（复述）

| | 第一次（硬件） | 第二次（人为） |
|---|---|---|
| 原因 | 主库磁盘坏道 | 配置中心改了回调 URL，两服务缓存版本不一致 |
| 时长 | ~3 分钟 | ~15 分钟 |
| 恢复 | 从库自动切主（RAID + 主从复制） | 排查根因 + 回滚 |
| 冗余有效？ | 有效 | 无效——流程问题 |

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
|---|---|---|
| hardware failure | 硬件故障 | A hardware failure is a problem **that** physical backup can fix. |
| failover | 故障切换 | Failover is the process **when** the backup node takes over. |
| human-triggered | 人为触发 | The incident was human-triggered, **which** means redundancy could not help. |
| root cause | 根因 | It took 15 minutes **to find the root cause**, **which** was a config mismatch. |
| RAID 10 | 磁盘阵列10 | RAID 10 is disk-level redundancy **that** tolerates one failed disk. |
| Seconds_Behind_Master | 主从落后秒数 | Seconds_Behind_Master shows how many seconds the slave lags **behind** the master. |
| blast radius | 爆炸半径 | Canary deployment limits the blast radius **of** a bad release. |

### 嵌套从句练习：讲硬件故障

**Layer 1：**
> The main disk failed, and the backup took over in 3 minutes.

**Layer 2 — 加定语从句：**
> The main disk, **which** had been showing bad sectors for days, failed, and the secondary node, **which** had been syncing data in real time, took over in about 3 minutes.

**Layer 3 — 加原因从句 (because/since)：**
> The main disk failed **because** it had bad sectors, but the secondary node took over in about 3 minutes **because** we had set up RAID 10 and master-slave replication **that** kept a live copy of the data.

**Layer 4 — 加非限制性从句 (which) + 时间从句 (when)：**
> **When** the primary database's disk failed, the secondary node, **which** had been replicating data continuously, took over in about 3 minutes, **which** meant that most users did not even notice the interruption.

**中文对照：** 主库磁盘故障时，一直在持续同步数据的从节点大约三分钟就接管了，这意味着大多数用户甚至没注意到中断。

### 嵌套从句练习：讲人为故障

**Layer 2：**
> Someone changed the payment callback URL, **but** two services were reading different cached versions, **so** redundancy could not help.

**Layer 3 — 嵌套定语从句：**
> Someone changed the payment callback URL in the config center, **but** two services, **each of which** had cached a different version of the config, started calling different endpoints, **which** caused downstream timeouts **that** lasted about 15 minutes.

**Layer 4 — 加非限制性总结从句：**
> The incident, **which** was entirely caused by a human config change, took 15 minutes to resolve **because** we had to trace the root cause and roll back the change, **which** showed us that redundancy offers no protection **when** the problem is a process failure rather than a hardware failure.

**中文对照：** 这次事故完全是由人为配置变更引起的，花了15分钟才解决，因为我们要追溯根因并回滚——这也让我们看到，当问题是流程故障而非硬件故障时，冗余起不到任何保护作用。

### 嵌套从句练习：监控的价值

**Layer 3：**
> Our monitoring system tracks disk health and replication lag, **so** we got an alert within seconds **when** write latency spiked.

**Layer 4 — 嵌套 + 虚拟语气/条件：**
> **Because** our monitoring stack tracks metrics **that** include replication lag and disk health, we received an alert within seconds **when** the primary node's write latency spiked, **without which** we might have discovered the failure only **when** users started complaining — **a delay that** would have turned a three-minute incident into a much longer outage.

**中文对照：** 因为监控栈追踪包括复制延迟和磁盘健康在内的指标，主节点写入延迟飙升时我们几秒钟就收到了告警；若没有这层监控，我们可能等用户投诉才发现——那种延迟会把三分钟的小故障拖成更长的中断。

---

## 概念 3：怎么防止再出问题

### 用自己的话理解（中英双语）

**中文：**

第二次故障之后，团队加了三道防线（纵深防御）：

**第一道：预发强制校验**——任何配置变更必须先过 Staging，形成硬性流程节点，未验证的变更进不了生产。

**第二道：金丝雀发布**——就算过了预发，也只推给极小比例流量，盯错误率，确认无误再全量。用最小爆炸半径换快速回滚的机会。

**第三道：代码层容错**——下游调用加指数退避重试；配置错误导致瞬断时，调用端拉长等待间隔再试，避免小故障雪崩成全链路不可用。

总结：硬件靠冗余，软件/人为靠流程与容错代码——staging、灰度、重试，每一道都是容错手段。

**English (B2):**

After the second incident, the team built **three layers of defence** against human errors — **a depth-in-defence approach** **that** combines process gates with code-level tolerance.

**The first layer** is mandatory staging validation: every config change must pass through a staging environment **that** mirrors production, **which** acts as a hard gate **that** blocks unvalidated changes **from reaching** live users.

**The second layer** is canary deployment: even after staging, the change is rolled out to only a tiny slice of traffic first, **and** the team monitors error rates **before** allowing a full release — **a strategy that** trades a smaller blast radius for a faster rollback **if** something goes wrong.

**The third layer** is code-level fault tolerance: downstream calls use retry logic with exponential backoff, **so that** when a service fails briefly — for example **because** of a config mismatch — the caller waits longer between retries **instead of** flooding the downstream **and** turning a transient error into a full-chain outage.

In short: **hardware faults need redundancy, but software and human faults need process controls and fault-tolerant code** — staging, canary releases, and retries, **each of which** is a separate layer of protection.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
|---|---|---|
| staging validation | 预发验证 | Staging is an environment **where** we test changes before production. |
| canary deployment | 灰度发布 | In canary deployment, we release to traffic **that** represents only a small percentage. |
| exponential backoff | 指数退避 | Backoff means each retry waits longer **than** the previous one. |
| depth-in-defence | 纵深防御 | Depth-in-defence means several layers **that** each stop a different kind of failure. |
| blast radius | 爆炸半径 | A canary release keeps the blast radius small **if** the change is bad. |

### 嵌套从句练习：说改进措施

**Layer 2：**
> We require staging validation **before** any config change reaches production, and we use canary deployment **where** we release to a small traffic slice first.

**Layer 3：**
> **After** the config incident, we introduced two rules **that** require every change **to be tested in staging**, **which** mirrors production, **before** it is released through a canary deployment **where** only a small percentage of traffic sees the new version first.

**Layer 4 — 完整嵌套版：**
> **To prevent** incidents **that** are caused by human config errors, we now require every change **to pass staging validation in an environment that** mirrors production, **after which** it must go through canary deployment, **where** the team monitors error rates **before** allowing a full release — **a process that**, **combined with** retry logic **that** uses exponential backoff on downstream calls, stops small failures **from becoming** outages **that** affect the whole system.

**中文对照：** 为防止人为配置错误引发的事故，我们现在要求每次变更先在镜像生产的环境中通过预发验证，之后必须走灰度发布、由团队监控错误率后才允许全量——这套流程，配合对下游调用做指数退避重试的逻辑，能阻止小故障演变成波及整个系统的中断。

---

## 概念 4：五个九要不要做

### 用自己的话理解（中英双语）

**中文：**

产品经理想要五个九（全年停机 < 5 分钟）。技术上要**多活架构**——至少三个可用区同时服务，数据**同步复制**，任何单点挂了都不影响对外。成本至少翻倍。

可用性是一种资源，不能盲目全盘五九。支付链直接保护收入 → 五九；订单查询短期不可用只影响体验、不影响交易 → 四九就够。可靠性预算花在真正驱动业务价值的链路上。

**English (B2):**

The product manager wants five nines — **which** means less than about five minutes of downtime per year. Technically, this requires a multi-active architecture **in which** at least three availability zones serve live traffic at the same time, **with** synchronous replication **that** keeps data consistent **so that** no single point of failure can take the service down — **a setup whose** infrastructure cost more than doubles.

Availability should be treated as a finite resource **that** must be allocated wisely, not chased uniformly. The payment pipeline, **through which** revenue actually flows, deserves five nines; the order query service, **whose** temporary unavailability hurts experience but not transactions, can remain at four nines. The reliability budget should go to the paths **where** downtime would cause the greatest business damage.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
|---|---|---|
| five nines | 五个九 | Five nines is a level **that** allows only 5 minutes of downtime. |
| multi-active | 多活 | Multi-active means several zones **that** all handle live traffic. |
| synchronous replication | 同步复制 | Sync replication ensures data **that** is written in one zone appears in others immediately. |
| tiered approach | 分级方案 | A tiered approach assigns different SLA levels **to services that** have different priorities. |
| reliability budget | 可靠性预算 | The reliability budget should go to paths **where** downtime costs the most money. |

### 嵌套从句练习：说成本权衡

**Layer 2：**
> Five nines requires systems in at least three zones, **which** doubles the cost, **so** I suggest different SLA levels for different services.

**Layer 3：**
> **Because** five nines requires a multi-active architecture **that** uses synchronous replication across at least three availability zones, the infrastructure cost more than doubles, **which** is why I would recommend five nines only for the payment pipeline, **which** directly protects revenue, **while** keeping the order query service at four nines.

**Layer 4 — 完整嵌套版：**
> **Although** the product manager wants five nines across the board, I would argue for a tiered approach **in which** the payment pipeline, **which** is the path **through which** revenue flows, is maintained at five nines, **whereas** the order query service, **whose** downtime would inconvenience users but not lose money, can stay at four nines — **a strategy that** spends the reliability budget on the services **where** an outage would hurt the business most.

**中文对照：** 虽然产品经理希望全盘五个九，我会主张分级方案：直接承载收入的支付链路维持五个九，而停机只会给用户带来不便、不会造成资金损失的订单查询服务保持四个九——这是一种把可靠性预算花在 outage 对业务伤害最大的服务上的策略。

---

## 概念 5：replication lag 怎么监控

### 用自己的话理解（中英双语）

**中文：**

Replication lag（复制延迟）就是：主库已经写进去的 binlog，从库还没执行完，两者之间差了多少。监控的核心是持续量化这个差距——用秒数或字节数表示，并接入告警。

最基础的做法是在从库跑 `SHOW SLAVE STATUS`，看 `Seconds_Behind_Master` 和日志位点对比。但这有坑：主库空闲时可能显示 0 但实际有延迟，还受时钟误差影响。

生产上更靠谱的是 **pt-heartbeat**：主库每秒更新心跳表时间戳，变更通过 binlog 复制到从库，从库对比时间戳算延迟，毫秒级精度，主库闲着也能测。

有 GTID 的话可以对比主从的 `gtid_executed` 集合，精确定位缺了哪些事务，但算"落后多少秒"还得配合别的方法。

最后要进 Prometheus + Grafana，设两级告警（比如 >10 秒警告、>60 秒严重）。对话里候选人正是靠持续盯 replication lag 和磁盘健康，写入延迟一飙就秒级告警，才把磁盘故障压在 3 分钟内——没有这层监控，小故障可能拖成大中断。

**English (B2):**

Replication lag measures **how far behind the slave database is compared to the master** — specifically, the gap **between** the log position **that** the master has already written **and** the position **that** the slave has applied. The core idea of monitoring is **to quantify this gap continuously**, express it in seconds or bytes, and feed it into an alerting system.

The most basic approach is to run `SHOW SLAVE STATUS` on the slave and check fields such as `Seconds_Behind_Master` and the relay log positions. However, this method has limitations: the lag may show as zero **when** the master is idle **even though** replication is not fully caught up, **and** clock drift **between** servers can distort the result.

In production, a more reliable approach is **pt-heartbeat**: a heartbeat table on the master is updated every second, the update is replicated through the binlog, and a monitor on the slave compares timestamps **to calculate** lag with millisecond precision — **which** works even **when** the master has very little write traffic.

If GTID replication is enabled, you can compare the `gtid_executed` sets on master and slave **to identify** transactions **that** the slave has not yet applied, **although** converting that into a time-based lag still requires additional tooling.

Finally, the lag metric must be integrated into systems such as Prometheus and Grafana, **where** alert rules — for example a warning at >10 seconds and a critical alert at >60 seconds — can fire **before** replication problems turn into user-facing outages. In the interview, the candidate relies on continuous tracking of replication lag and disk health **so that** when write latency spikes, alerts fire within seconds — **without which** a three-minute incident could easily grow into a much larger failure.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
|---|---|---|
| replication lag | 复制延迟 | Replication lag is the gap **between** what the master has written **and** what the slave has applied. |
| binlog | 二进制日志 | Changes on the master are recorded in the binlog **that** the slave replays. |
| pt-heartbeat | 心跳监控工具 | pt-heartbeat is a tool **that** measures lag by comparing heartbeat timestamps. |
| GTID | 全局事务标识 | GTID is an ID **that** uniquely labels each transaction **that** was committed. |
| alert threshold | 告警阈值 | We set alert thresholds **that** fire when lag exceeds 10 or 60 seconds. |
| mysqld_exporter | MySQL 指标导出器 | mysqld_exporter exposes MySQL metrics **that** Prometheus can scrape. |

### 嵌套从句练习：解释 replication lag

**Layer 2：**
> Replication lag is the gap **between** the master's log position **and** the slave's applied position.

**Layer 3：**
> **When** we monitor replication lag, we continuously measure the gap **between** the log position **that** the master has written **and** the position **that** the slave has executed, **so that** we can alert **before** the slave falls too far behind.

**Layer 4 — 完整嵌套版：**
> **Although** `Seconds_Behind_Master` from `SHOW SLAVE STATUS` is the easiest metric **to check**, production teams often prefer pt-heartbeat, **which** writes a timestamp to a heartbeat table on the master **that** is replicated to the slave, **where** a monitor compares timestamps **to produce** a lag value **that** remains accurate **even when** the master is idle — **a setup that** helped the candidate's team detect the disk failure within seconds **when** write latency spiked.

**中文对照：** 虽说 `SHOW SLAVE STATUS` 里的 `Seconds_Behind_Master` 最容易查，生产团队往往更倾向 pt-heartbeat——它在主库往心跳表写时间戳、经 binlog 复制到从库，由从库上的监控对比时间戳得出延迟，即便主库空闲也仍然准确——正是这套机制帮候选人的团队在写入延迟飙升时几秒钟就发现了磁盘故障。

### 嵌套从句练习：说监控价值

**Layer 4：**
> **Because** our monitoring stack tracks replication lag and disk health metrics **that** are exported to Prometheus, we received an alert within seconds **when** the primary node's write latency spiked, **without which** we might not have noticed the failure **until** users **who** could not complete payments started complaining — **a delay that** would have turned a short incident into a much longer outage.

**中文对照：** 因为监控栈追踪复制延迟和磁盘健康指标并导出到 Prometheus，主节点写入延迟飙升时我们几秒钟就收到告警；若没有这层监控，可能要等无法完成支付的用户开始投诉才发现——那种延迟会把短暂故障拖成更长的中断。

---

## 课堂对话套路（B2 + 嵌套从句）

### 套路 1：老师问"几个9怎么算"

> **When** you look at four nines, **which** means 99.99% availability, the allowed downtime is about 52 minutes per year, **whereas** three nines allows about 8.76 hours — a gap **that** shows how much harder each extra nine becomes. **Although** the maths is straightforward, hitting that target in production requires redundancy and monitoring systems **that** most teams **do not build until** they have already had an outage.

---

### 套路 2：老师问"讲讲真实故障"

**硬件：**
> The first incident was a disk failure on the primary database, **which** our secondary node, **that** had been replicating in real time, recovered from in about 3 minutes — **a response that** was possible **because** we had RAID 10 and master-slave replication **in place**.

**人为：**
> The second incident was caused by a config change **that** left two services reading different cached versions of the payment callback URL, **which** led to downstream timeouts **that** lasted 15 minutes — **a problem that** no amount of hardware redundancy could have prevented **because** it was a process failure, not a hardware failure.

---

### 套路 3：老师问"怎么防人为失误"

> **After** that incident, we built three layers of defence: staging validation in an environment **that** mirrors production, canary deployment **where** only a small traffic slice sees the change first, and retry logic with exponential backoff **that** stops transient downstream failures **from cascading**. **What** we learned is **that** hardware faults need redundancy and observability, **whereas** faults **that** are triggered by human mistakes need process gates **that** limit the blast radius.

---

### 套路 4：老师问"replication lag 怎么监控"

> **When** we monitor replication lag, we measure the gap **between** the log position **that** the master has written **and** the position **that** the slave has applied. In production we often use pt-heartbeat, **which** compares heartbeat timestamps **that** are replicated through the binlog, **because** `Seconds_Behind_Master` alone can show zero **even when** lag actually exists. Those metrics feed into Prometheus, **where** alert rules fire **before** lag grows into an outage **that** users would notice.

---

### 套路 5：老师问"产品经理要五个九"

> **Although** five nines sounds attractive, it requires a multi-active architecture **with** synchronous replication across at least three zones, **which** more than doubles the cost. I would recommend a tiered approach **in which** the payment pipeline, **which** directly protects revenue, stays at five nines, **while** the order query service, **whose** failures are less costly, remains at four nines.

---

### 套路 6：课上主动说话

| 你想做什么 | 嵌套从句版 |
|---|---|
| 确认理解 | So redundancy only helps **when** the failure is a hardware problem, **not when** it is caused by a config mistake, **right**? |
| 请老师举例 | Could you give an example of an outage **that** was caused by a human mistake **which** redundancy could not prevent? |
| 表示同意 | That makes sense — monitoring is what helps us find problems **before** users **who** depend on the service start complaining. |
| 提出疑问 | **But** wouldn't five nines be too expensive for a read-only service **whose** downtime would not directly lose revenue? |
| 问监控 | How do you monitor replication lag **when** `Seconds_Behind_Master` shows zero **but** the slave is actually behind? |

---

## 常用句式：嵌套从句版（改写，非原文）

| 功能 | 嵌套从句句式 |
|---|---|
| 算 SLA | **When** we say four nines, we mean an SLA **that** allows only 52 minutes of downtime per year, **which** is ten times less **than** what three nines allows. |
| 描述切换 | The secondary node, **which** had been replicating data continuously, took over in about 3 minutes **when** the primary disk failed. |
| 强调监控 | **Without** a monitoring system **that** tracks disk health and replication lag, we might have found the failure only **when** users **who** could not complete their orders started complaining. |
| 区分故障 | Hardware faults are problems **that** redundancy can fix, **whereas** human mistakes are problems **that** only process controls — **such as** staging and canary releases — can prevent. |
| 三道防线 | **To prevent** human errors, we use three layers — staging validation, canary deployment, and retry with backoff — **each of which** reduces the blast radius **of** a bad change. |
| 监控延迟 | Replication lag is the gap **between** what the master has written **and** what the slave has applied, **which** we track **so that** alerts fire **before** failover becomes risky. |
| 说成本 | Availability is a resource **that** should be spent on paths **where** downtime directly affects revenue, **not** applied uniformly **to every** service. |

---

## 老师可能追问 — 嵌套从句回答

| 老师问 | 你可以答 |
|---|---|
| Three nines vs four nines? | Three nines allows about 8.76 hours of downtime per year, **whereas** four nines allows only 52 minutes — a difference **that** shows how much stricter each extra nine becomes. |
| Why didn't redundancy help the second time? | **Because** the problem was a config mismatch **that** caused two services **to read different versions**, **which** is a process failure **that** backup servers cannot fix. |
| How did you find the disk problem fast? | Our monitoring tracks metrics **that** include replication lag and disk health, **so** we got an alert within seconds **when** write latency on the primary node spiked. |
| What is canary deployment? | It is a release strategy **where** you push a change to a small percentage of traffic first, **and** you only roll it out fully **if** the error rate stays within a range **that** the team has agreed on. |
| How do you monitor replication lag? | We measure the gap **between** the master's binlog position **and** the slave's applied position; in production we often use pt-heartbeat, **which** compares replicated heartbeat timestamps **because** `Seconds_Behind_Master` can be misleading **when** the master is idle. |
| What is pt-heartbeat? | It is a tool **that** updates a heartbeat table on the master every second; the update is replicated to the slave, **where** a monitor compares timestamps **to calculate** lag **that** stays accurate **even when** write traffic is low. |
| Why not five nines for everything? | **Because** five nines requires infrastructure **that** costs more than twice as much, **and** not every service is one **whose** downtime would justify that investment. |

---

## 跟读练习：五段 B2 嵌套从句（课前朗读 2 遍）

**Part 1 — 几个9**

> **When** engineers talk about four nines, they mean an SLA **that** allows only about 52 minutes of downtime per year, **whereas** three nines allows roughly 8.76 hours, **which** means each additional nine makes the allowed downtime ten times smaller. **Although** this calculation is simple, reaching four nines in production is difficult **because** it requires redundancy and monitoring systems **that** can catch failures **before** they affect users.

**Part 2 — 两次故障**

> Last year we had two incidents **that** caused 18 minutes of downtime in total. The first was a disk failure on the primary database, **which** the secondary node, **that** had been replicating data in real time, recovered from in about 3 minutes. The second was a config change **that** left two services reading different cached versions of a payment URL, **which** caused downstream timeouts **that** lasted 15 minutes — **an outage that** redundancy could not prevent **because** it was a process failure, not a hardware one.

**Part 3 — 三道防线**

> **After** the config incident, we built three layers of defence: staging validation in an environment **that** mirrors production, canary deployment **where** only a small slice of traffic sees the change first, and retry logic with exponential backoff **that** prevents transient downstream failures **from cascading**. **What** we learned is **that** hardware faults need redundancy and observability, **whereas** human-triggered faults need process controls **that** limit the blast radius of every release.

**Part 4 — 五个九**

> **Although** the product manager wants five nines, I would recommend a tiered approach **in which** the payment pipeline, **which** is directly tied to revenue, is maintained at five nines, **while** the order query service, **whose** downtime is less costly, stays at four nines — **a strategy that** treats availability as a resource **that** must be allocated **where** it protects business value most.

**Part 5 — replication lag 监控**

> **When** we monitor replication lag, we track the gap **between** the log position **that** the master has written **and** the position **that** the slave has applied. **Although** `SHOW SLAVE STATUS` is the simplest check, many teams use pt-heartbeat, **which** replicates a heartbeat timestamp **that** a monitor on the slave compares **to produce** an accurate lag value **even when** the master is idle. Those metrics feed into Prometheus, **where** alert rules fire within seconds **when** write latency spikes — **without which** a short hardware failure could grow into an outage **that** affects paying users.

---

## 附录：嵌套从句工具箱

| 从句类型 | 常用引导词 | 练法 |
|---|---|---|
| **定语从句（限定）** | that, which, who, whose, where | 修饰名词：*a system **that** can detect failures* |
| **定语从句（非限定）** | , which / , who | 补充信息：*…52 minutes, **which** is ten times less* |
| **时间 / 条件状语** | when, before, after, if, unless | *|**When** the disk failed, …* |
| **原因 / 结果状语** | because, since, so that | *…hard **because** you need redundancy **that** …* |
| **对比 / 让步状语** | although, whereas, while | *|**Although** the maths is simple, …* |
| **嵌套技巧** | 从句套从句 | 主句 → 定语从句里再套 that/when/which |

**拆句口诀：** 先找主句主干 → 标出每个 that/which/when/because 引导的从句 → 从外往里读 → 再试着合并回去。

---

**课前最少记：** 52 分钟 / 8.76 小时 / 5 分钟 · 磁盘 3 分钟 vs 配置 15 分钟 · 三道防线（staging / canary / retry）· replication lag = 主从日志位点差距 · *Hardware needs redundancy and observability; human mistakes need process controls.*
