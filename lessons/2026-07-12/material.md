# Scalability Interview – Vertical vs. Horizontal Scaling and Load Metrics

**Source:** Interview / System Design
**Level:** T2 / Intermediate
**Role:** Interviewer, Candidate (2–5 years backend engineer)
**Estimated Words:** ~452

---

## Background

### 故事 Prompt 及故事

**Prompt**

请根据以下系统设计知识点生成一个中文技术故事，用于后续英语教学。

知识点：[1.2 **可扩展性**]

故事形式：一段面试场景对话，对话双方是面试官和候选人。

技术要求：T2难度（方案对比级），适合2-5年经验后端工程师。

故事冲突：围绕面试中的常见追问展开——[什么时候该垂直扩展而不是水平扩展？]

【必须覆盖的核心概念】：

- 垂直扩展 vs 水平扩展
- QPS/延迟作为负载指标
- 状态服务的扩展优势

要求：故事简短，纯对话形式，字数350字。确保对话中自然包含以上所有核心概念。

**故事**

面试官在白板上画了一台服务器，旁边标了个数字"5000 QPS"。

"你们的订单服务现在单机能扛5000 QPS。如果下个月大促峰值要翻到15000，你选加机器还是换大机器？"

候选人想了想："看情况。如果瓶颈在CPU或内存，换个64核256G的大机器——垂直扩展，最快。如果瓶颈在数据库连接池这种无状态服务，加三台4核8G的机器做水平扩展更灵活，成本也低。"

"什么情况下你绝对不用垂直扩展？"

"当服务是无状态的时候。无状态服务没有需要同步的数据，水平扩展天然适合，加机器就能线性提升吞吐。反过来，如果服务有状态——比如内存里维护了一个用户登录态缓存——那我反而倾向先垂直扩展。"

面试官来了兴趣："为什么有状态反而要垂直？"

"因为水平扩展状态服务需要在多台机器之间同步数据，引入分布式缓存或一致性哈希，复杂度直接上去了。垂直扩展一台机器，状态全在本地，延迟低、不出脑裂问题。所以有状态服务扩展时，我会先评估能不能升级硬件解决，不够再说拆分。"

"那负载指标你怎么看？QPS和延迟哪个更影响扩展决策？"

"两个都要看。QPS决定要不要扩，P99延迟决定扩的方向。比如QPS还在承受范围内但P99延迟从50ms飙到300ms，那可能不是缺机器，是单机内部有锁竞争或IO瓶颈——这时候垂直扩展换更快的磁盘或更大的内存，比加机器更对症。"

面试官在白板上的服务器旁边又画了两台小机器，点了点头。

### 核心概念覆盖说明

- **垂直扩展 vs 水平扩展**：候选人明确对比了换大机器（垂直扩展）与加多台小机器（水平扩展），并分别说明适用场景。
- **QPS/延迟作为负载指标**：在讨论负载指标时，指出QPS决定是否需要扩容，P99延迟决定扩容方向（垂直还是水平）。
- **状态服务的扩展优势**：候选人解释了有状态服务在垂直扩展时能保持本地状态、避免分布式同步的复杂性，体现了状态服务扩展时的优势。

### 文章技术干点

这段面试对话深入探讨了系统扩容决策的核心逻辑，从简单的“加机器还是换大机器”展开，逐步深入到有状态服务的复杂性、负载指标的诊断价值以及真实案例的验证。

#### 1. 扩容策略的选择：垂直 vs 水平

候选人首先明确了选择取决于瓶颈类型，而非盲目跟随某种趋势：

- **垂直扩展（Vertical Scaling）**：换用更高配置的机器（如64核CPU、256GB内存、NVMe硬盘）。
  - **适用场景**：瓶颈在CPU计算、内存容量或磁盘I/O。无需修改代码，部署最快。对于有状态服务（如持有本地会话缓存），能避免分布式状态管理的复杂性。
- **水平扩展（Horizontal Scaling）**：部署多个实例并通过负载均衡分发流量。
  - **适用场景**：无状态服务，或瓶颈在数据库连接池等外部资源限制。更灵活，可弹性伸缩，成本更可控，因为可以随时缩减规模。

#### 2. 有状态服务的缩放陷阱

面试官追问“分布式缓存”时，候选人揭示了**水平扩展有状态服务**会引入的固有问题：

- **一致性哈希**：需要复杂的路由机制确保请求落到正确的节点，增加运维复杂度。
- **缓存复制延迟**：同步状态会带来网络开销和延迟。
- **脑裂**：多个节点同时认为自己是状态的所有者，导致数据不一致。

因此，对于状态量可控的场景，**垂直扩展以保持状态本地化**，换取简单、快速、无风险的本地访问，往往是更务实的首选。

#### 3. 负载指标的诊断逻辑：QPS 是症状，延迟是诊断

这是对话中最核心的方法论，候选人清晰区分了两个关键指标的不同用途：

- **QPS（每秒查询数）**：
  - **作用**：回答“**要不要扩容**”。
  - **判断**：当CPU打满且QPS达到瓶颈不再增长时，说明容量已达极限，需要扩容。
- **P99 延迟**：
  - **作用**：回答“**瓶颈在哪，该怎么扩**”。
  - **判断**：QPS正常但P99飙升，问题不在吞吐，而在于**锁竞争、I/O瓶颈等内部资源冲突**。
  - **关键指导**：这种情况下，水平增加实例只是分摊了同一种慢操作的痛苦，治标不治本。垂直升级（换更快SSD、加内存）才能根治。

#### 4. 案例验证：垂直升级解决I/O瓶颈

候选人分享了一个真实案例：报表服务QPS正常但P99延迟在高峰期飙高。

- **诊断**：不是流量过大，而是**后台任务争抢磁盘I/O**，导致数据库读延迟增加。
- **决策**：换用NVMe固态硬盘的机器（垂直扩展），P99延迟立即恢复正常。
- **教训**：如果当时水平扩展，每个新实例都会遇到同样的磁盘争用，无法解决问题。

#### 总结

这次面试体现了成熟的工程诊断思维：**系统扩容不是一个粗暴的“加机器”动作，而是一个基于指标证据的精准决策过程**。关键步骤是：

1. **用 QPS 判断是否需要行动**。
2. **用 P99 延迟定位瓶颈根因**（CPU/内存/IO/锁）。
3. **根据瓶颈类型选择垂直或水平方案**。
4. **对有状态服务优先考虑垂直扩展以换取简单性**。

最终，所有决策都回归到对系统内部状态的精确理解，而非盲目跟从“水平扩展为王”的潮流。

### 根据瓶颈类型选择垂直或水平方案

根据瓶颈类型选择垂直还是水平扩展，本质是一个“诊断-对症下药”的过程。不同类型的瓶颈，最优解法截然不同。

#### 1. CPU/内存瓶颈（算力不足）

**表现**：CPU使用率长期接近100%，QPS达到平台期无法再提升；或内存耗尽导致频繁GC、OOM。

- **垂直扩展**：直接换更大CPU、更多内存的机器。这是最快的路径，无需任何代码和应用架构改动。
- **水平扩展**：增加实例数量。前提是服务必须**无状态**，这样多实例才能并行处理请求，吞吐量近乎线性增长。如果是有状态服务（如本地缓存），水平扩展会引入分布式状态管理的一致性问题，此时垂直扩展反而更简单。

**选择逻辑**：无状态服务优先水平（弹性好），有状态服务先垂直（避免分布式复杂度），当单机物理上限无法满足时才拆分状态做水平。

#### 2. 数据库连接池瓶颈（资源连接数不足）

**表现**：应用日志频繁报“获取连接超时”，但CPU和内存使用率并不高。

- **垂直扩展无效**：换更大机器，数据库连接池的配置不会自动变大，单应用的连接数上限依然存在。瓶颈不在算力，而在连接数。
- **水平扩展有效**：每个新实例都有自己的连接池。部署三个4核实例，总的可用连接数就是单实例的三倍，直接打破连接数天花板。

**选择逻辑**：这是典型的水平扩展胜出场景，因为瓶颈在单实例的资源配额上限，而非物理资源耗尽。

#### 3. I/O瓶颈（磁盘/网络吞吐不足）

**表现**：CPU不忙、QPS也不高，但P99延迟飙升，日志显示大量线程在等待磁盘读写或网络IO。

- **水平扩展可能失效**：如果瓶颈是磁盘I/O，增加实例只是让更多实例共享同一个慢磁盘，每个实例依然要排队读写，延迟不会改善。候选人举的报表服务例子正是这种情况——后台任务争抢磁盘，加机器是分摊痛苦而非根除。
- **垂直扩展精准打击**：换NVMe固态盘、升级网络带宽，直接提升单机I/O能力，把慢操作从根源上消除。

**选择逻辑**：I/O瓶颈通常先考虑垂直，因为它在单机内部。水平扩展要求复制完整的数据集或做分片，改造成本巨大。

#### 4. 快速诊断表

| **瓶颈类型** | **主要症状** | **有效方案** | **为何有效/无效** |
| --- | --- | --- | --- |
| **CPU/内存** | CPU打满，内存溢出 | 无状态→水平，有状态→垂直 | 水平可分摊计算；垂直保持本地状态简单性 |
| **连接池** | 获取连接超时，CPU不高 | 水平扩展 | 新实例带来独立连接池，增加总可用连接数 |
| **磁盘I/O** | P99延迟飙升，磁盘队列长 | 垂直扩展（换SSD） | 水平扩展会让所有实例继续竞争同一个慢磁盘 |
| **锁竞争** | P99延迟高，线程阻塞在锁上 | 垂直（优化代码） | 根本在应用内部逻辑，加机器不能消除锁 |

**一句话总结**：看症状下药——算力不足可垂直可水平，连接数不足必须水平，I/O慢和锁竞争通常垂直或优化代码更对症。加机器不是万能药，乱用只会把问题隐藏到更大的规模里。

### 说一下一致性哈希

一致性哈希是一种分布式哈希算法，核心目标是**在节点数量变动时，尽可能减少需要重新分配的数据量**。它广泛应用于分布式缓存（如Redis集群）、分布式存储和负载均衡等场景。

#### 1. 为什么需要一致性哈希？

传统哈希取模算法（如 `hash(key) % N`）在 N 个节点中分配数据，简单高效。但当节点数 N 发生变化（扩容或故障）时，几乎所有数据的映射都会改变，导致大规模数据迁移。

一致性哈希通过将节点和数据映射到同一个环形空间，让节点增减只影响相邻的一小部分数据，从而避免全局洗牌。

#### 2. 核心概念：哈希环

一致性哈希将整个哈希空间（通常是 0 ~ 2^32-1）组织成一个环形结构。

**节点映射**：计算每个节点的哈希值（通常用节点IP或名称），将其分布在环上。

**数据映射**：计算每个数据对象的哈希值，同样分布在环上。数据对象被分配给**沿环顺时针方向遇到的下一个节点**。

#### 3. 节点增减的影响

**节点故障/删除**：当某个节点从环上移除，原本属于它的数据，只需迁移到顺时针方向的下一节点。其他节点上的数据不受影响。

**节点添加**：新节点加入后，只需从顺时针方向的下一节点迁移部分数据给它。同样只影响相邻节点。

这与传统取模算法形成鲜明对比——后者在节点数变化时，几乎全部数据需要重新分配。

#### 4. 虚拟节点：解决数据倾斜

当节点数较少或分布不均时，哈希环可能出现“倾斜”——某些节点负责的弧段过长，承担过多数据。

**解决方式**：为每个物理节点创建多个虚拟节点，分散在环上不同位置。虚拟节点越多，数据分布越均匀。通常实践中每个物理节点映射 100-200 个虚拟节点即可达到较好均衡。

当物理节点增减时，只需调整相应的虚拟节点映射，数据迁移仍然是局部且均匀的。

#### 5. 对话场景中的应用与权衡

候选人提到水平扩展有状态服务（如用户登录会话缓存）时，会引入一致性哈希问题：

- **为什么需要它**：当多台缓存服务器组成集群，必须用一种方式决定每个用户的会话数据存放在哪台机器上。一致性哈希是最常用的方案。
- **它带来的问题**：
  - **实现复杂**：客户端或代理需要感知集群拓扑并计算哈希路由。
  - **故障转移时的不一致风险**：节点宕机时，如果数据尚未完全复制到下一个节点，部分会话可能丢失。
  - **脑裂风险**：网络分区时，不同客户端可能对环拓扑认知不同，导致同一份数据被写入两个不同节点。

正因如此，候选人才说：“垂直扩展保持所有会话在本地，避免了引入一致性哈希的复杂度”——对于状态量可控的场景，用更大内存的单机垂直扩展，比水平拆分加分布式哈希更简单、更可靠。

**一句话总结**：一致性哈希解决了分布式系统中节点动态变化时的数据大规模迁移问题，但引入了一致性维护、故障处理和脑裂等分布式系统固有的复杂性。它是以系统复杂度换取扩展性的典型技术权衡。

### 说一下脑裂

**脑裂（Split-Brain）** 是指分布式系统中，由于网络故障，一个原本协同工作的集群被分割成多个无法互相通信的子集群。每个子集群都误以为自己仍然拥有完整的数据和权限，并继续对外提供服务，导致**多个节点同时写入同一份数据**或**多个节点争夺同一把锁**，最终造成数据严重不一致、资源冲突或服务状态混乱。

#### 1. 脑裂的发生条件

- 集群中的节点依赖心跳机制判断彼此存活。
- 网络分区导致心跳中断，但各节点本身运行正常。
- 没有足够的仲裁机制来决定谁拥有合法的主导权。

#### 2. 典型危害

| **场景** | **脑裂后果** |
| --- | --- |
| **数据库主从复制** | 出现两个“主库”同时接受写入，数据分叉，无法合并 |
| **分布式缓存（如Redis集群）** | 同一份数据在不同分区被独立更新，读取时可能得到过期值 |
| **分布式锁** | 两个节点都认为自己持有了锁，同时执行互斥操作 |

#### 3. 对话中的上下文

在之前讨论一致性哈希时，候选人提到水平扩展有状态缓存会引入脑裂风险：当网络分区发生时，两个缓存节点可能都认为自己是某份会话数据的唯一所有者，各自独立更新，导致用户状态不一致。

#### 4. 避免脑裂的常见手段

**① Quorum（多数派）机制**

要求写操作必须得到集群多数节点的确认才成功。网络分区后，只有包含多数节点的那一侧能继续写入，少数侧自动拒绝服务，防止数据分叉。

**② 仲裁（Arbitration）**

引入独立于主备节点之外的第三方仲裁服务（如 ZooKeeper、etcd）。只有获得仲裁者认可的节点才能成为主节点。

**③ Fencing Token（隔离令牌）**

每次选举主节点时生成一个单调递增的令牌号。写入存储时必须携带此令牌，存储系统拒绝携带旧令牌的写入，防止旧主“复活”后继续写数据。

**④ STONITH（Shoot The Other Node In The Head）**

在共享存储的高可用集群中，一旦检测到脑裂，直接通过硬件或软件手段强制关闭可疑节点，确保只有一个节点在操作存储。

**一句话总结**：脑裂是网络分区引发的“多重人格”灾难，必须通过多数派、仲裁或隔离令牌等手段，让集群在故障时能迅速达成“谁该闭嘴”的共识。

---

## Role and Scenario

- **Interviewer:** 考察候选人对系统扩展性的理解，从具体场景切入，逐步追问垂直扩展与水平扩展的决策依据。
- **Candidate:** 2–5 年经验后端工程师，负责订单服务，能结合负载指标和状态管理分析扩展策略。
- **Scene:** 面试。面试官在白板上画出一台服务器，标出当前 QPS，假设大促峰值翻倍，直接要求候选人给出扩展选择并解释理由。随后追问状态服务与无状态服务的扩展差异，以及 QPS 与延迟在决策中的作用。

---

## Dialogue (~452 words)

**Interviewer:**

Your order service runs on a single box handling 5,000 QPS. Next month a promotion will push peak traffic to 15,000. Would you add more servers or upgrade to a bigger machine?

**Candidate:**

It depends where the bottleneck is. If it's CPU or memory bound, I'd go with vertical scaling—swap in 64 cores and 256 GB of RAM. That's the quickest path, no code changes needed. But for a stateless service bottlenecked on the database connection pool, I'd choose horizontal scaling: deploy three extra 4‑core instances behind a load balancer. It's more flexible and often cheaper because you can scale back down after the peak.

**Interviewer:**

Is there a case where you'd absolutely avoid vertical scaling?

**Candidate:**

When the service is truly stateless. Stateless services don't need to synchronize data between instances, so horizontal scaling is a natural fit—add machines and throughput grows almost linearly. You just need the load balancer to distribute traffic evenly. However, for a stateful service—say it holds an in‑memory cache of user login sessions—I'd lean toward vertical scaling first. Why? Because keeping all state local avoids the complexity of distributing it.

**Interviewer:**

But can't you just use a distributed cache for that?

**Candidate:**

You can, and that's the standard horizontal solution. But it introduces problems. You now have to deal with consistent hashing to map sessions to nodes, or replicate the cache, which adds latency. You also risk split‑brain where two nodes think they own the same session. Vertical scaling gives you simple, fast local access. I'd only go horizontal when one machine physically can't hold the working set.

**Interviewer:**

So how do load metrics guide your decision? Do you look at QPS or latency?

**Candidate:**

Both, but they answer different questions. QPS tells you whether you need to scale at all. If the CPU is pegged and QPS plateaus, you've hit a capacity limit. P99 latency, on the other hand, tells you where the real pain is. Say QPS is still comfortable, but P99 jumps from 50ms to 300ms. That's not a throughput problem—it's likely lock contention or an I/O bottleneck inside the instance. Adding more boxes won't fix a slow disk. In that case, vertical scaling with faster SSDs or more memory is much more targeted.

**Interviewer:**

Can you give me a real example from your experience?

**Candidate:**

We once had a reporting service that looked fine on QPS, but P99 latency spiked during peak hours. It turned out a background job was competing for disk I/O, causing random read latencies. We moved to a machine with NVMe drives—vertical scaling—and the problem vanished. More instances would just have spread the same I/O contention.

**Interviewer:**

That's a clear case. So you use latency to diagnose the bottleneck type.

**Candidate:**

Exactly. QPS is the symptom; latency is the diagnosis.

---

## Vocabulary (25 Terms)

| Vocabulary | Pronunciation (IPA) | Chinese Meaning |
|---|---|---|
| QPS (Queries Per Second) | /ˌkjuː piː ˈes/ | 每秒查询数 |
| vertical scaling | /ˈvɜːrtɪkəl ˈskeɪlɪŋ/ | 垂直扩展（升级硬件） |
| horizontal scaling | /ˌhɒrɪˈzɒntəl ˈskeɪlɪŋ/ | 水平扩展（增加机器） |
| bottleneck | /ˈbɒtəlnek/ | 瓶颈 |
| CPU | /ˌsiː piː ˈjuː/ | 中央处理器 |
| memory | /ˈmeməri/ | 内存 |
| stateless service | /ˈsteɪtləs ˈsɜːrvɪs/ | 无状态服务 |
| database connection pool | /ˈdeɪtəbeɪs kəˈnekʃən puːl/ | 数据库连接池 |
| load balancer | /loʊd ˈbælənsər/ | 负载均衡器 |
| instance | /ˈɪnstəns/ | 实例 |
| throughput | /ˈθruːpʊt/ | 吞吐量 |
| stateful service | /ˈsteɪtfəl ˈsɜːrvɪs/ | 有状态服务 |
| in‑memory cache | /ɪn ˈmeməri kæʃ/ | 内存缓存 |
| consistent hashing | /kənˈsɪstənt ˈhæʃɪŋ/ | 一致性哈希 |
| split‑brain | /splɪt breɪn/ | 脑裂 |
| latency | /ˈleɪtənsi/ | 延迟 |
| P99 latency | /piː ˈnaɪnti naɪn ˈleɪtənsi/ | 第99百分位延迟 |
| lock contention | /lɒk kənˈtenʃən/ | 锁竞争 |
| I/O bottleneck | /aɪ oʊ ˈbɒtəlnek/ | I/O瓶颈 |
| SSD (Solid State Drive) | /ˌes es ˈdiː/ | 固态硬盘 |
| NVMe | /ˌen viː em ˈiː/ | 非易失性内存标准 |
| working set | /ˈwɜːrkɪŋ set/ | 工作集 |
| background job | /ˈbækɡraʊnd dʒɒb/ | 后台任务 |
| capacity limit | /kəˈpæsəti ˈlɪmɪt/ | 容量上限 |
| contention | /kənˈtenʃən/ | 竞争 |

---

## Sentence Patterns

| Function | English Pattern | Use Case |
|---|---|---|
| 说明扩展选择 | *"If it's X-bound, I'd go with vertical scaling. But for Y, I'd choose horizontal scaling."* | 对比两种扩展策略 |
| 描述无状态优势 | *"Stateless services don't need to synchronize data, so horizontal scaling is a natural fit."* | 解释无状态服务易扩展 |
| 解释有状态权衡 | *"Vertical scaling gives you simple, fast local access. I'd only go horizontal when one machine can't hold the working set."* | 说明有状态服务扩展的决策点 |
| 区分QPS与延迟 | *"QPS tells you whether you need to scale at all. P99 latency tells you where the real pain is."* | 负载指标在扩展决策中的角色 |
| 诊断延迟原因 | *"That's likely lock contention or an I/O bottleneck. Adding more boxes won't fix a slow disk."* | 分析延迟升高时的排查思路 |
| 总结指标关系 | *"QPS is the symptom; latency is the diagnosis."* | 概括性能指标的作用 |

---

## Reading Comprehension

1. **When would the candidate choose vertical scaling over horizontal scaling?**

   **Answer:** When the bottleneck is CPU or memory, or when the service is stateful and keeping data local avoids distributed complexity like consistent hashing and split‑brain.

2. **Why is horizontal scaling a natural fit for stateless services?**

   **Answer:** Stateless services don't need to synchronize data between instances, so adding machines behind a load balancer can increase throughput almost linearly.

3. **What risks does horizontal scaling introduce for stateful services?**

   **Answer:** It forces state synchronization across nodes, which may require a distributed cache or consistent hashing, adding latency and the risk of split‑brain.

4. **How does the candidate use QPS and P99 latency differently?**

   **Answer:** QPS indicates whether scaling is needed at all, while P99 latency reveals the type of bottleneck (e.g., lock contention or I/O), guiding whether to scale vertically or horizontally.

5. **What real example did the candidate give where vertical scaling solved a latency problem?**

   **Answer:** A reporting service with high P99 latency during peak hours caused by disk I/O contention; moving to NVMe drives (vertical scaling) eliminated the problem, while more instances would not have helped.

---

*Word count (dialogue): ~452 words*
*Level: Intermediate / T2*
*Self-assessment: 对话围绕可扩展性面试题展开，涵盖垂直/水平扩展的选择、QPS与P99延迟的决策区分、状态与无状态服务的扩展策略及真实案例。使用了中级后端技术词汇，对话自然有追问和实例，适合B1-B2学员练习系统设计面试中的扩展性话题表达。*
