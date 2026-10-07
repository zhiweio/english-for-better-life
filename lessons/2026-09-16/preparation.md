这份预习材料**不用 material 原文**，概念全部用自己的话复述。每个概念的「用自己的话理解」提供**中英双语**（英文按 **B2**）。长句练习的重点是**嵌套从句**——定语从句、状语从句、非限制性从句叠在一起练。

---

## 课前 3 分钟：今天讲什么

**话题：** 分片把写吞吐拉上去了，但一台机器挂了那个分片就彻底没了——**分片和副本到底什么关系？能不能用更少的机器同时拿到两者？**

**方案演进（material 技术干点）：**

```
① 4分片4机器无副本（写通了，却是单点）→ ② 每分片配从库（8台，成本翻倍）
→ ③ 混合部署（4台机器 × 4分片 × 1主2从）→ ④ 机器1挂了（同分片副本重选主）
→ ⑤ 扩到8台只加副本（读和可用性升，写吞吐不动）
```

**故事线：**

```
分片解决写吞吐和容量 → 但单分片无副本就是单点 → 分片与副本正交、不能互替
→ 混合部署把主从交叉铺开 → 4台机器仍是每分片3份拷贝 → 机器1挂：A重选主 / B、C各少一份 / D无感
→ 只有同分片的副本能接管 → 扩容时加分片才提写、加副本只提读和可靠性
→ 生产补课：资源隔离 / 半同步复制 / 元数据路由 / 在线再平衡 / 防脑裂
```

| 维度 | 分片 Sharding | 副本 Replication |
|---|---|---|
| 解决什么 | 写吞吐、磁盘容量 | 可用性、读扩展 |
| 怎么扩 | 增加分片数 | 增加副本数 |
| 对机器数的要求 | 直接增加主节点 | 可混合部署，摊薄开销 |
| 单点影响 | 该分片不可用，其他分片无感 | 副本冗余保证分片仍可用 |
| 故障切换 | 不参与 | 同分片副本才能接管 |

| 关键数字 | 含义 |
|---|---|
| 4 分片 × 2 副本 = **8 台** | 朴素"每分片配从库"的成本 |
| **4 台** × **3 份** = 12 份 | 混合部署下的总拷贝数 |
| **1 主 + 2 从 = 3 副本** | 每个分片实际拥有的拷贝数 |
| **4 → 8 台**（分片不变） | 只提升读吞吐和可用性，写吞吐不变 |
| 日常负载 ≤ **60%** | 留出一台机器宕机后的吸收余量 |

**规律：** **分片决定写能力，副本决定读能力和可靠性**——两个维度正交，谁也替代不了谁。这正好接上一课的结论：分区解决写入吞吐和容量，复制解决可用性和读扩展。

---

## 概念 1：分片与副本是两件正交的事

### 用自己的话理解（中英双语）

**中文：**

原方案是用 `user_id` 哈希把订单表切成 4 个分片，一个分片一台机器。写吞吐确实上来了——每条订单只落一个分片，4 个分片各自独立写，互不阻塞。

但这里有个漏洞：**分片只切开了数据，没有复制数据**。所以某台机器一挂，那个分片的数据就完全不可用——别的分片上根本没有它的副本，因为每条订单只属于一个分片。写吞吐解决了，可用性一点没解决。

关键在于，分片和副本是两个**正交**的维度：

- **分片（sharding）管写吞吐和磁盘容量。** 数据被切开，每片只存一部分，各有自己的主节点独立接受写请求；分片越多，写被分散到越多的主节点上。
- **副本（replication）管可用性和读扩展。** 同一个分片的数据被复制到多个节点，主节点写、从节点读，主挂了还能从副本里选出新的主。

结论就是谁也替代不了谁：**没有副本的分片是单点故障**，机器一挂数据就没了；**没有分片的副本只是多几份拷贝**，写依然集中在一个主库上，写吞吐照样卡住。

**English (B2):**

The original design hashed the order table by `user_id` into four shards, each sitting on its own machine. Write throughput improves immediately, **because** every order belongs to exactly one shard, **and** the four primaries write independently. **But** there is a hole: sharding only **splits** the data, it never **copies** it. **So if** one of those machines dies, that shard's data becomes completely unavailable, **since** no other shard holds a copy of it — every row belongs to exactly one shard.

Sharding and replication are **orthogonal** dimensions:

- **Sharding** addresses **write throughput and disk capacity**. Data is split **so that** each shard stores only a slice of it, **and** each shard owns a primary **that** accepts writes independently. The more shards there are, the more primaries share the write load.
- **Replication** addresses **availability and read scaling**. The same shard's data is copied to multiple nodes, **where** the primary takes writes **and** replicas serve reads, **so that when** the primary fails, another copy can be promoted.

**Neither can substitute for the other**: a shard **without** replicas is a single point of failure, **whereas** replicas **without** sharding only add copies of the same data, **which** leaves every write funneled through one primary **whose** capacity stays capped.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
|---|---|---|
| shard | 分片 | Each shard is a slice of the table **that** owns its own primary. |
| replica | 副本 | A replica is a copy **that** can serve reads **when** the primary is busy. |
| orthogonal | 正交的 | Two concerns are orthogonal **when** changing one does not affect the other. |
| single point of failure | 单点故障 | A shard **that** has no replica is a single point of failure. |
| write throughput | 写入吞吐 | Write throughput grows **only when** you add primaries **that** accept writes in parallel. |
| disk capacity | 磁盘容量 | Disk capacity is a limit **that** sharding raises **whereas** replication does not. |
| availability | 可用性 | Availability improves **because** replicas exist **so that** a failure does not stop service. |
| read scaling | 读扩展 | Read scaling comes from replicas, **which** spread SELECT traffic across more nodes. |

### 嵌套从句练习：说清"为什么不能互相替代"

**Layer 1 — 主句：**
> Sharding and replication solve different problems.

**Layer 2 — 加对比状语从句：**
> Sharding solves write throughput, **whereas** replication solves availability.

**Layer 3 — 两边各加原因从句：**
> Sharding solves write throughput **because** it splits data into independent primaries, **whereas** replication solves availability **because** it copies each shard to several nodes.

**Layer 4 — 完整嵌套版：**
> **Because** sharding splits a table into independent primaries **that** each own only part of the data, **and** **because** replication copies each of those shards to several nodes, the two mechanisms address problems **that** never overlap — **which** is why **if** you keep only one of them, you either lose the data **when** a machine dies, or you leave every write funneled through a single primary **whose** throughput cannot grow.

**中文对照：** 因为分片把一张表切成各自只拥有一部分数据的独立主节点，而复制又把每个分片拷到多个节点，这两个机制解决的是从不相交的问题——所以只保留其中一个，要么机器一挂就丢数据，要么所有写都挤在一个吞吐无法增长的主库上。

### 嵌套从句练习：说单点故障

**Layer 2：**
> **Without** replicas, one machine crash takes a whole shard offline.

**Layer 3：**
> **If** the machine **that** hosts shard A crashes, the data in shard A becomes unavailable, **because** no other shard stores a copy of it.

**Layer 4 — 完整嵌套版：**
> **If** the machine **that** hosts shard A crashes, every order **that** belongs to shard A becomes unreachable, **because** the only node **that** held that slice of data had no replica anywhere else — **which** is exactly the single point of failure **that** sharding alone cannot fix, **and** it is the reason **why** sharding and replication have to be deployed together.

**中文对照：** 承载分片 A 的机器一挂，属于分片 A 的每一笔订单都变得无法访问，因为持有这份数据的唯一节点在别处没有任何副本——这正是分片本身无法修复的单点故障，也是分片和副本必须同时部署的原因。

---

## 概念 2：混合部署——机器数不变，每个分片仍有副本

### 用自己的话理解（中英双语）

**中文：**

朴素做法是给每个分片单独配从库：4 个分片 × 2 副本 = 8 台机器，成本直接翻倍。而且不配也不行——主库一挂那个分片就没了。

候选人的答案是**混合部署（mixed deployment）**：让不同分片的主从副本交叉铺在同一批机器上。4 台机器、4 个分片，**每台机器扛 3 个分片实例——1 个是它负责的主分片，另外 2 个是别的分片的从副本**：

| 机器 | 主分片 | 从分片 |
|---|---|---|
| 机器 1 | A | B、C |
| 机器 2 | B | A、D |
| 机器 3 | C | A、D |
| 机器 4 | D | B、C |

这样机器数还是 4 台，但**每个分片都有 3 份拷贝（1 主 + 2 从）**，全系统一共 12 份。每台机器既处理自己那部分的写入，也替别的分片做备份。

好处是成本没变、冗余到位；代价也很明确：一台机器上同时跑多个分片实例，CPU、内存、磁盘 I/O 会互相抢资源；故障切换之后，剩下的机器还得临时多扛一份负载。所以容量规划必须留余量——常见标准是让每台机器日常负载控制在 **60% 左右**，才扛得住一台宕机后的额外压力。

**English (B2):**

The naive approach gives each shard its own replica set: four shards times two replicas means eight machines, **which** doubles the cost. Running without replicas is not an option either, **since** one primary failure wipes out that shard.

The answer is **mixed deployment**, **where** primaries and replicas of different shards are interleaved across the same set of machines. With four machines and four shards, **each machine hosts three shard instances — one primary that it owns, and two replicas that belong to other shards**.

The machine count stays at four, **yet** every shard ends up with **three copies (one primary plus two replicas)**, **which** adds up to twelve copies in total. Every machine serves its own writes **while** it also backs up other shards.

The benefit is clear, **and so** is the cost: **because** several shard instances share one box, they compete for CPU, memory, and disk I/O; **and** **after** a failover, the surviving machines have to absorb the load **that** the failed node used to carry. Capacity planning therefore has to keep headroom — a common rule of thumb is **that** normal utilisation should stay near **60%**, **which** is what makes a single-machine outage survivable.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
|---|---|---|
| mixed deployment | 混合部署 | Mixed deployment is a layout **where** one machine holds both a primary and other shards' replicas. |
| primary | 主分片 | The primary is the copy **that** accepts writes for its shard. |
| machine count | 机器数量 | The machine count stays flat **even though** each shard keeps three copies. |
| redundancy | 冗余 | Redundancy means extra copies **that** exist **so that** a failure does not stop the service. |
| resource contention | 资源竞争 | Resource contention happens **when** several instances compete for the same CPU and disk I/O. |
| capacity headroom | 容量余量 | Headroom is spare capacity **that** lets the cluster absorb a failure **without** degrading. |
| utilisation | 利用率 | Utilisation should stay near 60% **if** you want **to survive** one machine going down. |

### 嵌套从句练习：描述混合部署

**Layer 1：**
> Each machine hosts three shard copies.

**Layer 2 — 加结果从句：**
> Each machine hosts three shard copies, **so** every shard still ends up with three copies.

**Layer 3 — 加让步从句：**
> **Although** the machine count stays at four, each machine hosts one primary and two replicas, **so** every shard still has three copies.

**Layer 4 — 完整嵌套版：**
> **Although** the machine count stays at four, each machine hosts one primary **that** it owns together with two replicas **that** belong to other shards, **which** means every shard still has three copies spread across different boxes — **a layout that** keeps redundancy without adding hardware **whose** cost would otherwise double.

**中文对照：** 虽然机器数保持 4 台不变，但每台机器既跑着它自己负责的一个主分片，又装着两个属于别的分片的副本，这意味着每个分片仍然有三份拷贝分散在不同机器上——这种布局在不增加硬件的前提下保住了冗余，否则机器成本会翻倍。

### 嵌套从句练习：说混合部署的代价

**Layer 3：**
> **Because** several shard instances share one machine, they compete for CPU, memory and disk I/O.

**Layer 4 — 完整嵌套版：**
> **Because** several shard instances share one machine, they compete for the same CPU, memory and disk I/O, **and** **after** a failover the surviving machines must absorb the load **that** the failed node used to carry — **which** is why healthy clusters usually keep utilisation near 60% **rather than** running hot **until** the first machine dies.

**中文对照：** 因为一台机器上共享着多个分片实例，它们会争抢同样的 CPU、内存和磁盘 I/O；而故障切换之后，存活机器还必须吸收失败节点原来的负载——这就是为什么健康集群通常把利用率压在 60% 左右，而不是一直跑满直到第一台机器倒下。

---

## 概念 3：机器挂了谁接管——只有同分片的副本能接管

### 用自己的话理解（中英双语）

**中文：**

现在进入故障场景。假设**机器 1 宕机**，它在混合部署里同时扮演三个角色，要分开看：

- **它负责的主分片 A**：机器 2 和机器 3 上有 A 的从副本，从副本之间选出一个新主，A 的写入继续。
- **它承担的从分片 B 和 C**：这两份拷贝失效了，但 B 的主在机器 2、另一个从在机器 4；C 的主在机器 3、另一个从在机器 4。所以 B 和 C 的服务完全不受影响。
- **分片 D**：机器 1 上根本没有 D 的拷贝，D 完全无感。

三条结论：

1. **只有同一个分片的副本才能接管，跨分片不能**。机器 2 上那份"分片 B 的从副本"救不了分片 A——它们是不同的数据集。
2. **切换期间剩余 3 台机器负载变重，但只要留了余量就不会中断**。
3. **自动接管靠共识协议**（Raft、Paxos）选出新主，并且要保证新主的数据不比旧主落后。

还有候选人没提到的坑：如果不做半同步复制，主库宕机前那些"已经提交、但还没同步到副本"的写就会永久丢失。所以生产上要么半同步，要么上 Raft 这类强一致复制。

**English (B2):**

Now consider the failure scenario. **When** Machine 1 goes down, the three roles it plays in a mixed deployment have to be examined separately:

- **The primary it owns (shard A)**: replicas of A live on Machine 2 and Machine 3, **where** one of them is promoted to be the new primary, **so** writes to A resume.
- **The replicas it hosts (shards B and C)**: those copies become unavailable, **but** B's primary sits on Machine 2 **with** another replica on Machine 4, **and** C's primary sits on Machine 3 **with** another replica on Machine 4, **so** service for B and C is unaffected.
- **Shard D**: **since** Machine 1 never held a copy of D, D is untouched.

Three conclusions follow. First, **only a replica of the same shard can take over; a copy of a different shard cannot** — the replica of B on Machine 2 does nothing for A, **because** they hold different data sets. Second, **while** the failover is happening, the remaining three machines carry a heavier load, **although** service continues **as long as** headroom exists. Third, automatic takeover depends on a **consensus protocol** such as Raft or Paxos **that** elects a new primary **and** guarantees **that** it is at least as up to date as the old one.

There is also a trap **that** the candidate never mentions: **unless** semi-synchronous replication is in place, any write **that** was committed but not yet replicated is lost **when** the primary dies. In production, that means either semi-synchronous replication or a strongly consistent protocol such as Raft.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
|---|---|---|
| failover | 故障切换 | Failover is the process **that** promotes another copy **when** the primary dies. |
| promote / re-elect | 提升 / 重新选举 | A replica is promoted **after** the cluster agrees **which** copy is most up to date. |
| consensus protocol | 共识协议 | Raft is a protocol **that** ensures every node agrees **who** the new primary is. |
| quorum | 法定人数 | A quorum is the majority **that** must agree **before** a new primary is accepted. |
| semi-synchronous replication | 半同步复制 | Semi-synchronous replication waits **until** at least one replica has the log. |
| data loss window | 数据丢失窗口 | The loss window is the gap **in which** committed writes have not reached any replica. |
| load absorption | 负载吸收 | Load absorption is what the surviving machines do **while** a node is being replaced. |

### 嵌套从句练习：说故障接管

**Layer 1：**
> **When** Machine 1 fails, shard A's primary is re-elected.

**Layer 2 — 加地点从句：**
> **When** Machine 1 fails, shard A's primary is re-elected from a replica **that** lives on Machine 2 or 3.

**Layer 3 — 加对比：**
> **When** Machine 1 fails, shard A's primary is re-elected from a replica **that** lives on Machine 2 or 3, **while** the copies of B and C **that** Machine 1 hosted simply disappear.

**Layer 4 — 完整嵌套版：**
> **When** Machine 1 fails, shard A's primary is re-elected from a replica **that** lives on Machine 2 or 3, **whereas** the copies of B and C **that** Machine 1 used to host are simply lost — **a difference that** shows **why** only a replica of the same shard can take over, **and** **why** the remaining machines must be able to absorb the extra load **that** the failed node left behind.

**中文对照：** 机器 1 宕机时，分片 A 的主会从机器 2 或 3 上的一份副本中重新选出，而机器 1 原本承载的 B、C 副本就直接失效了——这个差别说明了为什么只有同一分片的副本才能接管，也说明了为什么剩下的机器必须能吸收失败节点留下的额外负载。

### 嵌套从句练习：说数据丢失风险

**Layer 3：**
> **If** the primary returns success **before** any replica has the write, that write can be lost **when** the primary dies.

**Layer 4 — 完整嵌套版：**
> **Unless** the primary waits **until** at least one replica has acknowledged the write, a failure can lose whatever was committed but not yet replicated — **which** is why production systems **that** care about durability choose semi-synchronous replication, or a consensus protocol such as Raft **that** guarantees the new primary is at least as up to date as the old one.

**中文对照：** 除非主库等到至少一个副本确认收到写入才返回成功，否则一旦发生故障，"已提交但尚未复制"的那些写就会丢失——这正是那些在意持久性的生产系统会选择半同步复制、或选择 Raft 这类能保证新主不比旧主落后的共识协议的原因。

---

## 概念 4：扩展维度——加副本 vs 加分片

### 用自己的话理解（中英双语）

**中文：**

最后一个问题是整场面试的收口：**机器从 4 台扩到 8 台，分片保持 4 个不变，副本从 2 增到 4——哪个维度变了？写吞吐会提升吗？**

答案是不会。分片数还是 4，写请求仍然只由 4 个主节点处理，**写吞吐一点没变**。变的只是副本数：读可以从更多节点分流，可用性也更好，能容忍更多机器同时挂。

要提升写吞吐，只能**增加分片数**——把数据切成更多份，让更多主节点并行写。这就是两个维度的本质区别：

- **分片数 → 决定写能力**（更多主节点，更多并行写路径）
- **副本数 → 决定读能力和可靠性**（更多读路径，更多容错）

成本效率也不一样：**加副本**是"同一份数据再拷一份"，边际收益递减——3 份拷贝已经能扛绝大多数单机故障；**加分片**是"增加真正新的写入路径"，收益更直接，但代价是数据迁移和运维复杂度。所以面试官那句总结很到位：**系统写得慢，第一反应应该是加分片，不是加副本**。

**English (B2):**

The final question closes the loop: expanding from four machines to eight **while** keeping four shards, **and** raising replicas from two to four — **which** dimension changed, **and** does write throughput improve?

It does not. **Since** the shard count is still four, writes are still handled by only four primaries, **so** write throughput stays exactly the same. What changed is the replica count: reads can be spread across more nodes, **and** availability improves **because** the cluster tolerates more machines failing at once.

To raise write throughput you must **add shards** — splitting the data into more pieces **so that** more primaries write in parallel. That is the essential difference:

- **Shard count determines write capacity** — more primaries, more parallel write paths.
- **Replica count determines read capacity and reliability** — more read paths, more fault tolerance.

Cost efficiency differs as well. **Adding replicas** means copying the same data again, **whose** marginal benefit drops quickly — three copies already survive almost any single-machine failure — **whereas** **adding shards** creates genuinely new write paths, **although** it brings data migration and operational complexity with it. **When** writes are slow, the first instinct should therefore be to add shards, **not** replicas.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
|---|---|---|
| shard count | 分片数 | The shard count is the variable **that** sets how many primaries accept writes. |
| replica count | 副本数 | The replica count is the variable **that** sets how many nodes can serve reads. |
| write scalability | 写扩展性 | Write scalability improves **only when** you add shards **that** accept writes independently. |
| read scalability | 读扩展性 | Read scalability improves **when** you add replicas **which** share the read traffic. |
| replication factor | 复制因子 | The replication factor is the number **that** tells you **how many** copies each shard keeps. |
| diminishing returns | 边际收益递减 | Adding replicas shows diminishing returns **once** three copies can already survive a failure. |
| data rebalancing | 数据再平衡 | Rebalancing is the migration **that** happens **when** the shard count changes. |

### 嵌套从句练习：对比两个扩展维度

**Layer 1：**
> Adding replicas improves reads, but not writes.

**Layer 2：**
> Adding replicas improves reads and availability, **but** it does not improve writes.

**Layer 3 — 加对比与原因：**
> Adding replicas improves reads and availability, **whereas** adding shards improves write throughput, **because** each new shard brings another primary **that** accepts writes.

**Layer 4 — 完整嵌套版：**
> **When** you expand the cluster from four machines to eight **while** keeping four shards, the replica count rises from two to four, **which** improves read scalability and availability but leaves write throughput unchanged — **because** writes are still handled by the same four primaries, **whereas** adding shards would create new primaries **that** write in parallel.

**中文对照：** 当你把集群从 4 台扩到 8 台、同时保持 4 个分片不变时，副本数从 2 升到 4，这提升了读扩展性和可用性，却没有改变写吞吐——因为写仍然由同样那 4 个主节点处理；而增加分片则会带来能够并行写入的新主节点。

### 嵌套从句练习：说"写慢先加分片"

**Layer 3：**
> **If** the system is slow on writes, you should add shards **rather than** replicas.

**Layer 4 — 完整嵌套版：**
> **When** someone says the system is slow on writes, the right instinct is to add shards **rather than** replicas, **because** replicas only create more copies **that** serve reads, **which** does nothing for the primary **that** has to keep up with every write.

**中文对照：** 当有人说系统写得慢时，正确的直觉是加分片而不是加副本，因为副本只是多出几份服务读的拷贝，对那个必须扛住每一次写的主分片毫无帮助。

---

## 概念 5：混合部署在生产上还要补什么

### 用自己的话理解（中英双语）

**中文：**

混合部署的图很好看，但落地还要补几件事，否则"机器数不变的高可用"只是纸面方案。

**一、资源隔离。** 一台机器跑 3 个分片实例，必须配 CPU 亲和、内存限额、磁盘配额。否则某个分片的突发写流量会把同机其他分片的 I/O 抢光，把"一台机器挂了"变成"一台机器上三个分片一起变慢"。

**二、切换不能丢数据。** 主从复制默认是异步的，主库宕机时可能有一部分已提交事务还没同步到副本。要靠半同步复制或 Raft 这类强一致复制，保证主库返回成功之前至少一个副本已经收到日志。

**三、客户端得知道新主在哪。** 分片到节点的映射要放在元数据服务里（ZooKeeper、etcd 之类），故障切换后及时更新，请求才能路由到新主，否则切换做完了请求还打向那台已经挂掉的机器。

**四、扩容要能平滑。** 从 4 分片扩到 8 分片涉及数据迁移。用一致性哈希或范围分片能减少迁移量，再配在线迁移工具，避免停机。

**五、要防脑裂。** 网络分区时，如果两边都以为自己还是主，就会出现双写。共识协议必须保证少数派不能继续写。

说到底，**混合部署解决的是"用更少的硬件买到冗余"，但它把风险从硬件转移到了调度、复制协议和元数据管理上**——这才是这套方案真正的运维成本。

**English (B2):**

The mixed-deployment diagram looks elegant, **but** several pieces must be added **before** "high availability without extra machines" becomes real.

**First, resource isolation.** Running three shard instances on one box requires CPU affinity, memory limits, and disk quotas. **Otherwise**, a burst of writes on one shard starves the others of I/O, **which** turns "one machine went down" into "three shards on one machine all went slow."

**Second, failover must not lose data.** Replication is asynchronous by default, **so when** the primary dies, transactions **that** were committed but not yet replicated can vanish. The fix is semi-synchronous replication or a strongly consistent protocol such as Raft, **which** ensures **that** at least one replica has the log **before** the primary confirms success.

**Third, clients must know where the new primary is.** The mapping **from** shards **to** nodes belongs in a metadata service such as ZooKeeper or etcd, **which** must be updated **as soon as** a failover completes; **otherwise**, requests keep hitting a machine **that** is already dead.

**Fourth, expansion has to be smooth.** Going from four shards to eight involves data migration, **which** consistent hashing or range partitioning can reduce, **and** **which** online migration tools can carry out **without** taking the service offline.

**Fifth, split-brain must be prevented.** **When** a network partition occurs, **if** both sides still believe they are primary, the cluster accepts double writes — **which** is why a consensus protocol must guarantee **that** a minority can never keep serving writes.

In the end, mixed deployment buys redundancy with less hardware, **but** it moves the risk from hardware to **scheduling, replication protocols, and metadata management** — **which** is where the real operational cost lives.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
|---|---|---|
| resource isolation | 资源隔离 | Resource isolation sets limits **that** stop one shard **from** starving the others. |
| CPU affinity | CPU 亲和 | CPU affinity pins an instance to specific cores, **which** reduces contention on a shared box. |
| metadata service | 元数据服务 | A metadata service stores the mapping **that** tells clients **which** node owns **which** shard. |
| online migration | 在线迁移 | Online migration moves data **while** the service keeps serving traffic. |
| consistent hashing | 一致性哈希 | Consistent hashing limits how much data moves **when** you add shards. |
| network partition | 网络分区 | A network partition is a split **in which** two sides cannot see each other. |
| split-brain | 脑裂 | Split-brain happens **when** two sides both think they are still primary. |
| minority write | 少数派写入 | The protocol must stop a minority **that** cannot reach a quorum from writing. |

### 嵌套从句练习：说资源隔离

**Layer 3：**
> **If** you do not set CPU affinity, memory limits and disk quotas, a burst on one shard will slow down the others.

**Layer 4 — 完整嵌套版：**
> **Unless** CPU affinity, memory limits and disk quotas are configured, a burst of writes on one shard will starve the other shards **that** share the same machine, **which** turns a single-node failure into a machine-wide slowdown.

**中文对照：** 除非配好 CPU 亲和、内存限额和磁盘配额，否则某个分片的写突发会把共享同一台机器的其他分片的资源抢光，把单节点故障变成整台机器一起变慢。

### 嵌套从句练习：说元数据服务和脑裂

**Layer 4 — 完整嵌套版：**
> **Because** the mapping **from** shards **to** nodes is kept in a metadata service, clients can be redirected to the new primary **as soon as** a failover finishes, **whereas** **without** it, requests would keep hitting a machine **that** is already down; **and** **if** a network partition ever leaves two sides both believing they are primary, a consensus protocol must stop the minority **from** writing, **otherwise** the cluster ends up with conflicting data **that** nobody can merge.

**中文对照：** 因为分片到节点的映射保存在元数据服务里，故障切换一完成客户端就能被重定向到新主；而没有这层服务，请求会继续打向已经宕掉的机器。同时，如果网络分区让两边都以为自己仍是主，共识协议必须阻止少数派继续写入，否则集群就会出现谁也合并不了的冲突数据。

---

## 课堂对话套路（B2 + 嵌套从句）

### 套路 1：老师问"分片和副本什么关系"

> Sharding solves write throughput and disk capacity, **because** each shard owns only a slice of the data **and** writes to it independently, **whereas** replication solves availability and read scaling, **because** it copies the same shard to several nodes **so that** **when** a primary dies, another copy can take over. **Neither can replace the other**: a shard **that** has no replica is a single point of failure, **and** replicas **without** sharding just leave every write flowing through one primary **whose** capacity stays capped.

---

### 套路 2：老师问"能不能不加机器还保证每个分片都有副本"

> Yes — through mixed deployment, **where** four machines and four shards are laid out so **that** each machine hosts three shard instances: one primary **that** it owns, **and** two replicas **that** belong to other shards. The machine count stays at four, **yet** every shard still keeps three copies, **which** comes to twelve copies in total. The trade-off is **that** several instances share one box, **so** they compete for CPU and disk I/O, **and** **after** a failover the survivors must absorb the extra load — **which** is why we keep normal utilisation near 60%.

---

### 套路 3：老师问"机器 1 挂了会怎么样"

> **When** Machine 1 fails, shard A's primary is re-elected from a replica **that** lives on Machine 2 or 3, **whereas** the copies of B and C **that** it hosted simply disappear — **although** B and C stay available, **because** their primaries and one more replica live on other machines. Shard D is untouched, **since** Machine 1 never held it. The important point is **that** only a replica of the same shard can take over: a copy of B on Machine 2 does nothing for A, **because** they hold different data sets.

---

### 套路 4：老师问"扩到 8 台但只加副本会怎样"

> **When** we expand from four machines to eight **while** keeping four shards, the replica count rises from two to four, **which** improves read scalability and availability but leaves write throughput unchanged, **because** writes are still handled by the same four primaries. To raise write throughput you have to add shards, **whereas** replicas only create more copies **that** serve reads — **which** is why the rule of thumb is **that** **if** writes are slow, you add shards, **not** replicas.

---

### 套路 5：老师问"这套方案在生产上还有什么风险"

> **Although** mixed deployment gives redundancy without more hardware, it moves the risk from hardware to **scheduling, replication protocols, and metadata management**. **Unless** resource isolation is configured, one shard's burst can starve the others; **unless** replication is semi-synchronous or Raft-based, a failover can lose writes **that** were committed but never replicated; **and** **unless** the shard-to-node mapping lives in a metadata service, clients keep hitting a machine **that** is already dead. **If** a network partition ever leaves both sides thinking they are primary, we also have to prevent the minority **from** writing, **otherwise** we end up with conflicting data.

---

### 套路 6：课上主动说话

| 你想做什么 | 嵌套从句版 |
|---|---|
| 确认理解 | So the point is **that** sharding and replication are orthogonal, **which** means adding replicas can never fix a write bottleneck, right? |
| 请老师再解释 | Could you walk through **what** happens to the replicas **that** the failed machine was hosting? |
| 提出疑问 | **But if** the same three machines now absorb the load, wouldn't the cluster be overloaded **when** it was already running hot? |
| 表示同意 | That matches **what** I saw — we kept utilisation near 60% **so that** a single failure would not cascade. |
| 追问切换 | How does the cluster decide **which** replica becomes primary, **and** how do clients learn **where** the new primary is? |
| 联系上一课 | Is this the same idea **that** we discussed last time, **where** partitioning solves writes **and** replication solves availability? |

---

## 常用句式：嵌套从句版（改写，非原文）

| 功能 | 嵌套从句句式 |
|---|---|
| 说正交关系 | Sharding and replication are orthogonal, **which** means **that** one addresses write throughput **while** the other addresses availability. |
| 说单点故障 | A shard **that** has no replica is a single point of failure, **because** no other shard holds a copy of its data. |
| 说混合部署 | **Although** the machine count stays at four, each machine hosts one primary **that** it owns **and** two replicas **that** belong to other shards. |
| 说切换逻辑 | **When** the primary fails, a replica **that** holds the same shard is promoted, **whereas** copies of other shards cannot take over. |
| 说数据丢失 | **Unless** replication is semi-synchronous, writes **that** were committed but not yet copied are lost **when** the primary dies. |
| 区分两个维度 | Shard count determines write capacity, **whereas** replica count determines read capacity and reliability. |
| 说扩容 | **If** writes are the bottleneck, you add shards, **because** replicas only create more copies **that** serve reads. |
| 说运维成本 | Mixed deployment moves the risk from hardware to scheduling and metadata, **which** is **where** the real operational cost lies. |

---

## 老师可能追问 — 嵌套从句回答

| 老师问 | 你可以答 |
|---|---|
| Why can't shards replace replicas? | **Because** sharding only splits the data, it never copies it, **so** **if** a machine dies the shard **that** lived on it is gone — **whereas** replication is what keeps another copy alive **when** that happens. |
| How do 4 machines give every shard 3 copies? | Each machine hosts one primary **that** it owns **and** two replicas **that** belong to other shards, **which** means every shard has one primary plus two replicas **that** sit on different boxes. |
| What happens to the replicas on the failed machine? | The copies of B and C **that** Machine 1 hosted are lost, **but** B and C stay available, **because** each still has a primary **and** one more replica elsewhere. |
| Could a replica of another shard take over? | No — only a replica **that** holds the same shard can be promoted, **since** a copy of a different shard contains a different data set **that** cannot serve those requests. |
| Does adding replicas raise write throughput? | Not at all. Write throughput depends on the shard count, **whereas** replicas only add read paths, **which** is why **if** writes are slow you add shards **rather than** replicas. |
| What can go wrong in production? | **Unless** resource isolation is set up, instances on one box starve each other; **unless** replication is semi-synchronous, a failover loses writes; **and** **unless** the shard map is in a metadata service, clients keep calling a dead node. |
| What if the network splits? | **If** two sides both believe they are primary, we get split-brain, **which** is why the consensus protocol must stop a minority **that** cannot reach a quorum **from** writing. |

---

## 跟读练习：五段 B2 嵌套从句（课前朗读 2 遍）

**Part 1 — 分片与副本是正交的**

> **When** we shard the order table by `user_id`, each row belongs to exactly one shard, **which** is exactly **why** write throughput improves and also **why** availability does not. Sharding addresses write throughput and disk capacity, **whereas** replication addresses availability and read scaling, **because** it copies every shard to several nodes. **Neither can replace the other**: a shard **that** has no replica stays a single point of failure, **and** replicas **without** sharding leave all writes flowing through one primary **whose** capacity cannot grow.

**Part 2 — 混合部署怎么省钱**

> The naive layout gives each shard its own replica set, **which** means four shards times two replicas — eight machines **whose** cost doubles. Mixed deployment solves this by interleaving primaries and replicas **so that** each of the four machines hosts three shard instances: one primary **that** it owns **and** two replicas **that** belong to other shards. **Although** the machine count stays at four, every shard still keeps three copies, **which** adds up to twelve in total.

**Part 3 — 机器挂了谁接管**

> **When** Machine 1 fails, shard A's primary is re-elected from a replica **that** lives on Machine 2 or 3, **whereas** the copies of B and C **that** it hosted are simply lost — **although** B and C remain available, **because** their primaries and one more replica sit on other machines. The key point is **that** only a replica of the same shard can take over, **since** a copy of a different shard holds a different data set. **While** the failover completes, the remaining machines absorb extra load, **which** is why we keep utilisation near 60%.

**Part 4 — 加副本还是加分片**

> **When** we expand from four machines to eight **while** keeping four shards, the replica count rises from two to four, **which** improves read scalability and availability but leaves write throughput unchanged, **because** writes are still handled by the same four primaries. Shard count determines write capacity, **whereas** replica count determines read capacity and reliability. **If** writes are the bottleneck, you add shards **rather than** replicas, **since** replicas only create more copies **that** serve reads.

**Part 5 — 生产上还要补什么**

> **Although** mixed deployment buys redundancy with less hardware, it moves the risk to scheduling, replication protocols and metadata management. **Unless** CPU affinity, memory limits and disk quotas are configured, one shard's burst starves the others; **unless** replication is semi-synchronous or Raft-based, a failover loses writes **that** were committed but never copied; **and** **unless** the shard-to-node mapping lives in a metadata service, clients keep hitting a machine **that** is already dead. **If** a partition ever leaves both sides believing they are primary, the protocol must stop the minority **from** writing, **otherwise** the cluster ends up with conflicting data **that** nobody can merge.

---

## 附录：嵌套从句工具箱

| 从句类型 | 常用引导词 | 练法 |
|---|---|---|
| **定语从句（限定）** | that, which, who, whose, where | 修饰名词：*a replica **that** holds the same shard* |
| **定语从句（非限定）** | , which / , whose | 补充说明：*…three copies, **which** adds up to twelve* |
| **时间 / 条件状语** | when, before, after, if, unless, as long as | *…**unless** headroom exists, a second failure would cascade* |
| **原因 / 结果状语** | because, since, so that, which is why | *…**because** each row belongs to exactly one shard* |
| **对比 / 让步状语** | although, whereas, while | *…**whereas** replicas add read paths, shards add write paths* |
| **嵌套技巧** | 从句套从句 | 主句 → 定语从句里再套 that/when/which |

**拆句口诀：** 先找主句主干（谁做什么）→ 标出每个 that / which / when / because 引导的从句 → 从外往里读 → 再试着合并回去。

---

**课前最少记：** 4 分片 × 2 副本 = 8 台 vs 混合部署 4 台 × 3 份 · 只扩副本写吞吐不变，扩分片才提写 · **同分片副本才能接管** · 日常利用率 60% · *Shards determine write capacity; replicas determine read capacity and reliability.*
