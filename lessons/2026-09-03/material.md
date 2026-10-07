# 【中级】Multi-Master Conflict Resolution: The Limits of Last Write Wins

**技术等级：** T2 · **英语等级：** 中 · **字数：** ~500

**Source:** Interview / System Design  
**Level:** T2 / Intermediate  
**Role:** Interviewer, Candidate (2–5 years backend engineer)  
**Estimated Words:** ~484

---

## 故事 Prompt 及故事

```jsx
请根据以下系统设计知识点生成一个中文技术故事，用于后续英语教学。

知识点：[2.2 多主复制与无主复制]
故事形式：一段面试场景对话，对话双方是面试官和候选人。
技术要求：T2难度（方案对比级），适合2-5年经验后端工程师。
故事冲突设定：
候选人团队部署了北京和新加坡双主库，解决了跨地域写入延迟问题。他说冲突处理很简单——"我们用 Last Write Wins，每条数据带一个时间戳，同步时谁的更新时间晚就保留谁，旧的被覆盖"。面试官追问：如果两个运营人员同时在不同数据中心编辑同一个商品——一个改标题，一个改价格，LWW 会怎么处理？

面试官追问链（必须严格遵循）：

1. "运营小张在北京把商品标题改成'2024新款羽绒服'，运营小王在新加坡把价格从 599 改成 499。两个操作几乎同时，小张的时间戳晚 3 毫秒。LWW 会拿小张的整条商品记录覆盖小王的——标题更新了，但小王的改价丢了。这不是同一字段的并发修改，是不同字段的独立操作。LWW 以整行为粒度做冲突裁决，分不清字段和字段之间的独立性。你怎么避免这种误伤？"
2. "你说可以把商品表拆成多个独立的 key——标题一个 key，价格一个 key。这样小张改标题只写标题 key，小王改价格只写价格 key，LWW 在各自的 key 上独立裁决，互不干扰。但如果小张和小王同时改了价格——一个改成 499，一个改成 479——落在同一个 key 上，LWW 还是按时间戳选一个赢，另一个丢。你能接受这种丢失吗？什么业务能接受，什么业务不能？"
3. "LWW 还有一个根上的问题——它完全信任机器时钟。小王在北京先改了价格，但北京主库的 NTP 快了 2 秒——他的时间戳变成了 10:00:02。小张在新加坡后改价格，新加坡主库时钟准确——时间戳是 10:00:01。物理上小张后改，但他的时间戳反而比小王小。LWW 选了小王赢——后到的小张被先到的小王覆盖了。你怎么避免这种时钟错位导致后改者反而丢数据的问题？你监控过两个数据中心的时钟偏差吗？偏差超过多少你的业务会出错？"

【必须覆盖的核心概念】（来自核心层）：
多主冲突处理（Last Write Wins）

【可选延伸概念】（来自扩展层，T2 可不强制要求）：

候选人的回答要求：
- 指出 LWW 的两个核心缺陷：无法区分"不同字段的并发"和"同一字段的冲突"；完全依赖物理时钟
- 给出至少一种缓解方案（如拆 key 粒度、版本号条件更新）
- 说明 LWW 的适用边界：什么场景下 LWW 足够用，什么场景下必须换方案

要求：故事简短，纯对话形式，字数350字。
生成完故事后，请用1-2句话说明你是如何通过追问实现方案对比深度的。
```

**Interviewer:** "你们部署了北京和新加坡双主库，冲突怎么处理？"

**Candidate:** "我们用 Last Write Wins——每条数据带时间戳，同步时谁的更新时间晚就保留谁，旧的被覆盖。"

**Interviewer:** "运营小张在北京把商品标题改成'2024新款羽绒服'，运营小王在新加坡把价格从 599 改成 499。小张的时间戳晚 3 毫秒，LWW 就拿小张的整条记录覆盖了小王的——标题更新了，但改价丢了。这不是同一字段的并发修改，是不同字段的独立操作。LWW 以整行为粒度裁决，分不清字段间的独立性。你怎么避免这种误伤？"

**Candidate:** "这正是 LWW 的粒度问题——它把整行当成冲突单位。我们的解法是拆 key：标题一个 key，价格一个 key。小张改标题只写标题 key，小王改价格只写价格 key，LWW 在各自的 key 上独立裁决，互不干扰。"

**Interviewer:** "拆 key 解决了不同字段的误伤。但小张和小王同时改了价格——一个改成 499，一个改成 479——落在同一个 key 上，LWW 还是选时间戳晚的赢。你能接受这种丢失吗？"

**Candidate:** "这取决于字段的重要性。商品标题、描述这类信息，丢一次让运营重改就行。但库存扣减、订单状态这类关键字段，冲突意味着超卖或资金错误。对关键字段我们用版本号做条件更新——`UPDATE WHERE version = old_version`，冲突时拒绝写入并通知业务方重试。"

**Interviewer:** "LWW 还完全信任机器时钟。小王在北京先改价，但北京主库 NTP 快了 2 秒，时间戳变成 10:00:02。小张在新加坡后改价，时钟准确，时间戳是 10:00:01。物理上小张后改，但时间戳反而比小王小，LWW 选了小王赢——后改者被先改者覆盖。怎么避免？"

**Candidate:** "我们监控了两个数据中心的时钟偏差，P99 在 5ms 以内。对 LWW 适用的低冲突场景，5ms 窗口足够安全。如果业务要求绝对时序——比如金融交易——我们直接放弃 LWW，用共识算法保证全局有序。"

**深度实现说明：** 第一轮追问逼出拆 key 粒度解决字段间误伤；第二轮追问区分可接受丢失和不可接受丢失，引出版本号条件更新替代 LWW；第三轮追问用时钟偏差量化数据划定 LWW 的适用边界。

---

## Background

### 文章技术干点

### 1. 多主复制下的冲突与 Last Write Wins

**场景**：北京和新加坡双主（dual masters），双方均可接受写入，之后异步同步。

**LWW 机制**：

- 每条记录附时间戳（物理时钟），同步时遇到同一主键冲突，**保留时间戳最新的记录，丢弃旧记录**。
- 优点：简单、无需锁、同步收敛快。
- 核心缺陷：完全依赖物理时间戳裁决，无法识别业务语义上的"独立变更"或"因果顺序"。

---

### 2. 冲突粒度过粗：无辜字段被整行覆盖

面试官指出：张改标题，王改价格，两个操作修改的是不同字段，逻辑上毫不冲突，但 LWW 以整行为单位，只保留时间戳较新的那一行，导致价格更新丢失。

**问题本质**：LWW 的冲突单位是**整行（row）**，但业务的冲突单位应当为**字段**。

**候选人的对策：字段级 key 拆分**

- 将一条产品记录拆成多个独立 key：`title_key`, `price_key`。
- 张写标题只影响 `title_key`，王写价格只影响 `price_key`。
- 每个 key 独自进行 LWW，**互不干扰**。
- 这样即使时间戳有微小差异，也只会覆盖同一字段，不同字段之间再无"连带伤害"。

---

### 3. 同一字段并发写入：静默丢失问题

继续深入：如果两人同时改了价格（同字段、同 key），LWW 仍然只是简单保留时间戳更新的那个值，另一个人的修改被**无声丢弃**。

**回答要点：分层对待**

- **非关键字段**（标题、描述）：冲突概率极低，即使丢失影响也很小（操作员再改一次即可），接受 LWW 的简单性。
- **关键字段**（库存扣减、订单状态）：冲突可能导致超卖或资金错误，**绝不能静默丢弃**。
- **针对关键字段的方案：版本化条件更新（乐观锁）**

```sql
UPDATE product
SET price = 479, version = version + 1
WHERE id = 123 AND version = old_version;
```

若版本已被其他事务修改，更新被数据库拒绝，应用层获知冲突后可重新读取最新值并重试。这属于**写前冲突检测**，而非 LWW 的事后覆盖。

---

### 4. 物理时钟信任问题：NTP 偏移导致因果倒置

面试官给出一个非常具体的例子：

- 北京主库时钟因为 NTP 同步问题快了 2 秒。
- 王（Beijing）先改价格，得到时间戳 `10:00:02`。
- 张（Singapore）后改价格，本地时钟准确，得到时间戳 `10:00:01`。
- 物理上张后改，但他的时间戳反而更小。**LWW 选择王的值获胜，张的后写被覆盖。**

这是 LWW 最根本的威胁：**它假定所有节点时钟一致，但实际上任何 NTP 异常都会导致"后发生的事获得更小时间戳"，从而错误地反向覆盖**。

**候选人的应对**：

1. **主动监控 NTP 偏移**，将 P99 偏移控制在 5 毫秒以内。5 毫秒窗口内，两个操作员同时修改同一 key 的同一字段的概率几乎为零。对于低冲突、非关键字段，这足够安全。
2. **需要绝对顺序的场合，彻底放弃 LWW，改用共识算法（如 Paxos/Raft）**。共识算法不依赖物理时钟，而是用逻辑时钟和多数派决议确定一个全局一致的顺序，能够保证：如果 A 在物理时间上先于 B 被提交，那么最终全局顺序中 A 也在 B 之前。代价是延迟增加，但顺序的正确性得到数学保证。

**针对例子中的 2 秒大偏移**：实际运维中这类大偏差会触发监控告警，并在造成写冲突前被修复，因此不会真的出现"北京快 2 秒并持续导致错误覆盖"的情况。但这也印证了：**LWW 的安全性高度依赖于运维对时钟偏差的控制**。

---

### 5. 总体设计取舍

这场对话展示了从简单的"谁后写谁赢"到工程落地的完整分层策略：

| **策略** | **适用场景** | **冲突单位** | **冲突处理** | **时钟依赖** |
| --- | --- | --- | --- | --- |
| LWW 行级 | 低冲突、整行更新 | 整行 | 最后写入覆盖 | 物理时钟 |
| LWW + 字段拆分 | 字段独立更新的低风险数据 | 单个字段 | 字段级最后写入覆盖 | 物理时钟 |
| 版本条件更新 | 库存、订单等高风险状态 | 行/对象 | 写入前检测冲突，拒绝后重试 | 应用层逻辑版本 |
| 共识算法 | 金融交易等需要绝对定序 | 状态机指令 | 多数派决议给出全局一致顺序 | 逻辑时钟 |

**核心方法论**：不试图用一种机制解决所有冲突，而是依据字段的关键程度和冲突频率，实施**差异化的冲突解决方案**。同时，对物理时钟的风险保持监控和敬畏，并在无法容忍时钟不确定性的环节将其彻底排除在外。

---

### We use versioned conditional updates—UPDATE WHERE version = old_version. 是不是修改之前，先读一下数据？这个如何工作？类似乐观锁？

**版本化条件更新（乐观锁）** 的核心思想是：**修改时带上你最初读到的版本号，如果版本号没变，说明没有别人改过，你的更新才能成功；如果版本变了，说明有冲突，更新失败，需要重试。**

它确实需要在修改前先读一次数据，但这个"读"发生在业务逻辑处理之前，而不是在 SQL 执行时临时去读。

---

#### 1. 完整工作流程

假设我们有一个商品表，其中 `version` 字段用于乐观锁控制。

**第一步：读取数据**

用户或操作员打开编辑页面时，系统从数据库读取当前数据，包括版本号。

```sql
SELECT title, price, version FROM products WHERE id = 1001;
```

返回结果：

```
title: "羽绒服"
price: 599
version: 5
```

此时，页面显示当前价格 599，并隐藏记录了 `version = 5`。

**第二步：用户修改并提交**

王五在 Singapore 将价格改为 499，提交更新请求。请求中携带了最初读到的版本号 `5`。

**第三步：执行条件更新**

```sql
UPDATE products
SET price = 499, version = version + 1
WHERE id = 1001 AND version = 5;
```

**第四步：判断结果**

- **如果受影响的行数 = 1**：说明在这段时间内没有其他操作修改过这条记录（版本号还是 5），更新成功。版本号自动递增为 6。
- **如果受影响的行数 = 0**：说明在你读取之后、提交之前，有另一个操作已经修改了这条记录（版本号已经变成 6 或更高），你的更新被拒绝。此时应用层需要处理冲突：通常的做法是告知用户"数据已被他人修改"，让用户重新加载最新数据后再做修改。

---

#### 2. 为什么需要"先读"？

因为**冲突检测的基准就是你最初读到的那个版本**。如果不先读，你就不知道当前的版本号是多少，也就无法在 WHERE 条件中写入正确的 `old_version`。

这与 `Last Write Wins (LWW)` 的关键区别在于：

- **LWW** 不关心你是否读过，它只看时间戳，后到达的写入会无条件覆盖先到达的。
- **乐观锁** 必须知道"你基于哪个版本做的修改"，只有当你基于的版本与当前数据库中的版本一致时，才允许写入。它拒绝的是"基于过时数据做出的修改"。

---

#### 3. 在对话中的实际应用

面试中提到，对于库存扣减这类关键操作，不能用 LWW，而要用版本化条件更新。

假设当前库存为 10，`version = 3`。两个用户同时下单，都读到 `stock = 10, version = 3`。

- **请求 A**：`UPDATE inventory SET stock = 9, version = 4 WHERE id = 1 AND version = 3;`
- **请求 B**：`UPDATE inventory SET stock = 9, version = 4 WHERE id = 1 AND version = 3;`

数据库会串行执行这两个更新。假设 A 先执行，它成功将版本从 3 改为 4。B 再执行时，发现 `version` 已经不再是 3，WHERE 条件不匹配，影响行数为 0。B 更新失败，应用层收到失败信号后，重新读取最新库存（此时为 9），再尝试扣减。这就从根本上避免了超卖，而不是像 LWW 那样让后到的写入覆盖先到的，导致库存计数错误。

**一句话总结**：乐观锁通过"先读版本号 → 业务处理 → 带版本号条件更新 → 检查是否冲突 → 冲突则重试"的闭环，用无锁的方式保证了分布式环境下的数据正确性。

---

### 什么是 NTP

NTP 的全称是 **Network Time Protocol（网络时间协议）**，简单说就是**让不同计算机的时钟保持同步的协议**。

结合刚才多主复制和 LWW 的讨论，你只要把握下面这几点就完全够用了：

---

#### 1. NTP 是干什么的？

每台服务器都有自己的内部时钟，但晶体振荡器会有微小误差，导致时钟慢慢"走偏"。NTP 通过让服务器定期从权威时间源（如原子钟、GPS）校准时间，把全球机器的时钟偏差控制在可接受范围。

#### 2. 为什么它影响 LWW？

LWW 全靠**物理时间戳**判先后：

- 在北京的主库写了一条数据，时间戳取自北京机器时钟。
- 在新加坡的主库也写了，时间戳取自新加坡机器时钟。

如果两台机器的时钟没有通过 NTP 对齐，**先发生的操作可能拿到一个更小的时间戳**，在冲突时就输了。这就是面试里提到的场景：新加坡的张后改了价格，但他的机器时钟慢了，导致他的时间戳"看起来"比北京的王更早，LWW 错误地保留了王的先改值。

#### 3. NTP offset 和 P99 是什么意思？

- **NTP offset（偏移）**：指本地时钟和参考时间源之间的差值。比如偏移 +100ms，意味着这台机器比标准时间快 100 毫秒。
- **P99 在 5ms 内**：意思是 99% 的时间里，两台机器的时钟差距不超过 5 毫秒。这个窗口越小，两个操作员"恰好在窗口内改同一条数据的同一字段"的概率就越低，LWW 的潜在错误就越可控。

---

**一句话总结**：NTP 就是给服务器对表的协议。一旦时间不对齐，所有依赖物理时钟做"谁后写谁赢"的系统（比如 LWW）就可能在冲突解决时做出违反真实因果的判定。

---

## 角色及场景

**Interviewer (面试官):** 深入追问候选人在多主复制架构下使用 LWW 的潜在风险，挑战其冲突粒度和时钟依赖的假设。

**Candidate (候选人):** 2-5年经验后端工程师，负责跨地域商品系统，需清晰阐述 LWW 的缺陷及缓解方案。

**场景:** 面试。候选人团队部署了北京和新加坡双主库，采用 LWW 处理冲突。面试官通过三个递进场景追问 LWW 的误伤问题、同字段冲突和时钟不可靠性。

---

## 面试对话 (中级，正文约 484 词)

**Interviewer:**

You've deployed dual masters in Beijing and Singapore. How do you handle write conflicts?

**Candidate:**

We rely on **Last Write Wins.** Every record carries a timestamp. **During synchronization, whichever has the later update time wins, and the older one gets overwritten**. It's simple and efficient.

**Interviewer:**

Consider this scenario. Operator Zhang in Beijing updates a product title to "2024 New Down Jacket." Almost simultaneously, Operator Wang in Singapore drops the price from 599 to 499. Zhang's timestamp is just 3 milliseconds later. LWW takes Zhang's entire product row and overwrites Wang's—the title update succeeds, but the price change is lost. These aren't conflicting edits to the same field. **They're independent changes to different fields. LWW can't tell the difference.** How do you prevent this kind of collateral damage?

**Candidate:**

That's exactly the granularity problem with LWW. It treats the whole row as the conflict unit instead of individual fields. **Our fix is to split the record into separate keys.** Title gets its own key. Price gets its own key. When Zhang updates the title, only the title key is written. When Wang updates the price, only the price key is touched. LWW arbitrates each key independently, so the two operations never interfere with each other.

**Interviewer:**

Splitting keys solves cross-field interference. **But what if Zhang and Wang both edit the price**—one sets it to 499, the other to 479? Now both writes hit the same key, and **LWW still picks whichever timestamp is later.** The other value is silently discarded. Can your business accept that kind of data loss?

**Candidate:**

**It depends on the criticality of the field**. For non‑critical fields like product titles or descriptions, losing one update means the operator just redoes it—a minor annoyance. But for inventory deductions or order status, a conflict means overselling or financial errors. For those critical fields, we don't use LWW at all. We use versioned conditional updates—`UPDATE WHERE version = old_version`. If the version has changed, the write is rejected outright, and the application layer is notified to retry with fresh data.

**Interviewer:**

**LWW also blindly trusts machine clocks.** Wang in Beijing edits the price first, but the Beijing master's NTP is 2 seconds fast, so his timestamp becomes 10:00:02. Zhang in Singapore edits the price second, and the Singapore clock is accurate, giving a timestamp of 10:00:01. Physically, Zhang edited later, yet his timestamp is actually smaller. LWW then picks Wang as the winner—the later editor loses their change, overwritten by the earlier one. **How do you prevent clock drift from causing the later editor to lose data?**

**Candidate:**

**We actively monitor NTP offset between data centers, and our P99 stays within 5 milliseconds.** For LWW's sweet spot—low‑conflict, non‑critical fields—that 5‑millisecond window is more than safe. The probability of two operators hitting the same key while one machine is seconds ahead is practically zero. But **for use cases demanding absolute ordering, such as financial transactions, we abandon LWW entirely** and rely on a consensus algorithm to guarantee a globally agreed sequence. That costs more latency, but the ordering is guaranteed correct.

---

## 词汇表 (25个高频技术词汇)

| **Vocabulary** | **Pronunciation (IPA)** | **Chinese Meaning** |
| --- | --- | --- |
| multi-master | /ˈmʌlti ˈmæstər/ | 多主架构 |
| write conflict | /raɪt ˈkɒnflɪkt/ | 写入冲突 |
| Last Write Wins (LWW) | /læst raɪt wɪnz/ | 最后写入胜出 |
| timestamp | /ˈtaɪmstæmp/ | 时间戳 |
| overwrite | /ˌoʊvərˈraɪt/ | 覆盖 |
| collateral damage | /kəˈlætərəl ˈdæmɪdʒ/ | 附带损害 |
| granularity | /ˌɡrænjʊˈlærəti/ | 粒度 |
| split keys | /splɪt kiːz/ | 拆分键 |
| arbitrate | /ˈɑːrbɪtreɪt/ | 裁决 |
| critical field | /ˈkrɪtɪkəl fiːld/ | 关键字段 |
| non-critical field | /nɒn ˈkrɪtɪkəl fiːld/ | 非关键字段 |
| overselling | /ˌoʊvərˈselɪŋ/ | 超卖 |
| versioned conditional update | /ˈvɜːrʒənd kənˈdɪʃənəl ʌpˈdeɪt/ | 带版本号的条件更新 |
| reject | /rɪˈdʒekt/ | 拒绝 |
| retry | /ˈriːtraɪ/ | 重试 |
| NTP (Network Time Protocol) | /ˌen tiː ˈpiː/ | 网络时间协议 |
| clock drift | /klɒk drɪft/ | 时钟偏差 |
| P99 | /piː ˈnaɪnti naɪn/ | 第99百分位 |
| consensus algorithm | /kənˈsensəs ˈælɡərɪðəm/ | 共识算法 |
| globally agreed sequence | /ˈɡloʊbəli əˈɡriːd ˈsiːkwəns/ | 全局一致顺序 |
| latency | /ˈleɪtənsi/ | 延迟 |
| ordering | /ˈɔːrdərɪŋ/ | 顺序 |
| conflict unit | /ˈkɒnflɪkt ˈjuːnɪt/ | 冲突单元 |
| data center | /ˈdeɪtə ˈsentər/ | 数据中心 |
| synchronization | /ˌsɪŋkrənaɪˈzeɪʃən/ | 同步 |

---

## 句式提炼

| **功能** | **英文句式** | **适用场景** |
| --- | --- | --- |
| 描述 LWW 机制 | *"Every record carries a timestamp. During synchronization, whichever has the later update time wins."* | 解释基本工作原理 |
| 指出粒度问题 | *"LWW treats the whole row as the conflict unit instead of individual fields. Our fix is to split the record into separate keys."* | 揭示缺陷并提出方案 |
| 区分字段重要性 | *"For non-critical fields, losing one update is a minor annoyance. But for critical fields like inventory, a conflict means overselling."* | 展示对不同数据的差异化处理 |
| 版本号防御 | *"We use versioned conditional updates—if the version has changed, the write is rejected and the application layer retries."* | 说明条件更新的防御逻辑 |
| 时钟监控 | *"We monitor NTP offset between data centers. Our P99 stays within 5 milliseconds."* | 量化风险窗口 |
| 适用边界 | *"For use cases demanding absolute ordering, we abandon LWW and rely on a consensus algorithm."* | 划定技术的适用边界 |

---

## 阅读理解题

1. What problem does LWW have when two operators edit different fields of the same record?

   **Answer:** LWW treats the whole row as the conflict unit, so a later timestamp on one field can overwrite independent changes made to another field, causing data loss.

2. How does splitting a record into separate keys help reduce LWW's collateral damage?

   **Answer:** Each field becomes an independent key. LWW arbitrates each key separately, so edits to different fields no longer interfere with each other.

3. What strategy does the candidate use for critical fields where losing an update is unacceptable?

   **Answer:** They use versioned conditional updates—`UPDATE WHERE version = old_version`. If the version has changed, the write is rejected and the application retries with fresh data.

4. How does clock drift between data centers cause LWW to produce a wrong result?

   **Answer:** If one machine's NTP is seconds ahead, a physically later edit may carry a smaller timestamp. LWW then picks the earlier physical write as the winner, causing the later editor to lose data.

5. Under what circumstances does the candidate say they would abandon LWW entirely?

   **Answer:** For use cases demanding absolute ordering, such as financial transactions. In those cases, they rely on a consensus algorithm to guarantee a globally agreed sequence.

---

*Word count (dialogue): ~484 words*  
*Level: Intermediate / T2*
