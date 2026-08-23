这份预习材料**不用 material 原文**，概念全部用自己的话复述。每个概念的「用自己的话理解」提供**中英双语**（英文按 **B2**）。长句练习的重点是**嵌套从句**——定语从句、状语从句、非限制性从句叠在一起练。

---

## 课前 3 分钟：今天讲什么

**话题：** 复制策略怎么选——异步、半同步、增强半同步，在写入性能和数据安全之间怎么权衡？

**方案演进（material 技术干点）：**

```
① 异步复制（高性能）→ ② 数据丢失风险 + 补偿兜底 → ③ 半同步延迟量化 → ④ 按表分级 → ⑤ 增强半同步评估后弃用
```

**故事线：**

```
异步复制保性能 → 主库宕机丢最后 200ms → RAID + 对账补偿 → 半同步同机房 +2-3ms / 跨机房 +10-15ms → P99 50ms 预算 → 支付表半同步 / 订单表异步 → 增强半同步只保进程崩溃不保盘坏 → 可靠性预算对准收入
```


| 复制模式               | 主库等待     | 延迟增加                    | 数据丢失风险        |
| ------------------ | -------- | ----------------------- | ------------- |
| 异步                 | 不等待从库    | ≈ 0                     | 可能丢最近几百 ms 写入 |
| 半同步 (AFTER_COMMIT) | 提交后等从库确认 | 同机房 +2-3ms，跨机房 +10-15ms | 提交后崩溃仍有小窗口    |
| 无损半同步 (AFTER_SYNC) | 提交前等从库确认 | 与半同步相近                  | 已确认事务不丢       |
| 增强半同步（对话简化版）       | 刷盘即返回    | ≈ 异步                    | 仅保进程崩溃，不保物理盘坏 |



| 关键数字            | 含义                  |
| --------------- | ------------------- |
| 200ms           | 异步下可能丢失的写入窗口        |
| 2-3ms / 10-15ms | 半同步 vs 异步：同机房 / 跨机房 |
| 50ms            | 支付写入 P99 延迟目标       |
| 支付表半同步 / 订单表异步  | 分级策略                |


**规律：** 不为全库选单一复制模式——把**可靠性预算**投到保护收入的核心表上，其余用异步 + 业务补偿兜底。

---



## 概念 1：异步复制——性能与数据丢失风险



### 用自己的话理解（中英双语）

**中文：**

**异步复制**下，主库把事务写入 binlog 并提交后，立刻返回成功，**不等任何从库确认**。从库自己异步拉取、重放日志。好处是写入延迟最低、吞吐最高——主库不用等网络往返。

代价是：主库返回成功时，从库可能还没收到最近的数据。一旦主库磁盘坏道、断电或整机故障，最后几百毫秒（对话里约 **200ms**）的写入可能永久丢失——从库根本没有这份 binlog。

候选人没有否认风险，而是用多层手段把「概率和影响」压到可接受范围：基础设施（云 + RAID 10）+ 业务层对账补偿。

**English (B2):**

With **asynchronous replication**, the master writes the transaction to the binlog, commits, and returns success **without waiting for any replica to acknowledge**. Replicas pull and replay logs on their own schedule. The benefit is the lowest write latency and the highest throughput, **because** the master does not block on a network round trip.

The cost is clear: **when** the master returns success, replicas may not yet have the most recent data. **If** the master suffers a disk failure, power outage, or full crash, writes from the last few hundred milliseconds — about **200 ms** in the interview scenario — may be lost forever, **because** no replica ever received that binlog.

The candidate does not deny the risk. Instead, they argue **that** probability and impact are manageable through infrastructure hardening and application-level compensation.

### 关键词（B2）


| 英文                       | 中文     | 带从句的例句                                                                                        |
| ------------------------ | ------ | --------------------------------------------------------------------------------------------- |
| asynchronous replication | 异步复制   | Async replication returns success **before** any replica confirms receipt of the binlog.      |
| binlog                   | 二进制日志  | The binlog is a log **that** records every change **which** replicas must replay.             |
| throughput               | 吞吐量    | Throughput stays high **because** the master never waits on replicas.                         |
| data loss                | 数据丢失   | Data loss happens **when** the master fails **before** replicas receive recent binlog events. |
| power outage             | 断电     | A power outage can destroy writes **that** never left the master.                             |
| RAID 10                  | 磁盘阵列10 | RAID 10 is storage **that** survives single-disk failures on the master.                      |




### 嵌套从句练习：说异步复制的代价

**Layer 2：**

> Async replication is fast **because** the master never waits for replicas **that** pull binlog events asynchronously.

**Layer 3：**

> **Although** async replication maximizes throughput, a master crash can destroy writes **that** were committed locally **but** never reached a replica — **which** is why the last 200 ms of binlog may be lost forever.

**Layer 4 — 完整嵌套版：**

> **When** you choose asynchronous replication for performance, the master returns success **as soon as** the transaction is committed locally, **without waiting for** a replica **that** may still be hundreds of milliseconds behind — **a trade-off in which** a disk failure or power outage on the master can permanently erase recent writes **that** no follower ever received, **even though** the client was told the operation succeeded.

**中文对照：** 选异步复制是为了性能——主库本地提交成功就立刻返回，不等可能还落后几百毫秒的从库；代价是主库磁盘故障或断电时，客户端已被告知成功、但从库从未收到的最近写入会永久丢失。

---



## 概念 2：业务层补偿——对账与补偿工作流



### 用自己的话理解（中英双语）

**中文：**

数据库层丢了订单，不代表用户丢了钱。候选人真正的安全网在**业务层**：

第三方支付平台会发**异步回调**——通知「这笔支付已成功」。系统收到回调后查本地订单；若找不到（说明异步复制窗口内主库挂了、订单没落到从库），自动触发**补偿工作流**：创建订单、更新支付状态。

用户可能看到几分钟的状态延迟，但资金由对账机制保证不会丢。这是用**可感知的短暂延迟**换**资金安全的确定性**——比在全库上开半同步更精准地保护真正重要的东西。

**English (B2):**

Losing a row in the database does not automatically mean the customer loses money. The candidate's real safety net lives in the **application layer**.

The third-party payment provider sends an **asynchronous callback** **that** reports a successful charge. **When** our system receives it, we look up the local order. **If** the order is missing — **which** can happen **when** the master failed inside the async replication window — a **compensation workflow** automatically creates the order and updates the payment status.

Users may see a delay of a few minutes, **but** reconciliation guarantees they never lose funds. This trades a short, visible delay for certainty about money — **a pattern that** protects what actually matters **without** forcing semi-sync on every table.

### 关键词（B2）


| 英文                    | 中文    | 带从句的例句                                                                                       |
| --------------------- | ----- | -------------------------------------------------------------------------------------------- |
| reconciliation        | 对账    | Reconciliation compares payment records **that** the provider sends against local orders.    |
| compensation workflow | 补偿流程  | A compensation workflow creates missing orders **when** callbacks find a gap.                |
| callback              | 回调    | A callback is a notification **that** the payment provider sends asynchronously.             |
| third-party provider  | 第三方支付 | The third-party provider is the system **whose** records act as an external source of truth. |
| manageable            | 可控的   | Risk is manageable **when** business logic can repair gaps **that** replication missed.      |




### 嵌套从句练习：说补偿如何兜底

**Layer 3：**

> **If** async replication loses an order, the payment callback still arrives, **which** triggers a workflow **that** creates the missing record.

**Layer 4 — 完整嵌套版：**

> **Although** the database may lose the last 200 ms of writes **when** the master fails, our reconciliation pipeline listens for callbacks **that** the payment provider sends — **and if** no matching order exists, a compensation workflow creates it automatically, **so that** users experience at most a few minutes of delay **rather than** losing money **because** an external system of record **that** we do not control still proves the payment succeeded.

**中文对照：** 主库故障时数据库可能丢掉最后 200ms 写入，但支付平台的回调仍会到达；若本地找不到对应订单，补偿工作流会自动创建——用户最多等几分钟看到状态，不会因我们无法控制的复制窗口而丢钱，因为外部支付记录仍能证明付款成功。

---



## 概念 3：半同步复制——延迟量化与适用边界



### 用自己的话理解（中英双语）

**中文：**

**半同步复制**要求主库在返回成功前，至少等**一个从库确认收到 binlog**（写入中继日志即算确认）。可靠性比异步高，代价是写入要多等一次网络往返。

候选人给了实测数据，不是泛泛说「半同步慢」：

- **同机房**：比异步多 **2-3ms**
- **跨机房**：多 **10-15ms**

支付接口 P99 写入目标是 **50ms**。同机房半同步完全在预算内；跨机房半同步可能超标。所以不是「全库半同步」或「全库异步」的二选一，而是看网络拓扑和业务 SLA 再定。

**English (B2):**

**Semi-synchronous replication** requires the master **to wait until at least one replica acknowledges** that it has received the binlog event — typically **after** the event is written to the replica's relay log. It is more durable than async, **but** each commit pays for an extra network round trip.

The candidate quotes measured numbers rather than vague claims:

- **Same data center**: only **2–3 ms** more than async
- **Cross data center**: about **10–15 ms** more

The payment API targets **50 ms** P99 write latency. Same-dc semi-sync fits comfortably; cross-dc semi-sync may exceed the budget. The decision is therefore not "all semi-sync" versus "all async", **but** a question of topology and SLA.

### 延迟对比表


| 场景  | 半同步额外延迟  | vs P99 50ms |
| --- | -------- | ----------- |
| 同机房 | +2-3ms   | ✅ 满足        |
| 跨机房 | +10-15ms | ⚠️ 可能超标     |




### 关键词（B2）


| 英文                           | 中文       | 带从句的例句                                                                               |
| ---------------------------- | -------- | ------------------------------------------------------------------------------------ |
| semi-synchronous replication | 半同步复制    | Semi-sync waits for a replica **that** confirms binlog receipt before returning.     |
| acknowledge                  | 确认       | A replica acknowledges an event **after** it writes the binlog to relay log.         |
| P99 latency                  | 第99百分位延迟 | P99 latency is the threshold **below which** ninety-nine percent of writes complete. |
| data center                  | 数据中心     | Same-dc replication avoids the extra latency **that** cross-dc links introduce.      |
| round trip                   | 往返       | Semi-sync adds a round trip **that** async replication skips entirely.               |




### 嵌套从句练习：用数据说半同步能不能用

**Layer 2：**

> Semi-sync adds only 2–3 ms **when** the replica sits in the same data center.

**Layer 3：**

> **Although** semi-sync is safer than async, cross-dc semi-sync adds 10–15 ms, **which** may exceed our 50 ms P99 target **that** payment writes must meet.

**Layer 4 — 完整嵌套版：**

> **When** we benchmarked semi-sync against async, same-dc replication added only 2–3 ms, **which** fits comfortably inside our 50 ms P99 budget for payment writes, **whereas** cross-dc semi-sync added 10–15 ms — **a gap that** is small in absolute terms **but** large enough **to push** some requests over the SLA **that** our payment API must satisfy.

**中文对照：** 实测同机房半同步只比异步多 2-3ms，落在支付写入 50ms P99 预算内；跨机房多 10-15ms，绝对值不大，却足以让部分请求超出支付 API 必须满足的 SLA。

---



## 概念 4：分级复制策略——可靠性预算对准业务价值



### 用自己的话理解（中英双语）

**中文：**

最终方案不是给整个库统一一种复制模式，而是**按表分级**：


| 表     | 策略     | 理由                 |
| ----- | ------ | ------------------ |
| 核心支付表 | 同机房半同步 | 资金数据零丢失，+2-3ms 可接受 |
| 普通订单表 | 异步     | 保吞吐，极低概率丢失由对账补偿兜底  |


核心思想：**可靠性预算有限**，不要均摊到每张表。支付表直接保护收入，值得付 2-3ms；订单表丢了最后几百毫秒，回调和对账能修，没必要全库半同步拖慢写入。

「Not every write needs the same level of durability」——把严格保障用在真正保护营收的地方。

**English (B2):**

The final design does not apply one replication mode to the entire database. Instead, the team uses a **tiered approach**:


| Table                | Strategy          | Rationale                                                    |
| -------------------- | ----------------- | ------------------------------------------------------------ |
| Core payment tables  | Same-dc semi-sync | Zero data loss for money; +2–3 ms is acceptable              |
| Regular order tables | Async             | Maximum throughput; rare gaps are repaired by reconciliation |


The idea is that **reliability budget is finite**. Payment tables directly protect revenue, **so** they earn the extra 2–3 ms of semi-sync. Order tables may lose the last few hundred milliseconds in extreme cases, **but** callbacks and reconciliation can repair them — **which** makes global semi-sync an unnecessary throughput tax.

Not every write needs the same durability. Strict guarantees belong **where** they actually protect revenue.

### 关键词（B2）


| 英文                 | 中文    | 带从句的例句                                                                                               |
| ------------------ | ----- | ---------------------------------------------------------------------------------------------------- |
| tiered approach    | 分级策略  | A tiered approach assigns different modes to tables **whose** business value differs.                |
| durability         | 持久性   | Durability is the guarantee **that** committed data survives failures.                               |
| reliability budget | 可靠性预算 | A reliability budget is the limited amount of latency **that** you can spend on stronger guarantees. |
| revenue            | 营收    | Payment tables protect revenue **that** order tables alone cannot recover.                           |
| payment table      | 支付表   | A payment table stores records **for which** zero data loss is mandatory.                            |




### 嵌套从句练习：说为何按表分级

**Layer 3：**

> Core payment tables use semi-sync **because** they need zero data loss, **whereas** order tables stay async **because** reconciliation can repair rare gaps.

**Layer 4 — 完整嵌套版：**

> **Although** we could enable semi-sync for every table, that would reduce throughput on writes **that** do not directly protect revenue — **which** is why we use a tiered approach **in which** payment tables, **whose** records must never be lost, run with same-dc semi-sync, **while** regular order tables stay on async replication **that** relies on callbacks and compensation workflows **to fix** the rare gaps **that** only appear **when** the master fails inside the async window.

**中文对照：** 虽说可以给每张表都开半同步，但会拖慢那些不直接保护营收的写入；因此采用分级策略：绝不能丢的支付表用同机房半同步，普通订单表保持异步，靠回调和补偿工作流修复主库在异步窗口内故障时的罕见缺口。

---



## 概念 5：增强半同步——评估后为何暂不引入



### 用自己的话理解（中英双语）

**中文：**

面试官提到的**增强半同步**（对话中的简化描述）：主库把 binlog **刷到本地磁盘**就返回，不等从库确认。性能和异步接近，可靠性介于异步和全半同步之间。

候选人评估结论：

- **能防什么**：主库**进程崩溃**——binlog 已在盘里，重启可恢复。
- **防不了什么**：**物理磁盘损坏**——盘坏了，数据和 binlog 一起没。
- **为何不采用**：增量收益（多覆盖一种故障）不足以抵消**运维复杂度**；支付已用半同步保零丢失，订单用异步 + 补偿已够。

标准 MySQL **无损半同步（AFTER_SYNC）** 是另一回事：在**提交前**等从库确认，可靠性更高，延迟与半同步相近。对话里候选人按面试官的简化版回答，重点在「故障类型覆盖 vs 运维成本」的取舍。

**English (B2):**

The interviewer describes **enhanced semi-sync** in simplified terms: the master **flushes the binlog to local disk** and returns **without waiting for replicas**. Latency stays close to async, **while** reliability sits between async and full semi-sync.

The candidate's evaluation:

- **What it protects**: **master process crashes** — the binlog is on disk and can be recovered after restart.
- **What it does not protect**: **physical disk damage** — **if** the disk itself fails, both data and binlog are gone.
- **Why they skipped it**: the incremental benefit does not justify **operational complexity**; payments already use semi-sync for zero loss, and orders are covered by async plus reconciliation.

Standard MySQL **lossless semi-sync (**`AFTER_SYNC`**)** is different: it waits for replica acknowledgment **before** commit, **which** offers stronger guarantees at similar latency. In the interview, the candidate answers the simplified version, **focusing on** which failure modes matter and whether extra configuration is worth it.

### 故障覆盖对比


| 故障类型 | 异步  | 增强半同步（对话版） | 半同步     |
| ---- | --- | ---------- | ------- |
| 进程崩溃 | 可能丢 | binlog 可恢复 | 从库已收到   |
| 物理盘坏 | 丢   | 仍丢         | 从库有副本   |
| 写入延迟 | 最低  | ≈ 异步       | +2-15ms |




### 关键词（B2）


| 英文                     | 中文     | 带从句的例句                                                                                       |
| ---------------------- | ------ | -------------------------------------------------------------------------------------------- |
| lossless semi-sync     | 无损半同步  | Lossless semi-sync waits before commit **so that** confirmed transactions cannot be lost.    |
| flush                  | 刷盘     | Flush means writing buffered binlog data to disk **before** returning.                       |
| physical disk damage   | 磁盘物理损坏 | Physical disk damage destroys data **that** no local flush can recover.                      |
| operational complexity | 运维复杂度  | Operational complexity rises **when** you add modes **that** teams must monitor separately.  |
| incremental benefit    | 增量收益   | Incremental benefit is the extra safety **that** a new mode buys over what you already have. |
| risk profile           | 风险状况   | Our risk profile is the set of failures **that** we actually need **to survive**.            |




### 嵌套从句练习：说为何弃用增强半同步

**Layer 3：**

> Enhanced semi-sync helps **when** the master process crashes, **but** it does nothing **if** the disk itself is destroyed.

**Layer 4 — 完整嵌套版：**

> **Although** enhanced semi-sync protects against process crashes **because** the binlog is flushed to local disk before the client receives success, it cannot survive physical disk damage **in which** both the data files and the binlog are destroyed — **a limitation that** makes its incremental benefit small **when** payment tables already use semi-sync for true zero-loss guarantees **and** order tables rely on reconciliation workflows **that** repair the rare gaps **which** async replication can leave behind.

  **中文对照：** 增强半同步能在进程崩溃时保护数据——刷盘成功后客户端才收到成功；但物理磁盘损坏时数据文件和 binlog 一并毁灭，它无能为力；在支付表已用半同步保零丢失、订单表靠对账修复异步罕见缺口的前提下，它带来的增量收益很小。

---



## 概念 6：Binlog 与两阶段提交——半同步卡在哪个节点



### 用自己的话理解（中英双语）

**中文：**

三种复制模式本质都在控制 **binlog 何时算「安全」**：

- **Binlog**：MySQL Server 层的变更日志，主从复制靠它同步；从库 I/O 线程拉 binlog 写入中继日志，SQL 线程重放。
- **Redo log**：InnoDB 引擎层的物理日志，保崩溃恢复。两者通过**两阶段提交**协作。

半同步插件的等待点决定可靠性：


| 模式           | 等待点                   |
| ------------ | --------------------- |
| 异步           | 不等待                   |
| AFTER_COMMIT | **提交后**、返回客户端前等从库     |
| AFTER_SYNC   | 写 binlog 后、**提交前**等从库 |


`AFTER_SYNC` 把等待点前移，确保提交前至少一个从库已有 binlog——已返回成功的交易切换后不丢。`AFTER_COMMIT` 有个漏洞：主库已提交、别的会话可见，但从库可能还没收到——此时主库崩溃会丢数据。

**English (B2):**

All three replication modes are really about **when the binlog is considered safe enough**.

The **binlog** is a server-level log of changes **that** replicas replay; the replica I/O thread pulls it into a relay log, **and** the SQL thread applies it. The **redo log** is InnoDB's physical crash-recovery log. Both cooperate through **two-phase commit**.

The semi-sync plugin pauses at different points:


| Mode         | Wait point                                           |
| ------------ | ---------------------------------------------------- |
| Async        | No wait                                              |
| AFTER_COMMIT | **After** commit, **before** returning to the client |
| AFTER_SYNC   | **After** binlog write, **before** commit            |


`AFTER_SYNC` moves the wait **before** commit, **so that** at least one replica holds the binlog **before** the transaction becomes visible. `AFTER_COMMIT` leaves a hole: the transaction is already visible on the master **while** replicas may still be waiting — **a window in which** a crash can lose data **that** clients were about **to be told** succeeded.

### 关键词（B2）


| 英文               | 中文    | 带从句的例句                                                                               |
| ---------------- | ----- | ------------------------------------------------------------------------------------ |
| relay log        | 中继日志  | The relay log is a buffer **where** the replica stores binlog events before replay.  |
| redo log         | 重做日志  | The redo log records physical page changes **that** InnoDB needs for crash recovery. |
| two-phase commit | 两阶段提交 | Two-phase commit coordinates InnoDB and the binlog **so that** both stay consistent. |
| AFTER_SYNC       | 提交前等待 | `AFTER_SYNC` waits for replicas **before** the transaction is committed.             |
| AFTER_COMMIT     | 提交后等待 | `AFTER_COMMIT` waits **after** commit, **which** leaves a small loss window.         |




### 嵌套从句练习：说 AFTER_SYNC 为何更安全

**Layer 4：**

> **Although** `AFTER_COMMIT` semi-sync waits for a replica, it does so **after** the transaction is already visible on the master — **a timing gap in which** a crash can lose data, **whereas** `AFTER_SYNC` waits **before** commit, **ensuring that** at least one replica holds the binlog **before** any client is told the write succeeded.

**中文对照：** `AFTER_COMMIT` 半同步虽等从库，但等待发生在事务已在主库可见之后——崩溃仍可能丢数据；`AFTER_SYNC` 在提交前等待，确保至少一个从库已有 binlog，客户端才会被告知写入成功。

---



## 课堂对话套路（B2 + 嵌套从句）



### 套路 1：老师问「异步复制丢了订单怎么办」

> Data loss is possible, **but** the probability and impact are manageable. Our master uses RAID 10 on cloud instances, **and even if** we lose the last 200 ms of binlog, our reconciliation pipeline listens for payment callbacks **that** the provider sends. **If** the order is missing, a compensation workflow creates it automatically — **so that** users may see a few minutes of delay **but** never lose money.

---



### 套路 2：老师问「半同步慢多少，支付能满足 50ms 吗」

> We measured it: same-dc semi-sync adds only 2–3 ms compared to async, **which** fits inside our 50 ms P99 target for payment writes, **whereas** cross-dc semi-sync adds 10–15 ms and may exceed the budget — **which** is why we enable semi-sync only **where** replicas sit in the same data center.

---



### 套路 3：老师问「为什么不全库半同步」

> **Although** semi-sync is safer, applying it everywhere would reduce throughput on writes **that** do not directly protect revenue. We use a tiered approach: payment tables run with semi-sync for zero data loss, **while** order tables stay on async **because** reconciliation can repair the rare gaps **that** only appear **when** the master fails inside the replication window.

---



### 套路 4：老师问「增强半同步为什么没上」

> We evaluated enhanced semi-sync, **which** protects against process crashes **because** the binlog is flushed to disk, **but** it cannot survive physical disk damage **in which** both data and binlog are destroyed. The incremental benefit did not justify the operational complexity, **especially when** payments already use semi-sync and orders rely on compensation workflows.

---



### 套路 5：老师问「AFTER_COMMIT 和 AFTER_SYNC 区别」

> `AFTER_COMMIT` waits for replicas **after** the transaction is committed, **which** leaves a window **where** other sessions already see the data **but** replicas may not — **whereas** `AFTER_SYNC` waits **before** commit, **ensuring that** at least one replica holds the binlog **before** the client receives success.

---



### 套路 6：课上主动说话


| 你想做什么 | 嵌套从句版                                                                                                                                         |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| 确认理解  | So async replication is fast **because** the master never waits, **but** a crash can lose writes **that** replicas never received, **right**? |
| 请老师举例 | Could you explain **when** `AFTER_COMMIT` leaves a loss window **that** `AFTER_SYNC` closes?                                                  |
| 表示同意  | That makes sense — a tiered approach spends reliability budget on payment tables **that** directly protect revenue.                           |
| 提出疑问  | **But** if we only semi-sync payment tables, what happens to orders **that** are lost **before** the callback arrives?                        |
| 追问边界  | How do you decide **which** tables deserve semi-sync **and which** can rely on reconciliation?                                                |


---



## 常用句式：嵌套从句版（改写，非原文）


| 功能     | 嵌套从句句式                                                                                                                                                                                     |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 承认风险可控 | Data loss is possible, **but** the probability and impact are manageable **because** infrastructure hardening and reconciliation workflows catch gaps **that** replication misses.         |
| 描述补偿   | **If** the order is missing **when** the callback arrives, a compensation workflow creates it automatically, **so that** users never lose money **even though** the database row was lost. |
| 量化延迟   | We measured same-dc semi-sync at 2–3 ms over async, **which** fits our 50 ms P99 target, **whereas** cross-dc adds 10–15 ms **that** may exceed the budget.                                |
| 分级策略   | We use a tiered approach **in which** payment tables run semi-sync for zero loss, **while** order tables stay async **because** reconciliation repairs rare gaps.                          |
| 评估后弃用  | We evaluated enhanced semi-sync, **but** the incremental benefit did not justify operational complexity **when** our two-tier strategy already covers the risk profile.                    |
| 可靠性预算  | Not every write needs the same durability — we allocate reliability budget to tables **whose** data directly protects revenue.                                                             |
| 两阶段提交  | `AFTER_SYNC` waits before commit, **ensuring that** at least one replica holds the binlog **before** the client is told the write succeeded.                                               |


---



## 老师可能追问 — 嵌套从句回答


| 老师问            | 你可以答                                                                                                                                       |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 异步复制最大风险？      | The master may return success **before** replicas receive the binlog, **so** a crash can lose recent writes **that** no follower ever got. |
| 200ms 意味着什么？   | It is the window of writes **that** may exist only on the master **if** it fails **before** replication catches up.                        |
| 半同步等的是什么？      | The master waits until at least one replica acknowledges **that** it has received the binlog event **which** was just written.             |
| 同机房 vs 跨机房？    | Same-dc adds 2–3 ms, **which** fits a 50 ms P99 budget; cross-dc adds 10–15 ms, **which** may not.                                         |
| 为何订单表可以异步？     | Order gaps are rare **and** reconciliation workflows **that** consume payment callbacks can recreate missing rows automatically.           |
| 增强半同步防什么？      | It protects against process crashes **where** flushed binlog survives on disk, **but not** physical disk destruction.                      |
| binlog 干什么用？   | Binlog records changes **that** replicas replay **so that** followers stay in sync with the master.                                        |
| AFTER_SYNC 优势？ | It waits before commit, **so** confirmed transactions cannot be lost **when** the master fails after the client receives success.          |
| 可靠性预算是什么？      | It is the limited latency and complexity **that** you spend on stronger guarantees **where** they protect revenue.                         |


---



## 跟读练习：五段 B2 嵌套从句（课前朗读 2 遍）

**Part 1 — 异步复制与数据丢失**

> We chose asynchronous replication **because** the master returns immediately **without waiting for** replicas **that** pull binlog events on their own schedule. The trade-off is clear: **if** the master suffers a disk failure or power outage, writes from the last few hundred milliseconds may be lost forever, **because** no replica ever received that binlog — **even though** clients were already told those operations succeeded.

**Part 2 — 补偿与基础设施**

> **Although** database replication can lose a row, our payment reconciliation pipeline listens for callbacks **that** the third-party provider sends asynchronously. **When** our system cannot find a matching order, a compensation workflow creates it and updates the payment status — **a safety net that** means users may wait a few minutes **but** never lose money, **because** an external record **that** we do not control still proves the charge succeeded.

**Part 3 — 半同步延迟与分级**

> We benchmarked semi-sync and found that same-dc replication adds only 2–3 ms compared to async, **which** fits inside our 50 ms P99 target for payment writes, **whereas** cross-dc semi-sync adds 10–15 ms and may exceed the budget. **That** is why we use a tiered approach: core payment tables run with semi-sync for zero data loss, **while** regular order tables stay on async **to preserve** throughput **because** reconciliation can repair the rare gaps **which** only appear **when** the master fails inside the async window.

**Part 4 — 增强半同步评估**

> We evaluated enhanced semi-sync, **which** flushes the binlog to local disk and returns **without waiting for** replicas. It protects against master process crashes **because** the binlog survives on disk, **but** it cannot help **when** physical disk damage destroys both data and logs. For us, the incremental benefit did not justify the operational complexity, **especially when** payments already use semi-sync and orders rely on compensation workflows **that** cover async replication's rare failure modes.

**Part 5 — 可靠性预算与工程原则**

> The core principle is **to match** the replication guarantee **to** the business criticality of each table. Not every write needs the same durability — applying semi-sync everywhere would hurt performance on data **that** does not directly protect revenue. **By** allocating our reliability budget to payment tables **whose** records must never be lost, **while** letting order tables enjoy async throughput **that** reconciliation can backstop, we get strong safety **where** it matters **without** paying the latency cost everywhere.

---



## 附录：嵌套从句工具箱


| 从句类型          | 常用引导词                          | 练法                                                           |
| ------------- | ------------------------------ | ------------------------------------------------------------ |
| **定语从句（限定）**  | that, which, who, whose, where | 修饰名词：*callbacks **that** the provider sends*                 |
| **定语从句（非限定）** | , which / , who                | 补充信息：*…2–3 ms, **which** fits the P99 budget*                |
| **时间 / 条件状语** | when, if, after, before        | ***When** the master crashes, recent binlog may be lost*     |
| **原因 / 结果状语** | because, since, so that        | *…use semi-sync **so that** payment records never disappear* |
| **对比 / 让步状语** | although, whereas, while       | ***Although** async is fast, crashes can lose recent writes* |
| **嵌套技巧**      | 从句套从句                          | 主句 → 定语从句里再套 that/when/which                                 |


**拆句口诀：** 先找主句主干 → 标出每个 that/which/when/because 引导的从句 → 从外往里读 → 再试着合并回去。

---

**课前最少记：** 异步 = 不等从库，可能丢最后 200ms · 补偿 = 支付回调 + 自动建单 · 半同步同机房 +2-3ms / 跨机房 +10-15ms · P99 50ms · 支付表半同步 / 订单表异步 · 增强半同步只保进程崩溃不保盘坏 · AFTER_SYNC 提交前等从库 · *Match durability to business criticality; spend reliability budget on revenue.*