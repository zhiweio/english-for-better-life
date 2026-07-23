这份预习材料**不用 material 原文**，概念全部用自己的话复述。每个概念的「用自己的话理解」提供**中英双语**（英文按 **B2**）。长句练习的重点是**嵌套从句**——定语从句、状语从句、非限制性从句叠在一起练。

---

## 课前 3 分钟：今天讲什么

**话题：** 系统可扩展性——流量涨了该换大机器还是加机器，以及 QPS 和延迟分别告诉你什么。

**四步决策（material 技术干点）：**

```
① QPS 判断要不要动 → ② P99 定位瓶颈类型 → ③ 按瓶颈选垂直/水平 → ④ 有状态优先垂直保简单
```

**故事线：**

```
5000 → 15000 QPS → 垂直 vs 水平怎么选 → 无状态先水平 / 有状态先垂直 → 一致性哈希与脑裂代价 → QPS 看要不要扩，P99 看往哪扩 → 报表服务 NVMe 案例
```

| 扩展方式 | 做法 | 典型场景 |
| --- | --- | --- |
| 垂直扩展 | 单机升配（更多 CPU/RAM/更快磁盘） | CPU/内存/I/O 瓶颈；有状态服务先保本地 |
| 水平扩展 | 加实例 + 负载均衡 | 无状态服务；连接池等可线性分摊的配额上限 |

| 指标 | 回答的问题 |
| --- | --- |
| QPS | 要不要扩？（CPU 打满、QPS 见顶 = 到容量上限） |
| P99 延迟 | 往哪扩？（QPS 还行但 P99 飙高 = 单机内部瓶颈） |

| 瓶颈类型 | 更有效的方向 |
| --- | --- |
| CPU/内存 | 无状态→水平；有状态→垂直 |
| 连接池 | 水平（新实例自带连接池） |
| 磁盘 I/O / 锁竞争 | 垂直或改代码（加机器常不治本） |

**规律：** QPS 是症状，延迟是诊断——先判断需不需要扩，再判断该垂直还是水平；有状态服务别急着上分布式。

---

## 概念 1：垂直扩展 vs 水平扩展

### 用自己的话理解（中英双语）

**中文：**

扩展系统容量有两条主路：**垂直扩展**是把一台机器换得更猛——更多核、更大内存、更快磁盘；**水平扩展**是加多台小机器，前面挂负载均衡，把流量分摊出去。

面试场景很具体：订单服务单机扛 5000 QPS，大促要冲到 15000。不能一刀切。CPU 或内存顶住了，垂直扩展往往最快——比如直接上到 64 核 256G，不用改代码，当天就能上线。瓶颈如果在无状态层、比如数据库连接池，水平加三台 4 核 8G 实例更划算，大促结束还能缩回去。

经验法则：瓶颈在**单机内部**（算力、内存、磁盘）→ 先想垂直；瓶颈在**可分摊的吞吐或配额**（无状态实例数、连接池）→ 先想水平。垂直是捷径，水平更弹性。别跟风「水平扩展为王」，先看瓶颈在哪。

**English (B2):**

There are two main ways **to grow system capacity**. **Vertical scaling** means upgrading a single machine — more CPU cores, more RAM, or faster disks — **whereas** **horizontal scaling** means adding more instances **that** sit behind a load balancer **and** share incoming traffic.

In the interview scenario, an order service **that** currently handles 5,000 QPS must survive a promotion peak of 15,000. The right choice depends on **where** the bottleneck sits. **When** the limit is CPU or memory, vertical scaling is often the fastest fix — for example, moving to a 64-core box with 256 GB of RAM, **which** requires no code changes **and** can be rolled out quickly. **If** the bottleneck is in a stateless layer such as the database connection pool, adding three 4-core instances is usually more flexible and cheaper, **because** you can scale them back down **after** the peak passes.

The practical rule is this: **when** the problem is inside one box, start with vertical scaling; **when** throughput or per-instance quotas can be split across instances **that** do not hold local state, start with horizontal scaling. Vertical scaling is the shortcut; horizontal scaling is the elastic option. Do not treat “horizontal first” as a religion — diagnose the bottleneck first.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| vertical scaling | 垂直扩展 | Vertical scaling is an approach **where** you upgrade hardware on a single server. |
| horizontal scaling | 水平扩展 | Horizontal scaling adds instances **that** share traffic through a load balancer. |
| load balancer | 负载均衡器 | A load balancer is a component **that** distributes requests across instances. |
| bottleneck | 瓶颈 | A bottleneck is the resource **that** limits how much traffic the system can handle. |
| CPU-bound | CPU 受限 | A CPU-bound workload is one **where** processors are the first resource **to saturate**. |
| connection pool | 连接池 | A connection pool is a set of DB connections **that** instances reuse. |
| scale back down | 缩容 | We scale back down **after** the peak **so that** we do not pay for idle machines. |

### 嵌套从句练习：大促怎么扩

**Layer 0 — 主句：**

> We need to handle 15,000 QPS instead of 5,000.

**Layer 1 — 加定语从句 (that/which)：**

> We need a scaling strategy **that** can handle 15,000 QPS instead of 5,000.

**Layer 2 — 加状语从句 (when/if)：**

> **When** peak traffic jumps from 5,000 to 15,000 QPS, we need a scaling strategy **that** matches the bottleneck.

**Layer 3 — 嵌套完整版（条件 + 对比）：**

> **When** peak traffic jumps from 5,000 to 15,000 QPS, **if** the bottleneck is CPU or memory, I would choose vertical scaling, **whereas** **if** the service is stateless and the limit is the connection pool, I would add instances **that** sit behind a load balancer.

**Layer 4 — 再加一层（成本与弹性）：**

> **Although** vertical scaling is the quickest path **when** you only need more compute on one box, horizontal scaling is often cheaper **because** you can deploy extra instances **that** handle the promotion peak **and** remove them **after** traffic drops — **a flexibility that** upgrading a single machine cannot offer.

**中文对照：** 虽说单机加配是加算力最快的路，水平扩展往往更省钱，因为你可以多部署实例扛大促峰值、流量回落后再撤掉——这是换大机器给不了的弹性。

---

## 概念 2：有状态 vs 无状态服务

### 用自己的话理解（中英双语）

**中文：**

**无状态服务**不保存请求之间需要共享的本地数据，实例之间不用同步状态。加机器、挂负载均衡，吞吐往往接近线性涨——这是水平扩展的天然主场。所以面试官问「什么情况下绝对不用垂直扩展」，候选人反过来说：无状态时优先水平，而不是垂直。

**有状态服务**相反——比如内存里缓存用户登录会话。状态在单机本地时，读写快、逻辑简单。硬要水平扩，就得引入分布式缓存、一致性哈希或复制，延迟上去，还要防脑裂（两个节点都以为同一会话归自己）。

因此有状态服务常**先垂直**：看能不能用更大内存把 working set 装下。只有单机物理上装不下了，才考虑拆分或分布式方案。垂直扩状态服务的好处是：状态留在本地，延迟低，不引入跨机同步复杂度。

**English (B2):**

A **stateless service** does not keep data **that** must be shared across requests on local disk or in local memory, **which** means instances do not need **to synchronize state with each other**. **When** you add machines and place a load balancer in front of them, throughput often grows almost linearly — **a pattern that** makes horizontal scaling the natural first choice. **That is why**, **when** the interviewer asks **when** you would avoid vertical scaling, the candidate flips the question: for stateless workloads, you prefer horizontal scaling rather than buying a bigger box.

A **stateful service** is different — for example, a service **that** keeps user login sessions in an in-memory cache. **While** state stays on one machine, reads and writes are fast **and** the logic stays simple. **If** you force horizontal scaling, you must introduce a distributed cache, consistent hashing, or replication, **all of which** add latency **and** create risks such as split-brain, **where** two nodes both believe **that** they own the same session.

For that reason, teams often start with vertical scaling for stateful services: they check **whether** a larger machine can hold the entire working set in memory. **Only when** one box physically cannot hold the data do they move toward sharding or distributed caches. The advantage of vertical scaling here is local state — low latency **and** no cross-node synchronization complexity.

### 对比表

| | 无状态服务 | 有状态服务 |
| --- | --- | --- |
| 首选扩展 | 水平（加实例） | 垂直（升配单机） |
| 原因 | 无需同步，吞吐可线性分摊 | 本地状态快、简单 |
| 水平扩的代价 | 低（负载均衡即可） | 高（一致性哈希、复制、脑裂风险） |
| 何时才水平扩 | 几乎总是优先 | 单机装不下 working set 时 |

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| stateless service | 无状态服务 | A stateless service is one **that** does not store session data locally. |
| stateful service | 有状态服务 | A stateful service keeps data **that** the next request may depend on. |
| in-memory cache | 内存缓存 | An in-memory cache is storage **where** hot data lives in RAM. |
| consistent hashing | 一致性哈希 | Consistent hashing is a technique **that** maps keys to nodes **so that** adding a node moves only part of the data. |
| split-brain | 脑裂 | Split-brain happens **when** two nodes both think **that** they own the same resource. |
| working set | 工作集 | The working set is the data **that** must stay in memory **for** the service **to run fast**. |
| synchronize | 同步 | Stateless services do not need **to synchronize state** **between** instances. |

### 嵌套从句练习：为什么有状态先垂直

**Layer 2：**

> **If** the service holds login sessions in memory, I would scale vertically first, **because** local state is faster **than** a distributed cache.

**Layer 3：**

> **When** a service holds user sessions in an in-memory cache, I prefer vertical scaling first, **because** keeping state local avoids the complexity of consistent hashing **that** you need **when** you spread sessions across nodes.

**Layer 4 — 完整嵌套版：**

> **Although** you can solve stateful scaling with a distributed cache, **which** is the standard horizontal approach, that path forces you **to deal with** consistent hashing or replication **that** adds latency **and** risks split-brain, **where** two nodes both claim the same session — **which is why** I only go horizontal **when** one machine cannot physically hold the working set **that** the service needs **to serve requests quickly**.

**中文对照：** 虽说分布式缓存是水平扩有状态服务的常规做法，那条路会逼你处理一致性哈希或复制，既加延迟又有脑裂风险（两个节点都声称拥有同一会话）——所以我只在单机物理上装不下服务快速响应所需的工作集时，才走水平扩展。

### 嵌套从句练习：无状态为什么爱水平

**Layer 3：**

> Stateless services, **which** do not share data **between** requests, are easy **to scale horizontally, because** you only need a load balancer **that** spreads traffic evenly.

**Layer 4：**

> **Because** stateless services do not need **to synchronize data between** instances, **each of which** can handle requests independently, horizontal scaling is a natural fit — **a setup in which** you add machines behind a load balancer **and** watch throughput grow almost linearly, **whereas** vertical scaling would leave unused capacity **on** instances **that** could have shared the load instead.

**中文对照：** 因为无状态服务不需要在实例之间同步数据，每个实例都能独立处理请求，水平扩展非常合适——加机器、挂负载均衡，吞吐几乎线性增长；而垂直扩展反而可能让本可分摊的负载挤在一台机器上，留下闲置容量。

---

## 概念 3：QPS 与 P99 延迟——两个指标各管什么

### 用自己的话理解（中英双语）

**中文：**

扩容不能只看一个数字。**QPS（每秒查询数）**回答「要不要扩」：CPU 已经打满、QPS 不再往上涨，说明到了容量天花板，该加资源了。

**P99 延迟**回答「往哪扩」：有时 QPS 看起来还健康，但 P99 从 50ms 跳到 300ms，说明最慢的那 1% 请求体验已经崩了。这往往不是吞吐不够，而是单机内部问题——锁竞争、磁盘 I/O 被后台任务抢走等。这时多加几台机器，只是把同样的磁盘争用复制多份；换更快 SSD/NVMe 或加内存做垂直扩展，更对症。

候选人举了报表服务：QPS 正常，高峰 P99 却飙高，查下来是后台任务和在线读盘抢 I/O。换 NVMe 机器后问题消失。总结成一句：**QPS 是症状，延迟是诊断**——先看流量有没有顶到上限，再用延迟判断瓶颈类型，决定垂直还是水平。

**English (B2):**

You should not make scaling decisions **based on** a single metric. **QPS**, or queries per second, answers **whether** you need **to scale at all**: **when** the CPU is fully utilized **and** QPS stops rising, you have hit a capacity limit **that** requires more resources.

**P99 latency**, on the other hand, answers **how** you should scale. Sometimes QPS still looks healthy, **but** P99 jumps from 50 ms to 300 ms, **which** means the slowest 1% of requests are already suffering. **That** is often not a throughput problem **but** an internal bottleneck on one machine — lock contention, or disk I/O **that** is stolen by a background job. **In** such cases, adding more boxes only copies the same disk contention; upgrading to faster SSDs or NVMe drives, **which** is vertical scaling, targets the real issue.

The candidate describes a reporting service **whose** QPS looked fine **while** P99 spiked during peak hours. The root cause was a background job **that** competed for disk I/O with online reads. **After** they moved to a machine with NVMe drives, the problem disappeared. The takeaway fits one line: **QPS is the symptom; latency is the diagnosis** — first check **whether** traffic has hit the ceiling, **then** use latency **to identify** the bottleneck type **that** tells you **whether** to scale vertically or horizontally.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| QPS | 每秒查询数 | QPS is a metric **that** shows how many requests arrive per second. |
| P99 latency | 第99百分位延迟 | P99 latency measures how slow the worst 1% of requests are. |
| capacity limit | 容量上限 | You hit a capacity limit **when** CPU is pegged **and** QPS plateaus. |
| lock contention | 锁竞争 | Lock contention happens **when** threads wait for a lock **that** another thread holds. |
| I/O bottleneck | I/O 瓶颈 | An I/O bottleneck is a slowdown **that** comes from disk or network waits. |
| background job | 后台任务 | A background job is work **that** runs **while** online traffic still needs disk access. |
| NVMe | 高速固态标准 | NVMe drives are storage **that** reduces read latency **for** I/O-heavy workloads. |

### 嵌套从句练习：QPS 和 P99 分工

**Layer 2：**

> QPS tells you **whether** you need **to scale**, **whereas** P99 latency tells you **which direction** **to choose**.

**Layer 3：**

> **Although** QPS is still comfortable, P99 latency **that** jumps from 50 ms to 300 ms suggests an internal bottleneck, **which** means adding instances may not help.

**Layer 4 — 完整嵌套版：**

> **When** QPS is still within a comfortable range **but** P99 latency spikes from 50 ms to 300 ms, the problem is likely lock contention or an I/O bottleneck **that** lives inside one instance — **a situation in which** vertical scaling with faster disks or more memory is more targeted **than** horizontal scaling, **which** would only spread the same contention across boxes **that** still share the underlying slow storage pattern.

**中文对照：** 当 QPS 还在舒适区但 P99 从 50ms 飙到 300ms，问题多半是单机内部的锁竞争或 I/O 瓶颈——这时用更快磁盘或更大内存做垂直扩展更对症，水平加机器只是把同样的争用摊到多台实例上，底层慢的存储模式并没变。

### 嵌套从句练习：报表服务案例

**Layer 3：**

> We had a reporting service **whose** QPS looked fine, **but** P99 spiked **because** a background job competed for disk I/O.

**Layer 4：**

> **Although** the reporting service showed healthy QPS during peak hours, P99 latency spiked **because** a background job, **which** ran on the same machine, competed for disk I/O with online reads — **a problem that** we fixed by moving to NVMe drives through vertical scaling, **whereas** adding more instances would only have duplicated the same I/O contention **on** servers **that** still shared one slow disk.

**中文对照：** 报表服务在高峰时段 QPS 看着正常，但 P99 延迟飙升，因为同机上的后台任务和在线读请求抢磁盘 I/O——我们通过垂直扩展换 NVMe 盘解决了；若只是加实例，会在多台仍共用慢盘的服务器上复制同样的争用。

---

## 概念 4：按瓶颈类型选型——看症状下药

### 用自己的话理解（中英双语）

**中文：**

垂直还是水平，本质是**诊断后再开方**。不同瓶颈对应的有效方案差很远：

**CPU/内存瓶颈**：CPU 长期打满、QPS 见顶，或内存耗尽导致频繁 GC/OOM。垂直换更大机器最快；水平也能分摊算力，但前提是无状态。有本地缓存的有状态服务，硬水平扩会立刻碰到状态同步问题，所以往往先垂直。

**连接池瓶颈**：日志里大量「获取连接超时」，CPU 和内存却不高。这时换更大机器几乎没用——连接池上限不会跟着机器变大。水平扩反而有效：每个新实例自带一套连接池，三台 4 核实例的总连接数大约是单机的三倍。

**I/O 瓶颈**：CPU 不忙、QPS 也不高，但 P99 飙、线程在等磁盘或网络。若瓶颈是慢磁盘，加实例可能只是让更多实例一起排队读写同一类慢资源；换 NVMe、加带宽才是对症。报表服务案例就是这类——后台任务抢磁盘，加机器是分摊痛苦，不是根治。

**锁竞争**：P99 高、线程堵在锁上。根因在应用内部逻辑，加机器通常消不掉锁；要优化代码，或用垂直扩买一点缓冲时间。

一句话：算力不足可垂直可水平；连接数不够必须水平；I/O 慢和锁竞争通常垂直或改代码更对症。加机器不是万能药。

**English (B2):**

Choosing vertical or horizontal scaling is really a **diagnose-then-prescribe** process. Different bottlenecks call for very different fixes.

**CPU or memory pressure** shows up **when** processors stay near 100%, QPS stops climbing, or memory exhaustion triggers heavy GC or OOM. Vertical scaling is the fastest path **because** you swap in a larger box **without** changing application code. Horizontal scaling can also share compute load, **but only when** the service is stateless. **If** the service keeps local caches, forcing more instances immediately introduces state-sync problems, **which** is why teams often go vertical first.

**Connection-pool limits** look different: logs report connection timeouts **while** CPU and memory still look fine. Upgrading the machine rarely helps, **because** the pool size does not automatically grow with hardware. Horizontal scaling works here **because** each new instance brings its own pool — three 4-core instances can roughly triple the total available connections.

**I/O bottlenecks** appear **when** CPU is idle and QPS is modest, **yet** P99 spikes **and** threads wait on disk or network. **If** the disk is slow, adding instances may only make more workers queue on the same kind of slow storage; faster NVMe drives or more bandwidth attack the root cause. The reporting-service story fits this pattern: a background job stole disk I/O, **so** more boxes would have spread the pain rather than removed it.

**Lock contention** is similar in spirit: high P99 with threads blocked on locks usually means the bug is inside application logic. Extra machines rarely dissolve the lock; you need code changes, **or** at best vertical scaling as temporary relief.

In short: compute shortages can go either way; connection-quota ceilings need horizontal scaling; slow I/O and lock fights usually need vertical upgrades or code fixes. Adding machines is not a universal cure.

### 快速诊断表（复述）

| 瓶颈类型 | 主要症状 | 更有效的方案 | 为什么 |
| --- | --- | --- | --- |
| CPU/内存 | CPU 打满，内存溢出 | 无状态→水平；有状态→垂直 | 水平分摊计算；垂直保住本地状态 |
| 连接池 | 拿连接超时，CPU 不高 | 水平扩展 | 新实例自带连接池，抬高总配额 |
| 磁盘 I/O | P99 飙，磁盘队列长 | 垂直（换 SSD/NVMe） | 加实例可能继续抢同一类慢盘 |
| 锁竞争 | P99 高，线程堵在锁上 | 改代码（垂直仅缓冲） | 根因在应用逻辑，加机器消不掉锁 |

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| prescribe | 对症下药 | You should prescribe a fix **that** matches the bottleneck type. |
| connection timeout | 连接超时 | Connection timeouts appear **when** the pool cannot hand out a free connection. |
| OOM | 内存耗尽 | OOM happens **when** the process needs more memory **than** the machine can give. |
| disk queue | 磁盘队列 | A long disk queue is a signal **that** storage cannot keep up with requests. |
| root cause | 根因 | Vertical scaling helps only **when** it attacks the root cause, not the symptom. |
| quota ceiling | 配额上限 | A connection-pool quota is a ceiling **that** bigger CPUs cannot raise by themselves. |

### 嵌套从句练习：连接池为什么必须水平

**Layer 2：**

> **If** the logs show connection timeouts **while** CPU is idle, horizontal scaling is usually better **than** a bigger box.

**Layer 3：**

> **When** the bottleneck is the database connection pool, vertical scaling rarely helps **because** a larger machine does not automatically enlarge the pool **that** each process is allowed **to use**.

**Layer 4：**

> **Although** upgrading to a more powerful server feels like the obvious fix, connection-pool limits are a per-instance quota problem — **which** means three smaller instances, **each of which** brings its own pool, can raise total available connections far more effectively **than** one big machine **that** still hits the same configured ceiling.

**中文对照：** 虽说换更强服务器看起来像理所当然的修法，连接池上限其实是单实例配额问题——三台各自带连接池的小实例，往往比一台仍撞上同一配置天花板的大机器更能抬高总可用连接数。

### 嵌套从句练习：I/O 瓶颈别盲目加机器

**Layer 4：**

> **When** P99 climbs **while** QPS stays modest, the pain is often disk I/O **that** lives inside one machine — **a case where** moving to NVMe drives through vertical scaling is more targeted **than** adding instances **that** would only queue on the same slow storage pattern.

**中文对照：** 当 P99 往上冲而 QPS 仍不算高时，痛点往往是单机内部的磁盘 I/O——这时用垂直扩展换 NVMe 盘更对症，加实例只会让更多机器继续排队在同一类慢存储模式上。

---

## 概念 5：一致性哈希——水平扩有状态时绕不开的路由

### 用自己的话理解（中英双语）

**中文：**

一致性哈希要解决的问题很具体：节点增减时，尽量少搬数据。传统 `hash(key) % N` 在 N 一变时几乎全体洗牌；一致性哈希把节点和 key 都映射到同一个环上，key 顺时针落到下一个节点，节点加减只影响相邻一小段。

为了避免少数节点弧段过长导致倾斜，实践里常给每个物理节点挂 100–200 个虚拟节点，让分布更均匀。

放到面试对话里：有状态会话缓存一旦水平扩成多机，就必须决定「这个用户的会话落在哪台机器」——一致性哈希是常用答案。但代价也不小：客户端或代理要感知拓扑；节点宕机时若复制没跟上，会话可能丢；网络分区时不同客户端对环的认知不一致，还可能和脑裂叠在一起。

所以候选人强调：状态量还能装进一台更大内存机器时，先垂直，别急着引入这套分布式路由复杂度。

**English (B2):**

Consistent hashing exists **to keep data remapping small when the number of nodes changes**. Classic `hash(key) % N` reshuffles almost everything **whenever** N grows or shrinks. Consistent hashing places both nodes and keys on the same ring; each key walks clockwise **until** it hits the next node, **so that** adding or removing a node only moves a neighboring slice of keys.

**When** the ring is uneven, some physical nodes may own overly long arcs. Teams usually create 100–200 virtual nodes per physical machine **so that** load spreads more evenly across the ring.

In the interview story, once a stateful session cache spreads across multiple machines, you need a rule **that** decides **which** node owns each user’s session — and consistent hashing is the usual answer. The cost is real: clients or proxies must understand cluster topology; **if** a node dies before replication catches up, sessions may disappear; **and** during a network partition, different clients may see different ring views, **which** can combine with split-brain problems.

That is why the candidate prefers vertical scaling **while** the working set still fits in one larger machine: local memory avoids this whole class of distributed routing complexity.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| consistent hashing | 一致性哈希 | Consistent hashing is a scheme **that** remaps only a slice of keys **when** nodes change. |
| hash ring | 哈希环 | A hash ring is a circular space **where** both nodes and keys are placed. |
| virtual node | 虚拟节点 | Virtual nodes are replicas **that** spread one physical machine across many ring positions. |
| data remapping | 数据重映射 | Remapping is the movement of keys **that** occurs **when** the cluster membership changes. |
| topology | 拓扑 | Clients must know the topology **that** describes **which** nodes currently exist. |
| hot spot / skew | 热点 / 倾斜 | Skew happens **when** some nodes own longer arcs **than** others. |

### 嵌套从句练习：为什么需要一致性哈希

**Layer 2：**

> Consistent hashing reduces remapping **when** you add or remove cache nodes.

**Layer 3：**

> **When** the cluster size changes, consistent hashing remaps only neighboring keys, **whereas** `hash(key) % N` reshuffles almost every key **that** used to map to a different slot.

**Layer 4：**

> **Although** consistent hashing helps you place sessions across cache nodes **without** reshuffling the whole dataset, it still forces clients **to track** a ring topology **that** can drift during failures — **a complexity that** vertical scaling avoids **when** one machine can still hold the entire working set.

**中文对照：** 虽说一致性哈希能在不洗牌全部数据的前提下把会话摊到多台缓存节点，它仍逼着客户端跟踪一份故障时可能漂移的环拓扑——而只要单机还能装下整个工作集，垂直扩展就可以躲开这层复杂度。

---

## 概念 6：脑裂——网络分区后的“多重人格”

### 用自己的话理解（中英双语）

**中文：**

**脑裂（split-brain）**指的是：集群因网络故障被拆成几个互不相通的小岛，每个小岛都以为自己还活着、还该对外服务，结果多个节点同时写同一份数据，或同时抢同一把锁，最终状态分叉、难以合并。

常见场景：主从库各认自己是主；Redis 一类缓存在不同分区里独立更新同一 key；分布式锁被两个节点同时“持有”。对话里，候选人担心的正是：水平扩会话缓存后，网络分区可能让两个节点都认为某会话归自己，用户状态就乱了。

常见止血手段包括：多数派（Quorum）只让拥有多数节点的一侧继续写；用 ZooKeeper/etcd 做仲裁；fencing token 拒绝旧主复活后的写入；共享存储场景下用 STONITH 直接关掉可疑节点。核心目标只有一个：故障时尽快让多余的“人格”闭嘴。

**English (B2):**

**Split-brain** is what happens **when** a network partition cuts one cooperative cluster into islands **that** can no longer talk to each other. Each island still believes it owns the full dataset and authority, **so** multiple nodes may write the same data or grab the same lock at once — **which** produces divergent state **that** is hard to merge later.

Typical damage includes two database primaries accepting writes, cache nodes updating the same key independently in different partitions, and two processes both believing they hold a distributed lock. In the interview, the candidate worries about exactly this risk: **after** you scale a session cache horizontally, a partition may leave two nodes convinced **that** they own the same session.

Common defenses include quorum writes **that** only succeed on the majority side, an external arbiter such as ZooKeeper or etcd, fencing tokens **that** reject writes from a stale primary, and STONITH-style node fencing on shared storage. The goal is simple: **when** the cluster splits, make the extra “personality” shut up quickly.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| split-brain | 脑裂 | Split-brain is a failure **where** two sides both believe they are still in charge. |
| network partition | 网络分区 | A network partition is a break **that** stops nodes from exchanging heartbeats. |
| quorum | 多数派 | Quorum requires a majority of nodes **before** a write is accepted. |
| fencing token | 隔离令牌 | A fencing token is a number **that** storage checks **before** it accepts a write. |
| arbiter | 仲裁者 | An arbiter is a third party **that** decides **which** node may become primary. |
| diverge | 分叉 | Data diverges **when** two primaries accept different writes for the same record. |

### 嵌套从句练习：解释脑裂

**Layer 2：**

> Split-brain happens **when** two nodes both believe **that** they own the same session.

**Layer 3：**

> **When** a network partition breaks heartbeats, each side may keep serving traffic **as if** it still owns the cluster, **which** can produce conflicting writes.

**Layer 4：**

> **Although** a distributed session cache can scale horizontally, a partition may leave two nodes convinced **that** they own the same login session — **a split-brain failure that** vertical scaling avoids **while** state still fits on one machine, **because** there is only one local owner **that** can update the cache.

**中文对照：** 虽说分布式会话缓存能水平扩展，网络分区可能让两个节点都坚信自己拥有同一登录会话——这正是垂直扩展在状态仍装得进单机时能躲开的脑裂：本地只有一个所有者能改缓存。

### 嵌套从句练习：怎么防脑裂

**Layer 4：**

> Teams fight split-brain with quorum rules **that** allow only the majority side **to accept writes**, or with an external arbiter **that** grants leadership to one node, **so that** a minority partition cannot keep writing data **that** would later diverge from the rest of the cluster.

**中文对照：** 团队用多数派规则只让多数侧继续写，或用外部仲裁把领导权交给一个节点，从而阻止少数分区继续写入那些之后会和集群其余部分分叉的数据。

---

## 课堂对话套路（B2 + 嵌套从句）

### 套路 1：老师问"5000 到 15000 QPS 你怎么扩"

> **When** peak traffic jumps from 5,000 to 15,000 QPS, I first check **where** the bottleneck is. **If** it is CPU or memory, I would upgrade the box through vertical scaling, **which** is the fastest path **that** needs no code changes. **But if** the service is stateless **and** the limit is the connection pool, I would add instances behind a load balancer, **because** horizontal scaling is more flexible **and** cheaper **after** the promotion ends.

---

### 套路 2：老师问"什么时候不用垂直扩展"

> For stateless services, **which** do not need **to synchronize data between** instances, horizontal scaling is the natural fit — **a case where** I would avoid vertical scaling **because** adding machines lets throughput grow almost linearly. **Conversely**, **when** the service is stateful **and** keeps sessions in an in-memory cache, I lean toward vertical scaling first, **so that** state stays local **and** I do not introduce distributed complexity **that** horizontal scaling would require.

---

### 套路 3：老师问"有状态服务能不能水平扩"

> You can, **and** a distributed cache is the usual horizontal solution, **but** it forces you **to handle** consistent hashing or replication **that** adds latency **and** risks split-brain, **where** two nodes both think **that** they own the same session. **That is why** I only go horizontal **when** one machine cannot hold the working set **that** the service needs **to run efficiently**.

---

### 套路 4：老师问"看 QPS 还是看延迟"

> I look at both, **because** they answer different questions. QPS tells you **whether** you need **to scale at all** — for example, **when** CPU is pegged **and** QPS plateaus, you have hit a capacity limit. P99 latency tells you **how** **to scale**: **if** QPS is fine **but** P99 jumps from 50 ms to 300 ms, the pain is likely inside one box, **which** points toward vertical scaling rather than adding more instances **that** would not fix a slow disk.

---

### 套路 5：老师问"举个真实例子"

> We once had a reporting service **whose** QPS looked healthy during peak hours, **but** P99 latency spiked **because** a background job on the same machine competed for disk I/O with online reads. **After** we moved to a server with NVMe drives — vertical scaling — the problem disappeared, **whereas** more instances would only have spread the same contention **across** boxes **that** still suffered from slow storage.

---

### 套路 6：老师问"连接池瓶颈怎么扩"

> **When** logs show connection timeouts **while** CPU stays low, the bottleneck is usually a per-instance quota, not raw compute. A bigger machine rarely helps **because** the pool ceiling does not grow with hardware, **whereas** three smaller instances, **each of which** brings its own pool, can raise total available connections almost linearly.

---

### 套路 7：老师问"一致性哈希是什么 / 脑裂是什么"

**一致性哈希：**
> Consistent hashing places keys and nodes on a ring **so that** adding or removing a node remaps only a neighboring slice of data, **whereas** `hash(key) % N` reshuffles almost everything **when** the cluster size changes.

**脑裂：**
> Split-brain is a failure mode **where** a network partition leaves two sides both believing **that** they still own the same resource — **which** is exactly the risk **that** appears **when** you horizontally scale a stateful session cache **without** strong ownership rules.

---

### 套路 8：课上主动说话

| 你想做什么 | 嵌套从句版 |
| --- | --- |
| 确认理解 | So for stateless services, horizontal scaling is preferred **because** instances do not need **to share state**, **right**? |
| 请老师举例 | Could you give an example **where** P99 latency rises **even though** QPS still looks fine? |
| 表示同意 | That makes sense — P99 shows pain **that** averages hide, **which** is why latency guides the scaling direction. |
| 提出疑问 | **But** wouldn't vertical scaling eventually hit a hardware ceiling **that** horizontal scaling could overcome? |
| 追问指标 | **When** QPS plateaus, does that always mean we need more machines, **or** could it be an internal bottleneck **that** vertical scaling would fix? |
| 追问选型 | **If** the bottleneck is the connection pool, why is horizontal scaling better **than** buying a bigger box? |
| 追问分布式代价 | What complexity does consistent hashing add **when** we spread sessions across cache nodes? |

---

## 常用句式：嵌套从句版（改写，非原文）

| 功能 | 嵌套从句句式 |
| --- | --- |
| 对比两种扩展 | **If** the bottleneck is CPU or memory, I would scale vertically; **whereas** **if** the service is stateless, I would add instances **that** sit behind a load balancer. |
| 说无状态优势 | Stateless services do not need **to synchronize data**, **which** is why horizontal scaling often increases throughput almost linearly. |
| 说有状态权衡 | **Although** distributed caches enable horizontal scaling, they introduce complexity **that** vertical scaling avoids **when** state can stay on one machine. |
| 区分两个指标 | QPS tells you **whether** you need **to scale**, **whereas** P99 latency reveals the bottleneck type **that** tells you **which direction** **to choose**. |
| 诊断单机瓶颈 | **When** P99 spikes **but** QPS is still comfortable, the problem is likely inside one instance, **which** more boxes will not fix. |
| 按瓶颈选型 | **When** the limit is a connection-pool quota, horizontal scaling works **because** each new instance brings a pool **that** a bigger CPU alone cannot enlarge. |
| 解释一致性哈希 | Consistent hashing remaps only neighboring keys **when** nodes change, **whereas** modulo hashing reshuffles almost every key. |
| 解释脑裂 | Split-brain happens **when** two partitions both believe **that** they own the same session, **which** vertical local state can avoid. |
| 总结指标关系 | QPS is the symptom **that** shows traffic pressure; latency is the diagnosis **that** points to the real bottleneck. |

---

## 老师可能追问 — 嵌套从句回答

| 老师问 | 你可以答 |
| --- | --- |
| Vertical vs horizontal? | Vertical scaling upgrades one machine **that** already runs the service, **whereas** horizontal scaling adds instances **that** share load through a balancer — **each approach fits a different bottleneck**. |
| Why horizontal for stateless? | **Because** stateless instances do not share local state, you can add machines **that** handle requests independently, **which** lets throughput grow almost linearly. |
| Why vertical for stateful? | **Because** keeping state local avoids consistent hashing and split-brain risks **that** appear **when** you spread sessions across nodes. |
| QPS vs P99? | QPS shows **whether** you are near capacity, **while** P99 shows **where** the slowest requests hurt — **often revealing** lock or I/O problems **that** averages hide. |
| Connection-pool bottleneck? | Horizontal wins **because** each new instance brings its own pool, **whereas** a bigger machine still hits the same configured ceiling. |
| I/O bottleneck? | **When** P99 spikes from slow disks, vertical upgrades such as NVMe are more targeted **than** instances **that** would keep queueing on the same storage pattern. |
| What is consistent hashing? | It is a ring-based mapping **that** moves only a slice of keys **when** nodes are added or removed, **unlike** `hash % N`, **which** reshuffles almost everything. |
| What is split-brain? | It is a failure mode **where** two nodes both believe **that** they own the same session, **which** can happen **when** state is replicated **without** clear ownership rules. |
| What is working set? | It is the set of data **that** must stay in memory **for** the service **to respond quickly** — **if** one machine cannot hold it, you must go horizontal or shard. |
| NVMe example? | The reporting service had healthy QPS **but** high P99 **because** a background job competed for disk I/O; NVMe drives fixed it **because** vertical scaling targeted the real bottleneck. |

---

## 跟读练习：六段 B2 嵌套从句（课前朗读 2 遍）

**Part 1 — 垂直 vs 水平**

> **When** peak traffic jumps from 5,000 to 15,000 QPS, the right choice depends on **where** the bottleneck sits. **If** CPU or memory is the limit, vertical scaling — upgrading to a larger machine — is often the fastest fix **that** needs no code changes. **But if** the service is stateless **and** the connection pool is the constraint, horizontal scaling is more flexible, **because** you can add instances behind a load balancer **and** remove them **after** the promotion ends.

**Part 2 — 有状态 vs 无状态**

> Stateless services, **which** do not need **to synchronize data between** instances, are a natural fit for horizontal scaling — **a pattern in which** throughput grows almost linearly **as** you add machines. Stateful services, **such as** those **that** keep login sessions in an in-memory cache, often start with vertical scaling, **because** local state is faster **and** avoids the complexity of consistent hashing or split-brain **that** distributed caches introduce.

**Part 3 — QPS 与 P99**

> QPS tells you **whether** you need **to scale at all**: **when** CPU is pegged **and** QPS plateaus, you have hit a capacity limit. P99 latency, on the other hand, tells you **how** **to scale**. **If** QPS still looks fine **but** P99 jumps from 50 ms to 300 ms, the problem is likely inside one instance — lock contention or disk I/O — **which** means vertical scaling with faster storage or more memory is more targeted **than** adding boxes **that** copy the same bottleneck.

**Part 4 — 按瓶颈选型**

> Different bottlenecks need different prescriptions. Connection-pool exhaustion favors horizontal scaling **because** each new instance brings a pool **that** a larger CPU cannot enlarge by itself. Disk I/O pain often favors vertical upgrades such as NVMe, **whereas** lock contention usually needs code changes, **not** more machines **that** still execute the same contended path.

**Part 5 — 一致性哈希与脑裂**

> **When** you spread sessions across cache nodes, consistent hashing decides ownership **so that** node changes remap only a neighboring slice of keys. The trade-off is topology awareness, failover inconsistency, and split-brain risk — **a set of costs that** vertical scaling avoids **while** one machine can still hold the working set.

**Part 6 — 案例与总结**

> We once ran a reporting service **whose** QPS looked healthy during peak hours, **but** P99 spiked **because** a background job competed for disk I/O with online reads. **After** we moved to a machine with NVMe drives through vertical scaling, latency returned to normal, **whereas** more instances would only have spread the same contention. **That** is why I say QPS is the symptom **that** shows traffic pressure, **and** latency is the diagnosis **that** reveals **which scaling direction** actually fixes the pain.

---

## 附录：嵌套从句工具箱

| 从句类型 | 常用引导词 | 练法 |
| --- | --- | --- |
| **定语从句（限定）** | that, which, who, whose, where | 修饰名词：*instances **that** share no state* |
| **定语从句（非限定）** | , which / , who | 补充信息：*…horizontal scaling, **which** is more flexible* |
| **时间 / 条件状语** | when, if, after, before | ***When** P99 spikes, check disk I/O* |
| **原因 / 结果状语** | because, since, so that | *…scale vertically **because** state stays local* |
| **对比 / 让步状语** | although, whereas, while | ***Although** caches can scale out, they add complexity* |
| **嵌套技巧** | 从句套从句 | 主句 → 定语从句里再套 that/when/which |

**拆句口诀：** 先找主句主干 → 标出每个 that/which/when/because 引导的从句 → 从外往里读 → 再试着合并回去。

---

**课前最少记：** 5000 → 15000 QPS · 垂直 = 升配单机 / 水平 = 加实例 + 负载均衡 · 无状态先水平，有状态先垂直 · 连接池→水平；I/O/锁→垂直或改代码 · 一致性哈希少搬数据但引入拓扑与脑裂风险 · P99 50ms → 300ms = 查单机瓶颈 · 报表服务 + NVMe 案例 · *QPS is the symptom; latency is the diagnosis.*
