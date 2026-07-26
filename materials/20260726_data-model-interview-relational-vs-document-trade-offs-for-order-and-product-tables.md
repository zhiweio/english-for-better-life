# 【中级】Data Model Interview: Relational vs. Document — Trade-offs for Order and Product Tables

**技术等级：** T2 · **英语等级：** 中 · **字数：** ~500

**Source:** Interview / System Design  
**Level:** T2 / Intermediate  
**Role:** Interviewer, Candidate (2–5 years backend engineer)  
**Estimated Words:** ~482

---

## 故事 Prompt 及故事

```jsx
请根据以下系统设计知识点生成一个中文技术故事，用于后续英语教学。

知识点：[1.4 数据模型]
故事形式：一段面试场景对话，对话双方是面试官和候选人。
技术要求：T2难度（方案对比级），适合2-5年经验后端工程师。
故事冲突设定：
候选人设计订单系统，订单表用关系型数据库，商品表用文档型（MongoDB）。面试官追问：为什么订单用关系型而不用文档型？你是在意 Schema 约束还是别的？

面试官追问链（必须严格遵循）：

1. "订单有固定的结构——买家ID、金额、状态——用文档型也能存。你说关系型强制 Schema 保证数据一致性，但业务变更时，加字段要走 DDL 流程，慢而且锁表。文档型直接写新字段，更灵活。你为什么不选灵活那个？"
2. "你说关系型支持 JOIN，订单和商品多对多查询方便。但如果用文档型，你可以把订单和商品嵌套存储，一次查询全拿出来，不用 JOIN。你的查询模式是什么？单次查询订单详情多，还是按商品维度统计销量多？哪个更影响选型？"
3. "如果你选关系型，商品属性的变化（比如新增'颜色'字段）会导致频繁改表结构。你说用扩展字段（比如 JSON 列）解决，那这和不设 Schema 有什么区别？你是在用关系型的壳做文档型的事吗？"

【必须覆盖的核心概念】（来自核心层）：

- Schema 强制 vs 无 Schema
- 嵌套数据的表达
- 两种模型在查询模式下的优劣

【可选延伸概念】（来自扩展层，T2 可不强制要求）：

- 图数据模型简介（仅概念）

候选人的回答要求：

- 给出订单用关系型、商品用文档型的选型理由（至少两个对比维度）
- 说明 Schema 强制在数据一致性上的价值，以及灵活性在商品迭代上的价值
- 解释 JSON 列与纯文档型在查询和维护上的差异

要求：故事简短，纯对话形式，字数350字。
生成完故事后，请用1-2句话说明你是如何通过追问实现方案对比深度的。
```

---

## Background

### 文章技术干点

这段面试对话深入探讨了数据库选型的核心权衡，特别是在电商核心链路中，如何在"数据正确性"与"模型灵活性"之间做取舍。候选人没有盲目选择某种数据库，而是根据业务场景将不同的存储模型用在了最合适的地方。

---

### 1. 事务与数据正确性：为什么订单用关系型数据库

面试官的第一个问题很直接：订单能不能也用 MongoDB？

- **候选人的核心论点**：创建订单、扣库存、更新支付状态必须在一个原子事务里完成。关系型数据库的 ACID 事务成熟、简单，且在高并发下比 MongoDB 的多文档事务延迟更低、冲突率更小。
- **Schema 校验作为安全网**：候选人补充了一个生产环境很常见的故障场景——有人误把字符串写进金额字段。关系型数据库会直接拒绝，而 MongoDB 会静默接受，等到跑财务报表时才发现金额计算全部报错。这就是 Schema 的价值：**在数据入库时就发现问题，而不是在报表查不出数时再追查**。
- **DDL 风险的可控性**：面试官追问 ALTER TABLE 锁表的问题，候选人回应已使用 `pt-online-schema-change` 在线变更工具，通过影子表+触发器+分批复制的方式完成 DDL，全程不阻塞业务。因此"变更不灵活"的代价是可控的，而数据正确性的收益是不可替代的。

---

### 2. 灵活性的代价：为什么产品信息用 MongoDB

面试官追问：如果文档型数据库更灵活，为什么不用？

- **候选人的反直觉回答**：灵活性的代价是可靠性被破坏。文档型数据库没有 Schema 约束，数据的正确性完全依赖应用层代码。一旦代码有 Bug，脏数据就会进入数据库，所有下游系统（报表、推荐、风控）全部受影响。这就是"沉默的腐败"。
- **产品信息的天然适配**：产品有大量可选属性（颜色、尺码、标签），如果用关系型数据库，只能选择"宽表满屏空值"或"复杂的 EAV 模型"。文档型数据库的嵌套结构能很自然地表达这种参差不齐的属性集合。

---

### 3. 方案选择：用 JSON 列实现"有边界的灵活性"

面试官继续追问：产品属性经常变（比如新加"颜色"字段），关系型数据库怎么办？

- **候选人的方案**：使用关系型数据库的 JSON 列来存储可选属性。但这里有一个与纯文档型数据库的关键区别：
  - **核心字段**（价格、库存）依然是普通关系列，享有完整约束和索引。
  - **非关键字段**（颜色、标签等）放入 JSON 列，获得灵活性。
- **本质**：这不是"用 JSON 列模拟文档型数据库"，而是在关系型数据库的强制约束内，开了一个灵活性的口子。**核心数据的正确性依然由 Schema 保障，只有边缘属性允许灵活扩展**。纯文档型数据库没有这种"分级保障"机制。

---

### 4. 查询模式驱动数据组织方式

面试官提出：文档型数据库可以把订单详情嵌套在订单文档里，一次读取搞定，为什么还要 JOIN？

- **候选人的解释**：这是由查询模式决定的。
  - **产品信息**用文档模型，因为产品属性参差不齐，嵌套结构天然合适。
  - **订单与产品的关联**用的是"快照 ID"，而不是嵌套。因为核心查询模式是按订单 ID 查详情，不是按产品维度做聚合。如果嵌套，产品属性变更时会引发大规模的订单文档刷新。
- **关键设计**：订单里只存产品的快照 ID，订单详情页去产品库拉取当前最新信息。这让订单和产品各自独立演化，互不拖累。

---

### 总结

这次面试展现的数据库选型逻辑非常务实：

- **订单用关系型数据库**，因为事务和 Schema 是交易数据的底线保障。
- **产品用 MongoDB**，因为嵌套模型能自然地表达参差不齐的属性集合。
- **可选属性用 JSON 列**，在核心数据严格约束的前提下，给边缘字段留出灵活性空间。
- **查询模式决定数据是否嵌套**，按订单 ID 查详情的模式决定了存快照 ID 而非嵌套文档。

核心原则是：**核心交易数据不允许任何灵活性的隐患，辅助信息允许有边界的灵活扩展。** 每一层的技术选择都有明确的故障场景作为支撑，而非仅仅基于理论上的"更灵活"或"更安全"。

---

### pt-online-schema-change 在线变更工具的工作原理

`pt-online-schema-change`（简称 pt-osc）是 Percona Toolkit 中一个专门用于 **在 MySQL 大表上在线执行 DDL 变更而不阻塞业务读写** 的工具。其核心原理可以概括为：**创建一个已应用变更的影子表，通过触发器同步增量数据，分批复制存量数据，最后用原子操作完成表切换**。

#### 1. 背景：直接 ALTER 的问题

在 MySQL 中，直接执行 `ALTER TABLE ... ADD COLUMN` 这类 DDL 语句，通常会获取元数据锁（MDL），并在拷贝数据时可能长时间持有表级锁，阻塞所有读写操作。对于高并发的生产环境，这会造成服务不可用。

#### 2. pt-osc 的工作原理（四个步骤）

**第一步：创建影子表**

- 工具连接到目标数据库，读取原始表（例如 `orders`）的结构。
- 根据你要执行的 `ALTER` 语句（例如 `ADD COLUMN rating_score int default 0`），生成一个**结构已变更的新表**，命名为 `_orders_new`（影子表）。
- 此时影子表是空的，原始表仍然正常对外提供服务。

**第二步：创建触发器，同步增量变更**

- 在原始表上创建三个触发器：`AFTER INSERT`、`AFTER UPDATE`、`AFTER DELETE`。
- 这些触发器的作用是：**任何对原始表的写操作，都会实时同步到影子表**。例如，当你在原始表插入一行时，触发器会在影子表也插入相同数据（并填充新增列的默认值）。
- 从触发器创建的那一刻起，所有新的数据变更都将在影子表中得到体现，**保证增量数据不丢失**。

**第三步：分批复制存量数据**

- 工具会分批将原始表中的**已有数据**复制到影子表。每批通常处理几千行（通过主键范围切分，如 `WHERE id BETWEEN ? AND ?`）。
- 复制过程中，每批数据被插入影子表。由于触发器的作用，这些数据也会带上新增列的默认值（或者根据转换逻辑生成）。
- **关键**：分批复制时使用的是 `LOCK IN SHARE MODE`（共享锁）或类似的弱锁，只锁定正在复制的少量行，且批次之间会休眠（通过 `-sleep` 参数），给其他操作让路。它**不会**长期持有表级锁。
- 工具还会监控数据库负载（如 `Threads_running`）和从库延迟，如果压力过大则自动暂停，确保不影响生产。

**第四步：原子切换**

- 当所有存量数据复制完毕，且增量数据也已追平（触发器仍在工作），pt-osc 会执行一个**原子性的 `RENAME TABLE`** 操作：
  - 将原始表 `orders` 重命名为 `orders_old`（废弃）。
  - 将影子表 `_orders_new` 重命名为 `orders`（接管）。
- `RENAME TABLE` 是 MySQL 中一个极快的元数据操作，它只会短暂地获取元数据锁，但不会复制数据，因此切换瞬间对业务的影响可以忽略不计（通常毫秒级）。
- 切换完成后，pt-osc 会删除触发器和旧表（可选）。

#### 3. 为什么全程不会锁表？

- **读操作**：在整个过程中，原始表一直存在并可读。切换前后应用层访问的表名不变（`orders`），只是在切换瞬间有一个极短的名称交换，查询几乎无感知。
- **写操作**：触发器保证了写操作不会丢失，无论是在存量复制期间还是切换瞬间。切换时因为 `RENAME` 是原子的，要么访问旧表，要么访问新表，不会出现表不存在的窗口。
- **锁粒度**：唯一可能产生阻塞的是 `RENAME TABLE` 时的元数据锁，但它只持续毫秒级。pt-osc 还会设置 `lock_wait_timeout` 来避免长时间等待。
- **分批控制**：存量复制时的行锁是瞬时的，且通过 chunk 和 sleep 机制让出资源，不会升级成表锁。

#### 4. 限制与注意事项

- **必须有主键或唯一索引**：pt-osc 依赖主键进行分批和行级锁定，没有主键的表无法使用。
- **磁盘空间**：影子表需要占用与原表相近的额外空间（取决于新增列的大小），需要提前评估。
- **外键**：处理外键较为复杂，需要额外配置，一般建议业务层处理。
- **触发器开销**：触发器会增加写操作的 CPU 开销，不过 pt-osc 设计得很轻量。
- **不能与其他 pt-osc 并发操作同一张表**。

**一句话总结**：`pt-online-schema-change` 通过"**触发器同步增量 + 分批复制存量 + 原子表重命名**"的三步策略，把一次危险的锁表 DDL 变成了一个安全的、几乎透明的在线变更操作。

---

### EAV 模型解释与示例

**EAV 模型**全称是 **Entity–Attribute–Value（实体–属性–值）模型**，是一种数据建模方式，将数据横向存储为行，而不是常见的列式结构。简单来说，就是把原本应该作为一列存储的数据，变成了一个键值对，存成多行。

这种模型专门用于解决**实体属性极度稀疏、且属性种类经常变化**的场景。但代价是查询会变得非常复杂。

在对话中，候选人提到产品表如果用关系型数据库，要么是"一张满是 NULL 的大宽表"，要么就得用"复杂的 EAV 模型"。这里的关键点在于：**EAV 模型虽然灵活，但会将一个简单的查询变得异常繁琐**。

#### 1. 背景：不同品类的产品需要不同的属性

假设你在设计一个电商产品库，需要存储以下三个产品：

- **一部手机**：有属性 `屏幕尺寸` (6.1) 和 `存储容量` (128GB)。
- **一件T恤**：有属性 `颜色` (黑色) 和 `尺码` (M码)。
- **一袋猫粮**：有属性 `口味` (三文鱼) 和 `重量` (1.5kg)。

可以看到，每个品类的属性和数量完全不同。如果用一张关系型表来存，你会怎么做？

#### 2. 传统宽表的困境

你需要把所有可能的属性都建成列，数据看起来会是这样：

| **product_id** | **name** | **屏幕尺寸** | **存储容量** | **颜色** | **尺码** | **口味** | **重量** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 手机 | 6.1 | 128 | NULL | NULL | NULL | NULL |
| 2 | T恤 | NULL | NULL | 黑色 | M码 | NULL | NULL |
| 3 | 猫粮 | NULL | NULL | NULL | NULL | 三文鱼 | 1.5kg |

可以看到，表里充满了 `NULL`。一旦新增一个品类（比如"桌子"需要"材质"属性），就得执行 `ALTER TABLE` 来添加新列。这就是"大宽表"的问题。

#### 3. EAV 模型的解决方案

EAV 模型不新增列，而是把属性当成数据行来存储。建一张属性表，每一行代表产品的一个属性，结构非常统一：

| **entity_id** | **attribute** | **value** |
| --- | --- | --- |
| 1 | 屏幕尺寸 | 6.1 |
| 1 | 存储容量 | 128 |
| 2 | 颜色 | 黑色 |
| 2 | 尺码 | M码 |
| 3 | 口味 | 三文鱼 |
| 3 | 重量 | 1.5kg |

- `entity_id` (实体ID)：标识是哪个产品（例如 product_id=1）。
- `attribute` (属性)：表示属性的名称。
- `value` (值)：属性的具体内容。

这样设计的好处是**极其灵活**。新增一个"材质"属性，只需要在表中插入一行数据，完全不用修改数据库结构。

#### 4. EAV 模型的代价：为什么它被称为"复杂的"

EAV 的灵活性是用查询复杂度换来的。即使做一个非常简单的查询，也会变得很麻烦。

**场景**：你需要查询"所有黑色、M码的T恤"。

- **传统宽表**的 SQL 非常简单：

```sql
SELECT * FROM products WHERE 颜色 = '黑色' AND 尺码 = 'M码';
```

- **EAV 模型**的 SQL 则需要用自连接或条件聚合来"拼凑"出这个信息，查询可能长这样：

```sql
SELECT p.entity_id
FROM eav_table p
WHERE (p.attribute = '颜色' AND p.value = '黑色')
   OR (p.attribute = '尺码' AND p.value = 'M码')
GROUP BY p.entity_id
HAVING COUNT(*) = 2;
```

仅仅是查出符合两个简单条件的产品，就需要用到 `GROUP BY` 和 `HAVING`。随着属性条件增多，SQL 的复杂度和性能开销会急剧增加。

#### 5. 为什么文档模型是更自然的解法？

这也是对话中候选人选择用文档模型的原因。在 MongoDB 中，每个产品的异构属性可以直接存为一个自包含的文档，结构一目了然：

```json
// 手机
{ "id": 1, "name": "手机", "屏幕尺寸": "6.1", "存储容量": "128GB" }

// T恤
{ "id": 2, "name": "T恤", "颜色": "黑色", "尺码": "M码" }
```

每个文档只存储自己拥有的属性，既没有 NULL 值，也不需要做复杂的跨行 JOIN。这就是文档模型处理"参差不齐"数据时的天然优势。

所以，候选人提到 EAV 模型，正是为了说明：在关系型数据库里追求这种灵活性，写出的查询会非常痛苦，性能也难以保证，从而反衬出文档数据库在此场景下的合理性。

---

### 快照 ID vs 嵌套文档：查询模式驱动数据组织

这段话解释了为什么在订单和产品之间，选择"存储引用ID"而不是"嵌套整个文档"。**核心原因是查询模式驱动了数据组织方式**，而"各取所长"意味着让每个模型做它最擅长的事。

我们可以从"存什么"、"怎么查"、"为什么这样更好"三个层面来理解。

#### 1. 存什么：快照ID vs 嵌套文档

假设一个订单包含一部手机和一件T恤。

- **嵌套文档的做法**：把产品信息直接塞进订单文档里。

```json
{
  "order_id": "1001",
  "items": [
    { "product_id": "P1", "name": "手机", "price": 4999, "color": "黑色" },
    { "product_id": "P2", "name": "T恤", "price": 199, "size": "M" }
  ]
}
```

- **候选人"存快照ID"的做法**：订单里只保留产品的唯一标识。

```json
{
  "order_id": "1001",
  "items": [
    { "product_id": "P1", "price_snapshot": 4999 },
    { "product_id": "P2", "price_snapshot": 199 }
  ]
}
```

产品名称、颜色、尺码等详细信息，都通过 `product_id` 去产品库（MongoDB）单独查询。

#### 2. 怎么查：主查询模式决定数据结构

候选人明确指出："我们的主查询模式是按订单ID查询订单详情，而不是按产品维度做聚合。"

- **查订单详情的流程**：
  1. 用 `order_id` 在订单库（关系型DB）快速查到订单记录，拿到商品ID列表。
  2. 用这些商品ID，去产品库（MongoDB）一次性查出所有相关产品的详细信息。
  3. 在应用层将两部分数据拼装，返回完整订单详情。
- **为什么不做产品维度的聚合**：如果业务上不需要频繁回答"某款黑色手机都被谁买走了"这类问题，就没有必要把产品信息冗余到订单里。按订单ID点查是最高效的路径。

#### 3. 为什么这样更好：各取所长

这个设计让每种数据库都发挥了自己的核心优势，同时避免了各自的问题。

**如果强行嵌套，会带来两个大麻烦：**

1. **级联更新的噩梦**：产品信息（比如标题、图片）是会变更的。如果变更了某款商品的主图，所有包含该商品的历史订单都必须更新，这会引发一次超大规模的写入操作，对性能影响巨大。存ID则完全规避了这个问题——产品信息变化，订单侧毫无感知。
2. **事务与一致性**：订单的核心在于创建时的原子性和数据正确性，这是关系型数据库的强项。如果把灵活多变的产品信息也混进来，会让订单模型变得臃肿、耦合，既破坏了交易数据的严谨性，也失去了产品信息的灵活性。

**"各取所长"体现在：**

- **关系型数据库（订单）**：发挥 **ACID事务** 和 **Schema约束** 的强项，保证交易数据的绝对正确和一致。
- **文档型数据库（产品）**：发挥 **嵌套结构** 和 **动态Schema** 的强项，灵活应对海量SKU的参差不齐的属性，避免EAV模型或大宽表的查询痛苦。

**总结来说，这个设计是：通过ID解耦，让交易数据保持严谨，让产品数据保持灵活，在查询时按需组装。** 这比试图用一种模型解决所有问题的"大一统"架构，要务实和高效得多。

---

## 角色及场景

**Interviewer (面试官):** 追问候选人为何在订单系统中混合使用关系型和文档型数据库，深入挑战其 Schema 设计、事务需求、查询模式及灵活性边界。

**Candidate (候选人):** 2-5年经验后端工程师，负责订单系统数据模型设计，需清晰阐述选型理由、对比维度和折中方案。

**场景:** 面试。候选人描述其订单系统将订单表放在关系型数据库，商品表放在 MongoDB（文档型）。面试官针对为何不统一为文档型、Schema 变更风险、嵌套查询优势和 JSON 列的使用边界进行多轮追问。

---

## 面试对话 (中级，正文约 482 词)

**Interviewer:**

**You put the order table in a relational DB and the product table in MongoDB**. **Why not use a document store for orders too?** Is schema enforcement your main reason, or is there something else?

**Candidate:**

The primary driver is transactional consistency. Creating an order, deducting inventory, and updating payment status all have to happen inside a single atomic transaction. A relational database gives you ACID out of the box—a simple `BEGIN; UPDATE orders; UPDATE inventory; COMMIT;` does the job. Document databases have weaker cross‑collection transaction support. Even though MongoDB has offered multi‑document transactions since 4.0, they come with higher latency and conflict rates compared to a relational DB. **I chose relational mainly for transactions; the strict schema is a bonus, not the primary factor.**

**Interviewer:**

But when business requirements change, **adding a column in a relational DB** means running `ALTER TABLE`, which can lock the table and risk downtime. A document store lets you write new fields directly—much more flexible. Why not pick the flexible option?

**Candidate:**

Flexibility has a cost. Imagine someone accidentally writes a string into the order amount field. A document store silently accepts it, and later your revenue reports explode. A relational DB rejects the write immediately—that's the value of schema enforcement: **catching errors at the entry point.** As for DDL risk, **we use `pt-online-schema-change` to apply schema changes online without locking tables, so the business isn't disrupted**. Between flexibility and safety, I pick safety for core transactional data.

**Interviewer:**

You also mentioned that relational DBs support JOINs. But with a document store, you could nest order items inside the order document and fetch everything in one read, no JOIN needed. What does your query pattern look like? Do you query order details more often, or product‑level aggregations?

**Candidate:**

That's exactly why I chose a document model for products. A product has dozens of optional attributes—color, size, tags—and a relational DB would force me into either a wide table full of NULLs or a complex EAV model. A document store handles nested attributes naturally. But for orders and products, we don't nest—orders store only a snapshot ID of the product. **Our main query pattern is fetching order details by order ID,** not aggregation by product dimension. **So each model plays to its strength**.

**Interviewer:**

**Product attributes change frequently—say you need a new "color" field. How does your relational DB handle that?**

**Candidate:**

We use a JSON column for optional attributes. But here's the difference from a pure document store: the JSON column is only for flexible, non‑critical fields. Core columns like price and stock remain regular relational columns with full constraints and indexing. In a pure document store, there's no schema at all—validation relies entirely on application code. One bug and your data gets dirty. **A relational JSON column gives you bounded flexibility**.

---

## 词汇表 (25个高频技术词汇)

| **Vocabulary** | **Pronunciation (IPA)** | **Chinese Meaning** |
| --- | --- | --- |
| relational database | /rɪˈleɪʃənəl ˈdeɪtəbeɪs/ | 关系型数据库 |
| document store | /ˈdɒkjʊmənt stɔːr/ | 文档型数据库 |
| transactional consistency | /trænˈzækʃənəl kənˈsɪstənsi/ | 事务一致性 |
| ACID | /ˈæsɪd/ | 原子性、一致性、隔离性、持久性 |
| atomic transaction | /əˈtɒmɪk trænˈzækʃən/ | 原子事务 |
| cross‑collection transaction | /krɒs kəˈlekʃən trænˈzækʃən/ | 跨集合事务 |
| latency | /ˈleɪtənsi/ | 延迟 |
| schema enforcement | /ˈskiːmə ɪnˈfɔːrsmənt/ | Schema 强制 |
| DDL (Data Definition Language) | /ˌdiː diː ˈel/ | 数据定义语言 |
| ALTER TABLE | /ˈɔːltər ˈteɪbəl/ | 修改表结构 |
| pt-online-schema-change | /ˌpiː tiː ˈɒnlaɪn ˈskiːmə tʃeɪndʒ/ | 在线 DDL 工具 |
| table locking | /ˈteɪbəl ˈlɒkɪŋ/ | 表锁定 |
| flexibility | /ˌfleksɪˈbɪləti/ | 灵活性 |
| revenue report | /ˈrevənjuː rɪˈpɔːrt/ | 营收报表 |
| nested document | /ˈnestɪd ˈdɒkjʊmənt/ | 嵌套文档 |
| JOIN | /dʒɔɪn/ | 表连接 |
| EAV (Entity-Attribute-Value) | /ˌiː eɪ ˈviː/ | 实体-属性-值模型 |
| JSON column | /ˈdʒeɪsən ˈkɒləm/ | JSON 列 |
| constraint | /kənˈstreɪnt/ | 约束 |
| index | /ˈɪndeks/ | 索引 |
| data validation | /ˈdeɪtə ˌvælɪˈdeɪʃən/ | 数据校验 |
| application layer | /ˌæplɪˈkeɪʃən ˈleɪər/ | 应用层 |
| schema-less | /ˈskiːmə les/ | 无 Schema |
| snapshot | /ˈsnæpʃɒt/ | 快照 |
| trade‑off | /ˈtreɪd ɒf/ | 权衡 |

---

## 句式提炼

| **功能** | **英文句式** | **适用场景** |
| --- | --- | --- |
| 陈述主因 | *"The primary driver is X. Y is a bonus, not the primary factor."* | 说明选型关键因素 |
| 对比事务支持 | *"A relational DB gives you ACID out of the box—a simple transaction does the job. Document databases have weaker cross‑collection transaction support."* | 解释为何选关系型保证事务 |
| 说明灵活性代价 | *"Flexibility has a cost. A document store silently accepts bad data; a relational DB rejects it immediately."* | 强调 Schema 强制的价值 |
| 描述查询模式 | *"Our main query pattern is X, not Y. So each model plays to its strength."* | 说明根据查询模式选型 |
| 对比 JSON 列与纯文档 | *"A relational JSON column gives you bounded flexibility—core columns still have full constraints."* | 区分有限灵活与全局无 Schema |

---

## 阅读理解题

1. Why did the candidate choose a relational database for the order table instead of a document store?

   **Answer:** Because orders require transactional consistency across multiple tables (order, inventory, payment). A relational DB provides ACID transactions natively, while document store cross‑collection transactions have higher latency and conflict rates.

2. How does the candidate handle the risk of `ALTER TABLE` locking when adding new columns in production?

   **Answer:** They use `pt-online-schema-change` to apply schema changes online without locking the table, so the business continues to operate normally.

3. What is the main advantage of storing product information in a document database?

   **Answer:** Products have many optional attributes (color, size, tags). A document store can nest these attributes naturally, avoiding wide tables full of NULLs or complex EAV models.

4. How does the candidate handle frequently changing product attributes like "color" in the relational database?

   **Answer:** They use a JSON column for flexible optional attributes while keeping core fields like price and stock in regular columns with full constraints and indexes.

5. What is the candidate's main argument against using a pure document store for orders?

   **Answer:** A pure document store lacks schema enforcement at the database level; it relies entirely on application code for validation, which risks dirty data if a bug occurs. A relational DB rejects invalid writes at the entry point.

---

*Word count (dialogue): ~482 words*  
*Level: Intermediate / T2*
