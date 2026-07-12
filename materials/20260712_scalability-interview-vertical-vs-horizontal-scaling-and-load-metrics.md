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

---

## Role and Scenario

- **Interviewer:** 考察候选人对系统扩展性的理解，从具体场景切入，逐步追问垂直扩展与水平扩展的决策依据。
- **Candidate:** 2–5 年经验后端工程师，负责订单服务，能结合负载指标和状态管理分析扩展策略。
- **Scene:** 面试。面试官在白板上画出一台服务器，标出当前 QPS，假设大促峰值翻倍，直接要求候选人给出扩展选择并解释理由。随后追问状态服务与无状态服务的扩展差异，以及 QPS 与延迟在决策中的作用。

---

## Technical Key Points

### 1. Vertical vs. Horizontal Scaling

| Strategy | What It Means | Best For |
|---|---|---|
| Vertical scaling | Upgrade a single machine (more CPU, RAM, faster disk) | CPU/memory-bound workloads; stateful services where local state avoids distributed complexity |
| Horizontal scaling | Add more machines behind a load balancer | Stateless services; connection-pool or throughput bottlenecks that scale linearly with instance count |

- **Key rule:** Vertical scaling is the fastest path when the bottleneck is inside one box; horizontal scaling is more flexible and often cheaper when you can scale back down after a peak.

### 2. Stateless vs. Stateful Services

| Service Type | Scaling Preference | Why |
|---|---|---|
| Stateless | Horizontal first | No data to synchronize; add instances and throughput grows almost linearly |
| Stateful (e.g., in-memory session cache) | Vertical first | Keeps state local—low latency, no split-brain; horizontal requires consistent hashing or distributed cache |

- **Horizontal stateful trade-offs:** Consistent hashing, replication, added latency, and split-brain risk.
- **Decision point:** Go horizontal for stateful services only when one machine physically cannot hold the working set.

### 3. Load Metrics — QPS vs. Latency

| Metric | Role in Scaling Decisions |
|---|---|
| QPS | Tells you *whether* you need to scale at all (e.g., CPU pegged and QPS plateaus = capacity limit) |
| P99 latency | Tells you *how* to scale—reveals bottleneck type (lock contention, I/O) even when QPS looks fine |

- **Example:** QPS comfortable but P99 jumps from 50 ms to 300 ms → likely internal contention or I/O bottleneck; faster SSDs or more memory (vertical) beats adding more boxes.
- **Summary:** QPS is the symptom; latency is the diagnosis.

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
