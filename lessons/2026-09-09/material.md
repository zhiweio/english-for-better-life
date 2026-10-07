# 【中级】Why Partitioning? From Read Replication to Write Scalability

**技术等级：** T2 · **英语等级：** 中 · **字数：** ~500

**Source:** Interview / System Design  
**Level:** T2 / Intermediate  
**Role:** Interviewer, Candidate (2–5 years backend engineer)  
**Estimated Words:** ~488

---

## 故事 Prompt 及故事

```jsx
请根据以下系统设计知识点生成一个中文技术故事，用于后续英语教学。

知识点：[2.4 分区（哈希 vs 范围）]
故事形式：一段面试场景对话，对话双方是面试官和候选人。
技术要求：T2难度（方案对比级），适合2-5年经验后端工程师。
故事冲突设定：
候选人负责的订单系统已经用了主从复制——主库写、从库读，读压力分摊得不错。但写入吞吐接近单库上限，磁盘也快写满。面试官问：主从复制不是已经解决扩展问题了吗？为什么还要引入分区？

面试官追问链（必须严格遵循）：

1. "你们已经做了主从复制——主库写、从库读，读压力分摊了。但现在写入瓶颈怎么解决？从库能帮你写吗？主从复制解决的到底是什么问题？"
2. "写入全压在主库上。那换一台更大的机器呢？垂直扩展能不能解决写入吞吐和磁盘容量的问题？它的上限在哪？"
3. "你刚才说分区能分摊写入。我要先确认——你指的是单机上的逻辑分区，还是分到多台机器上的分片？单机分区只是在同一台机器磁盘上切几刀，写入吞吐还是受这台机器限制。只有跨机器分片才能让每台机器承担一部分写入。你指哪种？"
4. "好，跨机器分片具体怎么提升查询性能？分区裁剪是怎么工作的？为什么它能减少扫描量？"

【必须覆盖的核心概念】（来自核心层）：
分区的必要性、单机分区 vs 跨机器分片

【可选延伸概念】（来自扩展层，T2 可不强制要求）：

候选人的回答要求：
- 说明主从复制只分摊读、不解决写；写入瓶颈必须另寻方案
- 对比垂直扩展和分片在写入吞吐和磁盘容量上的能力差异
- 明确区分单机分区和跨机器分片，说明只有后者能解决写入吞吐和容量
- 解释分区裁剪如何减少查询扫描范围

要求：故事简短，纯对话形式，字数350字。
生成完故事后，请用1-2句话说明你是如何通过追问实现方案对比深度的。
```

**Interviewer:** 你们订单系统已经做了主从复制——主库写、从库读，读压力分摊得不错。但我看监控，写入吞吐接近单库上限，磁盘也快写满。主从复制不是已经解决扩展问题了吗？为什么还要引入分区？

**Candidate:** 主从复制只解决了读扩展，没解决写扩展。从库只能处理读请求，写入永远压在主库上——主库撑不住，从库再多也帮不了写。它解决的问题是"读多写少"场景下的读并发，不是写入吞吐。

**Interviewer:** 那换一台更大的机器呢？垂直扩展能不能解决写入吞吐和磁盘容量？

**Candidate:** 能缓解，但有硬上限。加 CPU、加内存、换 NVMe——单机核心数有上限，内存有上限，磁盘带宽也有上限。订单量持续增长，早晚撞到天花板。而且大机器贵，512GB 内存的成本可能比十台小机器还高。垂直扩展只是把问题往后推，没有根除。

**Interviewer:** 你刚才说分区能分摊写入。我要先确认——你指的是单机上的逻辑分区，还是分到多台机器上的分片？

**Candidate:** 跨机器分片。单机分区只是把一张表在同一个磁盘上切成几段，写入还是打到同一台机器，受同一个 CPU 和 IO 限制，解决不了吞吐问题。只有跨机器分片，把数据分布到多台机器上，每台只扛一部分写入——这才是真正的横向扩展。

**Interviewer:** 那分片具体怎么提升查询性能？分区裁剪是怎么工作的？

**Candidate:** 比如按 `user_id` 哈希分 16 个库。查某个用户的订单时，先对 `user_id` 做哈希算出目标分区——比如分区 7——然后只扫分区 7，其他 15 个分区不碰。扫描范围从 5 亿行缩小到约 3000 万行。这就是分区裁剪：让每个查询只碰它需要碰的分区，而不是全表扫。

**深度实现说明：** 第一问揭示主从复制的本质局限——从库只能分担读，写入永远压在主库；第二问逼出垂直扩展的物理上限；第三问严格区分单机分区和跨机器分片，纠正"分区就能解决写入"的常见误区；第四问用哈希分片实例解释分区裁剪如何缩小查询扫描范围，完成从"复制不够用"到"分片怎么用"的完整逻辑链。

---

## Background

### 文章技术干点

这段对话围绕**数据库扩展性**展开，核心问题是：当写吞吐和存储容量达到单机瓶颈时，为什么复制不够，需要分片（sharding）。候选人清晰地解释了复制与分片的本质区别、垂直扩展的局限性，以及分片如何通过分区裁剪提升查询性能。以下从技术角度分析其中的要点。

---

### 1. 复制的局限性：只扩展读，不扩展写

**问题**：面试官认为已经用了主从复制，读压力分散了，为什么还需要分片？

**候选人回答**：

- 复制（replication）中，主库承担全部写请求，从库只服务读。
- 写吞吐瓶颈在主库，增加从库无法分担写负载。
- 因此复制解决的是**读扩展性**，对写扩展性没有任何帮助。

**技术本质**：

- 主从复制是**数据冗余**，每个从库拥有全量数据副本。
- 写操作必须先写入主库，然后通过 binlog 同步到从库，所以主库的写能力是系统写吞吐的上限。
- 读请求可以被多个从库分摊，但写请求只能由主库处理，无法水平扩展。

---

### 2. 垂直扩展（Scale Up）的物理与成本限制

**面试官追问**：能否通过升级硬件（更大的机器）解决写吞吐和磁盘容量问题？

**候选人回答**：

- 垂直扩展可以暂时缓解，但存在**物理上限**：CPU 核数、内存容量、磁盘带宽都有最大值。
- 高端机器成本高昂，性价比低（512GB 内存的机器可能比十台普通机器还贵）。
- 垂直扩展只是推迟瓶颈，无法根本解决持续增长的需求。

**技术评价**：

- 垂直扩展确实能提高单机处理能力，但扩展曲线非线性，且受限于硬件工艺。
- 对于快速增长的写负载，垂直扩展不能提供可持续的线性扩展能力。
- 当数据量超过单机磁盘容量时，垂直扩展也无法解决，因为单机磁盘容量有限。

---

### 3. 逻辑分区 vs 跨机器分片

**面试官澄清**：区分"逻辑分区"（同一台机器上分表）和"跨机器分片"，并指出逻辑分区不能解决写吞吐问题。

**候选人确认**：

- 明确指**跨机器分片（sharding）**，而非单机逻辑分区。
- 逻辑分区只是在同一磁盘上拆分表，所有写入仍打到同一台机器，受限于相同的 CPU 和 I/O。
- 只有将数据分布到多台机器，每台机器处理一部分写入，才能实现真正的水平扩展。

**技术解析**：

- **逻辑分区**：在同一数据库实例内，按某个键将大表拆成多个物理子表，但仍然共享同一服务器的 CPU、内存、磁盘 I/O。它主要解决单表过大带来的管理问题（如索引维护、锁竞争），但对总写吞吐没有提升。
- **水平分片**：将数据按分片键（如 `user_id`）分布到不同的物理节点上，每个节点拥有部分数据，并独立处理读写。写请求被路由到对应分片，从而线性扩展写吞吐。

---

### 4. 分片如何提升查询性能：分区裁剪

**面试官问**：分片如何提升查询性能？分区裁剪如何减少扫描范围？

**候选人举例**：

- 按 `user_id` 哈希分成 16 个分片。
- 查询特定用户的订单时，先计算 `hash(user_id) % 16` 得到目标分片，如分片 7。
- 只扫描分片 7，跳过其他 15 个分片。
- 扫描行数从 5 亿行缩小到约 3 千万行，这就是**分区裁剪**。

**技术原理**：

- **分片键（sharding key）** 是决定数据分布的字段。查询若包含该字段的等值条件，可以通过哈希路由直接定位到唯一分片。
- 避免全分片扫描，将 I/O 和计算压力集中在单个节点上，显著降低响应时间。
- 这种优化类似于数据库中的分区裁剪（partition pruning），但这里是在分布式层面实现的。

**限制**：

- 如果查询不包含分片键（例如按时间范围查询所有用户的订单），则必须扫描所有分片，性能提升有限。此时需要二级索引或全局索引等方案。
- 分片键的选择至关重要，需均衡数据分布和查询模式。

---

### 5. 分片带来的额外复杂性（隐含但未深入）

虽然对话未深入，但分片并非没有代价，通常需要考虑：

- **跨分片查询**：需要聚合多个分片结果，增加网络开销和延迟。
- **分布式事务**：跨分片的数据操作难以保证 ACID，需要引入两阶段提交或最终一致性方案。
- **全局唯一 ID 生成**：原来自增主键在分片环境下需要全局唯一，可能采用雪花算法或 UUID。
- **扩容与再平衡**：增加分片时需要迁移数据，影响可用性。
- **备份与恢复**：每个分片独立备份，恢复时需考虑一致性问题。

这些复杂性在对话中未展开，但实际生产中必须纳入设计考量。

---

### 总结

这段对话展示了从复制到分片的扩展路径：

- **复制**解决读扩展，但写仍单点。
- **垂直扩展**短期有效，但受物理和成本限制。
- **逻辑分区**不解决写吞吐，只有**跨机器分片**才能线性扩展写能力。
- **分区裁剪**通过分片键路由，大幅减少扫描范围，提升查询性能。

候选人准确抓住了复制与分片的本质区别，并明确了分片带来的查询优化机制。回答简洁且切中要害，体现了对分布式数据库扩展性的扎实理解。

---

### 系统架构演进图

#### 阶段一：单库架构

```
                          ┌─────────────────────────┐
                          │      应用服务器           │
                          └────────────┬────────────┘
                                       │ 读写请求
                                       ▼
                          ┌─────────────────────────┐
                          │     单库 MySQL           │
                          │                         │
                          │  • 存储全部数据           │
                          │  • 处理所有读写           │
                          │  • 5 亿行订单            │
                          └─────────────────────────┘

痛点：
• 查询响应从 50ms 恶化到 2 秒
• 读写都在一个库上，互抢资源
• 磁盘容量有限
```

---

#### 阶段二：主从复制架构

```
                            ┌──────────────────────────┐
                            │       应用服务器           │
                            └──────┬──────────┬────────┘
                                   │          │
                          ┌────────▼────┐  ┌──▼─────────────┐
                          │   主库       │  │    从库 1       │
                          │  (Master)   │  │   (Replica)    │
                          │             │  │                │
                          │ 处理所有写入  │  │  只处理读请求    │
                          │ 写压力集中    │  │  读压力分摊      │
                          └──────┬─────┘  └──▲─────────────┘
                                 │           │
                                 │ binlog 同步│
                                 └───────────┘

                                    ┌──▼─────────────┐
                                    │    从库 2       │
                                    │   (Replica)    │
                                    │  只处理读请求    │
                                    └────────────────┘

解决了：
✅ 读扩展——从库分摊读压力

仍然存在的痛点：
❌ 写入全压在主库上
❌ 写吞吐接近单库上限
❌ 磁盘容量仍然有限
```

---

#### 阶段三：垂直扩展——换大机器

```
                            ┌──────────────────────────┐
                            │       应用服务器           │
                            └────────────┬─────────────┘
                                         │
                            ┌────────────▼─────────────┐
                            │       更大的主库           │
                            │                          │
                            │  • 64 核 CPU             │
                            │  • 512GB 内存            │
                            │  • NVMe 磁盘             │
                            └─────────────────────────┘

短期效果：
✅ 查询快了一些
✅ 能扛住更多写入

但物理上限：
❌ CPU 核心数有上限
❌ 内存有上限
❌ 磁盘带宽有上限
❌ 成本昂贵，性价低

本质：只是把问题往后推，没有根除
```

---

#### 阶段四：跨机器分片

```
                            ┌──────────────────────────┐
                            │       应用服务器           │
                            │                          │
                            │  按 user_id 哈希路由       │
                            └──────┬──────────┬────────┘
                                   │          │
                      ┌────────────▼───┐  ┌───▼────────────┐
                      │   分片 0        │  │    分片 1       │
                      │  (Shard 0)     │  │   (Shard 1)    │
                      │  存一部分订单    │  │   存一部分订单   │
                      │  处理一部分写入  │  │   处理一部分写入  │
                      └────────────────┘  └────────────────┘

                      ┌────────────────┐  ┌────────────────┐
                      │   分片 2        │  │    分片 3 ...    │
                      │  (Shard 2)     │  │   (Shard 3)    │
                      │  存一部分订单    │  │   存一部分订单   │
                      │  处理一部分写入  │  │   处理一部分写入  │
                      └────────────────┘  └────────────────┘

                      ... 共 16 个分片

解决了：
✅ 写入吞吐——每台机器只扛一部分写入
✅ 磁盘容量——每台机器只存一部分数据
✅ 查询性能——分区裁剪只扫目标分片
```

---

#### 查询示例：分区裁剪

```
查询：查 user_id = 88888 的所有订单

步骤 1：对 user_id 做哈希
        hash(88888) % 16 = 7

步骤 2：只访问分片 7

                ┌───────────────────────────────────┐
                │  分片 0  分片 1  分片 2  ...        │
                │                                    │
                │        【分片 7】 ← 只扫这里         │
                │        约 3000 万行                 │
                │                                    │
                │  其他 15 个分片完全不碰             │
                └───────────────────────────────────┘

效果：扫描范围从 5 亿行 → 3000 万行
```

---

#### 架构演进总结

```
单库 → 主从复制 → 垂直扩展 → 跨机器分片
       (解决读)   (有限缓解)   (解决写)
```

| **阶段** | **解决问题** | **遗留问题** |
| --- | --- | --- |
| 单库 | — | 读写互抢，性能差 |
| 主从复制 | 读扩展 | 写瓶颈 |
| 垂直扩展 | 短期缓解 | 物理上限 |
| 跨机器分片 | 写扩展 + 容量 | 分区复杂度的引入 |

---

## 角色及场景

**Interviewer (面试官):** 考察候选人对分区必要性的理解，从主从复制的局限性切入，逐步追问垂直扩展的物理上限、单机分区与跨机器分片的区别，以及分片如何提升查询性能。

**Candidate (候选人):** 2-5年经验后端工程师，负责订单系统的扩展方案，需清晰解释为何主从复制不够用、为何必须引入跨机器分片，以及分区裁剪的工作机制。

**场景:** 面试。候选人团队的订单系统已使用主从复制，读压力得到缓解，但写入吞吐接近单库上限、磁盘容量告急。面试官通过四轮追问，逼出候选人对"为什么需要分区"的完整论证。

---

## 面试对话 (中级，正文约 488 词)

**Interviewer:**

Your order system already uses master-slave replication. The master handles writes, and the replicas handle reads—your read pressure is well distributed. But I'm looking at the monitoring dashboard now: your write throughput is approaching the single-node limit, and the disk is almost full. **Hasn't replication already solved your scaling problem? Why do you need partitioning on top of that?**

**Candidate:**

**Replication only solves read scalability, not write scalability**. The replicas can only serve read requests. Every write still has to hit the master—if the master can't keep up, adding more replicas doesn't help at all. What replication really solves is read concurrency in a read-heavy workload. It does nothing for write throughput.

**Interviewer:**

**What about upgrading to a bigger machine? Can vertical scaling solve the write throughput and disk capacity problem?**

**Candidate:**

It can help for a while, but there are hard physical limits. You can add more CPU cores, more memory, and switch to NVMe drives, but a single machine has a maximum number of cores, a maximum memory capacity, and a maximum disk bandwidth. As order volume keeps growing, you eventually hit that ceiling. And large machines are expensive—a box with 512 GB of RAM can cost more than ten smaller machines combined. Vertical scaling just pushes the problem further down the road. It doesn't eliminate it.

**Interviewer:**

You said partitioning can spread the write load. I need to clarify something first—**are you talking about logical partitioning on a single machine, or sharding across multiple machines?** Logical partitioning just slices a table into segments on the same disk. All writes still hit the same machine, still limited by the same CPU and I/O. It doesn't solve the throughput problem at all. Only cross-machine sharding lets each machine take a portion of the writes. **Which one do you mean?**

**Candidate:**

**I mean cross-machine sharding.** Logical partitioning on a single box just splits the table on the same disk—writes still go to the same machine, bound by the same CPU and I/O limits. It can't improve write throughput. **Only when you distribute data across multiple machines, with each machine handling a fraction of the writes, do you get true horizontal scaling**. That's what we need.

**Interviewer:**

Alright. **So how exactly does sharding improve query performance?** How does partition pruning work, and why does it reduce the scan range?

**Candidate:**

Take hashing by `user_id` into 16 shards as an example. When a query asks for a specific user's orders, we first hash the `user_id` to compute the target shard—say shard 7. Then we only scan shard 7 and skip the other 15 shards entirely. The scan range shrinks from 500 million rows down to roughly 30 million rows. That's partition pruning in action: **each query only touches the shard it actually needs instead of doing a full table scan.**

---

## 词汇表 (25个高频技术词汇)

| **Vocabulary** | **Pronunciation (IPA)** | **Chinese Meaning** |
| --- | --- | --- |
| master-slave replication | /ˈmæstər sleɪv ˌreplɪˈkeɪʃən/ | 主从复制 |
| replica | /ˈreplɪkə/ | 从库/副本 |
| read-heavy workload | /riːd ˈhevi ˈwɜːrkloʊd/ | 读多写少的工作负载 |
| write throughput | /raɪt ˈθruːpʊt/ | 写入吞吐 |
| vertical scaling | /ˈvɜːrtɪkəl ˈskeɪlɪŋ/ | 垂直扩展 |
| horizontal scaling | /ˌhɒrɪˈzɒntəl ˈskeɪlɪŋ/ | 水平扩展 |
| physical limit | /ˈfɪzɪkəl ˈlɪmɪt/ | 物理上限 |
| CPU cores | /ˌsiː piː ˈjuː kɔːrz/ | CPU核心数 |
| NVMe | /ˌen viː em ˈiː/ | 非易失性内存标准 |
| disk bandwidth | /dɪsk ˈbændwɪdθ/ | 磁盘带宽 |
| logical partitioning | /ˈlɒdʒɪkəl pɑːrˈtɪʃənɪŋ/ | 逻辑分区 |
| cross-machine sharding | /krɒs məˈʃiːn ˈʃɑːrdɪŋ/ | 跨机器分片 |
| shard | /ʃɑːrd/ | 分片 |
| sharding key | /ˈʃɑːrdɪŋ kiː/ | 分片键 |
| partition pruning | /pɑːrˈtɪʃən ˈpruːnɪŋ/ | 分区裁剪 |
| scan range | /skæn reɪndʒ/ | 扫描范围 |
| hash | /hæʃ/ | 哈希 |
| target shard | /ˈtɑːrɡɪt ʃɑːrd/ | 目标分片 |
| full table scan | /fʊl ˈteɪbəl skæn/ | 全表扫描 |
| single point of write | /ˈsɪŋɡəl pɔɪnt əv raɪt/ | 单点写入 |
| write concurrency | /raɪt kənˈkʌrənsi/ | 写入并发 |
| monitoring dashboard | /ˈmɒnɪtərɪŋ ˈdæʃbɔːrd/ | 监控仪表盘 |
| disk capacity | /dɪsk kəˈpæsəti/ | 磁盘容量 |
| workload | /ˈwɜːrkloʊd/ | 工作负载 |
| scaling solution | /ˈskeɪlɪŋ səˈluːʃən/ | 扩展方案 |

---

## 句式提炼

| **功能** | **英文句式** | **适用场景** |
| --- | --- | --- |
| 指出复制的局限 | *"Replication only solves read scalability, not write scalability. The replicas can only serve read requests—every write still has to hit the master."* | 解释主从复制的边界 |
| 垂直扩展的物理上限 | *"A single machine has a maximum number of cores, a maximum memory capacity, and a maximum disk bandwidth. You eventually hit that ceiling."* | 说明垂直扩展为何不是银弹 |
| 区分逻辑分区与分片 | *"Logical partitioning just slices a table into segments on the same disk. It can't improve write throughput. Only cross-machine sharding gives you true horizontal scaling."* | 澄清分区的两种含义 |
| 解释分区裁剪 | *"We hash the user ID to compute the target shard, then only scan that shard and skip the others. The scan range shrinks dramatically."* | 说明分区如何提升查询性能 |

---

## 阅读理解题

1. Why does master-slave replication fail to solve the write throughput problem?

   **Answer:** Because replicas only handle read requests. All writes must still go to the master, so adding more replicas does not increase write capacity.

2. What are the physical limits of vertical scaling mentioned by the candidate?

   **Answer:** A single machine has maximum limits on CPU cores, memory capacity, and disk bandwidth. Once those are reached, further scaling is impossible regardless of cost.

3. What is the difference between logical partitioning and cross-machine sharding?

   **Answer:** Logical partitioning slices a table on the same disk within one machine, so it remains bound by the same CPU and I/O limits. Cross-machine sharding distributes data across multiple machines, allowing each machine to handle a portion of the writes and enabling true horizontal scaling.

4. How does partition pruning reduce query scan range?

   **Answer:** By hashing the partition key (e.g., `user_id`) to compute the target shard, the query only scans that specific shard and skips all others. For example, scanning 1 of 16 shards reduces the scan range from 500 million rows to about 30 million rows.

5. According to the candidate, what problem does vertical scaling ultimately fail to solve?

   **Answer:** Vertical scaling only postpones the bottleneck. It does not eliminate the hard physical limits of a single machine, so write throughput and disk capacity will still hit a ceiling as data volume grows.

---

*Word count (dialogue): ~488 words*  
*Level: Intermediate / T2*
