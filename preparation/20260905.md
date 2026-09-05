这份预习材料**不用 material 原文**，概念全部用自己的话复述。每个概念的「用自己的话理解」提供**中英双语**（英文按 **B2**）。长句练习的重点是**嵌套从句**——定语从句、状语从句、非限制性从句叠在一起练。

---

## 课前 3 分钟：今天讲什么

**话题：** 读写分离下怎么保证**单调读**——用户已看到的数据，刷新后不能「又消失」。

**方案演进（material 技术干点）：**

```
① 问题：不同从库复制进度不一致 → ② 路由：IP/Cookie 不行 → 用户 ID 哈希 → ③ 故障：降级读主库 → ④ 精细：位点检查 + 200ms 超时 → ⑤ 底线：绝不返回旧数据
```

**故事线：**

```
订单时有时无 → 从库 A 100ms / 从库 B 500ms → IP 哈希 WiFi→4G 失效 → Cookie 不可信 → hash(user_id) 固定从库 → 从库挂了单调读仍破 → lag>1s 读主库 → binlog 位点 X 等待追平 → 200ms 超时读主 → 不返回 stale data
```

| 方案 | 机制 | 主要风险 |
| --- | --- | --- |
| IP 哈希 | 按 IP 粘滞从库 | 换网络路由变 |
| Cookie 粘滞 | 客户端记从库 | 可清除/篡改 |
| 用户 ID 哈希 | `hash(user_id)` 固定从库 | 从库故障时仍破 |
| 故障降级主库 | 不可用或 lag>1s → 读主 | 故障窗口主库压力↑ |
| 位点检查 + 等待 | 等到位点 ≥ X 再返回 | 需存位点；等待延迟 |
| 200ms 超时兜底 | 超时 → 读主库 | 频繁超时则主库压力大 |

| 关键数字 | 含义 |
| --- | --- |
| 100ms / 500ms | 从库 A vs B 复制延迟（订单出现/消失） |
| 1s | 从库 lag 超阈值 → 降级读主 |
| 200ms | 位点等待超时（≈ P99 lag × 2） |

**规律：** 单调读 = **会话级一致性**——要么粘到同一从库，要么故障/落后时读主或等到位点追平，**绝不把更旧的数据返回给用户**。

---

## 概念 1：单调读问题——读写分离 + 负载均衡

### 用自己的话理解（中英双语）

**中文：**

用户反馈：刷新订单列表，刚下的订单**时有时无**，像闹鬼。排查结论：**读写分离 + 无状态负载均衡**——两次刷新落到**不同从库**，复制进度不一致。

- 第一次：从库 A，延迟 **100ms**，订单已同步 → 用户看到订单
- 第二次：从库 B，延迟 **500ms**，订单未到 → 用户看到订单「消失」

**单调读（Monotonic Read）**：用户一旦读到某版本数据，后续读取**不能返回更旧的版本**——数据不能先出现后消失。

根因：各从库 lag 不同，LB 随机分发读请求，没有**会话级**一致性保证。

**English (B2):**

Users reported **that** their newly placed orders sometimes appear and sometimes disappear **when** they refresh the order list. The root cause is **read-write splitting plus stateless load balancing**: two refreshes land on **different replicas** **whose** replication progress differs.

On the first refresh, replica A with **100 ms** lag already has the order. On the second, replica B with **500 ms** lag does not — **so** the order seems **to vanish**.

**Monotonic read** means **that** once a user has seen a given version of the data, later reads must not return an older version. Data must not appear and then disappear.

The underlying issue is uneven replica lag combined with load balancing **that** spreads reads without any session-level consistency guarantee.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| monotonic read | 单调读 | Monotonic read means later reads must not return data **that** is older than what the user already saw. |
| read-write splitting | 读写分离 | Read-write splitting sends writes to the master **and** reads to replicas. |
| replication lag | 复制延迟 | Replication lag is the delay **between** the master and a replica **that** may still be catching up. |
| load balancing | 负载均衡 | Load balancing distributes requests **without** remembering which replica a user last hit. |
| stale data | 陈旧数据 | Stale data is a snapshot **that** is older than what the user read before. |
| session consistency | 会话一致性 | Session consistency keeps a user's read view **from** moving backwards within one session. |

### 嵌套从句练习：解释订单为何「消失」

**Layer 2：**
> **When** two refreshes hit different replicas **that** lag by different amounts, the user may see an order disappear.

**Layer 3：**
> **Because** the first request hit replica A, **which** had only 100 ms lag, the order was visible, **but** the second request hit replica B, **whose** 500 ms lag meant the order had not arrived yet — **which** violates monotonic read.

**Layer 4 — 完整嵌套版：**
> **When** read requests from the same user are load-balanced across replicas **whose** replication lag differs — for example, 100 ms on A versus 500 ms on B — the user can see an order on the first refresh **and** lose it on the second, **a failure of monotonic read in which** the second query returns data **that** is older than what the user already saw, **even though** no row was deleted on the master.

**中文对照：** 同一用户的读请求被负载均衡打到 lag 不同的从库（如 A 100ms、B 500ms）时，第一次刷新能看到订单、第二次却看不到——第二次返回的数据比用户已看到的更旧，单调读被破坏，尽管主库并未删单。

---

## 概念 2：路由方案对比——IP、Cookie vs 用户 ID 哈希

### 用自己的话理解（中英双语）

**中文：**

要保证单调读，理想情况是**同一用户总是读同一从库**，这样该用户看到的副本状态只会随复制**单调向前**（除非从库故障）。

三种常见粘滞方案对比：

| 方案 | 问题 |
| --- | --- |
| **IP 哈希** | WiFi 切 4G，IP 变，哈希结果变，路由到另一从库 |
| **Cookie 记从库** | 可被清除、篡改，跨设备不可靠 |
| **用户 ID 哈希** | `hash(user_id)` 固定从库，换网络不影响；用户 ID 在服务端会话中稳定 |

候选人最终选**用户 ID 哈希**：实现简单（Nginx 一致性哈希 等），同一用户读请求 **pinned** 到同一 replica。

仍有问题：该从库挂了，LB 摘掉后请求转到别的从库，单调读仍可能破——需要故障策略补位。

**English (B2):**

To preserve monotonic reads, the ideal is **that** the same user always reads from the same replica, **so** the copy they see can only move forward as replication catches up — **unless** that replica fails.

Three common stickiness approaches compare like this:

| Approach | Problem |
| --- | --- |
| **IP hashing** | Switching from WiFi to 4G changes the IP and therefore the hash target. |
| **Cookie stickiness** | Cookies can be cleared or tampered with and are unreliable across devices. |
| **User-ID hashing** | `hash(user_id)` pins the user to one replica regardless of network changes. |

The candidate chose **user-ID-based hash routing** because the user ID is stable in the server session and easy **to implement** with consistent hashing at the load balancer.

The gap remains: **if** the pinned replica goes down, traffic moves to another replica **whose** lag may differ — **which** breaks monotonic read until a failover policy kicks in.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| session stickiness | 会话保持 | Session stickiness routes the same user to the same backend **on every request**. |
| IP hashing | IP 哈希 | IP hashing breaks **when** the client IP changes after a network switch. |
| user-ID-based hash routing | 基于用户ID的哈希路由 | User-ID hashing pins reads to one replica **that** hash(user_id) selects. |
| pinned replica | 固定从库 | A pinned replica is the copy **to which** a user's reads are consistently routed. |
| tamper | 篡改 | Cookies can be tampered with, **which** makes them poor routing tokens. |

### 嵌套从句练习：说为何选用户 ID 哈希

**Layer 3：**
> **Although** IP hashing is simple, it fails **when** users switch networks, **whereas** user-ID hashing keeps the same replica **as long as** the user ID does not change.

**Layer 4 — 完整嵌套版：**
> **When** we need session stickiness for monotonic reads, IP hashing breaks **as soon as** the user moves from WiFi to 4G, **and** cookie-based routing is unreliable **because** cookies can be cleared or tampered with — **which** is why we pin each user's reads with `hash(user_id)`, **a key that** stays stable across network changes **even though** it still fails **if** the pinned replica itself goes down.

**中文对照：** 为保单调读需要会话粘滞时，IP 哈希在用户 WiFi 切 4G 后即失效，Cookie 路由也因可清除或篡改而不可靠——因此用 `hash(user_id)` 固定读路径，换网络仍稳定，但若固定从库本身宕机则仍会破。

---

## 概念 3：从库故障——降级读主库

### 用自己的话理解（中英双语）

**中文：**

用户 ID 哈希绑定的从库若**不可用**，或复制延迟**超过 1 秒**，同一用户的读请求**切到主库**，直到原从库恢复再切回。

主库始终最新 → 单调读不会破（甚至更强）。代价：故障窗口内主库读压力临时上升；若大量用户同时回源，主库可能过载，需熔断/限流。

这是**用主库换一致性**——不在故障时让用户看到更旧的数据。

**English (B2):**

**When** the replica **to which** a user is pinned is unavailable, **or when** its replication lag exceeds **one second**, that user's reads are redirected **to the master** until the original replica recovers.

The master is always up to date, **so** monotonic read holds — **and** often stronger consistency as well. The cost is temporarily higher read pressure on the master during the failover window. **If** many users fall back at once, the master may overload, **which** is why teams add circuit breakers or rate limits.

This trades master capacity for consistency: **the system does not serve the user stale data during a replica failure**.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| failover | 故障切换 | Failover moves reads to the master **when** the pinned replica fails. |
| fallback | 降级/回退 | Fallback to the master guarantees data **that** is at least as fresh as before. |
| failover window | 故障切换窗口 | The failover window is the period **during which** reads hit the master instead of the replica. |
| master | 主库 | The master holds the latest writes **that** replicas may not have applied yet. |
| circuit breaker | 熔断 | A circuit breaker limits how many reads can fall back **when** replicas fail at scale. |

### 嵌套从句练习：说故障时为何读主

**Layer 4：**
> **When** the pinned replica is down or its lag exceeds one second, we redirect that user's reads to the master, **which** is always up to date — **a fallback that** preserves monotonic read **at the cost of** extra master load **during** the failover window, **because** serving stale data from another lagging replica would recreate the exact "order disappeared" complaint **that** users already reported.

**中文对照：** 固定从库宕机或 lag 超 1 秒时，将该用户读请求切到始终最新的主库——以故障窗口内主库额外负载为代价保单调读，因为从另一台更落后的从库返回旧数据会重现用户已投诉的「订单消失」问题。

---

## 概念 4：位点检查——binlog position 与等待

### 用自己的话理解（中英双语）

**中文：**

更精细的方案：不强制粘在同一从库，而是记录用户**上次读到位点 X**，下次读时从库检查自身位点是否 **≥ X**，不够新则**等待 relay log 回放**追平再返回。

**位点**：MySQL 用 `binlog 文件名 + 偏移量`，如 `mysql-bin.000123:4567`。用户第一次在从库 A 读到订单时，A 已应用到 X；下次落到从库 B，若 B 当前位点 < X，说明 B 更旧，不能直接返回。

实现上可用 `SELECT MASTER_POS_WAIT(...)` 等，阻塞直到追平或超时。

优点：不必固定路由，只在落后时等待或回源，减轻主库压力。位点通常存**服务端 Session**，而非不可靠的 Cookie。

**English (B2):**

A finer approach does not require sticking to one replica forever. Instead, the system records the **replication position X** the user last read from. On the next read, the replica checks **whether** its current position is **at least X**. **If** not, it **waits for** the relay log **to replay** until it catches up before returning.

The **position** is typically a binlog file plus offset, such as `mysql-bin.000123:4567`. **When** the user first saw the order on replica A, A had applied up to X. **If** the next request lands on replica B **and** B's position is less than X, B's data may be too old **to return**.

Functions like `SELECT MASTER_POS_WAIT(...)` can block until catch-up or timeout.

The benefit is flexible routing with validation: wait or fall back only **when** a replica lags behind the user's last seen position. Positions are usually stored in a **server-side session**, not a fragile client cookie.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| replication position | 复制位点 | A replication position marks how far a replica has applied the master's binlog. |
| binlog | 二进制日志 | The binlog records writes **that** replicas replay to stay in sync. |
| offset | 偏移量 | An offset is a byte position **within** a binlog file. |
| relay log | 中继日志 | The relay log buffers binlog events **that** the SQL thread replays. |
| replay | 回放 | Replay applies logged changes **until** the replica reaches position X. |
| catch up | 追平 | A replica catches up **when** its position reaches the position the user last saw. |

### 嵌套从句练习：解释位点检查

**Layer 3：**
> **If** replica B's position is less than X, **which** is the position the user last saw, B waits for replay **until** it catches up **before** returning data.

**Layer 4 — 完整嵌套版：**
> **When** a read lands on replica B, B compares its current binlog position against X — the position **that** the user reached on a previous read — **and if** B has not yet applied events up to X, it waits for the relay log **to replay** until catch-up, **so that** the user never sees data **that** moves backwards, **without** requiring every request **to hit** the same physical replica.

**中文对照：** 读请求落到从库 B 时，B 将当前 binlog 位点与用户上次读到的 X 比较；若尚未应用到 X，则等待 relay log 回放追平再返回，使用户不会看到数据倒退，且不必每次请求都打同一物理从库。

---

## 概念 5：200ms 超时与「绝不返回旧数据」

### 用自己的话理解（中英双语）

**中文：**

位点等待有风险：网络抖动时从库可能等很久。候选人设 **200ms 超时**——约为从库 lag **P99 的两倍**。超时后**立即降级读主库**，不让用户一直转圈，也**绝不返回旧数据**。

底线策略：**要么等到足够新，要么读主库，二选一**。用户抱怨的就是「先看到又消失」——返回 stale data 等于重现 bug。

200ms 需随 P99 lag 调优：若 P99 很小但抖动常超 200ms，会频繁回源主库。

**English (B2):**

Waiting for catch-up is risky: network jitter can make a replica block for a long time. The candidate sets a **200 ms timeout**, roughly **twice the P99 replica lag**. **When** the timeout fires, the system **immediately falls back to the master** — no endless spinner, **and no stale data**.

The bottom line is binary: **either wait until the replica is fresh enough, or read from the master**. Users complained **because** rows appeared and then vanished; returning stale data would recreate that bug.

The 200 ms threshold should track P99 lag. **If** jitter often exceeds 200 ms, users will fall back to the master frequently, **which** raises master read pressure.

### 策略对比

| 超时后选择 | 单调读 | 用户体验 |
| --- | --- | --- |
| 读主库 | ✅ 保持 | 可能略慢，但数据正确 |
| 返回旧数据 | ❌ 破坏 | 订单再次「消失」 |

### 嵌套从句练习：说超时策略

**Layer 4：**
> **Although** waiting for a replica **to catch up** to position X avoids unnecessary master reads, we cap the wait at 200 milliseconds — **which** is about twice our P99 lag — **and if** catch-up does not finish in time, we fall back to the master **rather than** return stale data, **because** the original incident was exactly users seeing an order **that** later disappeared when a slower replica served the next refresh.

**中文对照：** 虽等待从库追到位点 X 可减少打主库，但等待上限 200ms（约 P99 lag 两倍）；若超时仍未追平则读主库，绝不返回旧数据——原事故正是用户先看到订单、下次刷新又被更慢从库「弄消失」。

---

## 概念 6：整体架构分层

### 用自己的话理解（中英双语）

**中文：**

候选人方案是**分层组合**，不是单点魔法：

1. **正常路径**：`hash(user_id)` 固定从库 → 单调读 + 负载分散
2. **故障/高 lag**：lag > 1s 或从库不可用 → 该用户读主库
3. **可选优化**：位点检查 + 200ms 等待 → 减少主库压力
4. **底线**：绝不返回比用户已见版本更旧的数据

对应一致性模型：**单调读**属于**会话一致性**，由路由粘滞 + 动态验证（位点/回源）共同保证。

**English (B2):**

The candidate's design is **layered**, not a single trick:

1. **Happy path**: `hash(user_id)` pins reads to one replica for monotonic reads and even load spread.
2. **Failure or high lag**: lag over one second or an unavailable replica sends that user's reads to the master.
3. **Optional refinement**: position checks with a 200 ms wait reduce master pressure.
4. **Bottom line**: never return data older than what the user already saw.

Monotonic read belongs to **session consistency**, achieved by stickiness plus dynamic checks — position validation or master fallback.

### 嵌套从句练习：总结分层策略

**Layer 4：**
> **Although** user-ID hashing covers the common case **where** one replica moves forward monotonically for each user, replica failure and uneven lag force a master fallback **that** keeps reads fresh, **while** optional position waits reduce how often we need that fallback — **all of which** serves one rule: never return data **that** is staler than what the user has already seen in the same session.

**中文对照：** 用户 ID 哈希覆盖「单用户单从库单调前进」的常见情况；从库故障和不均匀 lag 则靠读主保新鲜，可选位点等待减少回主频率——一切服务于同一条规则：同一会话内绝不返回比用户已见更旧的数据。

---

## 课堂对话套路（B2 + 嵌套从句）

### 套路 1：老师问「订单为什么时有时无」

> Users saw orders appear and then vanish **because** two refreshes hit different replicas **whose** replication lag differed — 100 ms on A versus 500 ms on B — **which** means the second read returned data **that** was older than the first, **violating** monotonic read.

---

### 套路 2：老师问「怎么保证同一用户读同一从库」

> IP hashing breaks **when** the user switches from WiFi to 4G, **and** cookies can be cleared or tampered with. We use user-ID-based hash routing **so that** all reads from the same user are pinned to the same replica **as long as** the user ID stays the same.

---

### 套路 3：老师问「从库挂了怎么办」

> **When** the pinned replica is unavailable or its lag exceeds one second, we redirect that user's reads to the master until the replica recovers. The master is always up to date, **so** monotonic read holds, **at the cost of** temporary master load **during** the failover window.

---

### 套路 4：老师问「位点检查怎么做」

> We record the binlog position X **that** the user last read from — for example `mysql-bin.000123:4567`. **If** the next replica's position is less than X, it waits for the relay log **to replay** until catch-up **before** returning, **so** the user never sees data move backwards.

---

### 套路 5：老师问「等待超时怎么办」

> We set a 200 ms timeout, roughly twice P99 replica lag. **If** the replica does not catch up in time, we fall back to the master **and** never return stale data — **because** the user's complaint was exactly about seeing a row **that** then disappeared on the next refresh.

---

### 套路 6：课上主动说话

| 你想做什么 | 嵌套从句版 |
| --- | --- |
| 确认理解 | So monotonic read means once I see an order, a later refresh must not hide it **because** I hit a slower replica, **right**? |
| 请老师举例 | Could you explain **how** `mysql-bin.000123:4567` tells a replica **whether** its data is fresh enough? |
| 表示同意 | That makes sense — user-ID hashing is stable **when** the network changes, **unlike** IP hashing. |
| 提出疑问 | **But** if many users fall back to the master at once, wouldn't that overload the primary **during** a replica outage? |
| 追问边界 | Why 200 ms specifically — is it always twice P99 lag, **or** does it depend on the workload? |

---

## 常用句式：嵌套从句版（改写，非原文）

| 功能 | 嵌套从句句式 |
| --- | --- |
| 描述问题 | Orders vanish on refresh **because** load balancing sends reads to replicas **whose** replication lag differs. |
| 定义单调读 | Monotonic read requires **that** later reads never return data **that** is older than what the user already saw. |
| 否定 IP/Cookie | IP hashing fails **when** the network changes; cookies fail **because** they can be cleared or tampered with. |
| 用户 ID 路由 | We pin reads with `hash(user_id)` **so that** the same user hits the same replica **regardless of** IP changes. |
| 故障降级 | **When** the pinned replica fails or lags beyond one second, we fall back to the master **which** is always up to date. |
| 位点等待 | **If** the replica's position is behind X, it waits for replay **until** catch-up **before** returning results. |
| 超时底线 | After a 200 ms timeout, we read from the master **rather than** serve stale data **that** would make rows disappear again. |

---

## 老师可能追问 — 嵌套从句回答

| 老师问 | 你可以答 |
| --- | --- |
| 什么是单调读？ | It means **that** once you read a version, later reads must not return an older version — data must not appear and then vanish. |
| 为何 IP 哈希不够？ | The hash key changes **when** the user switches networks, **which** routes them to a different replica **whose** lag may differ. |
| 为何不用 Cookie？ | Cookies can be cleared or tampered with, **so** they are unreliable for routing **that** must stay stable across sessions. |
| 用户 ID 哈希优点？ | The user ID is stable in the server session, **so** `hash(user_id)` pins reads **even when** the client IP changes. |
| 从库故障怎么办？ | We redirect that user's reads to the master **until** the pinned replica recovers, **because** the master is always freshest. |
| 1 秒阈值含义？ | **If** lag exceeds one second, we treat the replica as too stale **to** preserve monotonic read for that user. |
| 位点是什么？ | It is a binlog file plus offset **that** marks how far replication has applied on a replica. |
| 200ms 怎么定？ | It is roughly twice P99 replica lag — **a wait cap after which** we fall back to the master. |
| 超时能返回旧数据吗？ | No — returning stale data would recreate the bug **where** users saw orders disappear on refresh. |
| 和读己之写关系？ | Read-your-writes ensures you see your own writes; monotonic read ensures you never see time go backwards on later reads. |

---

## 跟读练习：五段 B2 嵌套从句（课前朗读 2 遍）

**Part 1 — 问题与单调读定义**

> Users complained **that** orders sometimes appear and then disappear **when** they refresh the list. We traced it to read-write splitting plus load balancing: the first refresh hit replica A, **which** had only 100 ms lag and already showed the order, **but** the second hit replica B with 500 ms lag, **where** the order had not arrived yet. That violates **monotonic read** — the rule **that** once you have seen a version, later reads must not return data **that** is older.

**Part 2 — 路由：IP、Cookie、用户 ID**

> IP hashing and cookie stickiness both fail for session-level routing. IP hashing breaks **as soon as** the user switches from WiFi to 4G, **and** cookies can be cleared or tampered with across devices. We chose user-ID-based hash routing **so that** every read from the same user is pinned to the same replica by `hash(user_id)` — **a key that** stays stable **even when** the network changes, **though** it still breaks **if** that replica itself goes down.

**Part 3 — 从库故障降级主库**

> **When** the pinned replica is unavailable or its replication lag exceeds one second, we redirect that user's reads to the master until the original replica recovers. The master is always up to date, **so** monotonic read remains intact **during** the failover window, **at the cost of** temporarily higher read pressure on the primary — **a trade-off we accept** **because** serving stale data from another lagging replica would bring back the exact "order vanished" experience.

**Part 4 — 位点检查与等待**

> A finer approach records the replication position X **that** the user last read — for example `mysql-bin.000123:4567`. **If** the next request lands on a replica **whose** current position is less than X, that replica waits for the relay log **to replay** until it catches up **before** returning, **so** the user never sees data move backwards **even when** routing is not strictly pinned to one physical copy.

**Part 5 — 超时底线与整体原则**

> Waiting is capped at 200 milliseconds, roughly twice our P99 replica lag. **If** catch-up does not finish in time, we fall back to the master immediately **and** never return stale data — **because** the original complaint was rows **that** appeared and then disappeared. The overall policy is layered: pin by user ID in the common case, fall back to the master on failure or timeout, optionally wait on position when replicas are only slightly behind — **all serving one rule: never serve data staler than what the user has already seen.**

---

## 附录：嵌套从句工具箱

| 从句类型 | 常用引导词 | 练法 |
| --- | --- | --- |
| **定语从句（限定）** | that, which, who, whose, where | *replicas **whose** lag differs* |
| **定语从句（非限定）** | , which / , who | *…500 ms lag, **which** hid the order* |
| **时间 / 条件状语** | when, if, before, after | ***When** lag exceeds one second, read the master* |
| **原因 / 结果状语** | because, since, so that | *…pin by user ID **so that** reads stay monotonic* |
| **对比 / 让步状语** | although, whereas, while | ***Although** waiting helps, we cap it at 200 ms* |
| **嵌套技巧** | 从句套从句 | 主句 → 定语从句里再套 that/when/which |

**拆句口诀：** 先找主句主干 → 标出每个 that/which/when/because 引导的从句 → 从外往里读 → 再试着合并回去。

---

**课前最少记：** 单调读 = 已读版本不能倒退 · 从库 A 100ms / B 500ms → 订单消失 · IP/Cookie 不行 → `hash(user_id)` · 从库故障或 lag>1s → 读主 · 位点 X + 等待追平 · 200ms 超时（≈2×P99）· 绝不返回 stale data · *Either wait until fresh enough, or read the master.*
