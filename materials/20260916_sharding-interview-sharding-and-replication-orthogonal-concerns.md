# 【中级】Sharding and Replication: Orthogonal Concerns in Distributed Storage

**技术等级：** T2 · **英语等级：** 中 · **字数：** ~500

**Source:** Interview / System Design  
**Level:** T2 / Intermediate  
**Role:** Interviewer, Candidate (2–5 years backend engineer)  
**Estimated Words:** ~492

---

## 故事 Prompt 及故事

```jsx
请根据以下系统设计知识点生成一个中文技术故事，用于后续英语教学。

知识点：[2.4 分区（哈希 vs 范围）]
故事形式：一段面试场景对话，对话双方是面试官和候选人。
技术要求：T2难度（方案对比级），适合2-5年经验后端工程师。
故事冲突设定：
候选人决定对订单表进行跨机器分片，按 user_id 哈希分 4 个分片，每个分片部署在一台独立机器上。技术评审时，面试官问：如果其中一台机器挂了，这个分片的数据就完全不可用——别的分片上没有它的副本。分片解决了写入吞吐，但可用性怎么办？要不要给每个分片配副本？机器成本怎么控制？

面试官追问链（必须严格遵循）：

1. "你按 user_id 分了 4 个分片，每个分片部署在一台独立的机器上。如果一个分片的机器挂了，这个分片的数据就完全不可用——别的分片上没有它的副本。写入吞吐解决了，但可用性怎么办？分片和副本到底什么关系？能互相替代吗？"
2. "你说要给每个分片配从库——如果 4 个分片 × 2 副本 = 8 台机器，成本翻倍。但如果不配，分片主库一挂，那个分片就没了。能不能既保证每个分片都有副本，又不让机器数量翻倍？你想过把分片和副本混合部署吗？比如 4 台机器、4 个分片，每台机器放 3 个分片——其中 1 个主分片、2 个从分片。这样每台机器既有自己负责的主分片，也承担其他分片的副本。你画出这个部署图，说说好处和风险。"
3. "这种混合部署下，4 台机器，每台机器扛 3 个分片（1 主 2 从）。如果其中 1 台机器挂了，它上面的主分片怎么办？它上面的从分片怎么办？其他 3 台机器上的副本能否自动接管？会不会出现某台机器的负载突然变重？"
4. "你还记得上一课我们说的：分区解决写入吞吐和容量，复制解决可用性和读扩展。现在这个部署图里，分片和副本是怎么同时满足这两点的？如果把机器数从 4 台扩到 8 台，但保持 4 个分片不变，副本数从 2 增加到 4，分片和副本哪个维度变了？对写入吞吐有影响吗？"

【必须覆盖的核心概念】（来自核心层）：

分区与复制的正交关系、分片与副本的部署组合

【可选延伸概念】（来自扩展层，T2 可不强制要求）：

候选人的回答要求：

- 说明分片后单个分片故障时，数据不会自动出现在其他分片，必须有副本
- 明确分区和复制解决不同问题，不能互相替代
- 画出 4 台机器 × 4 分片 × 3 副本的混合部署图，说明每台机器既有主分片又有从分片
- 分析机器故障时的接管逻辑：只有同分片的副本能接管，跨分片不能
- 对比"垂直增加副本"和"水平增加分片"对系统能力的不同影响

要求：故事简短，纯对话形式，字数350字。
生成完故事后，请用1-2句话说明你是如何通过追问实现方案对比深度的。
```

**面试官：** 你按 `user_id` 分了 4 个分片，每个分片部署在一台独立机器上。如果其中一个分片的机器挂了，这个分片的数据就完全不可用——别的分片上没有它的副本。写入吞吐解决了，但可用性怎么办？分片和副本到底什么关系？能互相替代吗？

**候选人：** 不能替代。分片解决的是写入吞吐和磁盘容量——每条数据只属于一个分片，各分片独立写。副本解决的是可用性和读扩展——同一个分片的数据复制到多个节点。如果没有副本，分片就是单点，机器一挂数据就丢。所以分片和副本必须同时存在，是正交的两件事。

**面试官：** 那给每个分片配从库——4 个分片 × 2 副本 = 8 台机器，成本翻倍。能不能既保证每个分片有副本，又不让机器数量翻倍？

**候选人：** 可以混合部署。4 台机器、4 个分片，每台机器放 3 个分片——1 个主分片、2 个从分片。比如机器 1 负责分片 A 的主副本，同时存分片 B 和 C 的从副本。这样每台机器既有自己负责的写入，也承担其他分片的备份，机器数不变但每个分片都有 3 个副本。

**面试官：** 如果其中 1 台机器挂了，它上面的主分片怎么办？从分片怎么办？其他 3 台机器能接管吗？

**候选人：** 机器 1 挂了，它上面的主分片 A 会在机器 2 或 3 上的从副本中选出新的主，继续服务。它上面的从分片 B 和 C 失效，但 B 和 C 在其他机器上还有主副本和另一个从副本，不影响可用性。短暂的负载会集中到剩余 3 台机器，但不会中断服务。这正是混合部署的价值——机器少，但每个分片都有冗余。

**面试官：** 那如果把机器数从 4 台扩到 8 台，但保持 4 个分片不变，副本数从 2 增到 4，哪个维度变了？对写入吞吐有影响吗？

**候选人：** 分片数没变，写入吞吐不变——还是 4 个分片在写。变的是副本数，读扩展和可用性提升了。要提升写入吞吐，得增加分片数，不是加副本。这就是分片和副本的本质区别：分片决定写能力，副本决定读能力和可靠性。

**深度实现说明：** 第一问逼出分片与副本的正交关系——一个管写，一个管可用性；第二问引出混合部署，用 4 机器 × 4 分片 × 3 副本的方案解决成本与冗余的矛盾；第三问用机器故障场景验证接管逻辑；第四问通过对比"加副本"和"加分片"对写入吞吐的不同影响，完成两者本质区别的闭环论证。

---

## Background

### 文章技术干点

这段对话围绕**分片（Sharding）与副本（Replication）的关系**展开，从可用性、成本、部署拓扑到扩容维度进行了深入讨论。候选人的回答整体准确，展示了清晰的分布式系统思维。下面从技术角度逐层分析其中的要点与潜在问题。

---

### 1. 分片与副本的本质区别：正交的扩展维度

**分片（Sharding）** 解决的是**写吞吐与存储容量**问题：

- 每个分片只存储一部分数据（例如按 `user_id` 哈希取模分到 4 个 shard）。
- 每个分片有自己的**主节点（primary）**，独立处理属于自己的写请求。
- 增加分片数量，写请求被分散到更多主节点，**写吞吐线性提升**。

**副本（Replication）** 解决的是**可用性与读扩展**问题：

- 同一个分片的数据被复制到多个节点（副本）。
- 主节点负责写，从节点提供读，并通过复制保持数据一致。
- 增加副本数量，可以分担读压力，并在主节点故障时提供冗余。

**关系**：两者正交，不能相互替代。

- 没有副本的分片是**单点故障**，一台机器宕机则该分片数据完全不可用。
- 没有分片的副本只能提高读能力，写仍集中在单主，写吞吐受限。

候选人的表述：*"Sharding solves write throughput and disk capacity—each row belongs to exactly one shard, and every shard writes independently. Replication solves availability and read scaling—the same shard's data is copied to multiple nodes."* 完全正确。

---

### 2. 混合部署：在固定机器数量下同时获得分片与副本

**问题**：为每个分片单独配置副本，机器数量会成倍增长（4 个分片 × 2 副本 = 8 台机器），成本过高。

**候选人的方案**：**混合部署（Mixed Deployment）**，将不同分片的主从副本交叉分布在同一批机器上。

- 假设 4 台机器、4 个分片（A、B、C、D）。
- 每台机器同时承担：
  - 一个分片的**主节点**（处理写请求）。
  - 另外两个分片的**从节点**（提供读与冗余）。
- 这样总共 4 台机器，但每个分片拥有 **1 主 + 2 从 = 3 个副本**，总副本数 4 × 3 = 12，实际节点数只有 4 台机器。

**示例拓扑**（常见排列）：

| **机器** | **主分片** | **从分片** |
| --- | --- | --- |
| M1 | A | B, C |
| M2 | B | A, D |
| M3 | C | A, D |
| M4 | D | B, C |

这种部署在分布式数据库中非常典型（如 Cassandra、TiKV、CockroachDB 等），通过**一致性哈希 + 多副本交叉分布**，在有限的物理资源下提供高可用。

**优点**：

- 机器数不变，但每个分片都有冗余。
- 任意一台机器宕机，其他机器上的副本可以接管，服务不中断。

**代价**：

- 每台机器同时运行多个分片实例，**资源竞争**加剧（CPU、内存、磁盘 I/O）。
- 故障转移后，剩余机器需要承担更多负载，可能出现过载。

---

### 3. 故障转移过程与自动接管

候选人描述了机器 1 宕机后的处理：

- **主分片 A**：从机器 2 或 3 上的 A 副本中选举出新的主节点，继续提供写服务。
- **从分片 B、C**：机器 1 宕机导致这些副本不可用，但 B、C 在其他机器上仍有主节点和另一个副本，因此服务不受影响。
- **负载吸收**：剩余 3 台机器需要临时承载原本分布在 4 台机器上的负载，可能出现性能下降，但不会中断。

**技术细节**：

- 自动故障转移需要**分布式共识协议**（如 Raft、Paxos）来选举新主并确保数据一致性。
- 新主必须满足数据最新（或至少不会丢失已确认写入），通常需要复制机制保证（如半同步复制、Raft 日志复制）。
- 客户端需要能够感知新主位置，通常依赖**配置中心**或**服务发现**机制。
- 机器 1 恢复后，需要重新加入集群并同步数据，然后可能作为副本回归。

**候选人回答中的潜在问题**：

- 未提及如何保证不丢数据。如果原主 A 宕机前有未复制到副本的写入，则故障切换可能导致数据丢失。需要依赖**半同步复制**或**强一致复制**来避免。
- "剩余三台机器吸收额外负载"短期可行，但如果集群原本就接近满载，故障切换可能导致雪崩。因此容量规划应预留冗余，例如每台机器日常负载不超过 60%，以承受一台宕机后的额外压力。

---

### 4. 扩展维度：分片数 vs 副本数

**场景**：从 4 台机器扩展到 8 台，保持 4 个分片不变，增加副本数。

- **分片数不变** → **写吞吐不变**。因为写请求仍由每个分片的主节点处理，主节点数量没变。
- **副本数增加** → **读扩展性提升**（更多节点可提供读服务），**可用性提升**（冗余更多）。

**写吞吐的提升只能通过增加分片数量实现**，而副本数量的增加主要改善读性能和容灾能力。

**进一步说明**：

- 增加机器数量后，即使分片数不变，也可以将每个分片的副本分布到更多机器上，从而提升读吞吐和可用性，但无法提升写吞吐。
- 如果希望同时提升写吞吐和读吞吐，需要同时增加分片数和副本数，并合理规划机器资源。

候选人的总结：*"shards determine write capacity; replicas determine read capacity and reliability"* 精准概括了核心。

---

### 5. 潜在问题与生产环境考量

虽然候选人的框架正确，但在实际落地中还需注意以下几点：

#### (1) 混合部署的资源隔离

每台机器运行多个分片实例，需要严格的资源隔离（CPU 亲和、内存限制、磁盘配额），否则一个分片的突发负载会影响同机其他分片。

#### (2) 故障转移的数据一致性

主从复制可能存在延迟。如果主节点宕机时，部分已提交事务尚未同步到从节点，则切换后可能丢失数据。解决方案：

- 使用**半同步复制**或 **Raft 强一致复制**，保证主节点确认前至少一个副本已收到日志。
- 对于金融级场景，可能需要**无损半同步（AFTER_SYNC）**或**共识协议**。

#### (3) 负载均衡与客户端路由

客户端需要知道每个分片的主节点位置。通常引入**元数据服务**（如 ZooKeeper、etcd）维护分片到节点的映射，并在故障切换时更新。

#### (4) 扩容与数据再平衡

如果未来需要从 4 分片扩到 8 分片，涉及数据迁移和再平衡。此时需要一致性哈希或范围分片来减少迁移量，并通过在线迁移工具平滑过渡。

#### (5) 网络分区

混合部署下，如果网络发生分区，可能导致脑裂。共识协议需要处理分区容忍性，确保少数派不能继续写入。

---

### 总结

这段对话完整地展示了分布式数据库扩展的核心思想：

| **维度** | **分片（Sharding）** | **副本（Replication）** |
| --- | --- | --- |
| 解决的问题 | 写吞吐、存储容量 | 可用性、读扩展 |
| 扩展方式 | 增加分片数 | 增加副本数 |
| 对机器数量的影响 | 直接增加主节点数量 | 可混合部署，减少额外开销 |
| 故障影响 | 单分片不可用，但其他分片不受影响 | 副本冗余保证分片可用 |

候选人的回答准确区分了正交关系，并给出了实用的混合部署策略，同时正确指出了扩展维度。整体逻辑清晰，体现了扎实的分布式系统设计功底。

---

## 架构图

### 1. 初始方案：4 个分片独立部署，无副本

```text
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  机器 1      │  │  机器 2      │  │  机器 3      │  │  机器 4      │
│              │  │              │  │              │  │              │
│  分片 A      │  │  分片 B      │  │  分片 C      │  │  分片 D      │
│  (Primary)   │  │  (Primary)   │  │  (Primary)   │  │  (Primary)   │
│              │  │              │  │              │  │              │
│  处理写入    │  │  处理写入    │  │  处理写入    │  │  处理写入    │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘

风险：
❌ 每个分片都是单点故障
❌ 机器 1 宕机 → 分片 A 数据完全不可用
❌ 没有冗余，数据可能永久丢失
```

---

### 2. 混合部署：4 台机器，4 个分片，每台机器 3 个分片副本（1 主 2 从）

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                              4 台机器混合部署                               │
└────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│     机器 1       │   │     机器 2       │   │     机器 3       │   │     机器 4       │
│                  │   │                  │   │                  │   │                  │
│  分片 A (主)     │   │  分片 B (主)     │   │  分片 C (主)     │   │  分片 D (主)     │
│  分片 B (从)     │   │  分片 A (从)     │   │  分片 A (从)     │   │  分片 B (从)     │
│  分片 C (从)     │   │  分片 D (从)     │   │  分片 D (从)     │   │  分片 C (从)     │
│                  │   │                  │   │                  │   │                  │
│  负责 A 的写入   │   │  负责 B 的写入   │   │  负责 C 的写入   │   │  负责 D 的写入   │
│  备份 B 和 C     │   │  备份 A 和 D     │   │  备份 A 和 D     │   │  备份 B 和 C     │
└──────────────────┘   └──────────────────┘   └──────────────────┘   └──────────────────┘

优点：
✅ 每台机器既有主分片（处理写入）也有从分片（提供冗余）
✅ 机器数不变（4台），但每个分片有 3 个副本（1主2从）
✅ 任何一个分片都有多个副本分布在其他机器上
```

---

### 3. 故障场景：机器 1 宕机，分片 A 主副本重新选举

**故障前：**

```text
分片 A：主副本在机器 1，从副本在机器 2 和机器 3
分片 B：主副本在机器 2，从副本在机器 1 和机器 4
分片 C：主副本在机器 3，从副本在机器 1 和机器 4
分片 D：主副本在机器 4，从副本在机器 2 和机器 3
```

**机器 1 宕机后：**

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                       机器 1 宕机后的系统状态                                  │
└────────────────────────────────────────────────────────────────────────────┘

分片 A：主副本在机器 1 ❌ 失效
        → 重新选举：机器 2 或机器 3 上的从副本提升为主副本 ✅
        → 分片 A 继续服务

分片 B：主副本在机器 2 ✅ 不受影响
        → 机器 1 上的从副本失效，但机器 4 还有从副本 ✅

分片 C：主副本在机器 3 ✅ 不受影响
        → 机器 1 上的从副本失效，但机器 4 还有从副本 ✅

分片 D：主副本在机器 4 ✅ 不受影响
        → 机器 1 上没有分片 D 的副本，完全不受影响 ✅

结果：
✅ 所有 4 个分片均保持可用
✅ 只有分片 A 经历了一次短暂的重新选举
⚠️ 剩余 3 台机器负载增加，但无中断
```

---

### 4. 扩展对比：加副本 vs 加分片

```text
当前状态：4 台机器，4 个分片，每个分片 2 个副本（1主1从）
写入吞吐：由 4 个主分片决定

方案 A：增加副本（4台 → 8台，分片数不变，副本数 2 → 4）

┌──────────────────────────────────────────────────────────────┐
│  8 台机器，仍然 4 个分片                                      │
│  每个分片：1 主 + 3 从 = 4 个副本                             │
│                                                              │
│  写入吞吐：不变（还是 4 个主分片在写）                          │
│  读吞吐：提升（更多从副本可以分担读）                           │
│  可用性：提升（更多冗余，容忍更多机器故障）                     │
└──────────────────────────────────────────────────────────────┘

方案 B：增加分片（4个分片 → 8个分片，机器数相应增加）

┌──────────────────────────────────────────────────────────────┐
│  8 个分片，每个分片部署在独立机器（或混合部署）                 │
│                                                              │
│  写入吞吐：提升（8 个主分片并行写）                             │
│  读吞吐：可能提升（分片更多，单个分片数据更少）                 │
│  可用性：取决于副本配置                                      │
└──────────────────────────────────────────────────────────────┘

核心区别：
✏️ 分片数 → 决定写能力
📖 副本数 → 决定读能力和可靠性
```

---

## 角色及场景

**Interviewer (面试官):** 考察候选人对分区与复制关系的理解。从分片后单点故障切入，逐步追问混合部署方案、故障接管逻辑，以及增加副本与增加分片对系统能力的不同影响。

**Candidate (候选人):** 2-5年经验后端工程师，负责订单系统的分片与副本架构设计，需清晰阐述分片与副本的正交关系，并画图说明混合部署下的故障接管机制。

**场景:** 面试。候选人已决定按 `user_id` 将订单表分成 4 个分片，每个分片部署在一台独立机器上。面试官指出单分片无副本时的可用性风险，并通过四轮追问，逼出候选人对"分片管写入、副本管可用性"的完整理解。

---

## 会议对话 (中级，正文约 492 词)

**Interviewer:**

You've sharded the order table by `user_id` into four shards, each deployed on its own machine. But **if one of those machines goes down**, that shard's data becomes completely unavailable—no other shard holds a copy. Sharding solves write throughput, but **what about availability**? **What exactly is the relationship between shards and replicas? Can they substitute for each other**?

**Candidate:**

No, they can't. Sharding solves write throughput and disk capacity—each row belongs to exactly one shard, and every shard writes independently. Replication solves availability and read scaling—the same shard's data is copied to multiple nodes. **Without replicas, a shard is a single point of failure**: one machine crash and that data is gone. So **sharding and replication have to coexist**. They're **orthogonal** concerns.

**Interviewer:**

So you'd add a replica for each shard—but 4 shards times 2 replicas means 8 machines. Your cost doubles. **Can you guarantee every shard has a replica without doubling the machine count?**

**Candidate:**

Yes, through mixed deployment. **Four machines, four shards, with each machine hosting three shard copies—one primary and two replicas**. For example, Machine 1 owns the primary for shard A, and also stores replicas for shards B and C. Every machine handles its own writes while also backing up other shards. The machine count stays the same, but each shard still has three copies.

**Interviewer:**

**Under this mixed deployment, if Machine 1 crashes, what happens to its primary shard**? What happens to its replica shards? Can the remaining three machines take over automatically? Will one machine suddenly become overloaded?

**Candidate:**

When Machine 1 fails, its primary shard A is re-elected from one of the replicas on Machine 2 or 3, and service continues. Its replica shards B and C become unavailable, but that's fine—B and C still have their primary and another replica on other machines. **The remaining three machines absorb the extra load for a short period, but service is not interrupted**. **That's the real value of mixed deployment: fewer machines, yet every shard still has redundancy.**

**Interviewer:**

Now let me ask you this. If we expand from 4 machines to 8, but keep the 4 shards unchanged, and increase the replica count from 2 to 4—which dimension changed? Does write throughput improve?

**Candidate:**

The shard count stays at four, so write throughput doesn't change—still only four primaries handling writes. What improved is replica count, which boosts read scalability and availability. If you want higher write throughput, you must add more shards, not more replicas. That's the essential difference: **shards determine write capacity; replicas determine read capacity and reliability**.

**Interviewer:**

So when someone says "**the system is slow on writes," your first instinct should be to add shards, not replicas.**

**Candidate:**

Exactly. Adding replicas just creates more copies to read from—it doesn't help the primary keep up with writes. You scale writes by partitioning your data into more independent primaries. Scale reads by adding replicas. Mix them correctly and you get both.

---

## 词汇表 (25个高频技术词汇)

| **Vocabulary** | **Pronunciation (IPA)** | **Chinese Meaning** |
| --- | --- | --- |
| shard | /ʃɑːrd/ | 分片 |
| replica | /ˈreplɪkə/ | 副本 |
| orthogonal | /ɔːrˈθɒɡənəl/ | 正交的 |
| single point of failure | /ˈsɪŋɡəl pɔɪnt əv ˈfeɪljər/ | 单点故障 |
| write throughput | /raɪt ˈθruːpʊt/ | 写入吞吐 |
| disk capacity | /dɪsk kəˈpæsəti/ | 磁盘容量 |
| primary | /ˈpraɪməri/ | 主副本/主分片 |
| mixed deployment | /mɪkst dɪˈplɔɪmənt/ | 混合部署 |
| machine count | /məˈʃiːn kaʊnt/ | 机器数量 |
| redundancy | /rɪˈdʌndənsi/ | 冗余 |
| failover | /ˈfeɪloʊvər/ | 故障切换 |
| re-elect | /ˌriː ɪˈlekt/ | 重新选举 |
| unavailable | /ˌʌnəˈveɪləbəl/ | 不可用的 |
| overload | /ˌoʊvərˈloʊd/ | 过载 |
| read scalability | /riːd ˌskeɪləˈbɪləti/ | 读扩展性 |
| write scalability | /raɪt ˌskeɪləˈbɪləti/ | 写扩展性 |
| availability | /əˌveɪləˈbɪləti/ | 可用性 |
| node | /noʊd/ | 节点 |
| backup | /ˈbækʌp/ | 备份 |
| data distribution | /ˈdeɪtə ˌdɪstrɪˈbjuːʃən/ | 数据分布 |
| independent write | /ˌɪndɪˈpendənt raɪt/ | 独立写入 |
| replication factor | /ˌreplɪˈkeɪʃən ˈfæktər/ | 复制因子 |
| cluster | /ˈklʌstər/ | 集群 |
| partition | /pɑːrˈtɪʃən/ | 分区 |
| durability | /ˌdjʊərəˈbɪləti/ | 持久性 |

---

## 句式提炼

| **功能** | **英文句式** | **适用场景** |
| --- | --- | --- |
| 说明正交关系 | *"Sharding solves write throughput; replication solves availability. They can't substitute for each other—they're orthogonal concerns."* | 解释分片与副本的本质区别 |
| 提出混合部署 | *"Each machine owns one primary and stores replicas for other shards. The machine count stays the same, but every shard still has redundancy."* | 描述不增加机器数的冗余方案 |
| 描述故障接管 | *"The primary is re-elected from a replica on another machine, and service continues."* | 说明机器故障时的自动恢复 |
| 区分加副本与加分片 | *"Shards determine write capacity; replicas determine read capacity and reliability. To scale writes, add shards—not replicas."* | 澄清两个维度的扩展能力 |

---

## 阅读理解题

1. Why can't shards and replicas substitute for each other?

   **Answer:** Shards solve write throughput and disk capacity by distributing data across independent primaries. Replicas solve availability and read scaling by copying the same shard to multiple nodes. Without replicas, a shard is a single point of failure; without shards, writes are concentrated on one primary. They are orthogonal concerns.

2. How does mixed deployment keep the machine count at 4 while still giving each shard 3 copies?

   **Answer:** Each machine hosts three shard copies—one primary and two replicas. For example, Machine 1 owns shard A's primary and stores replicas for shards B and C. Every machine both serves its own writes and backs up other shards.

3. What happens when Machine 1 fails under the mixed deployment?

   **Answer:** Shard A's primary is re-elected from a replica on another machine. The replica shards B and C on the failed machine become unavailable, but B and C still have their primaries and another replica elsewhere, so the system continues serving. The remaining machines briefly absorb more load.

4. If you increase the replica count from 2 to 4 while keeping shard count at 4, what improves and what doesn't?

   **Answer:** Read scalability and availability improve, because there are more copies to serve reads and survive failures. Write throughput does not improve, because there are still only four primaries handling writes.

5. According to the candidate, what is the essential difference between shards and replicas?

   **Answer:** Shards determine write capacity—more shards mean more independent primaries and higher write throughput. Replicas determine read capacity and reliability—more replicas mean more read paths and better fault tolerance. Scaling writes requires adding shards, not replicas.

---

## 正文单词统计

正文字数：492词

---

## 难度自评

等级：中级 / T2

理由：对话围绕分片与复制的正交关系展开，覆盖了单点故障、混合部署、故障接管和扩展维度对比等核心概念。使用了 shard、replica、orthogonal、primary、mixed deployment、re-elect 等专业词汇，通过四轮追问实现了从"为什么需要副本"到"分片与副本各管什么"的完整论证，适合 B1-B2 学员练习分布式存储架构中的技术表达。
