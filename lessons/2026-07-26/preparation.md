这份预习材料**不用 material 原文**，概念全部用自己的话复述。每个概念的「用自己的话理解」提供**中英双语**（英文按 **B2**）。长句练习的重点是**嵌套从句**——定语从句、状语从句、非限制性从句叠在一起练。

---

## 课前 3 分钟：今天讲什么

**话题：** 数据模型选型——订单系统里订单表放关系型、商品表放 MongoDB，怎么回答「为什么不统一用一种数据库」？

**四条主线（material 技术干点）：**

```
① 事务与正确性 → ② 商品灵活性 → ③ JSON 有边界扩展 → ④ 查询模式决定嵌套
```

**故事线：**

```
混合存储方案 → 追问为何订单不用文档型 → 追问 DDL 锁表 → 追问嵌套 vs JOIN → 追问 JSON 列是不是假关系型
```


| 存储          | 选型理由                    | 关键设计                 |
| ----------- | ----------------------- | -------------------- |
| 订单（关系型）     | ACID 原子事务 + Schema 入库校验 | 下单 / 扣库存 / 改支付状态同一事务 |
| 商品（MongoDB） | 异构属性、嵌套结构自然             | 避免宽表 NULL 或 EAV 复杂查询 |
| 订单↔商品       | 存快照 ID，不嵌套全文            | 主查询是按 order ID 查详情   |
| 可选属性        | 关系型 JSON 列              | 价格/库存仍走普通列 + 约束 + 索引 |



| 关系型赢在哪             | 文档型赢在哪          |
| ------------------ | --------------- |
| 多表 ACID、类型约束、报表可信  | SKU 属性参差不齐、结构常变 |
| DDL 可用 pt-osc 在线变更 | 嵌套文档表达异构字段更直观   |


**规律：** 核心交易数据要**正确性底线**；辅助/异构数据允许**有边界的灵活**——选型看事务需求、Schema 价值、查询模式，不是「谁更灵活」。

---



## 概念 1：订单为何用关系型——事务与 Schema



### 用自己的话理解（中英双语）

**中文：**

面试开场，候选人把订单放 MySQL、商品放 MongoDB。面试官第一个问题很尖：订单结构也固定（买家 ID、金额、状态），文档型一样能存——你是为了 Schema 约束才选关系型吗？

候选人的主因其实是**事务一致性**：创建订单、扣库存、更新支付状态必须在同一个原子事务里完成。关系型数据库一条 `BEGIN … COMMIT` 就能跨多表保证 ACID；MongoDB 虽然 4.0 起支持多文档事务，但延迟更高、冲突率更大，不适合高并发交易链路。

Schema 强制是**加分项**而非主因：有人把字符串写进金额字段，关系型直接拒绝写入，文档型会静默收下，等跑营收报表才发现全错——价值在于**入库时就拦住脏数据**。至于「加列要 ALTER、会锁表」，团队用 `pt-online-schema-change` 做在线 DDL，影子表 + 触发器 + 分批复制，把灵活性代价压到可控；交易数据的正确性收益则不可替代。

**English (B2):**

In the interview, the candidate places orders in a relational database **while** storing products in MongoDB. The interviewer asks whether schema enforcement is the real reason — **since** order fields such as buyer ID, amount, and status look fixed enough **to fit** a document model.

The candidate's **primary driver** is **transactional consistency**: creating an order, deducting inventory, and updating payment status must happen inside a single atomic transaction. A relational database can wrap these updates in one ACID transaction with a simple `BEGIN … COMMIT`, **whereas** MongoDB's multi-document transactions, **which** became available in version 4.0, still carry higher latency and conflict rates **that** make them less attractive for high-concurrency checkout paths.

Strict schema is a **bonus, not the main factor**. If someone accidentally writes a string into the amount field, a relational database rejects the write immediately, **whereas** a document store may accept it silently **until** revenue reports break — **which** shows the value of catching errors **at the entry point**. As for DDL risk, the team uses `pt-online-schema-change` **to apply** schema changes online, **so that** the flexibility penalty stays manageable **while** the correctness benefit for core transactional data remains non-negotiable.

### 关键词（B2）


| 英文                           | 中文              | 带从句的例句                                                                                              |
| ---------------------------- | --------------- | --------------------------------------------------------------------------------------------------- |
| transactional consistency    | 事务一致性           | Transactional consistency means updates **that** must succeed or fail together.                     |
| atomic transaction           | 原子事务            | An atomic transaction is a unit of work **in which** either all steps commit or none do.            |
| ACID                         | 原子性/一致性/隔离性/持久性 | ACID is a set of guarantees **that** relational databases provide out of the box.                   |
| schema enforcement           | Schema 强制       | Schema enforcement rejects invalid writes **that** would corrupt downstream reports.                |
| cross-collection transaction | 跨集合事务           | Cross-collection transactions are harder **when** latency and conflict rates matter.                |
| entry point                  | 入库点             | Catching errors at the entry point stops bad data **before** it reaches analytics.                  |
| DDL                          | 数据定义语言          | DDL changes, **such as** `ALTER TABLE`, can block production **if** they are not managed carefully. |
| pt-online-schema-change      | 在线 DDL 工具       | pt-osc is a tool **that** applies DDL **without** long table locks.                                 |




### 嵌套从句练习：说为何订单用关系型

**Layer 1：**

> Orders need ACID transactions across multiple tables.

**Layer 2 — 加定语从句：**

> Orders are data **that** require ACID transactions across multiple tables, **which** a relational database handles more naturally **than** a document store.

**Layer 3 — 加对比从句：**

> **Although** MongoDB supports multi-document transactions, I chose a relational database for orders **because** checkout paths need atomic updates **that** span inventory and payment tables, **whereas** document-store transactions tend to have higher latency **that** hurts throughput under load.

**Layer 4 — 完整嵌套版：**

> The primary driver for putting orders in a relational database is transactional consistency — **meaning** that creating an order, deducting stock, and updating payment status must commit inside one atomic transaction **that** relational engines support with mature ACID guarantees, **whereas** cross-collection transactions in document stores, **which** are available but slower and more conflict-prone, are a weaker fit for the checkout path **where** correctness matters more **than** schema flexibility.

**中文对照：** 订单放关系型的主因是事务一致性——下单、扣库存、改支付状态必须在同一原子事务里提交，关系型引擎用成熟的 ACID 保证这一点；文档库的跨集合事务虽有，但更慢、更易冲突，在正确性优先于 Schema 灵活性的结账链路上是更弱的选择。

---



## 概念 2：商品为何用文档型——异构属性与 EAV



### 用自己的话理解（中英双语）

**中文：**

面试官接着挑战：文档型更灵活，商品属性又经常变，为什么订单要死板、商品却可以灵活？

这里要分清两层。对**订单**来说，灵活性的代价是可靠性：无 Schema 时校验全靠应用代码，一个 Bug 脏数据就进库，报表、推荐、风控全受影响——这叫「沉默的腐败」。核心交易数据不能赌应用层永远没错。

对**商品**来说，灵活性反而是刚需：手机有屏幕尺寸、T 恤有颜色尺码、猫粮有口味重量，属性集合参差不齐。关系型只有两条路——**宽表**满屏 NULL，每加品类就要 ALTER；或 **EAV 模型**把属性拆成行，查「黑色 M 码 T 恤」得 `GROUP BY` + `HAVING`，查询又复杂又慢。文档型让每个 SKU 自带嵌套属性，没有 NULL 洪水，也没有跨行拼凑。

所以不是「文档型 universally 更好」，而是**商品这种异构、稀疏、常变的模型**，文档嵌套更自然。

**English (B2):**

The interviewer then challenges the split: **if** document stores are more flexible, **why** keep orders strict **while** products enjoy schema-less freedom?

The answer depends on **what** you are storing. For **orders**, flexibility has a cost: **without** database-level schema, validation lives entirely in application code, **and** one bug can let dirty data into storage **that** poisons reports, recommendations, and risk controls — **a failure mode** **that** teams sometimes call silent corruption. Core transactional data cannot rely on the hope **that** application code will never slip.

For **products**, flexibility is a genuine requirement. A phone has screen size, a T-shirt has colour and size, and pet food has flavour and weight — **a set of attributes that** varies by category. In a relational model, you either build a **wide table** **that** is full of NULLs **and** needs a new column for every new attribute, **or** you adopt an **EAV model** **in which** each attribute becomes a row, **which** turns a simple filter like "black, size M" into a `GROUP BY` / `HAVING` puzzle. A document store lets each SKU carry **only** the fields it needs in a nested structure, **without** NULL floods or painful row pivots.

So the point is not that document databases are universally better, **but that** heterogeneous, sparse, fast-changing product data is **where** nested documents play to their strength.

### 关键词（B2）


| 英文                       | 中文        | 带从句的例句                                                                                          |
| ------------------------ | --------- | ----------------------------------------------------------------------------------------------- |
| heterogeneous attributes | 异构属性      | Products have heterogeneous attributes **that** differ by category.                             |
| wide table               | 宽表        | A wide table is a design **where** most columns are NULL for most rows.                         |
| EAV model                | 实体-属性-值模型 | The EAV model stores attributes as rows, **which** makes simple filters hard to write.          |
| nested document          | 嵌套文档      | A nested document holds related fields **that** belong to one product.                          |
| schema-less              | 无 Schema  | A schema-less store accepts new fields **without** a DDL migration.                             |
| silent corruption        | 沉默的数据腐败   | Silent corruption happens **when** bad data enters storage **that** no one notices immediately. |
| sparse data              | 稀疏数据      | Sparse data is common in catalogues **where** each SKU has different optional fields.           |




### 案例对比表


| 方案  | 加「颜色」属性          | 查「黑色 M 码 T 恤」         |
| --- | ---------------- | --------------------- |
| 宽表  | `ALTER TABLE` 加列 | 简单 `WHERE`            |
| EAV | 插一行即可            | `GROUP BY` + `HAVING` |
| 文档型 | 文档里直接写字段         | 按嵌套字段过滤               |




### 嵌套从句练习：说商品为何用文档型

**Layer 2：**

> Products have optional attributes **that** vary by category, **so** a document model fits better **than** a wide relational table.

**Layer 3：**

> **Because** each product category needs a different set of optional attributes, a relational design forces you into either a wide table **that** is full of NULLs **or** an EAV model **in which** even simple queries require `GROUP BY` and `HAVING`, **whereas** a document store can nest **only** the fields **that** each SKU actually has.

**Layer 4 — 完整嵌套版：**

> I put products in MongoDB **not because** I want schema-less freedom everywhere, **but because** catalog data is heterogeneous and sparse — **meaning** that a phone, a T-shirt, and a bag of pet food each need different attribute sets **that** would either waste columns in a wide table **or** explode into rows in an EAV model, **which** is why nested documents, **where** each SKU stores just its own fields, are a more natural fit **than** forcing every attribute into relational rows.

**中文对照：** 商品放 MongoDB 不是因为到处都要无 Schema，而是目录数据异构且稀疏——手机、T 恤、猫粮各自需要不同属性集，宽表会浪费列，EAV 会把查询炸成行聚合；嵌套文档让每个 SKU 只存自己的字段，比把所有属性硬塞进关系行更自然。

---



## 概念 3：JSON 列——有边界的灵活性



### 用自己的话理解（中英双语）

**中文：**

面试官最后一击很毒：你说关系型加 JSON 列存可选属性，那和不设 Schema 有什么区别？是不是用关系型的壳干文档型的事？

候选人的边界很清楚：**分级保障**。价格、库存这类核心字段仍是普通关系列，有类型约束、索引、NOT NULL；颜色、标签等边缘属性才进 JSON 列。纯文档型是全局无 Schema，校验 100% 靠应用层，一个 Bug 整库都可能脏。

JSON 列的本质不是「假装文档数据库」，而是在**强制约束的框架里**给非关键字段开一个小口子——核心正确性仍由 Schema 兜底，边缘字段才允许快速扩展。这是 **bounded flexibility（有边界的灵活）**，和「整表 schema-less」不是一回事。

**English (B2):**

The interviewer's final challenge is sharp: **if** you store optional attributes in a JSON column, **how** is that different from having no schema at all — **are** you just using a relational shell **to do** document-style storage?

The candidate draws a clear boundary: **tiered protection**. Core fields such as price and stock remain ordinary relational columns **that** carry type constraints, indexes, and `NOT NULL` rules, **whereas** edge attributes like colour or tags live in a JSON column **that** allows faster iteration. In a pure document store, there is no schema at the database level at all, **which** means validation depends entirely on application code — **and** one bug can dirty the entire collection.

A JSON column is not a fake document database. It is **bounded flexibility inside** a schema-enforced framework: critical correctness still has a safety net, **while** only non-critical fields get a flexible extension point. That is fundamentally different from making the whole table schema-less.

### 关键词（B2）


| 英文                           | 中文      | 带从句的例句                                                                                                      |
| ---------------------------- | ------- | ----------------------------------------------------------------------------------------------------------- |
| JSON column                  | JSON 列  | A JSON column stores semi-structured fields **that** change often.                                          |
| bounded flexibility          | 有边界的灵活性 | Bounded flexibility keeps strict rules on core columns **while** relaxing edge fields.                      |
| constraint                   | 约束      | Constraints are rules **that** the database enforces on write.                                              |
| non-critical field           | 非关键字段   | Non-critical fields are attributes **whose** errors would not break checkout.                               |
| tiered protection            | 分级保障    | Tiered protection means core data stays strict **where** edge data can evolve.                              |
| application-layer validation | 应用层校验   | Application-layer validation fails **when** a bug bypasses checks **that** the database no longer provides. |




### 嵌套从句练习：区分 JSON 列与纯文档型

**Layer 2：**

> Core columns keep full constraints, **while** the JSON column holds optional attributes **that** change frequently.

**Layer 3：**

> **Although** a JSON column looks like document storage, price and stock remain regular columns **that** have indexes and constraints, **whereas** in a pure document store every field depends on application code **that** may fail to validate types correctly.

**Layer 4 — 完整嵌套版：**

> A relational JSON column gives you bounded flexibility — **meaning** that fields **which** directly affect money and inventory stay as strict relational columns **that** the database can reject **if** they are invalid, **whereas** optional attributes **that** change often can live in JSON, **which** is a very different trade-off from a schema-less document **where** one application bug can let dirty data into every field **that** downstream systems trust.

**中文对照：** 关系型 JSON 列提供的是有边界的灵活——直接影响资金和库存的字段仍是带索引和约束的严格关系列，数据库能在非法时拒绝；常变的可选属性才放 JSON。这与整库无 Schema、一个应用 Bug 就可能让所有下游信任的字段都变脏，是完全不同的权衡。

---



## 概念 4：查询模式驱动数据组织——快照 ID vs 嵌套



### 用自己的话理解（中英双语）

**中文：**

面试官第三问换角度：文档型可以把订单项嵌进订单文档，一次读全，何必 JOIN？

候选人回答的关键是**查询模式**。商品用文档型，因为属性参差不齐、嵌套自然。但订单和商品之间**不嵌套全文**——订单行里只存 `product_id` 和 `price_snapshot`，详情页再用 ID 去 MongoDB 批量拉商品信息，应用层拼装。

主查询是「按 order ID 查订单详情」，不是「按商品维度聚合销量」。若把商品全文嵌进订单，商品标题或主图一改，所有历史订单文档都要批量刷新——级联更新噩梦。存 ID 则订单与商品各自演化：产品库随便迭代，订单侧无感。

这是「各取所长」：关系型扛交易事务，文档型扛异构目录，用 ID 解耦、按查询模式组装。

**English (B2):**

The interviewer shifts angle: **with** a document store, you could nest order line items inside the order document and fetch everything in one read — **so why** bother with joins or separate lookups?

The candidate's answer hinges on **query patterns**. Products use a document model **because** their attributes are uneven and nest naturally. **But** the link between orders and products is **not** a full nested copy: each order line keeps a `product_id` and a `price_snapshot`, **and** the detail page loads product fields from MongoDB in batch **before** the application assembles the response.

The dominant access path is "fetch order details by order ID", **not** "aggregate sales by product dimension". **If** you embedded full product documents inside every order, a change to a product title or image would force a massive rewrite of historical order documents — **a cascade update** **that** is expensive and unnecessary. Storing IDs decouples evolution: the catalog can change freely **while** order records stay stable.

That is "each model plays to its strength": relational storage for transactional integrity, document storage for heterogeneous catalog data, **with** IDs **that** let the system assemble views **according to** how it is actually queried.

### 关键词（B2）


| 英文             | 中文    | 带从句的例句                                                                                |
| -------------- | ----- | ------------------------------------------------------------------------------------- |
| query pattern  | 查询模式  | Query pattern is the way **in which** the application most often reads data.          |
| snapshot ID    | 快照 ID | A snapshot ID points to a product **without** copying its whole document.             |
| price snapshot | 价格快照  | A price snapshot records the amount **that** was charged at checkout time.            |
| cascade update | 级联更新  | A cascade update rewrites many documents **when** one product field changes.          |
| decouple       | 解耦    | IDs decouple orders from products **so that** catalog changes do not touch history.   |
| assemble       | 拼装    | The service assembles the response **after** it loads orders and products separately. |




### 嵌套从句练习：说为何不嵌套商品全文

**Layer 2：**

> Our main query is by order ID, **not** by product, **so** we store snapshot IDs **instead of** nesting full product documents.

**Layer 3：**

> **Because** we mostly fetch order details by order ID, we keep only product IDs and price snapshots in the order store, **which** means we can load product attributes from MongoDB in one batch **without** rewriting historical orders **when** a product image changes.

**Layer 4 — 完整嵌套版：**

> **Although** nesting product documents inside an order would avoid a second lookup, our main query pattern is order-centric rather than product-centric, **which** means storing snapshot IDs is safer **because** catalog fields **that** change frequently would otherwise trigger cascade updates across every historical order **that** referenced them — **a cost that** ID-based assembly avoids **while** still letting each database do what it does best.

**中文对照：** 虽说把商品嵌进订单能省一次查询，但我们的主路径是按订单查详情而非按商品聚合；存快照 ID 更安全，因为常变的目录字段否则会触发对所有引用它的历史订单的级联更新——用 ID 拼装能避开这种成本，同时让各库发挥所长。

---



## 概念 5：pt-online-schema-change 怎么做到在线 DDL



### 用自己的话理解（中英双语）

**中文：**

直接 `ALTER TABLE` 在大表上容易长时间占 MDL、阻塞读写。pt-osc 的思路是别在原表上硬改，而是四步走完：**建影子表**（结构已含变更）→ **触发器同步增量**（INSERT/UPDATE/DELETE 实时镜像到影子表）→ **按主键分批复制存量**（chunk + sleep，弱锁、可暂停）→ **原子** `RENAME TABLE` **切换**（毫秒级，业务几乎无感）。

全程原表仍可读写；写不丢靠触发器，切换靠 rename 原子性。限制：表要有主键、要预留约一倍磁盘、触发器会增加写开销。对话里候选人提它，是为了说明「关系型 Schema 不灵活」在生产上**有工程手段对冲**，不能单独作为弃用关系型的理由。

**English (B2):**

Running `ALTER TABLE` directly on a large MySQL table can hold metadata locks for a long time **and** block reads and writes. **pt-online-schema-change** avoids that by never mutating the live table in place. Instead, it creates a **shadow table** **whose** structure already includes the change, installs **triggers that** copy every insert, update, and delete from the original table into the shadow, copies existing rows in **chunks that** are separated by short sleeps **so that** locking stays light, and finishes with an atomic `RENAME TABLE` **that** swaps names in milliseconds.

Throughout the process, the original table remains readable and writable; triggers prevent lost writes, **and** the rename step is fast enough **that** applications barely notice. There are constraints — you need a primary key, extra disk space, and triggers add write overhead — **but** the candidate mentions pt-osc **to show that** the "inflexible DDL" argument against relational storage can be managed in production, **which** means it should not be the sole reason **to abandon** schema enforcement on order data.

### 关键词（B2）


| 英文                  | 中文     | 带从句的例句                                                                        |
| ------------------- | ------ | ----------------------------------------------------------------------------- |
| shadow table        | 影子表    | A shadow table is a copy **whose** structure already includes the new DDL.    |
| trigger             | 触发器    | Triggers are routines **that** fire **when** rows on the source table change. |
| chunk copy          | 分批复制   | Chunk copy processes rows in batches **that** limit lock duration.            |
| RENAME TABLE        | 表重命名切换 | `RENAME TABLE` is an operation **that** swaps table names atomically.         |
| metadata lock (MDL) | 元数据锁   | MDL is a lock **that** can block queries **while** DDL runs.                  |
| online DDL          | 在线 DDL | Online DDL applies structural changes **without** long production outages.    |




### 嵌套从句练习：解释 pt-osc

**Layer 2：**

> pt-osc copies data to a shadow table **that** already has the new schema, **and** triggers keep the shadow in sync **while** migration runs.

**Layer 3：**

> **Instead of** running `ALTER TABLE` on a busy orders table, pt-osc builds a shadow table **that** includes the new column, uses triggers **that** mirror every write from the original table, and copies old rows in chunks **so that** the business keeps running **until** an atomic rename swaps the tables.

**Layer 4 — 完整嵌套版：**

> **When** teams worry **that** relational schema changes will lock production tables, pt-online-schema-change offers a path **in which** a shadow table — **which** is created with the target structure — receives both incremental updates through triggers **that** fire on every write **and** backfilled rows **that** are copied in small chunks, **after which** a fast `RENAME TABLE` replaces the old table **without** the long outage **that** a direct `ALTER` on a large hot table would cause.

**中文对照：** 若团队担心关系型改表会锁生产表，pt-osc 提供的路径是：先建带目标结构的影子表，用触发器接住每次写入的增量，再小批量回填存量，最后用快速的 `RENAME TABLE` 替换旧表，避免在大热表上直接 `ALTER` 造成的长中断。

---



## 课堂对话套路（B2 + 嵌套从句）



### 套路 1：老师问「订单为何不用 MongoDB」

> The primary driver is transactional consistency — **meaning** that order creation, inventory deduction, and payment updates must commit inside one atomic transaction **that** relational databases handle with mature ACID support, **whereas** multi-document transactions in MongoDB, **which** are available but slower and more conflict-prone, are a weaker fit for checkout. Strict schema is a bonus, **not** the main reason, **because** it rejects invalid writes **at the entry point** **before** they poison revenue reports.

---



### 套路 2：老师问「文档型更灵活，为何订单不选灵活」

> Flexibility has a cost for transactional data: **without** database-level schema, a document store may silently accept a string in the amount field, **which** breaks analytics **that** finance teams trust. For orders we prioritise safety over flexibility, **and** we use pt-online-schema-change **to apply** DDL online **so that** schema evolution does not force a false choice between flexibility and correctness.

---



### 套路 3：老师问「为何商品用文档型、订单却存 ID 不嵌套」

> Products belong in a document model **because** their attributes are heterogeneous — **a pattern that** would become either a wide table full of NULLs **or** an EAV model **in which** simple filters need painful `GROUP BY` queries. Orders, **whose** main access path is lookup by order ID rather than aggregation by product, store snapshot IDs **so that** catalog changes do not trigger cascade updates across every historical order **that** referenced a changed image or title.

---



### 套路 4：老师问「JSON 列和不设 Schema 有何区别」

> A JSON column gives bounded flexibility: price and stock stay as strict relational columns **that** keep constraints and indexes, **whereas** only optional attributes live in JSON. In a pure document store, validation depends entirely on application code, **which** means one bug can dirty every field **that** downstream systems read — **a risk that** tiered schema design is meant to prevent on core transactional paths.

---



### 套路 5：老师问「pt-osc 是什么、为何提到它」

> **When** interviewers argue **that** relational DDL is too rigid for production, I mention pt-online-schema-change, **which** migrates through a shadow table **that** stays in sync via triggers **while** existing rows are copied in chunks, **after which** an atomic rename swaps tables in milliseconds — **a workflow that** shows schema rigidity on orders is an operational problem **that** teams can manage, **not** a reason **to give up** ACID and entry-point validation.

---



### 套路 6：课上主动说话


| 你想做什么 | 嵌套从句版                                                                                                                                                       |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 确认理解  | So the split is not "relational vs document everywhere", **but** "relational **where** transactions matter, document **where** attributes vary", **right**? |
| 请老师举例 | Could you walk through an EAV query **that** becomes complex **when** you filter on two optional attributes?                                                |
| 表示同意  | That makes sense — nesting full products in orders would force updates **that** touch every historical document **when** a catalog field changes.           |
| 提出疑问  | **But** wouldn't two round-trips — one for the order and one for products — hurt latency on the detail page **if** we did not cache aggressively?           |
| 问边界   | How do you decide **which** fields stay in strict columns **and which** ones are safe **to put** in JSON?                                                   |


---



## 常用句式：嵌套从句版（改写，非原文）


| 功能      | 嵌套从句句式                                                                                                                                                                |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 陈述主因    | The primary driver is X, **meaning** that Y must happen inside one transaction **that** only a relational engine handles well; Z is a bonus, **not** the main factor. |
| 灵活性代价   | Flexibility has a cost: a document store may accept bad data **that** relational constraints would reject **at the entry point**.                                     |
| 商品选型    | Products need a model **in which** heterogeneous attributes can nest naturally, **which** avoids wide tables **that** are full of NULLs.                              |
| 查询模式    | Our main query pattern is X by order ID, **not** Y by product, **so** we store snapshot IDs **instead of** nested documents **that** would require cascade updates.   |
| JSON 边界 | A JSON column gives bounded flexibility — core columns **that** affect money keep full constraints, **whereas** edge fields **that** change often can evolve faster.  |
| 在线 DDL  | pt-osc migrates through a shadow table **that** triggers keep in sync, **so that** production traffic is not blocked **by** a long `ALTER TABLE`.                     |
| 各取所长    | Each model plays to its strength **when** transactional data stays relational **and** catalog data stays document-oriented, **with** IDs **that** decouple evolution. |


---



## 老师可能追问 — 嵌套从句回答


| 老师问                 | 你可以答                                                                                                                                                                                             |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Schema 还是事务？        | I chose relational mainly for transactions across order, inventory, and payment tables; strict schema is a bonus **that** rejects invalid writes **before** they reach reports.                  |
| ALTER TABLE 会锁表怎么办？ | We use pt-online-schema-change, **which** syncs writes to a shadow table through triggers **and** finishes with a fast rename, **so that** DDL does not block the checkout path.                 |
| 什么是 EAV？            | EAV stores each attribute as a row, **which** makes flexible schemas possible **but** turns simple filters into queries **that** need `GROUP BY` and `HAVING`.                                   |
| 为何不嵌套商品到订单？         | **Because** our main pattern is order lookup, **not** product aggregation; nesting would cause cascade updates **whenever** catalog fields **that** appear in many orders change.                |
| JSON 列 vs 纯文档？      | JSON columns keep core money fields under schema constraints, **whereas** a pure document store relies on application code **that** can let one bug corrupt every field.                         |
| 查订单详情怎么走？           | We load the order by ID in the relational store, fetch products by ID from MongoDB in batch, **and** assemble the response in the application layer **where** each store does what it does best. |
| 宽表有什么问题？            | A wide table adds columns for every new attribute, **most of which** are NULL for most SKUs, **which** wastes space and still needs DDL **when** categories evolve.                              |


---



## 跟读练习：五段 B2 嵌套从句（课前朗读 2 遍）

**Part 1 — 订单用关系型**

> **When** I design an order system, I put transactional data in a relational database **because** creating an order, deducting inventory, and updating payment status must commit inside one atomic transaction **that** ACID engines support natively, **whereas** multi-document transactions in MongoDB, **which** are available but slower and more conflict-prone, are a weaker fit for high-concurrency checkout. Strict schema is a bonus, **not** the primary driver, **since** it rejects invalid writes **at the entry point** **before** they break revenue reports **that** finance teams rely on.

**Part 2 — 商品用文档型**

> Products belong in a document store **because** each category needs a different set of optional attributes — **a pattern that** would force a relational design into either a wide table **that** is full of NULLs **or** an EAV model **in which** even a simple filter like "black, size M" becomes a `GROUP BY` puzzle. Nested documents let each SKU carry **only** the fields it needs, **which** is why flexibility makes sense for catalog data **but not** for core order amounts **where** silent corruption would be unacceptable.

**Part 3 — 查询模式与快照 ID**

> **Although** embedding full product documents inside an order would save a join, our main query pattern is fetching order details by order ID, **not** aggregating sales by product, **which** means we store snapshot IDs and price snapshots **so that** catalog changes do not trigger cascade updates across every historical order **that** referenced a product image or title **which** changed last week. The application assembles the page **after** it loads orders relationally and products from MongoDB in batch.

**Part 4 — JSON 列的边界**

> A relational JSON column is bounded flexibility: fields **that** directly affect money and inventory stay as strict columns **with** constraints and indexes, **whereas** optional attributes **that** change frequently can live in JSON. That is different from a schema-less document **where** validation depends entirely on application code, **which** means one bug can let dirty data into every field **that** downstream analytics treat as trustworthy.

**Part 5 — pt-osc 对冲 DDL 风险**

> **When** people argue **that** relational schemas are too rigid for fast-moving products, I separate two problems: catalog flexibility, **which** documents handle well, and order correctness, **which** still benefits from schema enforcement. For order tables **that** must evolve, pt-online-schema-change builds a shadow table **that** triggers keep in sync, copies rows in chunks **so that** traffic is not blocked, and swaps names atomically — **a process that** shows DDL risk on hot tables is manageable **without** giving up the safety net **that** transactional data needs.

---



## 附录：嵌套从句工具箱


| 从句类型          | 常用引导词                           | 练法                                                          |
| ------------- | ------------------------------- | ----------------------------------------------------------- |
| **定语从句（限定）**  | that, which, who, whose, where  | 修饰名词：*a transaction **that** spans three tables*            |
| **定语从句（非限定）** | , which / , who                 | 补充信息：*…MongoDB 4.0, **which** added multi-doc transactions* |
| **时间 / 条件状语** | when, before, after, if, unless | *                                                           |
| **原因 / 结果状语** | because, since, so that         | *…strict schema **because** reports must trust amounts*     |
| **对比 / 让步状语** | although, whereas, while        | *                                                           |
| **嵌套技巧**      | 从句套从句                           | 主句 → 定语从句里再套 that/when/which                                |


**拆句口诀：** 先找主句主干 → 标出每个 that/which/when/because 引导的从句 → 从外往里读 → 再试着合并回去。

---

**课前最少记：** 订单主因 = ACID 事务（Schema 是 bonus）· 商品 = 异构属性 / 避 EAV · 订单存 snapshot ID 不按商品聚合 · JSON 列 = bounded flexibility · pt-osc = 影子表 + 触发器 + 分批复制 + rename · *Core transactional data needs correctness; catalog data can use bounded flexibility.*