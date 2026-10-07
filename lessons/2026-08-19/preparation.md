这份预习材料**不用 material 原文**，概念全部用自己的话复述。每个概念的「用自己的话理解」提供**中英双语**（英文按 **B2**）。长句练习的重点是**嵌套从句**——定语从句、状语从句、非限制性从句叠在一起练。

---

## 课前 3 分钟：今天讲什么

**话题：** 读写分离下的「读己之写」——用户刚写入的数据，为什么立刻读可能查不到？怎么在正确性、主库压力和跨设备场景之间找平衡？

**方案演进（material 技术干点）：**

```
① 强制读主库 → ② 客户端时间戳 + 从库位点判断 → ③ Redis 写入窗口 → ④ 带上限的滑动窗口
```

**故事线：**

```
主库写、从库读 → 200ms 复制延迟 → 404 → 强制读主（15% 流量、CPU 80%）→ 客户端时间戳 → 跨设备 Cookie 漏洞 → Redis 30 秒窗口 → 活跃用户粘主库 → 滑动窗口 + 2 分钟上限 → 写后读 <2%
```

| 方案 | 一致性 | 主库压力 | 跨设备 |
| --- | --- | --- | --- |
| 强制读主 | 绝对可靠 | 大促 15% 写后读，CPU 80% | 无问题 |
| 客户端时间戳 | 带时间戳时精准 | 仅未同步时才 fallback | Cookie 不共享 → 漏读 |
| Redis 滑动窗口（无上限） | 窗口内可靠 | 活跃用户可能长期粘主库 | 服务端解决 |
| 滑动窗口 + 2 分钟 cap | 工程上足够好 | 写后读 <2% | 服务端解决 |

| 关键数字 | 含义 |
| --- | --- |
| 200ms | 正常复制延迟 |
| 15% → 2% | 写后读占流量：强制读主 vs 最终方案 |
| 30s / 2min | 写入窗口 TTL / 硬性上限（600× 延迟余量） |

**规律：** 读写分离省读压力，但「写后立即读」会把压力还回去——方案要逐层修补上一层的漏洞，并用监控数据验证取舍。

---

## 概念 1：Read-Your-Write 与复制延迟

### 用自己的话理解（中英双语）

**中文：**

订单系统采用**主从复制**：写走主库，读走从库，目的是把读流量分摊到副本，减轻主库压力。但有个经典坑：用户下单写入主库后，立刻跳转订单详情页，读请求被路由到从库——从库复制大约落后 **200ms**，新订单还没同步过来，用户看到 **404**。

这就是 **Read-Your-Write（读己之写）** 问题：用户刚写进去的数据，自己紧接着读却读不到。本质是副本传播有延迟，写和读打在了不同的节点上，一致性窗口还没关闭。

**English (B2):**

An order service uses **master–replica replication**: writes go to the master, **whereas** reads are routed to replicas **that** offload traffic from the primary. The goal is read offloading, **but** a classic failure appears **when** a user places an order and is immediately redirected to the detail page. The write lands on the master, **yet** the read request hits a replica **whose** copy is about **200 ms behind**, **so** the new order has not arrived **and** the user sees a 404.

This is the **read-your-write** problem: data **that** the user just wrote may not be visible on the next read. The root cause is replication lag — writes and reads hit different nodes **before** the change has propagated to every copy.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| read-your-write consistency | 读己之写一致性 | Read-your-write consistency means a user can read data **that** they have just written. |
| master–replica replication | 主从复制 | Master–replica replication is a pattern **where** one node accepts writes **and** copies them to followers. |
| replication lag | 复制延迟 | Replication lag is the delay **between** a write on the master **and** its arrival on a replica. |
| read offloading | 读负载分流 | Read offloading moves SELECT traffic to replicas **that** would otherwise hit the master. |
| replica | 从库/副本 | A replica is a copy **that** serves reads **while** the master handles writes. |
| post-write read | 写后读 | A post-write read is a query **that** happens immediately **after** a write on another node. |

### 嵌套从句练习：解释 404 从哪来

**Layer 1：**
> Replication lag causes read-your-write failures.

**Layer 2 — 加定语从句：**
> Replication lag, **which** is about 200 ms in our cluster, causes read-your-write failures **when** a user reads from a replica **that** has not caught up yet.

**Layer 3 — 加因果从句：**
> **Because** the detail query is routed to a replica **that** lags behind the master, the order **that** was just written on the master may not exist on the replica yet, **which** is why the user sees a 404.

**Layer 4 — 完整嵌套版：**
> **When** an order is written to the master **and** the user is redirected to a detail page **whose** read request is load-balanced to a replica, a replication lag of about 200 ms means the new row may not have arrived yet — **a read-your-write failure in which** the user cannot see data **that** they created moments ago, **even though** the write succeeded on the primary.

**中文对照：** 订单写入主库后，用户被重定向到详情页，读请求却被负载均衡打到从库；约 200ms 的复制延迟意味着新行可能尚未到达——用户刚创建的数据自己读不到，写明明在主库成功了，这就是读己之写失败。

---

## 概念 2：强制读主库——简单可靠但吃回读分流

### 用自己的话理解（中英双语）

**中文：**

最直接的修法：**写后读全部强制走主库**。实现简单，用户永远看不到 404，一致性有绝对保证。

代价在大促时暴露：这类「写后立即读」请求占到总流量 **15%**，主库 CPU 飙到 **80%**。读写分离本来省下来的读压力，又被写后读主库吃回去了——副本空着，主库反而更忙。

15% 看起来不多，但主库还要扛所有写操作，额外 15% 的读很容易把它推过安全线。所以这不是长期方案，而是正确性优先时的起点。

**English (B2):**

The most direct fix is **to force every post-write read to the master**. It is simple **and** reliable: users never see a 404, **because** consistency is guaranteed on the node **that** already holds the write.

The cost shows up during peak sales. Post-write reads can spike to **fifteen percent** of all traffic, **which** pushes master CPU toward **eighty percent**. The read-offloading benefit **that** replicas were supposed **to provide** gets eaten back — replicas sit idle **while** the master absorbs both writes **and** those immediate reads.

Fifteen percent may sound modest, **but** the master already handles every write, **so** an extra slice of read load can cross the safety threshold. **That** is why teams treat this as a starting point **that** prioritises correctness, not a long-term scaling strategy.

### 方案对比表

| | 强制读主 | 读写分离理想态 |
| --- | --- | --- |
| 写后读一致性 | 100% 可靠 | 200ms 窗口内可能 404 |
| 主库读压力 | 写后读全打主库 | 绝大部分读走副本 |
| 大促实测 | 15% 流量，CPU 80% | 主库主要扛写 |

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| force reads to master | 强制读主库 | We force reads to the master **when** the user has just written data. |
| fallback | 降级/回退 | A fallback to the master happens **when** the replica is stale. |
| peak sales | 销售高峰 | During peak sales, post-write reads are requests **that** spike in volume. |
| CPU | 中央处理器 | Master CPU rises **when** too many reads return to the primary. |
| consistency | 一致性 | Strong consistency here means the user always reads **what** they wrote. |

### 嵌套从句练习：说为何放弃强制读主

**Layer 3：**
> **Although** forcing post-write reads to the master is reliable, peak traffic **where** those reads reach fifteen percent can push CPU to eighty percent, **which** negates the read-offloading benefit **that** replicas were meant **to provide**.

**Layer 4 — 完整嵌套版：**
> **When** we forced every post-write read to the master, users never saw a 404, **which** was ideal for correctness — **but during** peak sales, those reads climbed to fifteen percent of traffic and drove master CPU toward eighty percent, **a load pattern in which** the replicas we added for read offloading could not help **because** the heaviest read path had been routed back to the primary.

**中文对照：** 强制写后读走主库时用户从不见 404，一致性最好——但大促期间这类读占到 15% 流量、主库 CPU 逼近 80%；副本本是为分流读而加，最重的读路径却被打回主库，分流收益被抵消。

---

## 概念 3：客户端时间戳——精准但有跨设备漏洞

### 用自己的话理解（中英双语）

**中文：**

第二版方案：前端下单时记下 `order_create_time`，查详情时把时间戳带给后端。后端优先读从库，但先问从库：**你的复制位点是否已经覆盖这个时间点？** 若从库已同步到该时间点之前的 binlog，就直接在从库返回；否则 **fallback** 到主库。

好处是只有「从库确实还没追上」的请求才打主库，主库压力大幅下降——比「所有写后读都读主」精准得多。

漏洞在**跨设备**：用户在手机下单，切换到 PC 查订单——Cookie 不共享，PC 不知道刚写的时间戳，请求不带标记，又落到从库，仍可能 404。任何依赖客户端状态一致的方案，在多设备场景都有漏网之鱼。

**English (B2):**

The second approach stores an `order_create_time` on the client **when** the order is created, **and** sends that timestamp with the detail query. The backend prefers the replica, **but** first asks **whether** the replica's replication position has already passed that point. **If** the replica has applied binlog events **up to** that time, it serves the read; **otherwise** the application falls back to the master.

The benefit is precision: only requests **where** the replica is genuinely behind hit the master, **which** cuts master pressure far more **than** forcing every post-write read upstream.

The leak is **cross-device** usage. A user may place an order on a phone **and** open the detail page on a laptop **whose** browser does not share the same cookie state, **so** the request arrives without the timestamp **and** may still read a stale replica. Any design **that** relies on client-side state for consistency will miss cases **where** the client on another device never learned about the write.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| timestamp | 时间戳 | A timestamp marks the moment **when** the write occurred on the master. |
| replication position | 复制位点 | The replication position shows how far a replica has applied binlog events. |
| binlog | 二进制日志 | The binlog is a log **that** records changes **which** replicas replay. |
| cross-device | 跨设备 | Cross-device access breaks schemes **that** depend on cookies **that** do not sync. |
| Cookie | 浏览器 Cookie | Cookies store client state **that** another device may not inherit. |
| stale replica | 过期从库 | A stale replica is one **that** has not yet applied the latest write. |

### 嵌套从句练习：说时间戳如何减少打主库

**Layer 2：**
> The replica serves the read **if** its replication position has passed the timestamp **that** the client sends.

**Layer 3：**
> **When** the client sends `order_create_time`, the application checks **whether** the replica has caught up to that point, **and only if** it has not does it fall back to the master — **which** is more efficient **than** routing every post-write read to the primary.

**Layer 4 — 完整嵌套版：**
> **Although** the client-timestamp scheme reduces master traffic **by** letting replicas serve reads **when** their replication position has already passed the write time, it fails **when** a user switches devices, **because** the new browser does not carry the timestamp **that** the phone stored — **a gap in which** the request hits a stale replica **that** still has not received the order.

**中文对照：** 客户端时间戳方案能在从库复制位点已超过写入时间时让从库直接返回，从而减少打主库——但用户换设备时，新浏览器没有手机存的时间戳，请求仍可能打到尚未收到订单的从库，方案在此失效。

---

## 概念 4：Redis 滑动窗口 + 2 分钟上限

### 用自己的话理解（中英双语）

**中文：**

跨设备漏洞的补救：在 **Redis** 里为每个用户维护「最近写入窗口」——下单后在 **30 秒**内，该用户所有读请求走主库。30 秒远大于正常 200ms 延迟，足够覆盖换设备的时间差；窗口过期后自动回从库，不长期占用主库。

新问题：活跃用户连续下单，每次写都刷新窗口，可能**永远粘在主库**。于是加硬性上限——滑动窗口每次写刷新 30 秒，但从首次创建起**最多 2 分钟**，超时强制回从库。200ms 延迟对比 2 分钟是 **600 倍**余量。

生产监控：最终方案下，真正落到主库的写后读稳定在总流量 **2% 以内**，远低于强制读主的 **15%**。

**English (B2):**

**To close** the cross-device gap, the team stores a **recent-write window** in Redis for each user. **For thirty seconds after** an order, every read from that user goes to the master — a window **that** is far longer **than** the normal **200 ms** lag **and** covers device switches. **When** the window expires, reads return to replicas **so that** the master is not occupied indefinitely.

A new problem appears **if** an active user keeps placing orders: each write refreshes the window, **which** can keep them on the master forever. The fix is a hard cap — a sliding window **that** resets to thirty seconds on each write **but** cannot exceed **two minutes** from the first creation. Two minutes is a **six-hundred-fold** margin over **200 ms** lag.

In production, monitored post-write reads on the master stay **below two percent** of traffic, **whereas** the naive force-master approach had reached **fifteen percent**.

### 演进对比表

| 阶段 | 机制 | 风险 |
| --- | --- | --- |
| 30s 固定窗口 | 写后 30s 读主 | 连续写 → 窗口无限延长 |
| 滑动 + 2min cap | 每次写刷新 TTL，max-age 2min | 极端情况下一瞬可能不一致 |
| 监控验证 | 写后读 <2% | 可预测、可量化 |

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| sliding window | 滑动窗口 | A sliding window refreshes its TTL **whenever** the user writes again. |
| TTL (Time To Live) | 生存时间 | TTL is the expiry **after which** reads return to replicas. |
| Redis | 内存数据库 | Redis holds per-user keys **that** record whether a write window is active. |
| safety margin | 安全余量 | A two-minute cap gives a safety margin **that** is six hundred times the normal lag. |
| workload | 工作负载 | Master workload stays predictable **when** only two percent of reads are post-write. |
| stress-test | 压力测试 | We stress-tested consecutive orders **to verify** the cap prevents master sticking. |

### 嵌套从句练习：说滑动窗口如何防滥用

**Layer 2：**
> Each write refreshes a thirty-second window, **but** we cap total duration at two minutes.

**Layer 3：**
> **Although** a thirty-second window covers cross-device delays, an active user **who** keeps ordering would extend it forever — **which** is why we use a sliding window **that** refreshes on each write **but** forces reads back to replicas **after** two minutes at most.

**Layer 4 — 完整嵌套版：**
> **When** we moved the write window to Redis **so that** reads no longer depend on client timestamps, we still had **to prevent** power users from sticking to the master indefinitely — **a failure mode in which** each order refreshes a thirty-second TTL **until** we added a two-minute max-age, **after which** reads must return to replicas **even if** the user keeps writing, **because** two minutes is a six-hundred-fold margin over our **200 ms** replication lag **that** makes the cap safe in production.

**中文对照：** 写入窗口放到 Redis 后，读不再依赖客户端时间戳，但仍要防止活跃用户无限粘主库——每单都会刷新 30 秒 TTL；加上 2 分钟 max-age 后，即使用户持续下单，超时也必须回从库——相对 200ms 延迟，2 分钟是 600 倍余量，生产上足够安全。

---

## 概念 5：读写分离路由——配置、框架还是代码？

### 用自己的话理解（中英双语）

**中文：**

「写主读从」不是单一实现方式，分三层：

**配置层**：MySQL Router、MaxScale、ShardingSphere-Proxy 等中间件按 SQL 类型自动分发——SELECT 去从库，INSERT/UPDATE/DELETE 去主库。对应用透明，但无法处理「写完马上读」。

**框架层**：Spring `@Transactional(readOnly=true)`、ShardingSphere `HintManager` 等，用注解或拦截器切换数据源，适合常规读写分离。

**代码层**：滑动窗口、写后读主库这类精细逻辑，必须业务代码自己写——查 Redis 判断用户是否在写入窗口内，再手动切数据源。简单读写分离用框架就够；Read-Your-Write 和复杂窗口只能代码兜底。

总结：**配置打底，框架分忧，代码兜底**。

**English (B2):**

Routing writes to the master **and** reads to replicas is not implemented in one single layer. At the **configuration layer**, proxies such as MySQL Router or ShardingSphere-Proxy parse SQL types **and** send SELECTs to replicas **while** sending mutations to the master — **an approach that** is transparent to the app **but** cannot handle read-your-write cases.

At the **framework layer**, annotations like `@Transactional(readOnly=true)` or ShardingSphere's `HintManager` switch data sources through AOP, **which** suits routine read/write splitting.

At the **code layer**, fine-grained rules — such as a Redis-backed sliding window **that** forces master reads — must be written in application logic: check **whether** the user is inside a write window, **then** pick the data source manually. Simple splitting can stay in the framework; read-your-write and capped windows need code **that** the middleware cannot express.

The summary fits three words: **configure the baseline, let the framework handle the common case, and use code for the edge cases**.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| read/write split | 读写分离 | Read/write split is routing **where** writes and reads use different nodes. |
| middleware | 中间件 | Middleware routes SQL **based on** statement type **without** changing application code. |
| data source | 数据源 | A data source is the connection target **that** the application selects per request. |
| HintManager | 路由提示管理器 | HintManager is a tool **that** lets code force routing to the master. |
| transparent | 对应用透明 | Transparent routing hides replicas **that** the app never names directly. |

### 嵌套从句练习：说为何滑动窗口必须写代码

**Layer 4：**
> **Although** a proxy can send SELECTs to replicas automatically, it cannot read a Redis key **that** marks a recent write window — **which** is why our capped sliding-window logic lives in application code **that** checks user state **before** it opens a connection, **whereas** simple read-only routing still fits framework annotations **that** mark methods **which** should hit replicas.

**中文对照：** 代理能自动把 SELECT 发到从库，但读不了 Redis 里标记「近期写入窗口」的 key——带上限的滑动窗口因此必须在应用代码里、开连接前先查用户状态；而普通只读路由仍可用框架注解标记走从库的方法。

---

## 概念 6：从库位点判断——应用层询问，不是从库自动转发

### 用自己的话理解（中英双语）

**中文：**

「从库检查复制位点，未同步则 fallback 主库」——容易误解成从库自己转发请求。实际是**应用层**的流程：

1. 请求带着 `order_create_time` 到达后端；
2. 应用先拿从库连接，执行 `SHOW SLAVE STATUS`（或等价接口）看复制进度；
3. 估算从库已应用到的时间点（如用 `Seconds_Behind_Master`）；
4. 若已覆盖写入时间 → 在从库 SELECT；否则换主库连接再查。

这是**代码层**逻辑，不是中间件配置。ShardingSphere 的 HintManager 能强制读主，但「按 binlog 时间点自动判断」仍需自己实现。

**English (B2):**

It is easy **to misread** the client-timestamp flow **as if** the replica forwarded stale queries by itself. In practice, the **application** orchestrates the steps. The request arrives with `order_create_time`; the app opens a replica connection **and** runs something like `SHOW SLAVE STATUS` **to learn** how far replication has progressed; it estimates the time **up to which** binlog events have been applied — often using `Seconds_Behind_Master`; **if** that covers the write time, it runs SELECT on the replica, **otherwise** it switches to a master connection.

This is **code-layer** logic, not proxy configuration. Tools like HintManager can force master reads, **but** automatic decisions **based on** binlog position still require custom code **that** wraps each post-write read.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| SHOW SLAVE STATUS | 查看从库复制状态 | `SHOW SLAVE STATUS` returns fields **that** describe how far a replica lags. |
| Seconds_Behind_Master | 落后主库秒数 | `Seconds_Behind_Master` is a metric **that** estimates replication delay in seconds. |
| orchestrate | 编排/协调 | The application orchestrates checks **before** it chooses which node to query. |
| estimate | 估算 | We estimate applied time **by subtracting** lag from the replica's clock. |

### 嵌套从句练习：澄清「谁」做 fallback 决策

**Layer 3：**
> The application, **not** the replica, decides **whether** **to fall back** to the master **after** it reads replication status **that** shows the replica is behind.

**Layer 4：**
> **When** a detail query carries `order_create_time`, our data-access layer queries replication status on the replica **that** it would prefer to use, **and if** the estimated applied time is still earlier **than** the write timestamp, it abandons that connection **and** re-runs the SELECT on the master — **a retry pattern that** middleware cannot configure automatically **because** it requires code **that** interprets binlog lag for each request.

**中文对照：** 详情查询带上 `order_create_time` 时，数据访问层先在拟用的从库上查复制状态；若估算的已应用时间仍早于写入时间戳，就放弃该连接、改在主库重跑 SELECT——这种按请求解读 binlog  lag 的重试模式，中间件无法自动配置，只能代码实现。

---

## 课堂对话套路（B2 + 嵌套从句）

### 套路 1：老师问「用户下单后立刻 404，怎么回事」

> **When** writes go to the master **but** the detail read is routed to a replica **that** lags by about 200 ms, the user hits a read-your-write failure — **a case in which** they cannot see the order **that** they just created, **even though** the write succeeded on the primary.

---

### 套路 2：老师问「强制读主库有什么问题」

> **Although** forcing post-write reads to the master guarantees consistency, during peak sales those reads can reach fifteen percent of traffic **and** push master CPU toward eighty percent, **which** means the replicas we added for read offloading cannot help **because** the heaviest read path was routed back upstream.

---

### 套路 3：老师问「客户端时间戳怎么工作」

> The frontend records `order_create_time` **when** the order is created, **and** the backend checks **whether** the replica's replication position has passed that timestamp **before** it serves the read — **falling back** to the master **only when** the replica has not caught up, **which** is far more efficient **than** sending every post-write read to the primary.

---

### 套路 4：老师问「跨设备怎么办」

> **When** a user switches from phone to laptop, cookies do not sync, **so** the laptop may send a request **that** lacks the timestamp **and** hits a stale replica. We fixed that with a Redis write window **that** forces master reads for thirty seconds after each write, **because** server-side state covers every device **that** the user might switch to.

---

### 套路 5：老师问「活跃用户会不会一直占着主库」

> **If** each order refreshes a thirty-second window without a cap, an active user could stick to the master indefinitely — **which** is why we use a sliding window **that** refreshes on each write **but** forces reads back to replicas **after** two minutes at most, **a cap that** keeps post-write master reads below two percent of traffic in production.

---

### 套路 6：老师问「读写分离是配置还是代码实现的」

> Simple SELECT-to-replica routing can live in middleware **that** parses SQL types, **whereas** read-your-write rules — especially a Redis-backed sliding window **that** checks per-user state — must be implemented in application code **that** chooses the data source **before** each query runs.

---

### 套路 7：课上主动说话

| 你想做什么 | 嵌套从句版 |
| --- | --- |
| 确认理解 | So read-your-write fails **when** the read hits a replica **that** has not applied the write yet, **right**? |
| 请老师举例 | Could you walk through **how** the app decides **whether** **to fall back** to the master **after** checking replication lag? |
| 表示同意 | That makes sense — forcing every post-write read to the master is safe, **but** fifteen percent traffic is a lot **when** the primary already handles all writes. |
| 提出疑问 | **But** after the two-minute cap expires, could a slow replica still return a 404 **if** lag spikes beyond 200 ms? |
| 追问实现 | **If** we use Redis for the write window, does the order service set the key **when** the write succeeds, **before** the client redirects? |

---

## 常用句式：嵌套从句版（改写，非原文）

| 功能 | 嵌套从句句式 |
| --- | --- |
| 描述核心问题 | Read-your-write fails **when** a post-write read hits a replica **that** has not yet received the row **which** was written on the master. |
| 强制读主权衡 | Forcing post-write reads to the master is reliable, **but** during peak sales those reads can reach fifteen percent of traffic, **which** pushes CPU toward eighty percent. |
| 时间戳方案 | The client sends a timestamp **that** marks the write time, **and** the app falls back to the master **only when** the replica's position has not passed that point. |
| 跨设备漏洞 | Cross-device access breaks client timestamps **because** cookies on one device do not carry state **that** another browser needs **to route** the read correctly. |
| Redis 窗口 | A Redis write window forces master reads for thirty seconds **after** each write, **so that** every device **that** the user might switch to sees consistent data. |
| 滑动窗口上限 | Each write refreshes the window, **but** we cap it at two minutes **so that** active users cannot stick to the master indefinitely. |
| 路由分层 | Middleware handles routine read/write split, **whereas** read-your-write logic requires code **that** checks Redis **before** it opens a connection. |

---

## 老师可能追问 — 嵌套从句回答

| 老师问 | 你可以答 |
| --- | --- |
| 什么是 read-your-write？ | It means a user can read data **that** they have just written — **which** fails **when** the read goes to a replica **that** has not caught up yet. |
| 200ms 延迟意味着什么？ | It is the gap **between** a successful write on the master **and** the moment **when** a replica can serve that row — **a window in which** immediate reads may 404. |
| 为何不用「前端等一会儿再查」？ | Retries add latency **and** poor UX, **whereas** routing policy fixes the root cause **by** sending the read to a node **that** already has the data. |
| 15% vs 2% 说明什么？ | Fifteen percent was the cost of forcing every post-write read to the master; two percent is what we measured **after** the capped sliding window, **which** shows the optimization worked. |
| 2 分钟 cap 安全吗？ | Two minutes is six hundred times our normal **200 ms** lag, **so** the cap still leaves a huge margin **even if** replication slows temporarily. |
| 从库会自己转发到主库吗？ | No — the application checks replication status **and** opens a master connection **when** the replica is behind, **not** the replica itself. |
| binlog 位点怎么查？ | The app runs status commands on the replica **that** expose lag metrics such as `Seconds_Behind_Master`, **which** it compares against the client timestamp. |
| 简单读写分离够用吗？ | For ordinary reads, yes — **but** post-write reads need code **that** overrides the default replica route **when** consistency matters. |

---

## 跟读练习：五段 B2 嵌套从句（课前朗读 2 遍）

**Part 1 — 问题与读写分离背景**

> Our order service uses master–replica replication **so that** writes stay on the primary **while** most reads hit replicas **that** offload traffic. **When** a user places an order **and** is immediately redirected to the detail page, however, the read may land on a replica **whose** copy is about **200 ms** behind, **which** produces a read-your-write failure — **a situation in which** the user sees a 404 **even though** the write succeeded on the master.

**Part 2 — 强制读主与时间戳**

> We first forced every post-write read to the master, **which** was simple **and** never returned a 404, **but during** peak sales those reads reached fifteen percent of traffic **and** pushed master CPU toward eighty percent. We then moved to a client timestamp: the frontend sends `order_create_time`, **and** the application falls back to the master **only when** the replica's replication position has not yet passed that point — **a scheme that** cuts master pressure **because** most replicas have already caught up **by** the time the user opens the detail page.

**Part 3 — 跨设备与 Redis 窗口**

> The timestamp approach failed **when** users switched devices, **because** cookies do not sync **and** the new browser sends a request **that** lacks the write time, **which** may still hit a stale replica. We patched that with a Redis write window **that** routes all reads from that user to the master for thirty seconds after each order — **a server-side rule that** covers every device **without** relying on client state.

**Part 4 — 滑动窗口上限与监控**

> **Although** a thirty-second window solves cross-device gaps, an active user **who** keeps ordering would refresh it forever **unless** we cap total duration at two minutes, **after which** reads must return to replicas **even if** orders continue. Two minutes is a six-hundred-fold margin over our normal lag, **and** in production monitored post-write reads on the master stay below two percent of traffic — **far lower than** the fifteen percent we saw **when** we forced every such read upstream.

**Part 5 — 实现层次与工程总结**

> Routine read/write splitting can live in middleware **that** sends SELECTs to replicas automatically, **whereas** read-your-write rules — especially a capped sliding window **that** reads Redis before each query — belong in application code **that** chooses the data source per request. The lesson is not to pick "strong consistency" or "eventual consistency" as a slogan, **but** to accept a measurable trade-off **that** you validate with metrics: enough correctness for the user journey, **without** sending fifteen percent of reads back to a master **that** already carries every write.

---

## 附录：嵌套从句工具箱

| 从句类型 | 常用引导词 | 练法 |
| --- | --- | --- |
| **定语从句（限定）** | that, which, who, whose, where | 修饰名词：*a replica **that** lags by 200 ms* |
| **定语从句（非限定）** | , which / , who | 补充信息：*…fifteen percent, **which** pushed CPU to 80%* |
| **时间 / 条件状语** | when, if, after, before | ***When** the read hits a stale replica, the user sees a 404* |
| **原因 / 结果状语** | because, since, so that | *…use Redis **so that** every device is covered* |
| **对比 / 让步状语** | although, whereas, while | ***Although** timestamps help, cross-device breaks them* |
| **嵌套技巧** | 从句套从句 | 主句 → 定语从句里再套 that/when/which |

**拆句口诀：** 先找主句主干 → 标出每个 that/which/when/because 引导的从句 → 从外往里读 → 再试着合并回去。

---

**课前最少记：** 200ms 复制延迟 · 读己之写 = 写主读从 + 立刻读 → 404 · 强制读主：15% 流量、CPU 80% · 时间戳：从库位点判断，跨设备 Cookie 漏洞 · Redis 30s 窗口 + 2min cap → 写后读 <2% · 配置/框架/代码三层路由 · *Measure the trade-off; don't chase absolute consistency at any cost.*
