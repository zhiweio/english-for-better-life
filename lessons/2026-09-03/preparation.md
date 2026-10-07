这份预习材料**不用 material 原文**，概念全部用自己的话复述。每个概念的「用自己的话理解」提供**中英双语**（英文按 **B2**）。长句练习的重点是**嵌套从句**——定语从句、状语从句、非限制性从句叠在一起练。

---

## 课前 3 分钟：今天讲什么

**话题：** 多主复制下 Last Write Wins（LWW）能走多远——粒度误伤、静默丢失、时钟不可靠，各怎么补？

**方案演进（material 技术干点）：**

```
① LWW 行级裁决 → ② 拆 key 解决跨字段误伤 → ③ 关键字段换乐观锁 → ④ NTP 监控划定边界 → ⑤ 金融场景放弃 LWW 用共识
```

**故事线：**

```
北京+新加坡双主 → LWW 时间戳大者赢 → 张改标题/王改价格 → 整行覆盖丢改价 → 拆 title/price key → 同字段仍静默丢 → 标题可丢/库存不可丢 → UPDATE WHERE version → NTP 快 2 秒因果倒置 → P99 5ms → 共识算法保绝对顺序
```

| 策略 | 冲突单位 | 适用 |
| --- | --- | --- |
| LWW 行级 | 整行 | 低冲突、整行更新 |
| LWW + 拆 key | 单字段 | 字段独立更新的低风险数据 |
| 版本条件更新 | 行/对象 | 库存、订单等高风险状态 |
| 共识算法 | 状态机指令 | 金融交易等需绝对定序 |

| 关键数字 | 含义 |
| --- | --- |
| 3ms | 张比王晚 3ms → 整行覆盖误伤 |
| 2s / 5ms | NTP 大偏移示例 vs 生产 P99 时钟偏差 |
| P99 5ms | 双机房时钟监控目标 |

**规律：** 不用一种冲突机制打天下——按**字段关键程度**和**冲突频率**分层，对物理时钟保持监控，不能容忍时钟不确定性的场景彻底换方案。

---

## 概念 1：多主复制与 Last Write Wins

### 用自己的话理解（中英双语）

**中文：**

团队在北京和新加坡各部署一个**可写主库**（双主），本地写入不用跨洋往返，解决了跨地域延迟。两边都能写，同步时必然出现**写入冲突**——同一主键被两个数据中心各自改过。

候选人的默认方案是 **Last Write Wins（LWW）**：每条记录带**物理时间戳**，同步时比较更新时间，**晚的覆盖早的**。优点：实现简单、无需分布式锁、收敛快。

缺陷也很根本：LWW 只看时间戳，不懂业务语义——分不清「两个独立字段的并发修改」和「同一字段的真正冲突」，也完全信任各节点时钟一致。

**English (B2):**

The team runs **dual writable masters** in Beijing and Singapore so that local writes avoid cross-Pacific round trips. Both sites accept writes, **which** means **write conflicts** are inevitable **when** the same primary key is updated in both data centers.

The candidate's default resolver is **Last Write Wins (LWW)**: every record carries a **physical timestamp**, and during synchronization the copy **whose** update time is later overwrites the older one. The benefits are simplicity, no distributed locks, and fast convergence.

The weaknesses are equally fundamental. LWW judges conflicts by timestamp alone — **it** cannot tell independent field edits from genuine same-field conflicts, **and** it blindly trusts **that** all node clocks are aligned.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| multi-master | 多主架构 | Multi-master replication lets each data center accept writes **that** later sync to peers. |
| write conflict | 写入冲突 | A write conflict occurs **when** two sites update the same key independently. |
| Last Write Wins (LWW) | 最后写入胜出 | LWW keeps the record **whose** timestamp is latest and discards the rest. |
| timestamp | 时间戳 | A timestamp is a clock value **that** LWW uses to pick a winner. |
| synchronization | 同步 | Synchronization merges changes **that** were made on different masters. |
| overwrite | 覆盖 | The later write overwrites the earlier one **without** asking the application. |

### 嵌套从句练习：说 LWW 怎么工作

**Layer 2：**
> LWW keeps the record **whose** timestamp is later **when** two copies of the same key conflict.

**Layer 3：**
> **When** Beijing and Singapore both write to the same product, synchronization compares timestamps **and** keeps whichever update arrived with the later time, **which** means the older copy is discarded entirely.

**Layer 4 — 完整嵌套版：**
> **Although** LWW is simple **because** it needs no locks and converges quickly, it resolves every conflict by comparing physical timestamps — **a rule in which** the latest timestamp wins **regardless of whether** the two writes touched the same field or independent fields **that** should never have conflicted in the first place.

**中文对照：** LWW 虽因无需锁、收敛快而简单，但一切冲突都靠物理时间戳裁决——时间戳最新者赢，不管两次写入是改了同一字段，还是本不该冲突的独立字段。

---

## 概念 2：粒度误伤——整行覆盖 vs 拆 key

### 用自己的话理解（中英双语）

**中文：**

经典误伤场景：小张在北京改商品标题，小王在新加坡把价格从 599 改成 499，几乎同时发生。小张时间戳晚 3ms，LWW 保留小张的**整行**——标题对了，**价格改动丢了**。

问题本质：LWW 的**冲突单位是整行**，业务的冲突单位应是**字段**。两个互不相关的字段修改，被当成一次冲突处理。

对策：**拆 key**——`title` 一个 key，`price` 一个 key。改标题只写 title key，改价格只写 price key，LWW 在各自 key 上独立裁决，**互不干扰**。这叫缩小冲突粒度，把「连带伤害」限制在同一字段内。

**English (B2):**

The classic collateral-damage case: Zhang updates a product title in Beijing **while** Wang drops the price from 599 to 499 in Singapore, almost at the same time. Zhang's timestamp is 3 ms later, so LWW keeps Zhang's **entire row** — the title is correct, **but** Wang's price change is lost.

The root issue is that LWW's **conflict unit is the whole row**, **whereas** the business conflict unit should be the **field**. Two unrelated field edits are treated as one conflict.

The fix is **key splitting**: `title` gets its own key, `price` gets its own key. A title edit touches only the title key; a price edit touches only the price key. LWW arbitrates each key independently, **so** the two operations no longer interfere. This narrows the conflict granularity and confines collateral damage to the same field.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| granularity | 粒度 | Granularity is the size of the unit **on which** LWW arbitrates conflicts. |
| collateral damage | 附带损害 | Collateral damage happens **when** one field's win overwrites another field's independent edit. |
| conflict unit | 冲突单元 | The conflict unit should match the field **that** operators actually edit. |
| split keys | 拆分键 | Split keys turn one row into multiple keys **that** LWW resolves separately. |
| arbitrate | 裁决 | LWW arbitrates each key **without** looking at other keys on the same product. |
| independent | 独立的 | Independent edits to different fields should not trigger row-level overwrites. |

### 嵌套从句练习：说拆 key 如何避免误伤

**Layer 3：**
> **Because** LWW treats the whole row as one conflict unit, a later timestamp on the title can erase a price change **that** happened on another field.

**Layer 4 — 完整嵌套版：**
> **When** Zhang updates the title **and** Wang updates the price at nearly the same time, row-level LWW keeps whichever row has the later timestamp — **a decision in which** an innocent price edit is lost **because** it lived on the same row as a title edit **that** happened to win by three milliseconds, **which** is why we split the record into separate keys **so that** each field is arbitrated independently.

**中文对照：** 张改标题、王改价格几乎同时发生时，行级 LWW 保留时间戳更晚的那一行——价格改动只因与标题在同一行、且标题恰好晚 3ms 而无辜丢失；因此把记录拆成独立 key，让每个字段单独裁决。

---

## 概念 3：同字段冲突——可接受丢失 vs 乐观锁

### 用自己的话理解（中英双语）

**中文：**

拆 key 解决不了**同一字段**上的并发：两人同时改价格，一个写 499、一个写 479，落在同一个 `price` key 上，LWW 仍只留时间戳晚的那个，另一个**静默丢失**。

候选人分层对待：

- **非关键字段**（标题、描述）：丢了让运营重改即可，接受 LWW 的简单性。
- **关键字段**（库存、订单状态）：静默丢失可能导致超卖或资金错误，**绝不能**用 LWW。

关键字段改用**版本化条件更新（乐观锁）**：

```sql
UPDATE products SET price = 479, version = version + 1
WHERE id = 123 AND version = old_version;
```

先读版本号 → 业务处理 → 提交时带 `old_version` → 若版本已变，更新影响 0 行，应用层拒绝并通知重试。这是**写前冲突检测**，不是 LWW 的事后覆盖。

**English (B2):**

Key splitting does not solve **same-field** concurrency. **If** two operators both change the price — one to 499, the other to 479 — both writes hit the same `price` key, **and** LWW still keeps whichever timestamp is later, **silently discarding** the other value.

The candidate treats fields differently:

- **Non-critical fields** (titles, descriptions): losing one edit is a minor annoyance; operators can redo the change, **so** LWW's simplicity is acceptable.
- **Critical fields** (inventory, order status): silent loss can cause overselling or financial errors, **so** LWW is unacceptable.

Critical fields use **versioned conditional updates (optimistic locking)**:

Read the version first → process the business logic → submit with `old_version` → **if** the version has changed, the update affects zero rows and the application rejects the write and retries. This is **conflict detection before write**, not LWW's post-hoc overwrite.

### 策略对比表

| | LWW | 乐观锁（版本号） |
| --- | --- | --- |
| 冲突发现时机 | 同步后事后覆盖 | 写入时检测 |
| 同字段双写 | 静默丢一个 | 拒绝 + 重试 |
| 适用 | 标题、描述 | 库存、订单状态 |

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| critical field | 关键字段 | A critical field is one **where** silent loss can cause overselling. |
| non-critical field | 非关键字段 | Non-critical fields are data **that** operators can safely redo by hand. |
| versioned conditional update | 带版本号的条件更新 | The update succeeds **only if** the version matches the value **that** the client read earlier. |
| optimistic locking | 乐观锁 | Optimistic locking rejects writes **that** are based on stale versions. |
| overselling | 超卖 | Overselling happens **when** inventory counts are overwritten instead of rejected. |
| retry | 重试 | The application retries **after** it reads fresh data **that** includes the new version. |

### 嵌套从句练习：说为何库存不能用 LWW

**Layer 3：**
> **Although** LWW is fine for titles **that** operators can redo, inventory needs versioned updates **that** fail **when** another transaction has already changed the stock.

**Layer 4 — 完整嵌套版：**
> **When** two requests both read `stock = 10, version = 3` and try to deduct one unit, LWW would let the later timestamp overwrite the earlier deduction — **a silent loss that** can cause overselling — **whereas** `UPDATE … WHERE version = 3` lets only the first write succeed, **forcing** the second request **to retry** **after** it reads the updated stock **that** the first transaction committed.

**中文对照：** 两个请求都读到 `stock=10, version=3` 并各扣 1 时，LWW 会让后到的覆盖先到的，静默丢一次扣减可能导致超卖；而 `UPDATE … WHERE version=3` 只允许第一个成功，第二个必须重读最新库存再试。

---

## 概念 4：时钟偏差——NTP、因果倒置与适用边界

### 用自己的话理解（中英双语）

**中文：**

LWW 最根本的假设：**所有节点时钟一致**。现实中靠 **NTP（网络时间协议）** 对表，但偏移永远存在。

面试官的例子：北京主库 NTP 快了 2 秒。王先改价，时间戳 `10:00:02`；张后改价，新加坡时钟准，时间戳 `10:00:01`。物理上张后写，但 LWW 认为王更新，**后改者被先改者覆盖**——因果倒置。

候选人应对：
1. **监控双机房 NTP offset**，P99 控制在 **5ms** 以内；低冲突、非关键字段场景，5ms 窗口足够。
2. 大偏移（如 2 秒）会触发告警，运维修复前不应持续写冲突。
3. 需要**绝对全局顺序**（金融交易）→ **放弃 LWW**，改用 **Paxos/Raft** 等共识算法，用逻辑时钟 + 多数派决议，不依赖物理时钟。

**English (B2):**

LWW's deepest assumption is **that** all node clocks agree. In practice, **NTP (Network Time Protocol)** keeps servers aligned, **but** offset never disappears entirely.

In the interview example, the Beijing master runs 2 seconds fast. Wang edits the price first and gets timestamp `10:00:02`. Zhang edits second with an accurate Singapore clock and gets `10:00:01`. Physically Zhang wrote later, **yet** LWW picks Wang — **the later editor loses to the earlier one**. Causality is reversed.

The candidate responds in layers:

1. **Monitor NTP offset** between data centers and keep P99 within **5 ms**; for low-conflict, non-critical fields, that window is safe enough.
2. Large offsets like 2 seconds trigger alerts and should be fixed before they cause sustained wrong winners.
3. **Use cases demanding absolute global order** — such as financial transactions — **abandon LWW** and use **Paxos/Raft** consensus, **which** orders events with logical clocks and quorum votes instead of physical time.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| NTP | 网络时间协议 | NTP is the protocol **that** keeps server clocks aligned across sites. |
| clock drift | 时钟偏差 | Clock drift is the gap **between** a local clock and the reference time. |
| causality | 因果顺序 | LWW can violate causality **when** a fast clock gives an earlier edit a later timestamp. |
| consensus algorithm | 共识算法 | A consensus algorithm picks a globally agreed sequence **without** trusting physical clocks. |
| ordering | 顺序 | Absolute ordering matters for transactions **that** must never be reordered. |
| P99 | 第99百分位 | P99 offset means ninety-nine percent of samples stay within the stated window. |

### 嵌套从句练习：说时钟如何搞乱 LWW

**Layer 2：**
> **If** Beijing's clock is two seconds fast, a later edit may carry a smaller timestamp **that** makes LWW pick the wrong winner.

**Layer 3：**
> **Although** Zhang edited the price after Wang, Beijing's fast NTP clock gave Wang the larger timestamp, **which** caused LWW to overwrite the later physical edit.

**Layer 4 — 完整嵌套版：**
> **When** one data center's NTP offset pushes its clock two seconds ahead, an edit **that** happened first can receive a timestamp **that** looks newer than a physically later edit from another site — **a failure mode in which** LWW trusts machine time over real causality, **which** is why we monitor offset with a P99 under five milliseconds for low-risk fields **and** abandon LWW entirely for financial workloads **that** need a consensus algorithm **whose** ordering does not depend on physical clocks.

**中文对照：** 当一个数据中心 NTP 偏移使时钟快 2 秒时，先发生的编辑可能拿到比另一站点物理上更晚的编辑还大的时间戳——LWW 信机器时间而非真实因果；因此对低风险字段监控 P99 5ms 内偏移，对需要绝对顺序的金融业务彻底放弃 LWW，改用不依赖物理时钟的共识算法定序。

---

## 概念 5：乐观锁完整流程

### 用自己的话理解（中英双语）

**中文：**

版本化条件更新 = **先读版本 → 改 → 带旧版本提交 → 冲突则重试**。

1. 打开编辑页：`SELECT …, version FROM products WHERE id = 1001` → 得到 `version = 5`
2. 用户改价并提交，请求携带 `version = 5`
3. `UPDATE … SET price = 499, version = 6 WHERE id = 1001 AND version = 5`
4. 影响行数 = 1 → 成功；= 0 → 期间别人已改过，提示重载再改

与 LWW 的关键区别：LWW 不管你是否基于旧数据写，只看谁时间戳晚；乐观锁必须证明「我基于的版本仍是当前版本」才允许写，拒绝的是**基于过时数据的修改**。

库存并发扣减：两人同时读到 `stock=10, version=3`，A 的 `UPDATE … WHERE version=3` 先成功变 version=4，B 再执行影响 0 行 → 重读 `stock=9` 再扣，避免超卖。

**English (B2):**

Versioned conditional updates follow a loop: **read version → edit → submit with old version → retry on conflict**.

1. Open the edit page: `SELECT …, version` returns `version = 5`.
2. The user submits a price change carrying `version = 5`.
3. `UPDATE … WHERE id = 1001 AND version = 5` runs.
4. One affected row means success; zero rows means someone else already changed the record, **so** the client reloads and retries.

The key difference from LWW: LWW does not care **whether** you based your edit on stale data — it only compares timestamps. Optimistic locking requires proof **that** the version you read is still current; it rejects edits **that** are based on outdated state.

For concurrent inventory deductions, both clients read `stock = 10, version = 3`. A's `UPDATE … WHERE version = 3` succeeds and bumps the version to 4. B's update affects zero rows, **so** B rereads `stock = 9` and retries — **which** prevents overselling.

### 嵌套从句练习：解释乐观锁闭环

**Layer 4：**
> **Because** conflict detection depends on the version **that** the client read at the start, the update includes `WHERE version = old_version` — **and if** another transaction has already incremented that version, the write is rejected **so that** the application can reload fresh data **instead of** silently overwriting a change **that** another operator or request committed in between.

**中文对照：** 冲突检测依赖客户端开始时读到的版本，因此 UPDATE 带 `WHERE version = old_version`；若另一事务已递增版本，写入被拒绝，应用可重载最新数据，而不是静默覆盖其间他人已提交的修改。

---

## 概念 6：分层冲突策略总览

### 用自己的话理解（中英双语）

**中文：**

不要试图用一种机制解决所有冲突。按字段关键程度和冲突频率选工具：

| 策略 | 何时用 |
| --- | --- |
| LWW 行级 | 低冲突、整行更新、可容忍偶发覆盖 |
| LWW + 拆 key | 多字段独立更新、非关键数据 |
| 版本条件更新 | 库存、订单状态、不能静默丢 |
| 共识算法 | 金融交易、必须绝对全局顺序 |

核心：**差异化冲突解决** + **对物理时钟监控与敬畏** + **时钟不可接受处彻底排除 LWW**。

**English (B2):**

Do not try to solve every conflict with one mechanism. Choose tools based on field criticality and conflict frequency:

Row-level LWW suits low-conflict, whole-row updates **where** occasional overwrites are tolerable. LWW plus key splitting suits products **whose** fields are edited independently and are non-critical. Versioned updates protect inventory and order state **where** silent loss is unacceptable. Consensus algorithms serve financial workloads **that** require absolute global ordering.

The core method is **differentiated conflict resolution**, **active monitoring of physical clocks**, and **removing LWW entirely** **where** clock uncertainty is unacceptable.

### 嵌套从句练习：说为何分层

**Layer 4：**
> **Although** a single LWW policy is tempting **because** it is easy to explain, applying the same durability rule to every field would either slow non-critical edits with heavy locking **or** leave critical inventory exposed to silent overwrites — **which** is why we match each field's conflict handler to the business risk **that** losing an update would create.

**中文对照：** 虽说统一 LWW 策略好讲，但对每个字段用同一持久化规则，要么给非关键编辑套上重锁拖慢，要么让关键库存暴露于静默覆盖——因此按「丢一次更新会造成多大业务风险」为各字段选配冲突处理器。

---

## 课堂对话套路（B2 + 嵌套从句）

### 套路 1：老师问「双主冲突怎么处理」

> We use Last Write Wins: every record carries a timestamp, **and during** synchronization whichever copy has the later update time wins. It's simple **and** needs no distributed locks, **but** it treats every conflict as a timestamp race **that** ignores field-level independence.

---

### 套路 2：老师问「改标题和改价格同时发生会怎样」

> Row-level LWW keeps whichever entire row has the later timestamp, **which** means an innocent price change can be lost **when** someone else updates the title on the same row. We fix that by splitting keys — title and price each get their own key **so that** LWW arbitrates them independently.

---

### 套路 3：老师问「两人同时改价格能接受吗」

> **It depends on field criticality.** For titles or descriptions, losing one edit is a minor annoyance **that** operators can redo. For inventory or order status, silent loss can cause overselling, **so** we use versioned conditional updates **that** reject stale writes **and** force the application **to retry** with fresh data.

---

### 套路 4：老师问「NTP 偏差怎么影响 LWW」

> **If** one master's clock runs two seconds fast, a physically earlier edit can carry a larger timestamp **than** a later edit from another site, **which** makes LWW pick the wrong winner. We monitor NTP offset and keep P99 within five milliseconds for low-risk fields, **but** financial workloads abandon LWW and use consensus **that** does not trust physical clocks.

---

### 套路 5：老师问「乐观锁是不是要先读」

> Yes — the client must read the current version first, **because** the UPDATE only succeeds **if** `version` still matches the value **that** the client saw. **If** another write bumped the version, the update affects zero rows **and** the application reloads instead of overwriting.

---

### 套路 6：课上主动说话

| 你想做什么 | 嵌套从句版 |
| --- | --- |
| 确认理解 | So LWW's conflict unit is the whole row by default, **which** is why independent field edits can cause collateral damage, **right**? |
| 请老师举例 | Could you walk through **how** `UPDATE WHERE version = old_version` prevents overselling **when** two clients deduct stock at the same time? |
| 表示同意 | That makes sense — split keys narrow granularity **so that** title and price edits don't fight each other. |
| 提出疑问 | **But** if NTP drifts beyond five milliseconds, how quickly would we detect it **before** LWW picks the wrong winner? |
| 追问边界 | **When** would you choose consensus over LWW plus tight clock monitoring? |

---

## 常用句式：嵌套从句版（改写，非原文）

| 功能 | 嵌套从句句式 |
| --- | --- |
| 描述 LWW | Every record carries a timestamp, **and during** sync whichever update is later wins, **regardless of whether** the edits touched the same field. |
| 粒度问题 | LWW treats the whole row as the conflict unit, **whereas** business conflicts often happen at field level — **which** causes collateral damage. |
| 拆 key 方案 | We split the record into separate keys **so that** LWW arbitrates each field independently **without** overwriting unrelated changes. |
| 字段分层 | Non-critical fields can tolerate LWW's silent loss, **but** critical fields like inventory need versioned updates **that** reject stale writes. |
| 乐观锁 | The update succeeds **only if** the version matches what the client read; **otherwise** the application retries **after** loading fresh data. |
| 时钟风险 | Clock drift can make a later edit carry a smaller timestamp, **which** causes LWW to violate real causality. |
| 适用边界 | For workloads **that** demand absolute ordering, we abandon LWW **and** use a consensus algorithm **whose** sequence does not depend on physical clocks. |

---

## 老师可能追问 — 嵌套从句回答

| 老师问 | 你可以答 |
| --- | --- |
| LWW 优点？ | It is simple, needs no locks, and converges quickly **because** every conflict is resolved by timestamp alone. |
| 整行覆盖问题？ | LWW keeps the whole row **whose** timestamp is latest, **so** an independent edit on another field can be lost. |
| 拆 key 做什么？ | Each field becomes its own key **that** LWW resolves separately, **so** title and price edits no longer interfere. |
| 同字段双写？ | LWW still picks one winner by timestamp **and** silently discards the other value on the same key. |
| 库存为何不用 LWW？ | Inventory conflicts can cause overselling **if** one deduction silently overwrites another — **which** versioned updates prevent by rejecting stale writes. |
| 乐观锁流程？ | Read version → edit → `UPDATE WHERE version = old` → retry **if** zero rows are affected. |
| NTP 是什么？ | NTP is the protocol **that** aligns server clocks; LWW fails **when** offsets make timestamps lie about causality. |
| P99 5ms 意义？ | It means ninety-nine percent of clock samples stay within five milliseconds — **a window in which** same-key collisions are unlikely for low-risk fields. |
| 何时用共识？ | **When** the business requires absolute global ordering, such as financial transactions, **where** physical timestamps are not trustworthy enough. |

---

## 跟读练习：五段 B2 嵌套从句（课前朗读 2 遍）

**Part 1 — 多主与 LWW 基础**

> We run dual masters in Beijing and Singapore **so that** each region can write locally **without** waiting for cross-Pacific replication. **When** both sites update the same key, we resolve conflicts with Last Write Wins — every record carries a timestamp, **and during** synchronization whichever copy has the later time overwrites the older one. The approach is simple **and** lock-free, **but** it judges conflicts by clock time alone, **without** understanding **whether** two edits were truly independent.

**Part 2 — 粒度误伤与拆 key**

> Consider two operators **who** edit different fields at nearly the same time: one changes the title, the other changes the price. Row-level LWW keeps whichever entire row has the later timestamp, **which** means the price update can disappear **even though** it never conflicted with the title edit. We narrow the conflict unit by splitting keys — title and price each get their own key — **so that** LWW arbitrates each field independently **and** cross-field collateral damage stops.

**Part 3 — 关键字段与乐观锁**

> Splitting keys does not help **when** two operators edit the same field: LWW still keeps whichever timestamp is later **and** silently discards the other value. For non-critical fields like descriptions, that loss is a minor annoyance. For inventory or order status, silent loss can cause overselling, **so** we use versioned conditional updates — `UPDATE WHERE version = old_version` — **which** reject stale writes **and** force the application **to retry** **after** reading fresh data **that** includes the new version.

**Part 4 — 时钟偏差与 NTP**

> LWW blindly trusts machine clocks. **If** one data center runs two seconds fast, a physically earlier edit can receive a timestamp **that** looks newer than a later edit from an accurately clocked site, **which** makes the later editor lose. We monitor NTP offset and keep P99 within five milliseconds for low-conflict fields, **but** large drift triggers alerts **because** sustained offset would break causality. For financial workloads **that** need absolute ordering, we abandon LWW entirely **and** rely on consensus algorithms **that** do not depend on physical time.

**Part 5 — 分层策略与工程原则**

> The lesson is not to pick one conflict resolver for the whole system. Row-level LWW suits low-risk whole-row updates; key splitting protects independent field edits; versioned updates guard inventory and order state **where** silent loss is unacceptable; consensus serves transactions **that** must be globally ordered. Match the mechanism to the field's criticality, monitor the clocks **that** LWW depends on, **and** remove physical-time arbitration entirely **where** the business cannot tolerate clock uncertainty.

---

## 附录：嵌套从句工具箱

| 从句类型 | 常用引导词 | 练法 |
| --- | --- | --- |
| **定语从句（限定）** | that, which, who, whose, where | *keys **that** LWW resolves separately* |
| **定语从句（非限定）** | , which / , who | *…five milliseconds, **which** is safe for low-risk fields* |
| **时间 / 条件状语** | when, if, before, after | ***When** two sites edit the same key, LWW compares timestamps* |
| **原因 / 结果状语** | because, since, so that | *…split keys **so that** fields don't overwrite each other* |
| **对比 / 让步状语** | although, whereas, while | ***Although** LWW is simple, it ignores field independence* |
| **嵌套技巧** | 从句套从句 | 主句 → 定语从句里再套 that/when/which |

**拆句口诀：** 先找主句主干 → 标出每个 that/which/when/because 引导的从句 → 从外往里读 → 再试着合并回去。

---

**课前最少记：** 双主 + LWW 时间戳大者赢 · 行级误伤 → 拆 key · 同字段仍静默丢 → 标题可丢 / 库存用 `UPDATE WHERE version` · NTP 偏移可因果倒置 · P99 5ms · 金融场景共识算法 · *Match conflict resolution to field criticality; don't trust clocks blindly.*
