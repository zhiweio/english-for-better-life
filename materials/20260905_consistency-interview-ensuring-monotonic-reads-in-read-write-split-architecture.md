# 【中级】Ensuring Monotonic Reads in a Read/Write Split Architecture

**技术等级：** T2 · **英语等级：** 中 · **字数：** ~500

**Source:** Interview / System Design  
**Level:** T2 / Intermediate  
**Role:** Interviewer, Candidate (2–5 years backend engineer)  
**Estimated Words:** ~482

---

## 故事 Prompt 及故事

```jsx
请根据以下系统设计知识点生成一个中文技术故事，用于后续英语教学。

知识点：[2.3 复制延迟问题]
故事形式：一段面试场景对话，对话双方是面试官和候选人。
技术要求：T2难度（方案对比级），适合2-5年经验后端工程师。
故事冲突设定：
用户反映"刷新订单列表，订单有时出现、有时消失——像闹鬼一样"。候选人排查发现是读写分离+负载均衡导致的——两次请求落到不同从库，复制进度不一致。面试官追问：你怎么保证单调读？

面试官追问链（必须严格遵循）：

1. "用户第一次刷新，请求落到从库 A，复制延迟 100ms，订单同步了。第二次刷新，落到从库 B，延迟 500ms，订单还没到——用户看到订单'消失'了。你怎么保证同一个用户总是读到同一个从库？用 IP 哈希做会话保持吗？如果用户的 IP 变了——比如从 WiFi 切换到 4G——哈希结果变了怎么办？用 Cookie 记录上一次访问的从库？Cookie 能信吗？"
2. "你说可以根据用户 ID 哈希路由到固定的从库。但如果那台从库挂了，负载均衡把它摘掉，用户的请求被迫转到另一台复制进度更慢的从库——单调读又被打破了。你怎么处理从库故障时的单调读保证？是降级读主库，还是让用户短暂牺牲一致性？"
3. "单调读的另一种实现是让从库检查自己的复制位点——如果用户上次请求时看到了位点 X，这次请求的从库必须等到自己的位点 >= X 再返回。但这是同步等待，如果网络抖动，从库可能要等很久。等待超时了怎么办？是超时后读主库，还是返回旧数据？你怎么和用户解释？"

【必须覆盖的核心概念】（来自核心层）：
单调读、复制延迟

【可选延伸概念】（来自扩展层，T2 可不强制要求）：

候选人的回答要求：
- 给出至少两种保证单调读的方案对比（用户哈希路由、位点检查、降级读主）
- 说明从库故障和网络切换场景下的额外处理
- 量化同步等待的超时时间设定依据

要求：故事简短，纯对话形式，字数350字。
生成完故事后，请用1-2句话说明你是如何通过追问实现方案对比深度。
```

**Interviewer:** 你之前提到，用户反馈刷新订单列表时，刚下的订单时有时无。你排查后认为是读写分离加负载均衡导致的——两次请求被路由到不同的从库，复制进度还不一致。那我们来具体聊聊：用户第一次刷新，请求落到从库 A，复制延迟 100ms，订单已经同步过去；第二次刷新，落到从库 B，延迟 500ms，订单还没到，用户就看到订单"消失"了。你怎么保证同一个用户总是读到同一个从库？用 IP 哈希做会话保持？可用户 IP 会变，比如从 WiFi 切到 4G。用 Cookie 记录上一次访问的从库？Cookie 能信吗？

**Candidate:** IP 哈希和 Cookie 都不行。IP 哈希在用户切换网络后就会变；Cookie 则可能被清除或篡改。我们最终选择按用户 ID 哈希路由，把同一用户的所有读请求固定到同一个从库。只要用户 ID 不变，路由就稳定，切网络也不影响。但如果这个从库挂了，负载均衡把它摘掉，请求就会转到另一个从库——单调读还是会被打破。

**Interviewer:** 那从库故障时，你怎么保证单调读？

**Candidate:** 我们做降级读主库。一旦检测到从库不可用，或者延迟超过 1 秒，同一用户的请求就切到主库，直到原从库恢复。主库一定是最新的，所以单调读不会破。代价是主库压力临时增加，但只发生在故障窗口内。

**Interviewer:** 还有一种方案是让从库检查自己的复制位点，等它追到用户上次看到的位置再返回。但我不太明白位点检查具体怎么做，你能解释一下吗？如果网络抖动导致从库要等很久，超时了怎么办？

**Candidate:** 位点就是数据库复制的位置标记，通常用 binlog 文件加偏移量表示。用户上次在从库 A 读到订单时，A 已经应用到了位点 X——比如 `mysql-bin.000123:4567`。下次请求路由到从库 B 时，B 会对比自己的当前位点。如果 B 的位点小于 X，说明 B 的数据更旧，可能还没包含那条订单。这时 B 可以等待回放，直到位点追到 X 再返回结果，这样用户就不会看到数据"倒退"。但等待有风险，我们设了 200 毫秒超时——这是从库延迟 P99 的两倍。超时后就降级读主库，保证用户能看到数据，而不是一直转圈。我们绝不返回旧数据，因为用户抱怨的就是"先看到又消失"。所以策略很简单：要么等到足够新，要么直接读主库，二选一。

**深度实现说明：** 第一问对比 IP 哈希、Cookie 和用户 ID 哈希三种路由方案，逼出用户 ID 哈希的稳定性；第二问引入从库故障时的降级读主策略；第三问完整解释了位点检查的机制（binlog 位置比较），并量化等待超时为 200ms，明确了不返回旧数据的底线，实现了从路由、故障到超时的完整单调读方案对比。

---

## Background

### 文章技术干点

这段对话深入探讨了**读写分离架构下的单调读（Monotonic Read）一致性问题**，以及如何在副本延迟波动时保证用户不会看到数据"回退"。候选人先后提出了用户 ID 哈希路由、故障回源主库、以及副本等待 binlog position 追上后再返回三种方案，并给出了超时兜底策略。以下对其中技术点进行系统分析。

---

### 1. 问题本质：读写分离 + 负载均衡破坏单调读

- **单调读定义**：如果用户已经读到某个版本的数据，那么后续读取不能返回更旧的版本。即数据不能"先出现后消失"。
- **场景**：用户两次刷新请求被路由到不同副本。副本 A 延迟 100ms，已包含新订单；副本 B 延迟 500ms，尚未同步。用户第一次看到订单，第二次又看不到，体验类似数据丢失。
- **根本原因**：不同副本的复制进度不一致，而负载均衡无状态地将请求分散，没有维持会话级的一致性保证。

---

### 2. 候选人方案一：基于用户 ID 的哈希路由

**原理**：将同一用户的所有读请求固定到同一副本，保证该用户看到的副本状态只会单调向前（除非副本故障），从而满足单调读。

**优点**：

- 比 IP 哈希稳定（用户切换网络不影响）。
- 比 Cookie 可靠（不依赖客户端存储，用户 ID 在服务端会话中稳定）。
- 实现简单，负载均衡层（如 Nginx 一致性哈希）即可支持。

**缺点**：

- 副本故障时，请求会被重新分配到其他副本，可能破坏单调读。
- 负载可能不均衡：某些用户 ID 哈希聚集导致热点。
- 增加副本或缩容时需要一致性哈希来减少重映射。

---

### 3. 故障场景处理：回源主库

候选人提出当检测到用户被固定到的副本不可用或延迟超过 1 秒时，将该用户的读请求重定向到主库。

**分析**：

- **主库始终是最新**，因此可以保证单调读（甚至更强的一致性）。
- **代价**：主库读压力短期增加，可能成为瓶颈。需要限制回源比例或快速恢复副本。
- **风险**：如果大量用户同时因为副本故障回源，主库可能过载，反而影响写入性能。通常需要熔断或限流。

---

### 4. 更精细的方案：副本等待复制位置（Position Check）

面试官提出另一种方案：让副本检查自身复制位置，如果落后于用户上次看到的位置，则等待追平后再返回。候选人详细解释了 binlog position 机制。

**技术细节**：

- **位置标记**：在 MySQL 中，使用 `binlog文件名 + 偏移量`（例如 `mysql-bin.000123:4567`）标识主库写入的二进制日志位置。
- 当用户第一次读取时，副本 A 已经应用到了位置 X，可以在响应中附带这个位置（例如通过 Cookie 或服务端 Session 存储）。
- 下一次请求路由到副本 B 时，副本 B 查询自己当前的 `Exec_Master_Log_Pos`（或 GTID），与 X 比较。如果小于 X，说明数据可能过旧，不能直接返回。
- 副本 B 可以调用类似 `SELECT MASTER_POS_WAIT('mysql-bin.000123', 4567, 0.2)` 的函数，阻塞等待直到应用超过 X，或超时返回。
- **超时策略**：候选人设置 200ms 超时（约为 P99 延迟的两倍）。如果超时，则回源主库，确保用户不会看到旧数据。

**优点**：

- 减少主库压力，仅在副本追不及时才回源。
- 实现更细粒度的会话一致性，不依赖固定路由。

**潜在问题**：

- **位置存储方式**：如果使用 Cookie，则又回到 Cookie 不可靠的问题。通常做法是服务端存储 Session 与最后位置，或使用加密签名 Cookie。
- **200ms 超时是否合理**：如果 P99 延迟很小但网络抖动导致偶尔超过 200ms，用户会频繁回源主库，增加主库压力。需要动态调整。
- **等待期间用户感知延迟**：如果副本追平通常只需几十毫秒，等待是可接受的；但如果超时，用户可能经历额外延迟再被重定向，总体响应时间可能增加。
- **对写后读（Read-your-writes）的支持**：如果用户在写入后立即读取，需要确保副本位置至少达到用户写入时的位置。候选人的方案可以扩展到 read-your-writes，但需要额外记录写入位置。

---

### 5. 整体策略总结：绝不返回旧数据

候选人最终策略概括为：**要么等待副本追平，要么读主库，绝不返回旧数据**。这是对单调读的严格保证，但实现上需要权衡可用性与性能。

**架构分层**：

- **正常情况**：用户 ID 哈希路由到固定副本，提供单调读且负载分散。
- **副本故障或延迟过高**：回源主库，保证一致性。
- **可选优化**：在副本正常但短暂落后时，等待位置追平，减少主库压力。

**与标准一致性模型的对应**：

- 单调读属于**会话一致性**的一种，通常由客户端或中间件保证。
- 候选人方案本质上是**会话粘滞（Session Stickiness）** + **动态验证**的组合。

---

### 6. 潜在追问与改进点

- **主库故障怎么办？** 如果主库宕机发生故障切换，新主库的数据可能回退（如果旧主库未完全同步），此时需要更强的一致性协议（如半同步复制）保证已提交事务不丢失，否则单调读仍可能被破坏。
- **多数据中心场景**：副本可能跨地域，延迟更高，等待位置可能不现实，需要更复杂的路由策略。
- **负载均衡的动态调整**：用户 ID 哈希可能导致某些用户永远集中在某副本，而其他副本空闲。可以结合一致性哈希和虚拟节点改善分布。
- **位置存储的安全性与效率**：如果使用 Cookie，需要加密防篡改；如果使用服务端存储，需要额外查询开销。更现代的做法是使用 **GTID** 替代文件偏移，更易管理。

---

### 结论

候选人展示了一套从简单到精细的单调读保证方案，核心思想是**维持会话到固定副本，并在异常时回退到主库或等待副本追平**。方案在工程上可行，但需要关注主库压力、位置传递机制、超时调优等实现细节。整体逻辑清晰，体现了对分布式一致性和用户体验的深刻理解。

---

### 架构图

#### 1. 问题场景：读写分离 + 负载均衡导致订单"消失"

```
                            ┌──────────────────────────────┐
                            │         应用服务器             │
                            │   (处理用户订单列表请求)        │
                            └──────────────┬───────────────┘
                                           │ 读请求
                                           ▼
                            ┌──────────────────────────────┐
                            │       负载均衡器 (LB)          │
                            │   根据某种策略路由到从库        │
                            └──────┬──────────────┬─────────┘
                                   │              │
                      ┌────────────▼───┐      ┌───▼────────────┐
                      │  从库 A (Replica) │      │ 从库 B (Replica) │
                      │  复制延迟: 100ms  │      │ 复制延迟: 500ms  │
                      │  已同步订单       │      │ 未同步订单       │
                      └────────────────┘      └────────────────┘
                                   ▲              ▲
                                   │              │
                            第一次刷新        第二次刷新
                            用户看到订单      用户看到订单消失
```

**根因**：同一个用户两次读请求被路由到不同从库，而各从库的复制进度不一致，导致第二次读到旧数据。

---

#### 2. 方案一：基于用户 ID 哈希路由（保证同一用户固定到同一从库）

```
                            ┌──────────────────────────────┐
                            │         应用服务器             │
                            │  计算 hash(user_id) 选择从库   │
                            └──────────────┬───────────────┘
                                           │
                            ┌──────────────▼───────────────┐
                            │       路由层 (Hash Router)     │
                            │   user_id → replica 映射       │
                            └──────┬──────────────┬─────────┘
                                   │              │
                      ┌────────────▼───┐      ┌───▼────────────┐
                      │  从库 A (Replica) │      │ 从库 B (Replica) │
                      │  负责用户 1,3,5... │      │ 负责用户 2,4,6... │
                      └────────────────┘      └────────────────┘

效果：
✅ 同一用户的所有读请求固定到同一从库
✅ 切换网络也不影响（哈希基于 user_id，不是 IP）
❌ 若该从库宕机，单调读仍会破坏
```

---

#### 3. 方案二：从库故障或延迟超阈值 → 降级读主库

```
用户请求到达
      │
      ▼
检查目标从库状态
      │
      ├── 从库健康 & 复制延迟 ≤ 1 秒
      │        │
      │        ▼
      │   读从库（正常）
      │
      └── 从库不可用 OR 复制延迟 > 1 秒
               │
               ▼
         降级读主库
               │
               ▼
      ┌──────────────────┐
      │  主库 (Master)    │
      │  始终拥有最新数据  │
      └──────────────────┘

实现要点：
• 检测到故障后，该用户后续请求切到主库
• 直到原从库恢复，再切回
• 代价：故障窗口内主库读压力增加，但保证了单调读
```

---

#### 4. 方案三：从库复制位点检查 + 超时降级主库

```
用户在从库 A 读到订单时，记录复制位点 X
（例如：mysql-bin.000123:4567）

下次请求路由到从库 B
      │
      ▼
从库 B 比较自己的当前位点 与 X
      │
      ├── B 的位点 >= X  → 数据够新，直接返回
      │
      └── B 的位点 < X   → 数据不够新
               │
               ▼
          从库 B 等待 relay log 回放，直到追到 X
               │
               ├── 200ms 内追平 → 返回数据
               │
               └── 200ms 超时未追平
                        │
                        ▼
                   降级读主库（立即返回最新数据）

策略总结：
要么等待从库追到足够新，要么读主库——绝不返回旧数据。
```

---

#### 方案对比总结

| **方案** | **机制** | **优点** | **缺点/风险** |
| --- | --- | --- | --- |
| IP 哈希 | 按 IP 固定从库 | 实现简单 | WiFi→4G 切换后路由变化 |
| Cookie 粘滞 | 客户端记录从库 | 无需改路由层 | 可清除/篡改，跨设备不可靠 |
| 用户 ID 哈希 | `hash(user_id)` 固定从库 | 网络切换稳定 | 从库故障时单调读破坏 |
| 故障降级主库 | 从库不可用或 lag>1s → 读主 | 主库最新，单调读不破 | 故障窗口主库压力增加 |
| 位点检查 + 等待 | 等到位点 ≥ X 再返回 | 减少主库压力 | 需存储位点；等待有延迟 |
| 200ms 超时兜底 | 超时 → 读主库 | 不返回旧数据 | 频繁超时则主库压力大 |

---

## 角色及场景

**Interviewer (面试官):** 考察候选人如何解决读写分离下因负载均衡和复制延迟导致的"订单消失"问题，逐步追问路由策略、故障降级和位点检查等方案。

**Candidate (候选人):** 2-5年经验后端工程师，负责订单系统，需清晰阐述按用户 ID 哈希路由、从库故障降级主库、以及基于 binlog 位点的等待回放与超时处理机制。

**场景:** 面试。用户反馈刷新订单列表时订单时有时无。候选人已排查出原因是读写分离加负载均衡导致两次请求路由到不同从库。面试官据此追问单调读的保证方案。

---

## 面试对话 (中级，正文约 482 词)

**Interviewer:**

**You mentioned earlier that users complained their orders sometimes appear and sometimes disappear when they refresh the order list.** You traced it to read-write splitting plus load balancing—**two requests were routed to different replicas with different replication progress**. Let's dig in. On the first refresh, the request hits replica A, which has a 100ms replication lag, so the order is already synced. On the second refresh, it hits replica B, which has a 500ms lag, so the order hasn't arrived yet—the user sees the order "vanish." How do you guarantee that the same user always reads from the same replica? Would you use IP hashing for session stickiness? But the user's IP can change, say from WiFi to 4G. Or would you use cookies to record the last replica? Can cookies really be trusted?

**Candidate:**

IP hashing and cookies both fail. IP hashing breaks as soon as the user switches networks. Cookies can be cleared or tampered with, and they are not reliable across devices. We eventually **chose user-ID-based hash routing**. All read requests from the same user are pinned to the same replica by hashing the user ID. As long as the user ID stays the same, the routing remains stable regardless of network changes. However, **if that particular replica goes down and the load balancer removes it,** the user's requests get redirected to another replica—monotonic read is still broken in that case.

**Interviewer:**

So how do you guarantee monotonic reads when a replica fails?

**Candidate:**

**We fall back to the master. As soon as we detect that the pinned replica is unavailable or its replication lag exceeds one second,** we redirect that user's read requests to the master until the original replica recovers. The master is always up to date, so monotonic read remains intact. The trade-off is temporarily higher pressure on the master, but only during the failure window. This keeps the user experience consistent without silently serving stale data.

**Interviewer:**

Another approach is to have **the replica check its replication position and wait until it catches up to the position the user last saw**. I'm not entirely clear on how position checking works—could you explain? And if network jitter causes the replica to wait too long, what do you do on timeout?

**Candidate:**

The position is a database replication marker, typically a binlog file plus an offset. For example, when the user last read the order on replica A, A had applied up to position X—say `mysql-bin.000123:4567`. On the next request routed to replica B, B compares its current position against X. If B's position is less than X, that means B's data is older and may not yet include that order. **B can wait for the relay log to replay until its position catches up to X before returning,** so the user never sees data go backwards. **But waiting is risky, so we set a 200-millisecond timeout,** which is roughly twice the P99 of our replica lag. If the timeout fires, we immediately fall back to the master to guarantee the user gets data instead of a spinning loader. We never return stale data, because the original complaint was exactly about seeing a row and then having it disappear. So the policy is simple: **either wait until the replica is fresh enough, or read from the master—never serve old data.**

---

## 词汇表 (25个高频技术词汇)

| **Vocabulary** | **Pronunciation (IPA)** | **Chinese Meaning** |
| --- | --- | --- |
| monotonic read | /ˌmɒnəˈtɒnɪk riːd/ | 单调读 |
| read-write splitting | /riːd raɪt ˈsplɪtɪŋ/ | 读写分离 |
| load balancing | /loʊd ˈbælənsɪŋ/ | 负载均衡 |
| replica | /ˈreplɪkə/ | 从库/副本 |
| replication lag | /ˌreplɪˈkeɪʃən læɡ/ | 复制延迟 |
| session stickiness | /ˈseʃən ˈstɪkinəs/ | 会话保持 |
| IP hashing | /ˌaɪ ˈpiː ˈhæʃɪŋ/ | IP哈希 |
| cookie | /ˈkʊki/ | Cookie |
| user-ID-based hash routing | /ˈjuːzər aɪ diː beɪst hæʃ ˈruːtɪŋ/ | 基于用户ID的哈希路由 |
| pinned replica | /pɪnd ˈreplɪkə/ | 固定从库 |
| load balancer | /loʊd ˈbælənsər/ | 负载均衡器 |
| failover | /ˈfeɪloʊvər/ | 故障切换 |
| master | /ˈmæstər/ | 主库 |
| fallback | /ˈfɔːlbæk/ | 降级/回退 |
| replication position | /ˌreplɪˈkeɪʃən pəˈzɪʃən/ | 复制位点 |
| binlog | /ˈbɪnlɒɡ/ | 二进制日志 |
| offset | /ˈɒfset/ | 偏移量 |
| relay log | /ˈriːleɪ lɒɡ/ | 中继日志 |
| replay | /ˈriːpleɪ/ | 回放 |
| timeout | /ˈtaɪmaʊt/ | 超时 |
| P99 | /piː ˈnaɪnti naɪn/ | 第99百分位 |
| stale data | /steɪl ˈdeɪtə/ | 陈旧数据 |
| consistency | /kənˈsɪstənsi/ | 一致性 |
| read path | /riːd pæθ/ | 读路径 |
| failover window | /ˈfeɪloʊvər ˈwɪndoʊ/ | 故障切换窗口 |

---

## 句式提炼

| **功能** | **英文句式** | **适用场景** |
| --- | --- | --- |
| 描述问题背景 | *"Users complained their orders sometimes appear and sometimes disappear. You traced it to read-write splitting plus load balancing."* | 引出技术问题 |
| 否定候选方案 | *"IP hashing and cookies both fail. IP hashing breaks when the user switches networks; cookies can be cleared or tampered with."* | 排除不靠谱方案 |
| 提出主方案 | *"We chose user-ID-based hash routing. All read requests from the same user are pinned to the same replica."* | 说明核心路由策略 |
| 描述故障降级 | *"As soon as we detect the pinned replica is unavailable, we redirect the user's reads to the master."* | 解释降级读主库 |
| 解释位点检查 | *"The position is a binlog file plus an offset. If the replica's position is less than X, it waits for replay until catching up."* | 说明位点等待机制 |
| 给出超时兜底 | *"We set a 200ms timeout. If it fires, we fall back to the master and never return stale data."* | 说明超时后的兜底策略 |

---

## 阅读理解题

1. Why do IP hashing and cookie-based sticky sessions fail to guarantee that the same user always reads from the same replica?

   **Answer:** IP hashing breaks when the user switches networks (e.g., from WiFi to 4G). Cookies can be cleared or tampered with, making them unreliable for maintaining a stable replica routing.

2. What routing strategy did the candidate ultimately choose, and why is it more stable?

   **Answer:** They chose user-ID-based hash routing, which pins all read requests from the same user to the same replica. It remains stable across network changes because the routing key is the user ID, not the IP or a cookie.

3. How does the system preserve monotonic reads when the pinned replica fails or lags too far behind?

   **Answer:** When the pinned replica is unavailable or its replication lag exceeds one second, the system redirects that user's reads to the master until the replica recovers. The master is always up to date, so monotonic read is preserved.

4. Explain how binlog position checking works in the context of replica lag.

   **Answer:** The position is a binlog file plus an offset (e.g., `mysql-bin.000123:4567`). When a request hits a different replica, that replica compares its current position with the position the user last saw. If its position is smaller, it waits for replication to catch up before returning data.

5. What happens if the replica waits too long to catch up? What is the timeout, and what is the fallback?

   **Answer:** They set a 200-millisecond timeout, roughly twice the P99 replica lag. If the replica does not catch up within that time, the system falls back to the master. It never returns stale data.

---

*Word count (dialogue): ~482 words*  
*Level: Intermediate / T2*
