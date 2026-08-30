# 【中级】Multi-Master Replication: Cross-Region Latency, Availability, and Conflict Trade-offs

**技术等级：** T2 · **英语等级：** 中 · **字数：** ~500

**Source:** Interview / System Design  
**Level:** T2 / Intermediate  
**Role:** Interviewer, Candidate (2–5 years backend engineer)  
**Estimated Words:** ~502

---

## 故事 Prompt 及故事

```text
请根据以下系统设计知识点生成一个中文技术故事，用于后续英语教学。

知识点：[2.2 多主复制与无主复制]
故事形式：一段面试场景对话，对话双方是面试官和候选人。
技术要求：T2难度（方案对比级），适合2-5年经验后端工程师。
故事冲突设定：
候选人所在公司的电商系统部署在单一数据中心，所有写入都走北京主库。业务拓展到东南亚后，新加坡用户下单要跨海写回北京，平均延迟 300ms，用户体验很差。技术负责人提议用多主复制：在北京和新加坡各部署一个主库，用户就近写入各自的本地主库，两个主库互相同步。候选人质疑：两个主库同时修改同一条数据怎么办？技术负责人反问他：你觉得多主复制到底解决了什么问题？

面试官追问链（必须严格遵循）：

1. "你说多主复制有冲突问题。那单主复制就没有问题吗？新加坡用户每次下单要等 300ms 跨海写入北京主库，大促期间并发上去了，跨海链路一抖动，整个东南亚用户都下不了单。多主复制让用户就近写入本地主库，延迟降到 10ms 以内，可用性也更高。你怎么权衡这 300ms 延迟和冲突处理的复杂度？你的业务能接受 300ms 的下单等待吗？"
2. "多主复制还解决了一个问题：单主故障时的可用性。如果北京主库挂了，单主方案必须等从库切换——至少几十秒不可用。多主方案下，新加坡主库还在服务，东南亚用户完全不受影响。你这个业务对可用性要求高吗？RTO 能接受多长？"
3. "那你说冲突怎么处理？多主复制确实引入了冲突，但冲突概率取决于你的数据分布。如果订单表按用户 ID 路由——东南亚用户的订单永远写新加坡主库，中国用户的订单永远写北京主库，两个主库其实不会修改同一条数据。那冲突还多吗？你真正需要在多主之间同步的数据是哪些？这些数据的冲突概率高吗？"

【必须覆盖的核心概念】（来自核心层）：

- 多主冲突处理（Last Write Wins）

【可选延伸概念】（来自扩展层，T2 可不强制要求）：

候选人的回答要求：

- 说出单主复制在跨地域场景下的两个核心痛点（写入延迟高、主库故障导致全局不可用）
- 解释多主复制如何解决这两个痛点，以及引入的新问题（冲突）
- 说明如何通过数据分区策略（按地理位置或用户 ID 路由）减少冲突概率

要求：故事简短，纯对话形式，字数350字。
生成完故事后，请用1-2句话说明你是如何通过追问实现方案对比深度的。
```

**Interviewer:** "你说多主复制有冲突问题。那单主复制就没有问题吗？新加坡用户每次下单要等 300ms 跨海写入北京主库，大促期间并发上去了，跨海链路一抖动，整个东南亚用户都下不了单。多主复制让用户就近写入本地主库，延迟降到 10ms 以内，可用性也更高。你怎么权衡这 300ms 延迟和冲突处理的复杂度？你的业务能接受 300ms 的下单等待吗？"

**Candidate:** "300ms 完全不能接受。用户点下单，转圈三秒钟，A/B 测试显示转化率至少掉 20%。多主复制是硬需求。但冲突确实让我担心——订单表按用户 ID 路由，东南亚用户永远写新加坡主库，中国用户永远写北京主库，同一个用户的数据不会落在两个主库上，订单和用户表的冲突概率趋近于零。"

**Interviewer:** "那库存、优惠券这种共享数据呢？两个主库的用户可能同时买最后一件库存，这个冲突你能接受吗？"

**Candidate:** "概率小，但后果不小——库存算错就是超卖，超卖就是客诉和退款。对共享数据，我不用多主写，指定北京主库为库存的唯一写入者，新加坡主库只读。从源头消灭冲突，而不是事后修补。"

**Interviewer:** "多主复制还解决了可用性问题。北京主库挂了，单主方案要等故障切换，至少 30 秒不可用；多主方案下新加坡主库继续服务，东南亚完全不受影响。你们的 SLA 是多少？"

**Candidate:** "SLA 是 99.99%，全年只有 52 分钟停机预算，一次 30 秒的故障切换就烧掉一半以上。多主让故障域隔离，北京挂了不影响新加坡。按用户路由的多主换来低延迟和高可用，共享数据用单写路由单独处理，整体收益远大于冲突复杂度。"

**深度实现说明：** 第一轮追问用 300ms 延迟与冲突复杂度的二选一逼出多主的必要性；第二轮追问把冲突按数据归属分类，逼出"共享数据回归单主"的差异化策略；第三轮追问转向可用性与 SLA，逼出故障域隔离的收益，三轮从延迟、冲突、可用性三个维度实现了完整的方案对比深度。

---

## Background

### 文章技术点分析

这段面试对话深入探讨了跨地域多主复制的架构抉择，核心围绕如何解决**写入延迟**与**数据一致性**这一对根本矛盾。候选人的思考展示了根据数据冲突特性进行差异化处理的务实设计。

---

### 1. 核心问题：跨地域延迟与用户体验

- **现状**：所有写入都跨越海洋访问北京主库，新加坡用户经历 300ms 的写入延迟，点击下单后需要等待数秒。
- **业务影响**：根据 A/B 测试，如此长的延迟直接导致转化率下降至少 20%。这表明**延迟不仅是技术指标，更是核心业务指标**。
- **技术需求**：必须将新加坡用户的写入延迟降至 10ms 以下，多主复制是唯一可行的路径。

---

### 2. 多主复制的风险：写入冲突的分类处理

多主复制的最大风险是写入冲突。候选人没有笼统地评估冲突概率，而是**按数据的归属特性对冲突概率进行了分类**，并据此设计不同的写入策略。

#### 低冲突数据：基于用户 ID 路由，本地写入

- **范畴**：订单表、用户资料表等"有主"数据。每个数据行都明确属于一个用户。
- **策略**：按用户 ID 将流量路由到对应的地域主库。东南亚用户永远写入新加坡主库，中国用户永远写入北京主库。
- **效果**：同一用户的数据永远不会在两个主库上并发写入，冲突概率趋近于零。**这是多主复制能安全落地的关键前提。**

#### 高冲突数据：回归单主写入，消除冲突源

- **范畴**：库存、优惠券等全局共享资源。两个地域的用户可能同时购买最后一件商品。
- **策略**：对于这类数据，**不采用多主写入**。指定一个主库作为唯一的写入者（如库存主库在北京），另一个主库仅提供只读。这直接消除了冲突，而非事后修补。
- **代价**：写入仍然有跨地域延迟，但这是为数据正确性必须付出的代价。

---

### 3. 可用性的飞跃：故障域隔离

- **对比**：单主架构下，主库故障需要故障转移，至少导致 30 秒的停机。对于一个年停机时间仅 52 分钟（99.99% SLA）的系统来说，一次故障就耗尽了一半以上的年度预算。
- **多主方案**：故障域被地域隔离。北京主库宕机对新加坡用户的影响为零，他们完全可以在本地正常读写。**可用性实现了质的飞跃**，将全球性故障的风险转化为了局部可控的事件。

---

### 4. 混合路由层：封装复杂性

为了实现以上差异化的写入策略，候选人提出了一个**数据访问路由层**，将复杂性集中管理，对应用代码透明。

- **封装逻辑**：路由层检查每个写操作的目标表和用户上下文，自动决定：

  - 有主数据 → 按用户 ID 路由到所属地域的主库。
  - 共享数据 → 路由到指定的单一写主库。

- **应用接口**：业务代码只需调用 `write(data, userContext)`，无需关心底层复杂的路由规则。
- **核心价值**：**将分布式复杂性限制在可管理的边界内**，既获得了多主的低延迟和高可用，又保证了共享数据的强一致性，同时保持了开发者的生产力。

---

### 总结

候选人的架构决策体现了一个清晰的权衡公式：

**低延迟 + 高可用 + 数据正确性 = 按数据冲突概率分层处理**

- 对**有主数据**，用多主写，靠用户归属消除冲突，追求极致延迟和可用性。
- 对**共享数据**，用单主写，放弃写延迟，追求绝对正确性。
- 用**集中路由层**屏蔽底层复杂性，让应用层无感知。

这套方案没有试图用一把钥匙开所有锁，而是在不同数据上用了最合适的并发控制策略，最终在用户体验、系统可靠性和业务数据正确性之间找到了最佳平衡点。

---

## 架构图

以下是文章涉及的架构对比图：

### 方案一：单主复制（当前痛点）

```
          ┌─────────────────────────────────┐
          │           北京主库 (Master)        │
          │        所有写入都必须到这里         │
          │         ┌─────┐  ┌─────┐         │
          │         │订单表│  │用户表│         │
          │         └─────┘  └─────┘         │
          └──────────────┬──────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
    ┌─────────▼──────┐    ┌─────────▼──────┐
    │   北京应用服务器  │    │  新加坡应用服务器  │
    │   (本地读取)     │    │  (跨海读取+写入)  │
    │   延迟: 1ms     │    │  写入延迟: 300ms │
    └────────────────┘    └────────────────┘
              │                     │
    ┌─────────▼──────┐    ┌─────────▼──────┐
    │   中国用户      │    │  东南亚用户      │
    │   ✅ 快速       │    │   ❌ 300ms 等待  │
    └────────────────┘    └────────────────┘
```

**痛点：** 新加坡用户写入跨海 300ms，大促网络抖动导致整个东南亚不可用。

### 方案二：多主复制（最终方案）

```
    ┌─────────────────────────┐      ┌─────────────────────────┐
    │     北京数据中心          │      │    新加坡数据中心          │
    │                         │      │                         │
    │  ┌──────────────────┐  │      │  ┌──────────────────┐  │
    │  │   北京主库 (Master) │  │      │  │ 新加坡主库 (Master) │  │
    │  │                  │  │      │  │                  │  │
    │  │  用户订单 (中国)   │◄─┼──────┼─►│  用户订单 (东南亚)  │  │
    │  │  按 user_id 路由   │  │ 同步  │  │  按 user_id 路由   │  │
    │  │                  │  │      │  │                  │  │
    │  │  ┌─────────────┐ │  │      │  │  ┌─────────────┐ │  │
    │  │  │  库存表      │ │  │      │  │  │  库存表      │ │  │
    │  │  │ (唯一写入者)  │ │  │      │  │  │  (只读副本)   │ │  │
    │  │  └─────────────┘ │  │      │  │  └─────────────┘ │  │
    │  └──────────────────┘  │      │  └──────────────────┘  │
    │           │             │      │           │             │
    │  ┌────────▼──────────┐  │      │  ┌────────▼──────────┐  │
    │  │  北京应用服务器    │  │      │  │  新加坡应用服务器   │  │
    │  │  本地读写: 10ms   │  │      │  │  本地读写: 10ms    │  │
    │  └───────────────────┘  │      │  └───────────────────┘  │
    │           │             │      │           │             │
    │  ┌────────▼──────────┐  │      │  ┌────────▼──────────┐  │
    │  │  中国用户          │  │      │  │  东南亚用户         │  │
    │  │  ✅ 10ms 延迟      │  │      │  │  ✅ 10ms 延迟      │  │
    │  └───────────────────┘  │      │  └───────────────────┘  │
    └─────────────────────────┘      └─────────────────────────┘
```

**设计策略：**

| **数据类型** | **写入策略** | **冲突概率** |
| --- | --- | --- |
| 订单、用户表 | 按 `user_id` 路由到归属主库 | 趋近于零 |
| 库存、优惠券等共享数据 | 指定北京主库为唯一写入者，新加坡主库只读 | 从源头消灭 |

**可用性提升：** 北京主库故障，新加坡主库继续服务，故障域隔离，全年停机预算可控（99.99% SLA）。

---

## 角色及场景

**Interviewer (面试官):** 追问候选人为何从单主复制转向多主复制，深入挑战其方案在延迟、可用性和冲突处理上的权衡。

**Candidate (候选人):** 2-5年经验后端工程师，负责跨地域电商系统的数据库架构设计，需清晰阐述多主复制的收益与冲突缓解策略。

**场景:** 面试。候选人团队因东南亚业务延迟问题引入多主复制。面试官通过三轮追问，逼出候选人对单主痛点、多主收益、冲突概率和可用性提升的全面对比。

---

## 面试对话 (中级，正文约 502 词)

**Interviewer:**

**Your users in Singapore suffer 300ms write latency on every order because all traffic crosses the ocean to the Beijing master.** **During peak sales, a single network hiccup blocks the entire Southeast Asia region**. Multi-master replication would let Singapore users write locally, cutting latency to under 10ms. Which would you rather deal with—300ms latency or the complexity of conflict resolution?

**Candidate:**

300ms is simply unacceptable. A user clicks "place order" and the spinner spins for three full seconds—that directly kills our conversion rate by at least 20% according to our A/B tests. Low latency with multi-master is a hard requirement. **But I'm genuinely worried about write conflicts.** Here's my thinking: if we route orders by user ID—Southeast Asian users always write to the Singapore master, Chinese users always to Beijing—then the same user's order never lands on two masters. Conflict probability for order and user tables drops to near zero.

**Interviewer:**

**So you need to distinguish data by conflict probability**. Orders and user profiles can be pinned to a region by user ownership—conflicts approach zero. But what about shared data like inventory or coupons? Two users on different masters could both target the last item in stock. Can you tolerate that small probability?

**Candidate:**

**The probability is small, but the consequence isn't**—an inventory miscount means overselling real products, which leads to customer complaints and refunds. For shared data like stock, I'd rather not use multi-master at all. Instead, **I'd designate one master as the sole writer for stock, and the other master only serves reads. That eliminates conflicts at the source instead of patching them afterwards.** We can still keep the read latency low everywhere.

**Interviewer:**

**You mentioned the latency benefit, but multi-master also improves availability**. If the Beijing master fails, a single-master setup needs a failover—at least 30 seconds of downtime. With multi-master, the Singapore master still serves traffic. What's your SLA, and how does that influence your thinking?

**Candidate:**

Our SLA is 99.99%—just 52 minutes of total downtime per year. A single 30-second failover burns more than half of that yearly budget in one incident. With multi-master, the failure domain is isolated: Beijing going down has zero impact on Singapore. That's a qualitative leap for high availability. **Taken together, a user-routed multi-master design gives us low latency and high availability, while we handle shared data separately with single-writer routing.** The overall benefit far outweighs the added conflict complexity.

**Interviewer:**

So you essentially use multi-master for owner-specific data and fall back to single-master for shared data. **How do you plan to roll out such a hybrid approach without confusing the application layer?**

**Candidate:**

**We'll build a lightweight routing layer** in our data access service. It inspects the table and the user context on each write, then decides whether to follow the multi-master routing rule or stick to the designated single master. The application code just calls `write(data, userContext)` and the routing logic is centralized. That keeps the complexity manageable and the developers happy.

---

## 词汇表 (25个高频技术词汇)

| **Vocabulary** | **Pronunciation (IPA)** | **Chinese Meaning** |
| --- | --- | --- |
| multi-master replication | /ˈmʌlti ˈmæstər ˌreplɪˈkeɪʃən/ | 多主复制 |
| single-master replication | /ˈsɪŋɡəl ˈmæstər ˌreplɪˈkeɪʃən/ | 单主复制 |
| write latency | /raɪt ˈleɪtənsi/ | 写入延迟 |
| cross-region | /krɒs ˈriːdʒən/ | 跨地域 |
| peak sales | /piːk seɪlz/ | 销售高峰 |
| network hiccup | /ˈnetwɜːrk ˈhɪkʌp/ | 网络抖动 |
| conflict resolution | /ˈkɒnflɪkt ˌrezəˈluːʃən/ | 冲突解决 |
| conversion rate | /kənˈvɜːrʒən reɪt/ | 转化率 |
| user-based routing | /ˈjuːzər beɪst ˈruːtɪŋ/ | 按用户路由 |
| shared data | /ʃeəd ˈdeɪtə/ | 共享数据 |
| inventory | /ˈɪnvəntəri/ | 库存 |
| overselling | /ˌoʊvərˈselɪŋ/ | 超卖 |
| designated master | /ˈdezɪɡneɪtɪd ˈmæstər/ | 指定主库 |
| failover | /ˈfeɪloʊvər/ | 故障切换 |
| downtime | /ˈdaʊntaɪm/ | 停机时间 |
| SLA (Service Level Agreement) | /ˌes el ˈeɪ/ | 服务等级协议 |
| failure domain | /ˈfeɪljər dəˈmeɪn/ | 故障域 |
| high availability | /haɪ əˌveɪləˈbɪləti/ | 高可用性 |
| conflict probability | /ˈkɒnflɪkt ˌprɒbəˈbɪləti/ | 冲突概率 |
| single-writer routing | /ˈsɪŋɡəl ˈraɪtər ˈruːtɪŋ/ | 单写入者路由 |
| coupon | /ˈkuːpɒn/ | 优惠券 |
| routing layer | /ˈruːtɪŋ ˈleɪər/ | 路由层 |
| data access service | /ˈdeɪtə ˈækses ˈsɜːrvɪs/ | 数据访问服务 |
| centralized | /ˈsentrəlaɪzd/ | 集中的 |
| manageable | /ˈmænɪdʒəbəl/ | 可管理的 |

---

## 句式提炼

| **功能** | **英文句式** | **适用场景** |
| --- | --- | --- |
| 陈述延迟的不可接受性 | *"X ms is simply unacceptable—the spinner spins for three full seconds and that kills our conversion rate by at least Y%."* | 用业务指标量化技术问题 |
| 提出按归属路由减少冲突 | *"If we route by user ID, the same user's data never lands on two masters—conflict probability drops to near zero."* | 说明如何从源头减少冲突 |
| 区分数据冲突概率 | *"We need to distinguish data by conflict probability. Orders can be pinned to a region, but shared data like inventory still risks concurrent writes."* | 展示精细化的数据分区策略 |
| 共享数据回归单主 | *"For shared data, I'd designate one master as the writer and the other only serves reads—that eliminates conflicts at the source."* | 表达"不同数据不同策略"的设计 |
| 用 SLA 量化可用性需求 | *"Our SLA is 99.99%—just 52 minutes per year. A single failover burns more than half of that budget."* | 用 SLA 数据支撑架构决策 |
| 描述混合方案的路由层 | *"We'll build a lightweight routing layer that inspects the table and user context, then decides the write path—keeping complexity centralized and manageable."* | 说明如何落地混合架构 |

---

## 阅读理解题

1. Why does the candidate insist on multi-master replication despite the conflict risks?

   **Answer:** Because 300ms cross-region write latency is unacceptable for user experience—it can drop conversion rates by 20% or more. Multi-master brings latency under 10ms, which is a hard requirement.

2. How does the candidate plan to minimize conflicts for order and user data?

   **Answer:** By routing writes based on user ID—Southeast Asian users always write to the Singapore master, and Chinese users to Beijing. This way the same user's data never conflicts across masters.

3. What strategy does the candidate propose for shared data like inventory?

   **Answer:** Instead of multi-master, they designate one master as the sole writer for inventory and let the other master only serve reads. This eliminates conflicts at the source.

4. How does the candidate use SLA numbers to justify the multi-master decision?

   **Answer:** Their SLA is 99.99%, allowing only 52 minutes of downtime per year. A single 30-second failover in a single-master setup would consume more than half of that yearly budget. Multi-master isolates the failure domain so one region's outage doesn't affect others.

5. How will the hybrid approach (multi-master for some data, single-master for others) be implemented without confusing the application layer?

   **Answer:** They will build a centralized routing layer in the data access service. It inspects the table and user context on each write and decides the path, keeping complexity away from application code.

---

*Word count (dialogue): ~502 words*  
*Level: Intermediate / T2*
