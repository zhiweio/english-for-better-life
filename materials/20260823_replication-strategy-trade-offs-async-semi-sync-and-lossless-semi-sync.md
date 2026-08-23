# 【中级】Replication Strategy Trade-offs: Async, Semi-Sync, and Lossless Semi-Sync

**技术等级：** T2 · **英语等级：** 中 · **字数：** ~500

**Source:** Interview / System Design  
**Level:** T2 / Intermediate  
**Role:** Interviewer, Candidate (2–5 years backend engineer)  
**Estimated Words:** ~490

---

## 故事 Prompt 及故事

```jsx
请根据以下系统设计知识点生成一个中文技术故事，用于后续英语教学。

知识点：[2.1 主从复制]
故事形式：一段面试场景对话，对话双方是面试官和候选人。
技术要求：T2难度（方案对比级），适合2-5年经验后端工程师。
故事冲突设定：
候选人说订单主库用了异步复制。面试官问：如果主库崩溃，从库还没同步的数据怎么办？为什么不用半同步？

面试官追问链（必须严格遵循）：

1. "你说异步复制性能好——主库写完就返回，不等待从库。但如果主库磁盘坏道、机房断电，最后 200ms 的写入没同步到从库就丢了。这些丢失的数据能恢复吗？不能恢复的话，用户付了钱但订单没了，你怎么处理？"
2. "你说为了安全应该用半同步——主库等至少一个从库确认收到 binlog 才返回。但半同步的写入延迟比异步高多少？你测过吗？如果支付场景要求写入延迟 < 50ms，半同步能满足吗？不能满足的话，你有折中方案吗？"
3. "你们有没有考虑过 '增强半同步'——等主库把 binlog 刷到自己的磁盘，不等从库确认就返回？这叫 lossless semi-sync。性能和可靠性介于异步和全同步之间。你评估过这个方案吗？在你业务的延迟和可靠性要求下，哪个最合适？"

【必须覆盖的核心概念】（来自核心层）：

- 复制延迟
- 写主读从模式

【可选延伸概念】（来自扩展层，T2 可不强制要求）：

- Binlog/redo log 概念

候选人的回答要求：

- 给出复制延迟排查的系统化步骤（至少三个排查方向）
- 说明并行复制的适用场景和潜在风险
- 提出防止误写从库的多层防护措施

要求：故事简短，纯对话形式，字数350字。
生成完故事后，请用1-2句话说明你是如何通过追问实现方案对比深度的。
```

**Interviewer:** "你说异步复制性能好——主库写完就返回，不等待从库。但如果主库磁盘坏道、机房断电，最后 200ms 的写入没同步到从库就丢了。用户付了钱但订单没了，你怎么处理？"

**Candidate:** "确实丢数据，但概率和影响可控。我们主库部署在云上，磁盘做 RAID 10，单机故障率远低于网络抖动。即使极端情况下丢了最后 200ms 的 binlog，我们的支付回调有对账机制——第三方支付平台会异步通知，如果订单不存在就触发补偿流程，自动创建订单并更新状态。用户最多看到几分钟的延迟，不会丢钱。"

**Interviewer:** "你说为了安全应该用半同步——主库等至少一个从库确认收到 binlog 才返回。但半同步的写入延迟比异步高多少？如果支付场景要求写入延迟小于 50ms，半同步能满足吗？"

**Candidate:** "我们测过，同机房半同步比异步多 2-3ms，跨机房多 10-15ms。支付场景 P99 要求 50ms，同机房半同步能满足，但跨机房不够。所以我们只对核心支付表开半同步，普通订单表保持异步，分级保证。"

**Interviewer:** "你们考虑过增强半同步吗？主库把 binlog 刷到自己的磁盘就返回，不等从库确认。性能和可靠性介于异步和全同步之间。"

**Candidate:** "评估过，但增强半同步解决的是主库自身宕机后数据可恢复，解决不了主库磁盘物理损坏——盘坏了 binlog 也没了。它的可靠性比异步高，比全同步低，但延迟和异步一样。我们的折中是支付核心用半同步保证零丢失，订单写入用异步保性能，增强半同步暂时没引入，因为运维复杂度增加但收益有限。"

**深度实现说明：** 第一轮追问逼出异步复制的数据丢失风险及业务层补偿兜底；第二轮追问用实测延迟数据（同机房 2-3ms、跨机房 10-15ms）量化半同步代价，引出按表分级的折中方案；第三轮追问引入增强半同步作为第三种选项，逼出候选人对故障类型覆盖范围和运维复杂度的评估，三轮追问在可靠性、性能和工程取舍三个维度实现了完整的方案对比深度。

---

## Background

### 文章技术干点

这段面试对话深入探讨了数据库复制策略的权衡，核心围绕一个关键矛盾：**如何在高性能写入与绝对数据安全之间找到平衡**。候选人的回答展现了一个渐进式的决策过程，最终通过分级策略将可靠性预算精确分配到业务关键路径上。

---

### 1. 异步复制的数据丢失风险与补偿

面试官直指异步复制的致命缺陷：主库返回成功时，从库可能尚未复制最近的数据。一旦主库发生磁盘故障或宕机，最后几百毫秒的写入将永久丢失。

候选人承认这种可能性，但给出了多层防护：

- **基础设施降险**：使用云实例的 RAID 10 存储，将单盘故障概率大幅降低。
- **业务层补偿**：真正的安全保障来自支付对账流水线。第三方支付服务商会发送异步回调通知，系统若未找到对应订单，会自动触发补偿工作流，创建订单并更新支付状态。
- **可观测承诺**：用户可能感知到几分钟的延迟，但绝不会丢钱。这是用短暂的可感知延迟换取资金安全的确定性。

---

### 2. 半同步复制的延迟量化与适用边界

面试官追问半同步复制的代价——主库必须等待至少一个从库确认收到 binlog 后才能返回成功。

候选人给出了实测数据：

- **同机房**：半同步相比异步仅增加 2-3ms 延迟。
- **跨机房**：延迟增加约 10-15ms。

基于支付接口 P99 写入延迟 50ms 的目标，同机房半同步完全可以满足，而跨机房半同步则可能超标。这为后续的分级策略提供了精确的数据支撑——不是笼统地说"半同步慢"，而是明确在什么条件下慢多少。

---

### 3. 无损半同步的评估与取舍

面试官提出增强半同步（Lossless Semi-Sync）：主库将 binlog 刷入本地磁盘后立即返回，不等待从库确认。

候选人对此有清晰评估：

- **保护的故障类型**：仅保护主库进程崩溃（重启后可恢复 binlog），但对物理磁盘损坏毫无帮助。
- **可靠性排序**：高于异步，低于全半同步，延迟开销接近零。
- **放弃理由**：增量收益（仅保护进程崩溃场景）不足以覆盖引入新配置带来的运维复杂度。保留作为未来选项，但当前不采用。

这体现了务实的工程判断——不是所有理论上更好的东西都值得引入。

---

### 4. 分级复制策略：将可靠性预算对准业务价值

最终方案是按表的业务关键性分两级处理：

| **表类型** | **复制策略** | **延迟** | **可靠性** |
| --- | --- | --- | --- |
| **核心支付表** | 同机房半同步 | +2-3ms | 零数据丢失 |
| **普通订单表** | 异步 | 基准 | 极低概率丢失，有补偿兜底 |

**核心思想**：不是所有写入都需要同等级别的持久化保障。对支付表施加严格的半同步，确保资金数据绝对可靠；对普通订单表保持异步的高吞吐，依赖业务层对账补偿机制兜底。这样将可靠性作为有限的预算，精准投放到直接保护收入的核心链路上，而非在整个系统上均摊性能代价。

---

### 什么是 binlog

**Binlog**（Binary Log，二进制日志）是 MySQL 中一个至关重要的日志，它记录了所有对数据库产生实际更改的操作（如 `INSERT`, `UPDATE`, `DELETE`）以及可能改变数据的 DDL 语句（如 `ALTER TABLE`），但不记录单纯的 `SELECT` 查询。它是 MySQL 实现**主从复制**和**数据恢复**的基石。

---

#### 1. Binlog 记录了什么？

它不是记录 SQL 语句本身（取决于格式），而是记录**数据库的变更事件**。包括：

- 事务的开始和结束。
- 每一行数据的修改前和修改后的值（取决于格式）。
- DDL 语句的执行。

例如，当你执行 `UPDATE orders SET status = 'paid' WHERE order_id = 100`，binlog 里就会记录这个更新操作。

---

#### 2. Binlog 的核心作用

**① 主从复制**

这是 binlog 最主要的功能。主库将 binlog 发送给从库，从库在本地重放这些日志，从而实现数据同步。我们之前讨论的异步、半同步、无损半同步，本质上都是在控制 binlog 的传输和确认时机。

**② 数据恢复**

利用备份和 binlog，可以将数据恢复到任意时间点。备份负责恢复全量数据，binlog 负责回放备份之后到故障发生前的所有增量变更。例如：

- 凌晨 3 点做了全量备份。
- 上午 10 点误删了一张表。
- 可以用凌晨 3 点的备份恢复数据，然后重放 3 点到 10 点之间的 binlog，将数据恢复到误删前一刻。

---

#### 3. Binlog 的三种格式

| **格式** | **记录内容** | **优点** | **缺点** |
| --- | --- | --- | --- |
| **STATEMENT** | 记录执行的 SQL 语句 | 日志量小，可读性好 | 某些函数（如 `UUID()`, `NOW()`）在从库重放可能产生不一致结果 |
| **ROW** | 记录每一行数据被修改后的具体值 | 主从严格一致，最安全 | 日志量最大，尤其批量操作时 |
| **MIXED** | 通常用 STATEMENT，遇到可能不一致的情况自动切 ROW | 平衡了日志量和一致性 | 逻辑复杂，一般直接推荐 ROW |

MySQL 5.7 之后，默认格式是 **ROW**。

---

#### 4. Binlog 在主从复制中的工作流程

1. **主库**：事务提交时，将变更写入 binlog。
2. **从库 I/O 线程**：连接主库，拉取 binlog，写入自己的**中继日志（Relay Log）**。
3. **从库 SQL 线程**：读取中继日志，重放其中的变更，完成数据同步。

**我们之前讨论的"主从延迟"，就是指从库 SQL 线程重放的速度跟不上主库 I/O 线程拉取的速度，导致从库数据滞后于主库。**

---

#### 5. 与 Redo Log 的区别

| **特性** | **Binlog** | **Redo Log** |
| --- | --- | --- |
| **所属层** | MySQL Server 层，所有存储引擎通用 | InnoDB 存储引擎特有 |
| **记录内容** | 逻辑变更（SQL 或行变化） | 物理页修改（如"将第 100 号页偏移 50 处的值改为 1"） |
| **主要用途** | 主从复制、数据恢复 | 崩溃恢复（保证已提交事务不丢失） |

两者共同协作，通过**两阶段提交**保证主从数据一致性。

---

**一句话总结**：Binlog 是 MySQL 记录所有数据变更的二进制流水账，主从复制依靠它保持同步，数据恢复依靠它回到任意时间点。它是 MySQL 可靠性的基石。

---

### 异步复制，半同步复制，无损半同步的概念解释及区别，及各自适应的场景

**异步复制、半同步复制与无损半同步复制** 是 MySQL 主从复制中三个递增的可靠性级别。它们的核心区别在于，主库提交事务后，是否需要以及如何等待从库的确认，这直接决定了写入延迟和数据丢失的可能性。

---

#### 1. 三种复制模式的概念

**异步复制 (Asynchronous Replication)**

主库将事务写入 `binlog` 后，立即提交并返回成功给客户端，**完全不等待任何从库的确认**。从库异步地拉取并应用这些日志。

**半同步复制 (Semi-Synchronous Replication)**

主库在提交事务后，**必须等待至少一个从库确认已接收到 `binlog` 事件**，才能向客户端返回成功。从库在将日志写入自己的中继日志后即发送确认。默认的等待点是 `AFTER_COMMIT`：主库先将事务提交到存储引擎，再等待从库确认。此时其他会话可能已看到该数据，若主库在确认前崩溃，主库上提交的数据可能丢失，但从库可能还未接收到。

**无损半同步复制 (Lossless Semi-Sync / Enhanced Semi-Sync)**

这是 MySQL 5.7 引入的增强模式，等待点改为 **`AFTER_SYNC`**。主库在事务 prepare 阶段就等待从库确认，**收到确认后才在存储引擎层提交事务**。这样可以确保：事务在主库上提交之前，至少一个从库已经收到了该事务的 `binlog`。因此，即使主库崩溃，该事务在主库上并未提交，而至少一个从库已拥有完整的 `binlog`，切换后不会丢失数据。

> **注意**：面试官提到的"主库将 binlog 刷到自己的磁盘并立即返回，不等待从库"实际上是另一种配置——它并非标准无损半同步，而是带有本地持久化的异步模式。候选人在回答中认可了对话中的简化描述，可将其理解为一种保护主库进程崩溃、但不保磁盘损坏的中间方案。标准无损半同步（`AFTER_SYNC`）的等待点在提交前，需等待从库确认后才提交事务。

---

#### 2. 核心区别对比

| **特性** | **异步复制** | **半同步复制 (AFTER_COMMIT)** | **无损半同步 (AFTER_SYNC)** |
| --- | --- | --- | --- |
| **主库等待点** | 无等待 | 提交后等待从库确认 | prepare 后等待从库确认 |
| **写入延迟增加** | ≈ 0ms | 同机房 2-3ms，跨机房 10-15ms | 与半同步相同，同机房约 2-3ms |
| **数据丢失风险** | 可能丢失最近一段时间的写操作 | 主库故障时，已提交但未确认的事务可能丢失 | 主库故障时，未提交的事务不会被其他会话看到，且至少一个从库已保证收到 |
| **故障保护范围** | 无 | 保护从库侧故障，但主库提交后瞬间崩溃仍有少量丢失风险 | 保护主库进程崩溃、网络中断等，但不保护主库物理磁盘同时损坏 |
| **吞吐量** | 最高 | 中等 | 中等 |

---

#### 3. 对话中的实际应用与权衡

候选人基于业务关键性，采用了分级复制策略：

- **核心支付表 → 半同步（同机房）**
  支付表要求**零数据丢失**。启用半同步后，主库在收到至少一个从库确认后才返回成功，确保已确认的支付记录不会在故障切换后丢失。同机房延迟仅增加 2-3ms，完全在 50ms 的 P99 写入延迟预算内。

- **普通订单表 → 异步复制**
  订单表追求**极致写入吞吐量**。容忍极低概率的最后几百毫秒数据丢失，因为上游有支付回调的**补偿工作流**，能自动创建订单并更新状态。用户至多感受到短暂延迟，但资金安全无损。

- **增强半同步未被采用**
  候选人评估后认为，这种仅保护进程崩溃、不保护物理磁盘损坏的方案，增量收益有限，却引入额外运维复杂度。当前两级策略已能覆盖风险需求，无需引入更多配置维度。

---

#### 4. 适用场景总结

- **异步复制**：适用于数据允许少量丢失且对性能敏感的场景，如日志、非关键用户行为、社交媒体内容等。
- **半同步复制**：适用于需要强数据一致性但对极端情况有少量容忍的场景，或作为无损半同步的备选（当网络条件较好时）。
- **无损半同步**：适用于金融交易、支付核心表、订单状态等**必须保证已确认事务不丢失**的关键业务数据。

**核心思想**：不为整个系统选择单一复制模式，而是根据每张表的业务价值，将"可靠性预算"精确分配到真正保护收入的核心链路上，让大多数数据享受异步的高性能，同时确保资金数据绝对安全。

---

### MySQL 内部的两阶段提交及异步复制、半同步复制、无损半同步的发生时机

理解事务提交流程与半同步复制的关系，关键在于看清 MySQL 内部**两阶段提交**的各个节点，以及半同步插件是在哪个节点"暂停等待从库确认"的。

---

#### 1. 事务提交的两阶段提交

MySQL InnoDB 的事务提交分为三个阶段：

- **Prepare 阶段**：InnoDB 将事务写入 redo log 并刷盘，事务状态标记为 `PREPARE`。此时事务未提交，其他会话不可见，但崩溃恢复时可以根据 redo log 恢复。
- **Commit 阶段**：MySQL Server 层写入 binlog 并刷盘，然后通知 InnoDB 将事务标记为 `COMMIT`。事务提交完成，数据对其他会话可见。

半同步复制插件就嵌入在这个流程中，在某个关键步骤**强制等待从库确认收到 binlog**。

---

#### 2. 交互流程对比

**异步复制**

没有任何等待，事务提交后立刻返回成功给客户端。

```
客户端发起 COMMIT
    │
    ▼
InnoDB Prepare (写 redo log)
    │
    ▼
Server 写 binlog
    │
    ▼
InnoDB Commit (事务提交)
    │
    ▼
返回成功给客户端
```

**半同步复制 (AFTER_COMMIT)**

在 InnoDB Commit **之后**，返回成功给客户端**之前**，等待从库确认。

```
客户端发起 COMMIT
    │
    ▼
InnoDB Prepare (写 redo log)
    │
    ▼
Server 写 binlog
    │
    ▼
InnoDB Commit (事务提交)          ← 事务已提交，其他会话可见
    │
    ▼
★ 等待至少一个从库确认收到 binlog   ← 此时主库已提交，但客户端还没收到成功
    │
    ▼
返回成功给客户端
```

**缺陷**：主库提交后、等待确认前，如果主库崩溃，该事务在主库上已提交（其他会话可见），但从库可能还没收到 binlog。故障切换后，这个事务在新主库上丢失，造成数据不一致。

**无损半同步复制 (AFTER_SYNC)**

在 InnoDB Commit **之前**，即写完 binlog 后，立刻等待从库确认，**收到确认后才提交事务**。

```
客户端发起 COMMIT
    │
    ▼
InnoDB Prepare (写 redo log)
    │
    ▼
Server 写 binlog
    │
    ▼
★ 等待至少一个从库确认收到 binlog   ← 此时事务未提交，其他会话不可见
    │
    ▼
InnoDB Commit (事务提交)          ← 收到确认后才提交
    │
    ▼
返回成功给客户端
```

**优势**：在事务真正提交前，至少有一个从库已经收到了完整的 binlog。此时如果主库崩溃，主库上这个事务还是 `PREPARE` 状态，对其他会话不可见，崩溃恢复时会回滚。而至少一个从库有这份 binlog，可以成为新主库并提交这个事务。

---

#### 3. 直观对比

```
异步：              主库直接提交，不等待从库
AFTER_COMMIT：      主库提交 → 等从库确认 → 返回成功
AFTER_SYNC：        主库写 binlog → 等从库确认 → 主库提交 → 返回成功
```

**一句话总结**：`AFTER_SYNC` 把等待点从"提交后"前移到"提交前"，确保事务所依赖的 binlog 已被从库接收，才允许提交，从而消除了主库提交后、从库未同步导致的潜在数据丢失。

---

## 角色及场景

**Interviewer (面试官):** 深入追问候选人为何在支付系统中采用异步复制，挑战其在数据丢失风险和性能之间的权衡，并对比半同步与增强半同步的适用性。

**Candidate (候选人):** 2-5年经验后端工程师，负责订单与支付数据库架构，需清晰阐述不同复制策略的延迟、可靠性和运维代价。

**场景:** 面试。候选人描述其订单系统采用异步复制以保证写入性能。面试官针对主库崩溃导致数据丢失、半同步的性能开销以及增强半同步的评估发起三轮追问。

---

## 面试对话 (中级，正文约 490 词)

**Interviewer:**

You chose **asynchronous replication** for **performance**—the master returns instantly without waiting for replicas. But if the master suffers a disk failure or a power outage, the last 200 milliseconds of writes are lost because they haven't been replicated. **A user pays but the order disappears. How do you handle that?**

**Candidate:**

Data loss is possible, but the probability and impact are manageable. Our master runs on cloud instances with RAID 10 storage, so single‑disk failures are far less likely than network glitches. Even in the rare case where we lose the last 200ms of binlog, our payment reconciliation pipeline kicks in. The third‑party payment provider sends an asynchronous callback. If our system doesn't find the corresponding order, a compensation workflow creates it and updates the payment status automatically. Users may see a delay of a few minutes, but they never lose their money.

**Interviewer:**

You mentioned that for safety you could use **semi‑synchronous replication**—the master waits for at least one replica to acknowledge the binlog write before returning. How much latency does semi‑sync add compared to async? If your payment scenario requires a write latency below 50 milliseconds, can semi‑sync meet that?

**Candidate:**

We measured it. Within the same data center, semi‑sync adds only 2–3ms compared to async. Across data centers, it adds around 10–15ms. Our payment flow has a P99 write latency target of 50ms. Same‑dc semi‑sync fits comfortably, but cross‑dc semi‑sync exceeds the budget. So we use a tiered approach: **core payment tables run with semi‑sync for zero data loss, while regular order tables stay on async to preserve throughput.** This way we guarantee consistency where it matters and performance where it's needed.

**Interviewer:**

Did you consider enhanced semi‑sync, also called lossless semi‑sync? The master flushes the binlog to its own disk and returns immediately, without waiting for the replica. Reliability sits between async and full sync, but latency stays the same as async. Why didn't you choose that?

**Candidate:**

We evaluated it. Lossless semi‑sync protects against master process crashes because the binlog is on disk and can be recovered after a restart. But it doesn't help with physical disk damage—if the disk itself fails, both the data and the binlog are gone. Its reliability is higher than async but lower than full semi‑sync, while the latency overhead is nearly zero. For us, the incremental benefit didn't justify the operational complexity. **We opted to keep payment on semi‑sync for true zero‑loss guarantees and orders on async for maximum throughput**. Lossless semi‑sync remains an option if we need a middle ground later, but right now the two‑tier strategy covers our risk profile well.

**Interviewer:**

So you essentially match the replication strategy to the business criticality of each table.

**Candidate:**

Exactly. **Not every write needs the same level of durability. Applying the same strict guarantee everywhere would hurt performance without meaningfully reducing business risk.** The tiered approach lets us allocate reliability budget where it actually protects revenue.

---

## 词汇表 (25个高频技术词汇)

| **Vocabulary** | **Pronunciation (IPA)** | **Chinese Meaning** |
| --- | --- | --- |
| asynchronous replication | /eɪˈsɪŋkrənəs ˌreplɪˈkeɪʃən/ | 异步复制 |
| semi‑synchronous replication | /ˈsemi ˈsɪŋkrənəs ˌreplɪˈkeɪʃən/ | 半同步复制 |
| lossless semi‑sync | /ˈlɒsləs ˈsemi sɪŋk/ | 无损半同步 |
| master | /ˈmæstər/ | 主库 |
| replica | /ˈreplɪkə/ | 从库/副本 |
| binlog | /ˈbɪnlɒɡ/ | 二进制日志 |
| RAID 10 | /reɪd ten/ | 磁盘阵列10 |
| reconciliation | /ˌrekənsɪliˈeɪʃən/ | 对账 |
| compensation workflow | /ˌkɒmpənˈseɪʃən ˈwɜːrkfloʊ/ | 补偿流程 |
| P99 latency | /piː ˈnaɪnti naɪn ˈleɪtənsi/ | 99百分位延迟 |
| throughput | /ˈθruːpʊt/ | 吞吐量 |
| data center | /ˈdeɪtə ˈsentər/ | 数据中心 |
| tiered approach | /tɪrd əˈproʊtʃ/ | 分级策略 |
| payment table | /ˈpeɪmənt ˈteɪbəl/ | 支付表 |
| flush | /flʌʃ/ | 刷盘 |
| physical disk damage | /ˈfɪzɪkəl dɪsk ˈdæmɪdʒ/ | 磁盘物理损坏 |
| operational complexity | /ˌɒpəˈreɪʃənəl kəmˈpleksəti/ | 运维复杂度 |
| risk profile | /rɪsk ˈproʊfaɪl/ | 风险状况 |
| durability | /ˌdjʊərəˈbɪləti/ | 持久性 |
| reliability budget | /rɪˌlaɪəˈbɪləti ˈbʌdʒɪt/ | 可靠性预算 |
| revenue | /ˈrevənjuː/ | 营收 |
| callback | /ˈkɔːlbæk/ | 回调 |
| crash | /kræʃ/ | 崩溃 |
| power outage | /ˈpaʊər ˈaʊtɪdʒ/ | 断电 |
| data loss | /ˈdeɪtə lɒs/ | 数据丢失 |

---

## 句式提炼

| **功能** | **英文句式** | **适用场景** |
| --- | --- | --- |
| 承认风险并说明可控 | *"Data loss is possible, but the probability and impact are manageable because…"* | 解释为何接受某种风险 |
| 描述补偿机制 | *"Our reconciliation pipeline catches the discrepancy—if the order is missing, a compensation workflow creates it automatically."* | 说明应用层兜底方案 |
| 量化延迟差异 | *"We measured it. Within the same data center, semi‑sync adds only 2–3ms compared to async."* | 用数据支撑方案对比 |
| 分级策略表述 | *"We use a tiered approach: core payment tables run with semi‑sync, while regular order tables stay on async."* | 说明按业务重要程度分配技术资源 |
| 评估后弃用某方案 | *"We evaluated it, but the incremental benefit didn't justify the operational complexity."* | 表达经过评估后的技术取舍 |

---

## 阅读理解题

1. How does the candidate handle the rare case where a committed payment is lost due to asynchronous replication?

   **Answer:** A payment reconciliation pipeline listens for callbacks from the payment provider. If the order is missing, a compensation workflow creates it and updates the payment status, ensuring the user never loses money.

2. What is the latency difference between async and semi‑sync replication, and how does it affect the payment flow?

   **Answer:** Same‑dc semi‑sync adds 2–3ms; cross‑dc adds 10–15ms. The payment flow's P99 target is 50ms, so same‑dc semi‑sync fits but cross‑dc exceeds the budget.

3. Why does the candidate apply semi‑sync only to payment tables and not to all tables?

   **Answer:** Because only payment writes require zero data loss. Applying semi‑sync everywhere would reduce throughput without meaningfully lowering business risk. The tiered approach allocates reliability where it protects revenue.

4. What is lossless semi‑sync, and why didn't the team adopt it?

   **Answer:** Lossless semi‑sync flushes the binlog to the master's own disk and returns immediately without waiting for replicas. It protects against process crashes but not physical disk damage. The team found its incremental benefit didn't justify the added operational complexity.

5. What is the main principle behind the candidate's replication strategy?

   **Answer:** Match the replication guarantee to the business criticality of each table—strict durability for core payment data, maximum throughput for less critical order writes.

---

*Word count (dialogue): ~490 words*  
*Level: Intermediate / T2*
