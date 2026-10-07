这份预习材料**不用 material 原文**，概念全部用自己的话复述。每个概念的「用自己的话理解」提供**中英双语**（英文按 **B2**）。长句练习的重点是**嵌套从句**——定语从句、状语从句、非限制性从句叠在一起练。

---

## 课前 3 分钟：今天讲什么

**话题：** 主从复制已经分摊读了，为什么还要**分区/分片**？——写吞吐和磁盘容量怎么扩？

**方案演进（material 技术干点）：**

```
① 主从复制（读扩展）→ ② 写仍单点 → ③ 垂直扩展（有限）→ ④ 跨机器分片（写扩展）→ ⑤ 分区裁剪（查性能）
```

**故事线：**

```
主库写+从库读 OK → 写吞吐见顶、磁盘快满 → 从库不能帮写 → 换大机器有 CPU/内存/带宽上限 → 512GB 比十台小机贵 → 单机逻辑分区仍同一 CPU/IO → 跨机器分片每台扛部分写 → hash(user_id)%16 → 只扫分片7 → 5亿行→3000万行
```

| 阶段 | 解决什么 | 遗留什么 |
| --- | --- | --- |
| 单库 | — | 读写互抢 |
| 主从复制 | 读扩展 | 写瓶颈、容量 |
| 垂直扩展 | 短期缓解 | 物理上限 |
| 跨机器分片 | 写吞吐 + 容量 + 查询裁剪 | 运维复杂度 |

| 关键数字 | 含义 |
| --- | --- |
| 16 分片 | `hash(user_id) % 16` |
| 5 亿 → 3000 万 | 分区裁剪后扫描行数 |
| 512GB vs 十台小机 | 垂直扩展性价比 |

**规律：** **复制扩读，分片扩写**——单机逻辑分区不切写入路径，只有跨机器分片才是横向扩展。

---

## 概念 1：主从复制——只扩读，不扩写

### 用自己的话理解（中英双语）

**中文：**

订单系统已做**主从复制**：主库写、从库读，读压力分摊不错。但监控显示**写入吞吐接近单库上限**，磁盘也快满。

候选人核心观点：**复制只解决读扩展，不解决写扩展**。

- 从库**只能**处理读请求
- 所有写必须打主库；主库撑不住，加再多从库也帮不了写
- 复制适合**读多写少**的读并发，对**写入吞吐**无帮助

技术本质：主从是**全量数据冗余**——写先落主库，再经 binlog 同步到从库。主库写能力是系统写吞吐的**天花板**，写无法像读那样水平扩展。

**English (B2):**

The order system already uses **master-slave replication**: the master handles writes, **and** replicas handle reads, **which** spreads read pressure nicely. **But** monitoring shows **write throughput** approaching the single-node limit **and** the disk is nearly full.

The candidate's core point: **replication scales reads, not writes**.

Replicas can **only** serve read requests. Every write must hit the master — **if** the master cannot keep up, adding more replicas does not help at all. Replication fits a **read-heavy workload** **where** read concurrency is the pain point. It does nothing for **write throughput**.

Technically, replication is **full-data redundancy**: writes land on the master first, **then** sync to replicas through the binlog. The master's write capacity is the **ceiling** on system write throughput — writes cannot scale out the way reads can.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| master-slave replication | 主从复制 | Master-slave replication copies data to replicas **that** serve reads only. |
| write throughput | 写入吞吐 | Write throughput is capped by the master **because** replicas cannot accept writes. |
| read-heavy workload | 读多写少负载 | A read-heavy workload benefits from replicas **that** offload SELECT traffic. |
| replica | 从库/副本 | A replica is a copy **that** cannot replace the master for writes. |
| single point of write | 单点写入 | The master remains a single point of write **no matter** how many replicas you add. |
| read scalability | 读扩展性 | Read scalability improves **when** you add replicas **that** share read load. |

### 嵌套从句练习：说为何复制不够

**Layer 2：**
> Replication scales reads **because** replicas handle SELECTs, **but** every write still hits the master.

**Layer 3：**
> **Although** adding replicas spreads read pressure, write throughput stays capped **because** all INSERTs and UPDATEs must go through the master, **which** replicas cannot help with.

**Layer 4 — 完整嵌套版：**
> **When** write throughput approaches the single-node limit **and** the disk is almost full, adding more replicas does not help **because** replication only creates redundant copies **that** serve reads — **a pattern in which** the master remains the sole write path, **so** the system's write capacity cannot grow horizontally **no matter** how many read-only followers you deploy.

**中文对照：** 写吞吐接近单库上限、磁盘快满时，加从库无济于事——复制只是多出服务读的冗余副本，主库仍是唯一写路径，写能力无法随从库数量水平扩展。

---

## 概念 2：垂直扩展——缓解但有硬上限

### 用自己的话理解（中英双语）

**中文：**

面试官问：换更大机器（**垂直扩展 / scale up**）能否解决写吞吐和磁盘容量？

候选人：能**暂时缓解**，但有**物理上限**——CPU 核数、内存、磁盘带宽都有最大值。订单量持续增长，迟早撞天花板。

成本也不划算：512GB 内存的大机器可能比**十台小机器**还贵，扩展曲线非线性。

结论：垂直扩展是**把问题往后推**，不能根除持续增长带来的写和容量需求；数据量超过单机磁盘时，换大盘也解决不了根本问题。

**English (B2):**

The interviewer asks **whether** upgrading to a bigger machine — **vertical scaling or scale-up** — can fix write throughput and disk capacity.

The candidate says it helps **for a while**, **but** there are **hard physical limits**: maximum CPU cores, memory, and disk bandwidth. **As** order volume keeps growing, you eventually hit that ceiling.

Cost is poor too: a box with **512 GB** of RAM can cost more **than ten smaller machines** combined, **and** the scaling curve is not linear.

Vertical scaling **pushes the problem down the road**. It does not remove the need for sustained write and storage growth. **When** data exceeds what one disk can hold, a bigger box alone cannot solve the root issue.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| vertical scaling | 垂直扩展 | Vertical scaling upgrades one machine **whose** limits you eventually hit again. |
| physical limit | 物理上限 | Physical limits are caps on cores, memory, and bandwidth **that** no vendor can exceed forever. |
| disk bandwidth | 磁盘带宽 | Disk bandwidth is a bottleneck **that** bigger CPUs alone cannot fix. |
| disk capacity | 磁盘容量 | Disk capacity on one node is finite **when** orders keep accumulating. |
| NVMe | 高速固态 | NVMe drives improve I/O **but** still share one machine's bandwidth ceiling. |

### 嵌套从句练习：说垂直扩展的边界

**Layer 3：**
> **Although** vertical scaling adds cores and NVMe storage, a single machine still has maximum limits **that** growing write load will eventually exceed.

**Layer 4 — 完整嵌套版：**
> **When** write throughput and disk usage keep climbing, you can scale up to a 64-core box with 512 GB of RAM, **which** may buy time — **but** because CPU cores, memory, and disk bandwidth all have hard ceilings **and** large machines cost more per unit of capacity than many small ones, vertical scaling only postpones the bottleneck **rather than** giving you the linear write growth **that** cross-machine sharding can provide.

**中文对照：** 写吞吐和磁盘占用持续上升时，可升级到 64 核、512GB 的大机器争取时间——但 CPU、内存、磁盘带宽都有硬顶，大机器单位容量成本更高，垂直扩展只是推迟瓶颈，无法像跨机器分片那样线性扩展写入。

---

## 概念 3：单机逻辑分区 vs 跨机器分片

### 用自己的话理解（中英双语）

**中文：**

「分区能分摊写入」——面试官先要澄清：是**单机逻辑分区**，还是**跨机器分片**？

| | 单机逻辑分区 | 跨机器分片 |
| --- | --- | --- |
| 做法 | 同一实例/磁盘上把大表切成几段 | 按分片键把数据分布到多台机器 |
| 写路径 | 仍打同一台机器的 CPU/IO | 每台机器只扛一部分写 |
| 解决写吞吐？ | ❌ 否 | ✅ 是（真正水平扩展） |
| 主要价值 | 大表管理、索引/锁 | 写扩展 + 容量 + 查询裁剪 |

候选人明确：**跨机器分片（sharding）**。单机分区只是在同一块磁盘上切几刀，写入吞吐仍受单机限制。

**English (B2):**

**When** the candidate says partitioning can spread writes, the interviewer first clarifies: **logical partitioning on one machine**, or **sharding across machines**?

| | Logical partitioning | Cross-machine sharding |
| --- | --- | --- |
| What it does | Splits a large table on one instance/disk | Spreads data across nodes by sharding key |
| Write path | Still hits the same CPU and I/O | Each node handles a fraction of writes |
| Fixes write throughput? | No | Yes — true horizontal scaling |
| Main benefit | Manage huge tables, indexes, locks | Write scale, capacity, query pruning |

The candidate is clear: **cross-machine sharding**. Logical partitioning only slices the table on the same disk — write throughput remains bound to one machine.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| logical partitioning | 逻辑分区 | Logical partitioning splits a table **that** still lives on one server. |
| cross-machine sharding | 跨机器分片 | Cross-machine sharding routes writes to nodes **that** each own part of the data. |
| shard | 分片 | A shard is a node **that** stores and serves a subset of rows. |
| horizontal scaling | 水平扩展 | Horizontal scaling adds machines **that** each take a share of writes. |
| sharding key | 分片键 | A sharding key is the field **that** decides **which** shard holds a row. |

### 嵌套从句练习：纠正「分区就能扩写」误区

**Layer 4：**
> **Although** people say "partitioning" as if it always scales writes, logical partitioning on a single box only splits a table on the same disk — **a change that** does not increase total CPU or I/O capacity — **whereas** cross-machine sharding distributes data across nodes **that** each handle a fraction of the writes, **which** is the only approach **that** truly scales write throughput and storage capacity.

**中文对照：** 虽说「分区」听起来能扩写，单机逻辑分区只是在同盘切表，总 CPU/IO 容量不变；跨机器分片把数据摊到各节点、各扛一部分写，才是真正扩展写吞吐和存储容量的做法。

---

## 概念 4：分区裁剪——分片如何加速查询

### 用自己的话理解（中英双语）

**中文：**

跨机器分片不仅扩写，还能通过**分区裁剪（partition pruning）** 缩小查询扫描范围。

例子：按 `user_id` **哈希**成 **16** 个分片。查某用户订单时：

1. 计算 `hash(user_id) % 16` → 目标分片，如**分片 7**
2. **只扫分片 7**，其余 15 个分片不碰
3. 扫描从 **5 亿行** 降到约 **3000 万行**

原理：查询带**分片键**等值条件时，路由到**唯一**分片，避免全分片扫描（类似单机分区裁剪，但是在分布式层）。

限制：查询**不含分片键**（如按时间查全站订单）需扫所有分片，裁剪失效，要靠全局索引等方案。

**English (B2):**

Cross-machine sharding not only scales writes **but** also shrinks query scans through **partition pruning**.

Example: hash by `user_id` into **16** shards. **When** a query asks for one user's orders:

1. Compute `hash(user_id) % 16` → target shard, say **shard 7**
2. **Scan only shard 7**; skip the other 15 shards entirely
3. Scan drops from **500 million rows** to roughly **30 million**

The idea: **when** the query includes an equality condition on the **sharding key**, routing hits a **single** shard and avoids a full shard scan — like partition pruning on one database, **but** at the distributed layer.

The limit: **if** the query lacks the sharding key — for example, a time-range report across all users — every shard must be scanned, **and** pruning does not help much.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| partition pruning | 分区裁剪 | Partition pruning skips shards **that** the query does not need. |
| scan range | 扫描范围 | The scan range shrinks **when** only one of sixteen shards is touched. |
| hash | 哈希 | Hash routing maps a user ID to the shard **that** stores that user's rows. |
| target shard | 目标分片 | The target shard is the one **where** `hash(user_id) % 16` lands. |
| full table scan | 全表扫描 | Without the sharding key, the query may fall back to scans **that** hit every shard. |

### 嵌套从句练习：解释 5 亿 → 3000 万

**Layer 3：**
> **When** we hash `user_id` to shard 7, we scan only that shard, **which** holds about one sixteenth of the rows.

**Layer 4 — 完整嵌套版：**
> **When** a query filters by `user_id`, we compute `hash(user_id) % 16` to find the target shard — **say** shard 7 — **and** scan only that shard instead of all sixteen, **which** cuts the scan range from five hundred million rows to roughly thirty million, **because** partition pruning ensures each query touches only the shard **that** actually contains the data **that** the predicate needs.

**中文对照：** 查询带 `user_id` 条件时，用 `hash(user_id) % 16` 定位目标分片（如分片 7），只扫该分片而非全部 16 个——扫描从 5 亿行降到约 3000 万，因为分区裁剪让查询只碰含所需数据的分片。

---

## 概念 5：扩展路径总结——单库到分片

### 用自己的话理解（中英双语）

**中文：**

架构演进一条线：

```
单库 → 主从复制 → 垂直扩展 → 跨机器分片
       (解决读)   (有限缓解)   (解决写+容量)
```

- **单库**：读写互抢，5 亿行后查询从 50ms 恶化到 2s
- **主从**：读扩展 ✅；写仍单点、容量仍有限 ❌
- **垂直扩展**：短期 ✅；物理上限、性价比 ❌
- **分片**：写吞吐、磁盘容量、带分片键的查询 ✅；引入跨分片查询、分布式事务、扩容再平衡等复杂度 ❌

核心记忆：**Replication scales reads. Sharding scales writes.**

**English (B2):**

The architecture path runs like this:

```
Single DB → replication → scale up → cross-machine sharding
            (reads)       (delay)     (writes + capacity)
```

Single database: reads and writes fight on one node; queries degrade **as** rows grow. Replication: read scale yes; write and capacity still limited. Scale-up: temporary relief; hard limits and poor cost. Sharding: write throughput, disk capacity, and keyed queries improve; complexity rises for cross-shard queries, transactions, and rebalancing.

Remember: **replication scales reads; sharding scales writes**.

### 嵌套从句练习：串讲演进逻辑

**Layer 4：**
> **Although** master-slave replication solved our read pressure **by** adding replicas **that** serve SELECTs, write throughput still hit the master's ceiling **because** every write must land there first — **which** is why we moved to cross-machine sharding **that** distributes both data and writes, **whereas** logical partitioning on one box would have left us bound to the same CPU and disk limits **that** replication never removed in the first place.

**中文对照：** 主从复制通过增加服务 SELECT 的从库缓解了读压力，但写仍必须先落主库，写吞吐仍触顶——因此转向跨机器分片以分散数据和写入；若在单机做逻辑分区，仍受复制从未消除的同一 CPU/磁盘上限束缚。

---

## 课堂对话套路（B2 + 嵌套从句）

### 套路 1：老师问「复制不是已经扩展了吗」

> Replication only solves read scalability, not write scalability. Replicas can only serve reads — **every write still hits the master**, **so** adding replicas does not increase write capacity **even when** read pressure is well distributed.

---

### 套路 2：老师问「换大机器行不行」

> Vertical scaling can help for a while, **but** a single machine has hard limits on CPU cores, memory, and disk bandwidth. A 512 GB box can cost more than ten smaller machines, **and** it only pushes the bottleneck further down the road **without** giving linear write growth.

---

### 套路 3：老师问「逻辑分区和分片区别」

> Logical partitioning slices a table on the same disk within one machine, **so** all writes still share the same CPU and I/O. **Only** cross-machine sharding distributes data across nodes **that** each handle a fraction of the writes — **which** is true horizontal scaling.

---

### 套路 4：老师问「分区裁剪怎么工作」

> We hash `user_id` to compute the target shard — **say** shard 7 out of sixteen. The query scans only that shard and skips the other fifteen, **which** shrinks the scan range from five hundred million rows to roughly thirty million **because** each query touches only the shard **that** contains the rows it needs.

---

### 套路 5：老师问「什么查询分片帮不上忙」

> **When** the query does not include the sharding key — for example, a time-range report across all users — the router must scan every shard, **which** means partition pruning does not apply **and** you need other patterns like global indexes or aggregated pipelines.

---

### 套路 6：课上主动说话

| 你想做什么 | 嵌套从句版 |
| --- | --- |
| 确认理解 | So replicas offload reads **but** cannot accept writes, **which** is why write throughput still caps at the master, **right**? |
| 请老师举例 | Could you walk through **how** `hash(user_id) % 16` picks the target shard for an order lookup? |
| 表示同意 | That makes sense — logical partitioning on one box doesn't add write capacity **because** CPU and I/O are still shared. |
| 提出疑问 | **But** if we shard by `user_id`, how do we run reports **that** filter only by order date? |
| 追问选型 | Why hash instead of range partitioning for user IDs — **is** it mainly for even load spread? |

---

## 常用句式：嵌套从句版（改写，非原文）

| 功能 | 嵌套从句句式 |
| --- | --- |
| 复制边界 | Replication scales reads **because** replicas handle SELECTs, **but** every write still goes to the master **that** sets the write ceiling. |
| 写瓶颈 | **When** write throughput nears the single-node limit, adding replicas does not help **because** they cannot take write load. |
| 垂直扩展 | Vertical scaling buys time **until** you hit hard limits on cores, memory, and disk bandwidth **that** a bigger box cannot remove forever. |
| 区分分区 | Logical partitioning splits a table **that** still lives on one machine, **whereas** sharding spreads data across nodes **that** each own part of the writes. |
| 分区裁剪 | **If** the query includes the sharding key, we route to one shard **that** we scan alone, **which** avoids touching the other fifteen shards. |
| 扫描缩小 | Partition pruning cuts the scan range **when** only one of sixteen shards contains the rows **that** the query needs. |

---

## 老师可能追问 — 嵌套从句回答

| 老师问 | 你可以答 |
| --- | --- |
| 从库能帮你写吗？ | No — replicas only serve reads, **so** write throughput stays limited by the master **no matter** how many replicas you add. |
| 复制解决什么？ | It solves read concurrency in read-heavy workloads **by** adding copies **that** offload SELECT traffic from the master. |
| 垂直扩展上限？ | CPU cores, memory, and disk bandwidth all have maximum values **that** a single machine cannot exceed. |
| 512GB 机器问题？ | It is expensive and still one node, **so** it postpones rather than removes the capacity ceiling. |
| 单机分区扩写吗？ | No — writes still hit the same CPU and I/O **because** the data stays on one machine. |
| 什么是 sharding key？ | It is the field — such as `user_id` — **that** determines **which** shard stores and serves a row. |
| 16 分片怎么路由？ | We compute `hash(user_id) % 16` to find the target shard **that** holds that user's orders. |
| 5 亿变 3000 万？ | We scan one shard instead of all sixteen, **which** is roughly one sixteenth of the total rows. |
| 无分片键查询？ | The query must scan every shard, **because** pruning needs an equality filter on the sharding key. |
| 分片代价？ | Cross-shard queries, distributed transactions, and rebalancing add complexity **that** replication alone did not introduce. |

---

## 跟读练习：五段 B2 嵌套从句（课前朗读 2 遍）

**Part 1 — 复制只扩读**

> Our order system uses master-slave replication, **so** read pressure is spread across replicas **that** handle SELECTs. **But** write throughput is approaching the single-node limit **because** every write must hit the master first — **a bottleneck that** adding more read-only replicas cannot relieve, **since** replication solves read scalability in read-heavy workloads **but** does nothing for write throughput or total disk capacity on one primary.

**Part 2 — 垂直扩展的局限**

> We could scale up to a larger machine with more CPU cores, more memory, and NVMe drives, **which** helps for a while. **However**, a single box still has hard physical limits, **and** a 512 GB machine can cost more than ten smaller ones — **which** means vertical scaling only pushes the problem down the road **rather than** providing the sustained linear growth **that** our order volume will eventually require.

**Part 3 — 逻辑分区 vs 分片**

> **When** people talk about partitioning, I mean cross-machine sharding, not logical partitioning on one box. Logical partitioning only slices a table on the same disk, **so** writes still share one CPU and one I/O path. **Only when** data is distributed across multiple machines, **each of which** handles a fraction of the writes, do we get true horizontal scaling **that** replication and single-node partitioning cannot deliver.

**Part 4 — 分区裁剪**

> Take sixteen shards keyed by `user_id`. **When** a query asks for one user's orders, we hash the user ID to find the target shard — **say** shard seven — **and** scan only that shard while skipping the other fifteen. That is partition pruning: the scan range shrinks from five hundred million rows to roughly thirty million **because** the query touches only the shard **that** actually contains the rows **that** the filter needs.

**Part 5 — 演进总结**

> The scaling path is clear: replication solved reads, **but** writes stayed on the master until we hit throughput and disk limits. Vertical scaling bought time **until** physical ceilings and cost stopped making sense. Cross-machine sharding finally spread writes and storage across nodes **that** each serve part of the data, **while** partition pruning keeps keyed queries fast — **provided that** the query includes the sharding key **that** routing depends on.

---

## 附录：嵌套从句工具箱

| 从句类型 | 常用引导词 | 练法 |
| --- | --- | --- |
| **定语从句（限定）** | that, which, who, whose, where | *replicas **that** serve reads only* |
| **定语从句（非限定）** | , which / , who | *…the master, **which** caps write throughput* |
| **时间 / 条件状语** | when, if, before, after | ***When** writes hit the master ceiling, sharding helps* |
| **原因 / 结果状语** | because, since, so that | *…shard by user ID **so that** each node owns part of the writes* |
| **对比 / 让步状语** | although, whereas, while | ***Although** replication helps reads, it does not scale writes* |
| **嵌套技巧** | 从句套从句 | 主句 → 定语从句里再套 that/when/which |

**拆句口诀：** 先找主句主干 → 标出每个 that/which/when/because 引导的从句 → 从外往里读 → 再试着合并回去。

---

**课前最少记：** 复制扩读不扩写 · 写全打主库 · 垂直扩展有 CPU/内存/带宽硬顶 · 单机逻辑分区 ≠ 跨机器分片 · 只有分片才横向扩写 · `hash(user_id)%16` → 只扫目标分片 · 5 亿→3000 万 = 分区裁剪 · *Replication scales reads; sharding scales writes.*
