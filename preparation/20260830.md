这份预习材料**不用 material 原文**，概念全部用自己的话复述。每个概念的「用自己的话理解」提供**中英双语**（英文按 **B2**）。长句练习的重点是**嵌套从句**——定语从句、状语从句、非限制性从句叠在一起练。

---

## 课前 3 分钟：今天讲什么

**话题：** 多主复制——跨地域电商怎么在延迟、可用性和冲突之间做取舍。

**故事线：**

```
单主痛（300ms 跨海 + 主库挂了全球瘫） → 多主爽（10ms 本地写 + 故障隔离）
→ 但引入冲突 → 按冲突概率分层（有主数据按 user ID 路由 / 共享数据单写）
→ 路由层把复杂度藏起来
```

**关键数字：**

| 数字 | 含义 |
|---|---|
| 300ms | 新加坡写入跨海到北京主库的延迟 |
| < 10ms | 多主方案下写入本地主库的延迟 |
| ≥ 20% | A/B 测试里转化率下降的幅度 |
| 99.99% / 52 分钟 | SLA / 全年允许的停机总时长 |
| 30 秒 | 单主故障切换至少需要的停机时间（烧掉一半以上年度预算） |

**核心规律一句话：** 数据按"冲突概率"分层——有主数据用多主，共享数据用单写，路由层把复杂度藏起来，让应用层无感知。

---

## 概念 1：300ms 为什么不能忍

### 用自己的话理解（中英双语）

**中文：**

单主复制的结构简单：全世界只有一个主库，所有写入都得先到它那里。业务只在中国时没问题，可一旦新加坡用户也要下单，每次写入就得跨海到北京主库，平均 300ms。

300ms 听起来不多，但用户点"下单"后，前端还有加载、渲染、确认等一堆步骤，加在一起转圈要三秒。他们做过 A/B 测试，转化率掉至少 20%——也就是说，延迟不只是技术指标，它直接变成业务损失。

更糟的是大促：并发一高，跨海链路只要抖一下，整个东南亚都下不了单。这就是单主在跨地域场景下的两个核心痛点：**写入延迟高**，以及**主库故障时全局不可用**。

**English (B2):**

Single-master replication is simple **because** there is only one master, **which** every write has to reach first. **While** this works fine **when** all users are in one country, it becomes painful **once** Singapore users start placing orders, **because** every write must travel across the ocean to the Beijing master, **which** adds about 300ms of latency on average.

Although 300ms sounds small, the user **who** clicks "place order" actually waits three full seconds overall, **because** the front end still has rendering and confirmation steps **that** come after the write. Their A/B tests showed a conversion drop of at least 20% — **which** proves **that** latency is not just a technical metric **but** a direct business loss.

The situation gets worse **during** peak sales: **when** concurrency goes up, a single network hiccup on that cross-ocean link can block the entire Southeast Asia region. That is **why** single-master replication has two core problems in a cross-region scenario: high write latency, and global unavailability **when** the master fails.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
|---|---|---|
| write latency | 写入延迟 | Write latency is the time **that** a write takes **before** the user sees the result. |
| cross-region | 跨地域 | Cross-region writes are requests **that** must travel between data centers in different regions. |
| conversion rate | 转化率 | The conversion rate is a business metric **that** drops when users wait too long. |
| peak sales | 销售高峰 | During peak sales, the traffic **that** hits the link is many times higher. |
| network hiccup | 网络抖动 | A network hiccup is a brief problem **that** can make the whole region fail. |
| hard requirement | 硬性要求 | Low latency became a hard requirement **after** the A/B test showed a 20% drop. |

### 嵌套从句练习：说 300ms 为什么不行

**Layer 0 — 主句：**
> Cross-region writes cost about 300ms per order.

**Layer 1 — 加定语从句 (which)：**
> Cross-region writes, **which** go over an undersea link, cost about 300ms per order.

**Layer 2 — 加条件/时间状语 (when)：**
> **When** users in Singapore place an order, every write crosses the ocean to the Beijing master, **which** adds about 300ms of latency.

**Layer 3 — 加原因从句 + 非限制性从句：**
> **Because** all traffic crosses the ocean to the Beijing master, users in Singapore wait about 300ms on every order, **which** hurts the conversion rate by at least 20% **according to** our A/B tests.

**Layer 4 — 完整嵌套版：**
> **Although** 300ms sounds small, a user **who** clicks "place order" waits three full seconds overall, **which** is **why** our A/B tests show a conversion drop of at least 20%, **and** that is **why** multi-master replication, **which** lets users write to a local master, becomes a hard requirement.

**中文对照：** 虽说 300ms 听起来不多，但点"下单"的用户整体要等三秒，这就是为什么 A/B 测试显示转化率至少掉 20%，也是为什么让用户写本地主库的多主复制成了硬性要求。

### 嵌套从句练习：说单主的全局故障

**Layer 3：**
> **If** the Beijing master fails, a single-master setup needs a failover **that** takes at least 30 seconds, **during which** the whole system is unavailable.

**Layer 4 — 完整嵌套版：**
> **When** the master fails in a single-master setup, every region **that** depends on it goes down together, **because** there is no other master **that** can serve writes, **which** is **why** the second pain point is global unavailability rather than just slow writes.

**中文对照：** 单主架构下主库故障时，所有依赖它的地域会一起停摆，因为没有其他主库能承接写入，这就是为什么第二个痛点是全局不可用而不只是写入慢。

---

## 概念 2：冲突概率怎么分类

### 用自己的话理解（中英双语）

**中文：**

多主复制最大的新问题是**写入冲突**：两个主库同时改同一条数据，结果以谁为准？但候选人没有笼统地说"冲突概率高"，而是按数据的归属特性分类。

**第一类：有主数据**（订单、用户资料）。每一行数据都明确属于一个用户。按用户 ID 路由——东南亚用户的订单永远写新加坡主库，中国用户的订单永远写北京主库——同一个用户的数据永远不会在两个主库上并发写，冲突概率趋近于零。这是多主能安全落地的关键前提。

**第二类：共享数据**（库存、优惠券）。两个地域的用户可能同时抢最后一件商品。这类数据**不搞多主写**：指定一个主库（如北京）作为唯一写入者，另一个主库只读。这不是事后修补冲突，而是从源头消灭冲突。代价是共享数据的写入仍有跨地域延迟，但这是为保证数据正确性必须付的。

**English (B2):**

The biggest new problem **that** multi-master introduces is write conflicts — **when** two masters modify the same record at the same time, **whose** result should win? The candidate does not just say "the probability is high"; instead, he classifies data by its ownership characteristics.

**The first category is owner-specific data**, such as orders and user profiles, **where** every row clearly belongs to one user. **If** we route by user ID — Southeast Asian users always write to the Singapore master, **while** Chinese users always write to the Beijing master — the same user's data is never written on two masters at the same time, **which** pushes the conflict probability **for** order and user tables close to zero. This is the key precondition **that** makes multi-master safe to adopt.

**The second category is shared data**, such as inventory and coupons, **which** users in two regions may compete for at the same time. For this kind of data, we do **not** use multi-master writes at all: we designate one master, for example the one in Beijing, as the sole writer, **and** the other master only serves reads. This does not patch conflicts afterwards — it eliminates them at the source. The cost is **that** shared-data writes still cross regions, **which** is the price we pay **so that** the data stays correct.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
|---|---|---|
| conflict probability | 冲突概率 | Conflict probability is the chance **that** two masters modify the same record. |
| user-based routing | 按用户路由 | User-based routing sends each write to the master **where** that user belongs. |
| owner-specific data | 有主数据 | Owner-specific data is information **that** clearly belongs to one user. |
| shared data | 共享数据 | Shared data is a resource **that** many users may update at the same time. |
| sole writer | 唯一写入者 | We designate one master as the sole writer **so that** conflicts cannot happen. |
| eliminate at the source | 从源头消除 | The strategy eliminates conflicts at the source **instead of** patching them later. |
| overselling | 超卖 | An inventory miscount leads to overselling, **which** causes complaints and refunds. |

### 嵌套从句练习：讲有主数据按用户 ID 路由

**Layer 1：**
> If we route orders by user ID, the same user's data never lands on two masters.

**Layer 2 — 加定语从句 (which)：**
> If we route orders by user ID, **which** is a natural ownership attribute, the same user's data never lands on two masters, **so** conflict probability drops to near zero.

**Layer 3 — 加对比从句 (whereas)：**
> **Because** orders are owner-specific data, we can route them by user ID **so that** Southeast Asian users always write to the Singapore master, **whereas** Chinese users always write to the Beijing master, **which** means the same user's data never conflicts across masters.

**Layer 4 — 完整嵌套版：**
> **When** we classify data by conflict probability, owner-specific tables such as orders and user profiles, **whose** records belong to a single user, can be pinned to a region through user-based routing, **which** ensures **that** no user's record is ever written on two masters at the same time, **whereas** shared resources such as inventory, **which** two regions may update concurrently, need a different strategy.

**中文对照：** 当我们按冲突概率给数据分类时，订单、用户资料这类行属于单一用户的有主表，可以通过按用户路由钉在某个地域，确保同一个用户的记录永远不会同时写在两个主库上；而库存这类两个地域可能并发更新的共享资源，则需要另一套策略。

### 嵌套从句练习：讲共享数据回归单写

**Layer 2：**
> For shared data like inventory, we designate one master as the sole writer, **so** the other master only serves reads.

**Layer 3：**
> **Although** the conflict probability for inventory is small, the consequence is serious, **because** a miscount leads to overselling, **which** causes customer complaints and refunds, **so** we prefer a single writer.

**Layer 4 — 完整嵌套版：**
> **Because** two users **who** sit on different masters could both target the last item in stock, we avoid multi-master writes for shared data entirely: instead, we designate one master as the sole writer **while** the other master only serves reads, **which** eliminates conflicts at the source **rather than** patching them afterwards, **even though** shared-data writes still cross regions.

**中文对照：** 因为分处两个主库的用户可能同时抢最后一件库存，我们干脆不对共享数据做多主写：指定一个主库为唯一写入者，另一个主库只读，这样是从源头消灭冲突而不是事后修补，尽管共享数据的写入仍然要跨地域。

---

## 概念 3：故障域隔离与 SLA

### 用自己的话理解（中英双语）

**中文：**

多主复制的第二个大收益是**可用性**。单主架构下，北京主库一挂，所有人都要等故障切换——至少 30 秒不可用。而多主方案下，北京挂了，新加坡主库还在服务，东南亚用户完全无感。

为什么这事重要？因为他们的 SLA 是 99.99%，全年只能停 52 分钟。一次 30 秒的故障切换，就烧掉一半以上的年度预算。单主架构里一次故障就能把一整年的可用性指标打残。

多主的本质是把**故障域**按地域隔开：北京的故障影响不到新加坡。全球性故障被转化成局部可控事件——这是可用性上的质的飞跃。这也是为什么 30 秒的 RTO 对多主方案来说几乎可以忽略：另一个地域的写入根本没停下来过。

**English (B2):**

The second major benefit of multi-master is **availability**. In a single-master setup, **when** the Beijing master fails, everyone has to wait for a failover **that** takes at least 30 seconds, **during which** writes are simply lost to users. With multi-master, **when** Beijing goes down, the Singapore master keeps serving traffic, **so** Southeast Asian users do not notice anything.

This matters **because** their SLA is 99.99%, **which** allows only 52 minutes of downtime per year. A single 30-second failover burns more than half of that yearly budget in one incident — **which** means **that**, in a single-master architecture, one outage can cripple the availability target for the whole year.

The essence of multi-master is **that** it isolates the failure domain by region: a Beijing failure has zero impact on Singapore. A global failure **that** used to affect everyone becomes a local, controllable event — **which** is a qualitative leap **for** high availability. That is also **why** a 30-second RTO becomes almost irrelevant here: the other region's writes never stopped at all.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
|---|---|---|
| failover | 故障切换 | Failover is the process **when** a backup node takes over after the primary fails. |
| downtime | 停机时间 | Downtime is the period **during which** the service is unavailable. |
| SLA | 服务等级协议 | The SLA is a promise **that** defines how much downtime is allowed. |
| failure domain | 故障域 | A failure domain is a boundary **within which** a fault can spread. |
| high availability | 高可用 | High availability is the ability **that** keeps a service running **even when** part of it fails. |
| isolated | 隔离的 | The failure domain is isolated, **which** means one region cannot affect another. |

### 嵌套从句练习：用 SLA 数字说话

**Layer 1：**
> Our SLA is 99.99%, which allows 52 minutes of downtime per year.

**Layer 2 — 加结果从句 (so)：**
> Our SLA is 99.99%, **which** allows only 52 minutes of downtime per year, **so** a single 30-second failover burns more than half of that budget.

**Layer 3 — 加原因从句 (because) + 定语从句：**
> **Because** our SLA is 99.99%, **which** means only 52 minutes of downtime per year, a single 30-second failover, **which** we cannot avoid in a single-master setup, consumes more than half of the yearly budget in one incident.

**Layer 4 — 完整嵌套版：**
> **When** the Beijing master fails in a single-master setup, we need a failover **that** takes at least 30 seconds, **which** burns more than half of our 52-minute yearly budget, **whereas** in a multi-master setup the Singapore master keeps serving traffic **because** the failure domain is isolated, **which** is **why** the availability gain feels like a qualitative leap.

**中文对照：** 单主架构下北京主库故障时，我们需要至少 30 秒的故障切换，这烧掉我们 52 分钟年度预算的一半以上；而多主方案下，因为故障域被隔离，新加坡主库继续服务，这就是为什么可用性提升感觉像是质的飞跃。

### 嵌套从句练习：解释故障域隔离

**Layer 3：**
> With multi-master, a failure in Beijing is isolated, **so** it cannot spread to Singapore, **where** users keep writing and reading normally.

**Layer 4 — 完整嵌套版：**
> **Although** a single-master architecture treats all regions as one failure domain, multi-master splits them by geography, **so** **when** the Beijing master goes down, users **who** belong to Southeast Asia continue to work on the Singapore master, **which** turns a global outage **that** would have affected everyone into a local event **that** no one in the other region even notices.

**中文对照：** 单主架构把整个系统当作一个故障域，而多主按地域把它拆开，所以当北京主库宕机时，归属东南亚的用户继续在新加坡主库上工作——这会把原本波及所有人的全球性故障，变成另一个地域的人完全感知不到的局部事件。

---

## 概念 4：混合路由层怎么落地

### 用自己的话理解（中英双语）

**中文：**

方案定了：有主数据走多主、共享数据走单写。但应用层怎么知道该走哪条路？如果每个业务团队都自己写路由判断，很快会乱套。

候选人的答案是**集中路由层**：放在数据访问服务里。每次写入时，它检查目标表和用户上下文，自动决定——有主数据按用户 ID 路由到所属地域主库，共享数据路由到指定的单一写主库。

对应用层来说，一切透明：业务代码只需要调用 `write(data, userContext)`，不用关心数据最终落到哪里。核心价值是把分布式复杂性限制在一个可管理的边界内——既拿到多主的低延迟和高可用，又保证共享数据的强一致性，还让开发者保持生产力。

**English (B2):**

The strategy is clear: owner-specific data goes multi-master, **while** shared data goes single-writer. But **how** does the application layer know **which** path to take? **If** every business team wrote its own routing logic, things would quickly fall apart.

The candidate's answer is a **centralized routing layer**, placed inside the data access service. On every write, it inspects the target table and the user context **and** then decides automatically: owner-specific data is routed by user ID to the master **where** the user belongs, **while** shared data is routed to the designated single writer.

For the application layer, everything is transparent: business code simply calls `write(data, userContext)`, **without** caring **where** the data finally lands. The core value is **that** the routing layer keeps distributed complexity inside one manageable boundary — **so that** the team gets multi-master's low latency and high availability, keeps strong consistency for shared data, **and** developers stay productive.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
|---|---|---|
| routing layer | 路由层 | The routing layer is the component **that** decides where each write goes. |
| data access service | 数据访问服务 | The data access service is the place **where** the routing logic lives. |
| user context | 用户上下文 | The routing layer reads the user context, **which** tells it which region owns the user. |
| centralized | 集中的 | The logic is centralized, **which** means one place controls all routing decisions. |
| manageable | 可管理的 | The complexity stays manageable **because** it lives inside one boundary. |
| transparent | 透明的 | The routing is transparent to developers, **who** do not see the distributed rules. |

### 嵌套从句练习：讲路由层

**Layer 1：**
> We build a routing layer that decides where each write goes.

**Layer 2 — 加目的从句 (so that)：**
> We build a routing layer **that** inspects the table and the user context on every write, **so that** the application code does not need to know the routing rules.

**Layer 3 — 加非限制性从句 (which)：**
> We build a lightweight routing layer in the data access service, **which** inspects the table and the user context on each write and then decides **whether** to follow multi-master routing **or** to stick to the designated single master, **so that** the application just calls `write(data, userContext)`.

**Layer 4 — 完整嵌套版：**
> **To keep** the hybrid approach workable, we build a centralized routing layer **whose** job is to inspect the table and the user context on every write, **after which** it decides between the multi-master path **and** the single designated master, **so that** application developers, **who** should not care about distributed complexity, can simply call `write(data, userContext)` **without** worrying about **where** the data actually lands.

**中文对照：** 为了让混合方案能落地，我们建一个集中的路由层，它的职责是检查每次写入的目标表和用户上下文，然后决定走多主路径还是指定的单主，这样那些本不该关心分布式复杂性的应用开发者，只需调用 `write(data, userContext)`，不必操心数据最终落到哪里。

---

## 课堂对话套路（B2 + 嵌套从句）

### 套路 1：老师问"为什么不能用单主 / 300ms 能接受吗"

> **Although** 300ms may sound acceptable on paper, a user **who** clicks "place order" actually waits three full seconds, **which** is **why** our A/B tests show a conversion drop of at least 20%, **so** multi-master replication, **which** lets users write to a local master, becomes a hard requirement **for** our business.

---

### 套路 2：老师问"多主引入了冲突，怎么办"

> I think we should distinguish data by conflict probability. Owner-specific data such as orders can be routed by user ID, **which** means the same user's record never lands on two masters, **whereas** shared data such as inventory still needs a different treatment, **because** users in two regions could compete for the same resource.

---

### 套路 3：老师问"库存这种共享数据怎么办"

> For shared data like inventory, **where** two users on different masters could both buy the last item at the same time, I would not use multi-master at all; instead, I would designate one master as the sole writer **while** the other only serves reads, **which** eliminates conflicts at the source **rather than** patching them afterwards.

---

### 套路 4：老师问"可用性怎么提升 / 你们的 SLA 是多少"

> Our SLA is 99.99%, **which** allows only 52 minutes of downtime per year, **so** a single 30-second failover would burn more than half of that budget; with multi-master, however, the failure domain is isolated, **which** means Beijing going down has zero impact on Singapore, **because** the Singapore master keeps serving traffic.

---

### 套路 5：老师问"混合方案怎么落地，应用层不晕吗"

> We plan to build a lightweight routing layer in the data access service, **which** inspects the table and the user context on each write and then decides **whether** to follow multi-master routing **or** to use the designated single master, **so that** the application code stays simple and developers **who** write business logic never see the distributed rules.

---

### 套路 6：课上主动说话

| 你想做什么 | 嵌套从句版 |
|---|---|
| 确认理解 | So the key point is **that** we classify data by conflict probability, and only owner-specific data **that** belongs to one user is safe for multi-master writes, **right**? |
| 请老师举例 | Could you give an example of shared data **that** two regions might update at the same time, **which** would then cause a conflict? |
| 表示同意 | That makes sense, **because** inventory is a resource **that** many users may target simultaneously, **which** is **why** a single writer is safer. |
| 提出疑问 | **But** wouldn't the routing layer become a single point of failure **if** it inspects every write **that** the application sends? |
| 问 SLA | How do we measure availability in a multi-region setup **when** each region has its own master **that** serves local users? |

---

## 常用句式：嵌套从句版（改写，非原文）

| 功能 | 嵌套从句句式 |
|---|---|
| 说延迟不可接受 | 300ms is unacceptable to us **because** a user **who** clicks "place order" waits three full seconds, **which** drops our conversion rate by at least 20%. |
| 区分数据 | We classify data by conflict probability, **so** owner-specific tables, **whose** records belong to one user, can be routed locally, **whereas** shared resources cannot. |
| 按用户路由 | **If** we route orders by user ID, the same user's data never lands on two masters, **which** reduces conflicts to near zero. |
| 共享数据单写 | For shared data such as inventory, we designate one master as the sole writer, **which** eliminates conflicts at the source **instead of** patching them. |
| 用 SLA 说话 | **Because** our SLA allows only 52 minutes of downtime per year, a single 30-second failover, **which** we cannot avoid in a single-master setup, is simply too expensive. |
| 说故障隔离 | With multi-master, the failure domain is isolated by region, **which** means **that** a Beijing outage has zero impact on Singapore users. |
| 说路由层 | The routing layer centralizes the write path decision **so that** application developers, **who** should not care about distributed complexity, just call `write(data, userContext)`. |

---

## 老师可能追问 — 嵌套从句回答

| 老师问 | 你可以答 |
|---|---|
| 300ms 真的不可接受吗？ | Yes, **because** the conversion rate, **which** is a core business metric, drops by at least 20% **when** users **who** place orders have to wait three seconds. |
| 为什么按用户 ID 路由能减少冲突？ | **Because** every order belongs to a single user, and **if** we route by user ID, that user's writes always go to the same master, **which** means the same record is never modified on two masters at the same time. |
| 库存冲突的概率不是很小吗？ | The probability is small, **but** the consequence is serious, **because** an inventory miscount leads to overselling, **which** causes customer complaints and refunds **that** we cannot afford. |
| 多主怎么提升可用性？ | **Because** the failure domain is isolated by region, a Beijing master failure does not affect Singapore, **whereas** a single-master setup would need a failover **that** takes at least 30 seconds. |
| 应用层怎么感知路由规则？ | It does not, **because** we centralize the logic in a routing layer **that** inspects the table and user context, **so** the application just calls `write(data, userContext)` **without** knowing the rules. |
| RTO 能接受多长？ | With multi-master, our RTO is effectively zero for the other region, **because** Singapore keeps serving traffic **even when** Beijing is down, **whereas** single-master would cost us at least 30 seconds of downtime. |

---

## 跟读练习：五段 B2 嵌套从句（课前朗读 2 遍）

**Part 1 — 单主的痛点**

> **Although** single-master replication is simple and safe, it becomes painful **when** the business goes global, **because** every write from Singapore has to cross the ocean to the Beijing master, **which** adds about 300ms of latency on each order. **During** peak sales, a single network hiccup on that link can block the whole Southeast Asia region, **which** is **why** the team started to look for a different architecture.

**Part 2 — 多主的收益与新问题**

> Multi-master replication solves both problems at once: users write to a local master, **which** cuts latency from 300ms to under 10ms, and **if** one master fails, the other region keeps serving traffic. **However**, it introduces a new problem, **which** is write conflicts, **because** two masters could modify the same record at the same time **unless** we route carefully.

**Part 3 — 按冲突概率分层**

> The way we handle conflicts is to classify data by conflict probability. Owner-specific data such as orders and user profiles can be pinned to a region through user-based routing, **which** means the same user's record never lands on two masters. Shared data such as inventory and coupons, **which** users in different regions may update at the same time, should go back to a single designated writer, **so that** conflicts are eliminated at the source **rather than** patched afterwards.

**Part 4 — 可用性与 SLA**

> Availability is another reason we chose multi-master, **because** our SLA is 99.99%, **which** allows only 52 minutes of downtime per year. In a single-master setup, a failover takes at least 30 seconds, **which** burns more than half of that budget in one incident, **whereas** multi-master isolates the failure domain, **so** Beijing going down has zero impact on Singapore.

**Part 5 — 路由层落地**

> **To make** the hybrid approach work **without** confusing the application layer, we build a lightweight routing layer in the data access service, **which** inspects the table and the user context on each write and then decides **whether** to follow the multi-master rule **or** to use the designated single master. The application code just calls `write(data, userContext)`, **because** the routing logic is centralized and manageable, **which** keeps the complexity inside one boundary **and** the developers happy.

---

## 附录：嵌套从句工具箱

| 从句类型 | 常用引导词 | 练法 |
|---|---|---|
| **定语从句（限定）** | that, which, who, whose, where | 修饰名词：*a user **who** clicks "place order"* |
| **定语从句（非限定）** | , which / , who | 补充信息：*…52 minutes, **which** is half the budget* |
| **时间 / 条件状语** | when, before, after, if, unless | *When the Beijing master fails, …* |
| **原因 / 结果状语** | because, since, so that | *…hard **because** every write crosses the ocean* |
| **对比 / 让步状语** | although, whereas, while | *Although 300ms sounds small, …* |
| **嵌套技巧** | 从句套从句 | 主句 → 定语从句里再套 that/when/which |

**拆句口诀：** 先找主句主干 → 标出每个 that/which/when/because 引导的从句 → 从外往里读 → 再试着合并回去。

---

**课前最少记：** 300ms → <10ms · 转化率 −20% · 99.99% = 52 分钟，一次 30 秒切换烧掉一半 · 有主数据按 user ID 路由、共享数据单写 · 路由层集中复杂度 · *Data is routed by conflict probability: owner-specific data goes multi-master, shared data goes single-writer.*
