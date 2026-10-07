这份预习材料**不用 material 原文**，概念全部用自己的话复述。每个概念的「用自己的话理解」提供**中英双语**（英文按 **B2**）。长句练习的重点是**嵌套从句**——定语从句、状语从句、非限制性从句叠在一起练。

---

## 课前 3 分钟：今天讲什么

**话题：** 查询语言——声明式 SQL 不是万能药；动态报表、优化器误判、多数据源整合，各自该用什么手段？

**三条主线（material 技术干点）：**

```
① 动态查询可读性 → ② 优化器与索引调优 → ③ 多源查询整合
```

**故事线：**

```
主张 SQL 声明式够用 → 追问动态筛选拼接 → 追问 status 索引误判 → 追问 MySQL + MongoDB + ES 怎么整合
```

| 场景 | 推荐风格 | 关键手段 |
| --- | --- | --- |
| 固定查询 | 声明式 SQL | 优化器自动选计划 |
| 十几个可选筛选 | 命令式 QueryBuilder | `.where().filter().paginate()`，条件独立可测 |
| 优化器选错索引 | 诊断 → 修统计 → hint | `EXPLAIN ANALYZE`，差距 >50% 怀疑误判 |
| 三数据源报表 | GraphQL 网关 + correlation ID | 复杂聚合走统一层，简单单源走原生 API |

| 声明式赢在哪 | 命令式赢在哪 |
| --- | --- |
| 条件固定、一条 SQL 说清意图 | 用户动态勾选、分支多、要逐层拼装 |
| 优化器负责执行计划 | 每个 filter 独立测试、意图显式 |

**规律：** **按场景选风格，并管理工具代价**——动态查询换可读性，索引问题走流程化运维，多源整合不为统一而统一。

---

## 概念 1：声明式 vs 命令式——动态查询怎么建

### 用自己的话理解（中英双语）

**中文：**

面试开场，候选人说团队用 SQL 处理所有查询：声明式简洁，优化器自动选索引。面试官立刻举反例：报表页用户可选十几个筛选——时间、状态、金额、品类、支付方式……拼出来的 SQL 几百行，读不懂也难调试。

候选人承认这类场景**不用纯声明式 SQL**，而是用命令式 QueryBuilder：`.where().filter().paginate()`，用户选了什么条件才加对应 WHERE 子句。每个 filter 可单独单测，代码意图一目了然。

核心不是「SQL 好还是代码好」，而是**场景驱动**：固定查询写一条完整 SQL 最清晰；动态组合时你写的其实是「拼 SQL 的函数」，读的人得脑补所有分支，声明式反而成了负担。

**English (B2):**

The interview opens with the candidate claiming that SQL's declarative style handles every query — **because** it is concise **and** the optimizer picks indexes automatically. The interviewer pushes back with a report page **where** users can combine a dozen optional filters, **which** would produce a SQL string **that** is hundreds of lines long and painful **to debug**.

The candidate agrees **that** this scenario needs imperative construction instead. They use a QueryBuilder **that** chains methods like `.where()`, `.filter()`, and `.paginate()`, **and** each condition adds a clause **only when** the user actually selects it. Every filter can be unit-tested on its own, **which** makes the intent explicit.

The real lesson is not "SQL versus code", **but** scene-driven choice: a fixed query is clearest as one declarative statement, **whereas** dynamic combinations turn SQL into a function **that** assembles strings, **forcing** readers **to mentally trace** every branch — **a case in which** declarative style hurts readability.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| declarative | 声明式的 | A declarative query states **what** you want, **not how** to fetch it. |
| imperative | 命令式的 | Imperative code builds a query step by step **when** each filter is selected. |
| QueryBuilder | 查询构建器 | A QueryBuilder is a pattern **that** adds WHERE clauses only **when** needed. |
| dynamic query | 动态查询 | A dynamic query is one **whose** filters change at runtime. |
| filter | 筛选条件 | Each filter is a condition **that** the user may or may not apply. |
| paginate | 分页 | Pagination limits rows **that** the report returns to the client. |
| maintainability | 可维护性 | Maintainability improves **when** each filter lives in its own testable method. |

### 嵌套从句练习：说为何动态场景用命令式

**Layer 1：**
> Dynamic reports need imperative query building.

**Layer 2 — 加定语从句：**
> Dynamic reports, **which** let users combine many optional filters, need imperative query building **that** adds clauses only **when** each filter is selected.

**Layer 3 — 加对比从句：**
> **Although** declarative SQL is clear for fixed queries, a report page **where** users pick a dozen filters forces you **to write** a function **that** assembles SQL, **which** is harder **to read** **than** a QueryBuilder **where** each condition is explicit.

**Layer 4 — 完整嵌套版：**
> **When** a report page allows users **to combine** a dozen optional filters — time range, status, amount bracket, and payment method — declarative SQL becomes a liability **because** you are no longer writing one query **that** states the intent, **but** a function **that** must handle every branch, **whereas** imperative QueryBuilder code adds each WHERE clause **only when** the user selects it, **which** keeps every filter independently testable and easier **to maintain** over time.

**中文对照：** 当报表页允许用户组合十几个可选筛选时，声明式 SQL 反而成了负担——你写的不再是一条表达意图的查询，而是必须处理所有分支的拼装函数；命令式 QueryBuilder 只在用户选中时才加 WHERE 子句，每个 filter 可独立测试，长期更好维护。

---

## 概念 2：优化器误判——EXPLAIN ANALYZE 与 FORCE INDEX

### 用自己的话理解（中英双语）

**中文：**

面试官第二问：优化器也会选错索引。比如 `orders` 表按 `status` 过滤——只有 5 个值，**低选择性**；优化器可能误判，走了 `status` 索引或全表扫描，其实先按 `create_time` 缩时间窗更快。

候选人用 `EXPLAIN ANALYZE` 诊断：对比**实际扫描行数**和**预估行数**，差距超过 50% 就怀疑优化器判断错了。修复分两步：先 `ANALYZE` 更新统计信息让优化器重估；还不行才加 `FORCE INDEX`，并在代码注释里写清原因。

`FORCE INDEX` 有维护风险——数据分布变了，旧 hint 可能拖慢查询。团队用 CI 定期跑慢查询检查，hint 过的 SQL 一旦退化就告警，把一次性调优变成**可监控的运维流程**。

低选择性索引常伴随大量**回表**：二级索引只存主键，要拿完整行还得回主键索引，随机 I/O 多，有时还不如顺序全表扫。

**English (B2):**

The interviewer's second challenge is **that** optimizers can pick the wrong index. On an `orders` table, filtering by `status` — a column **that** has only five distinct values and therefore **low selectivity** — may lead the optimizer **to choose** an index **that** scans far more rows **than** filtering first by `create_time`, **which** is more selective.

The candidate diagnoses this with `EXPLAIN ANALYZE`, **comparing** actual rows scanned against estimated rows. **If** the gap exceeds fifty percent, they suspect a bad plan. The fix is two-step: first update table statistics **so that** the optimizer can re-evaluate; **only if** that fails do they add a `FORCE INDEX` hint, **which** must be documented in code.

Hints carry maintenance risk **because** data distribution shifts over time, **and** an old hint may become harmful. Their CI pipeline runs periodic slow-query checks, **so that** any hinted query **that** starts regressing triggers an alert — **turning** one-off tuning into a monitored operational process.

Low-selectivity indexes often cause heavy **lookups back to the primary key**, **where** the engine must fetch full rows after reading secondary index entries — **a pattern that** can make a full table scan cheaper **when** too many rows match.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| optimizer | 优化器 | The optimizer chooses a plan **that** it believes is cheapest. |
| selectivity | 选择性/区分度 | Selectivity measures **how well** a column narrows the result set. |
| EXPLAIN ANALYZE | 执行计划分析 | `EXPLAIN ANALYZE` runs the query **and** shows actual row counts. |
| full table scan | 全表扫描 | A full table scan reads every row **when** the optimizer gives up on indexes. |
| statistics | 统计信息 | Outdated statistics are data **that** mislead the optimizer's estimates. |
| FORCE INDEX | 强制索引 | `FORCE INDEX` is a hint **that** overrides the optimizer's choice. |
| index hint | 索引提示 | An index hint tells the engine **which** index it must consider. |
| lookup / back to table | 回表 | A lookup happens **when** the engine fetches full rows **after** an index scan. |

### 案例对比表

| | `status` 索引（低选择性） | `create_time` 索引（高选择性） |
| --- | --- | --- |
| 过滤效果 | 5 个值，可能匹配几十万行 | 时间窗通常只覆盖近期少量行 |
| 风险 | 大量回表、随机 I/O | 先缩范围再筛 status |
| 发现手段 | EXPLAIN ANALYZE 实际行数 >> 预估 | 对比两种计划的 actual rows |

### 嵌套从句练习：说如何发现并修复误判

**Layer 2：**
> We run `EXPLAIN ANALYZE` **when** a query is slow, **and** we compare actual rows **to** estimated rows.

**Layer 3：**
> **If** `EXPLAIN ANALYZE` shows **that** actual rows scanned are more than fifty percent above the estimate, we suspect the optimizer misjudged selectivity on a low-cardinality column **like** `status`, **which** may trigger millions of lookups **that** are slower **than** scanning by `create_time` first.

**Layer 4 — 完整嵌套版：**
> **When** we suspect a bad plan, we run `EXPLAIN ANALYZE` on the slow query, **comparing** actual rows scanned against the optimizer's estimate — **and if** the gap exceeds fifty percent, we first refresh table statistics **so that** the optimizer can re-evaluate data distribution, **whereas** a `FORCE INDEX` hint is our last resort, **which** we document in code and monitor through CI **because** hints **that** made sense last year may hurt performance **after** the table grows.

**中文对照：** 怀疑执行计划有问题时，我们对慢查询跑 `EXPLAIN ANALYZE`，对比实际扫描行数与预估值；若差距超 50%，先刷新统计信息让优化器重估分布，仍不行才用 `FORCE INDEX`——并在代码里注释、用 CI 监控，因为去年合理的 hint 在表变大后可能反而拖慢查询。

---

## 概念 3：多数据源整合——GraphQL 网关与分层策略

### 用自己的话理解（中英双语）

**中文：**

第三问：报表要从 MySQL 拿订单、MongoDB 拿商品描述、Elasticsearch 做全文搜索——三套查询语言（SQL、Mongo query、ES DSL），应用层怎么组织？

候选人方案是 **GraphQL 网关**作统一查询层：前端用 GraphQL 表达要什么数据，网关拆成三路并行调用，最后拼装返回。好处是前端一个端点，不用知道后端的存储分布。

代价是**调试变难**——出问题要跨三个源排查。团队在网关注入 **correlation ID**，每个后端调用日志都带上，才能把整条链路串起来。

务实分层：需要聚合的复杂报表走 GraphQL；按 ID 查订单这种简单单源查询，直接走各库原生 API。**不为统一而统一**，避免简单操作也被卷进高开销抽象层。

**English (B2):**

The third question is **how** to organise queries **when** a report needs orders from MySQL, product descriptions from MongoDB, and full-text search from Elasticsearch — three systems **that** speak different query languages.

The candidate uses a **GraphQL gateway** as a unified layer: the frontend expresses **what** data it needs in GraphQL, **and** the gateway splits the request into three parallel backend calls **that** are assembled into one response. The benefit is a single endpoint **that** hides storage layout from the client.

The cost is debugging complexity. **When** something fails, engineers must trace across three sources, **which** is why they inject a **correlation ID** at the gateway **that** every downstream log entry carries, **so that** the full call chain can be stitched together.

They apply a pragmatic split: aggregated report queries go through GraphQL, **whereas** simple single-source lookups — such as fetching an order by ID — still use each database's native API. **This** keeps the common case simple **while** making the complex case possible, **without** forcing every query through a heavy abstraction layer.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| GraphQL | 图查询语言 | GraphQL lets the client describe **which** fields it needs in one request. |
| gateway | 网关 | A gateway is a layer **that** routes one request to several backends. |
| correlation ID | 关联追踪 ID | A correlation ID is a token **that** links logs across services. |
| abstraction layer | 抽象层 | An abstraction layer hides details **that** the frontend should not need. |
| native API | 原生 API | The native API is the interface **that** each database exposes directly. |
| assemble | 拼装/聚合 | The gateway assembles results **after** parallel calls complete. |
| trace | 追踪 | Tracing shows the path **that** a request took through each data source. |

### 嵌套从句练习：说多源整合的权衡

**Layer 2：**
> We use a GraphQL gateway **that** splits one frontend query into parallel backend calls.

**Layer 3：**
> **Although** a GraphQL gateway gives the frontend one endpoint, debugging is harder **because** failures must be traced across three data sources, **which** is why we inject a correlation ID **that** every backend log includes.

**Layer 4 — 完整嵌套版：**
> **When** a report needs data from MySQL, MongoDB, and Elasticsearch, we route aggregated queries through a GraphQL gateway **that** fans out parallel calls and assembles the response, **whereas** simple lookups **that** hit only one source still use native APIs — **a split that** avoids turning every low-cost query into a multi-hop abstraction **whose** debugging cost would outweigh the benefit for the common case.

**中文对照：** 当报表需要 MySQL、MongoDB 和 Elasticsearch 的数据时，聚合查询走 GraphQL 网关做并行调用并拼装响应；只打单一数据源的简单查询仍用原生 API——这样避免把每次低成本查询都变成多跳抽象，而常见场景下的调试代价超过收益。

---

## 概念 4：低选择性与回表——为什么 status 索引会坑你

### 用自己的话理解（中英双语）

**中文：**

**选择性** = 不同值数量 ÷ 总行数。`order_id` 几乎每行唯一，选择性接近 1.0，索引能精准命中；`status` 只有几种值，选择性极低，过滤后仍可能剩几十万行。

InnoDB 二级索引叶子节点只存「索引列 + 主键」。查询要 `SELECT *` 时，引擎得拿主键再回聚集索引取完整行——这就是**回表**，每次都是随机 I/O。低选择性索引若匹配大量行，就会触发海量回表，有时比顺序全表扫还慢。

复合索引要把**高选择性列放前面**，如 `(create_time, status)` 优于 `(status, create_time)`：先用时间窗大幅缩范围，再用 status 细筛。对话里优化器误判，往往就是对低选择性列过于乐观。

**English (B2):**

**Selectivity** is the ratio of distinct values **to** total rows. A column like `order_id`, **which** is unique on almost every row, has very high selectivity **that** makes index lookups efficient. A column like `status`, **which** has only a few values shared by millions of rows, has low selectivity **that** leaves a huge result set even after filtering.

In InnoDB, secondary index leaves store the indexed column plus the primary key. **When** the query needs columns **that** are not in the index, the engine must **look up** the full row in the clustered index — **an operation** often called a table lookup. **If** a low-selectivity index matches hundreds of thousands of rows, those lookups can cost more **than** a sequential full table scan.

For composite indexes, teams put the **more selective column first** — for example `(create_time, status)` rather than `(status, create_time)` — **so that** the index narrows the range early. **This** is exactly the kind of mistake optimizers make **when** they overestimate how much a low-cardinality column like `status` will filter.

### 关键词（B2）

| 英文 | 中文 | 带从句的例句 |
| --- | --- | --- |
| low selectivity | 低选择性 | Low selectivity means a filter **that** still matches many rows. |
| high selectivity | 高选择性 | High selectivity helps indexes **that** must pinpoint few rows. |
| cardinality | 基数/不同值个数 | Cardinality is the count of distinct values **that** a column contains. |
| clustered index | 聚集索引 | The clustered index stores full rows **that** secondary indexes point to. |
| covering index | 覆盖索引 | A covering index includes all columns **that** the query needs, **so** no lookup is required. |
| composite index | 复合索引 | A composite index orders columns **so that** the most selective one comes first. |

### 嵌套从句练习：解释低选择性为何慢

**Layer 3：**
> **Because** `status` has low selectivity, an index on it may return hundreds of thousands of rows, **each of which** requires a lookup **that** fetches the full row from the clustered index.

**Layer 4 — 完整嵌套版：**
> **When** the optimizer chooses an index on a low-selectivity column like `status`, **which** may match forty percent of the table, the engine often performs far more random lookups **than** a plan **that** first narrows by `create_time` — **a mistake that** `EXPLAIN ANALYZE` reveals **when** actual rows scanned dwarf the optimizer's estimate by more than fifty percent.

**中文对照：** 当优化器选择低选择性列（如 `status`）上的索引，而该列可能匹配表中 40% 的行时，引擎往往要做比「先用 `create_time` 缩范围」多得多的随机回表——`EXPLAIN ANALYZE` 会在实际扫描行数比预估高出 50% 以上时暴露这类错误。

---

## 概念 5：EXPLAIN ANALYZE 怎么用

### 用自己的话理解（中英双语）

**中文：**

普通 `EXPLAIN` 只看优化器**打算**怎么做；`EXPLAIN ANALYZE` 会**真正执行**查询，并给出每步的 actual time、actual rows，和预估对比。

用法：在 SELECT 前加 `EXPLAIN ANALYZE`。注意它会真跑语句，写操作要在事务里回滚，或放备库、低峰期分析。

看计划树里每个节点：若 `Rows Removed by Filter` 很大、actual rows 远超 estimate，说明优化器对数据分布判断错了——对话里「差距超 50%」就是这个信号。修完再跑一遍验证。

**English (B2):**

A plain `EXPLAIN` shows **what** the optimizer **plans** to do, **whereas** `EXPLAIN ANALYZE` actually runs the query and reports real timings and row counts **that** you can compare against estimates.

You prefix the statement with `EXPLAIN ANALYZE`. **Because** it executes the query, you should be careful with writes — run them inside a transaction **that** you roll back, **or** analyse on a replica **during** a quiet period.

In the plan tree, **when** you see huge `Rows Removed by Filter` values **or** actual rows far above the estimate, the optimizer likely misjudged data distribution — **which** is the signal **that** the candidate describes as a gap over fifty percent. **After** fixing statistics or adding a hint, you rerun the command **to verify** the new plan.

### 嵌套从句练习：说 EXPLAIN ANALYZE 的价值

**Layer 4：**
> **Although** guessing why a query is slow is tempting, `EXPLAIN ANALYZE` turns the problem into numbers **by** showing actual rows and timings **that** you can compare with the optimizer's estimates — **without which** you might add indexes **that** make performance worse **when** the real issue is a plan **that** scans far more rows **than** expected.

**中文对照：** 虽说猜慢查询原因很诱人，但 `EXPLAIN ANALYZE` 用实际行数和时间把问题量化，可与优化器预估对比；没有它，你可能加了反而更慢的索引，而真正的问题是执行计划扫描的行数远超预期。

---

## 课堂对话套路（B2 + 嵌套从句）

### 套路 1：老师问「动态报表为什么不用纯 SQL」

> **Although** declarative SQL is ideal **when** filters are fixed, our report page lets users combine a dozen optional conditions, **which** means we are really writing a function **that** assembles SQL rather than one query **that** states the intent. **That** is why we use a QueryBuilder **where** each filter adds a clause **only when** the user selects it, **making** every condition independently testable and easier **to maintain**.

---

### 套路 2：老师问「优化器选错索引怎么办」

> We catch bad plans with `EXPLAIN ANALYZE`, **comparing** actual rows scanned **to** the optimizer's estimate. **If** the gap exceeds fifty percent — **which** often happens **when** a low-selectivity column like `status` is involved — we first refresh statistics, **and only then** add a `FORCE INDEX` hint **that** we document and monitor through CI **so that** we notice regressions **before** they hit production.

---

### 套路 3：老师问「MySQL + MongoDB + ES 怎么整合」

> For aggregated reports, we use a GraphQL gateway **that** splits one frontend query into parallel calls to MySQL, MongoDB, and Elasticsearch, **then** assembles the result. **Because** debugging across three sources is painful, we inject a correlation ID **that** every backend log carries. Simple single-source lookups, **which** do not need federation, still go through each database's native API.

---

### 套路 4：老师问「FORCE INDEX 有什么风险」

> A `FORCE INDEX` hint can become harmful **when** data distribution shifts, **because** an index **that** was optimal last quarter may force the engine **to scan** more rows **than** a newer plan would. **That** is why we comment every hint with the reason it was added and let CI alert us **when** the hinted query starts slowing down.

---

### 套路 5：老师问「什么是低选择性、回表」

> A column like `status`, **which** has only a few distinct values, has low selectivity, **so** an index on it may match a huge fraction of the table. **When** the query needs columns **that** are not in the index, each match triggers a lookup back to the clustered index — **and if** there are hundreds of thousands of matches, those random reads can cost more **than** scanning the table sequentially.

---

### 套路 6：课上主动说话

| 你想做什么 | 嵌套从句版 |
| --- | --- |
| 确认理解 | So declarative SQL is for fixed queries, **whereas** imperative builders are for filters **that** users combine at runtime, **right**? |
| 请老师举例 | Could you show an `EXPLAIN ANALYZE` output **where** actual rows are much higher **than** the estimate? |
| 表示同意 | That makes sense — a GraphQL gateway helps aggregation, **but** it makes tracing harder **when** one of three backends fails. |
| 提出疑问 | **But** wouldn't `EXPLAIN ANALYZE` on production be risky **if** the query scans millions of rows? |
| 问边界 | How do you decide **which** queries stay on native APIs **and which** ones go through the gateway? |

---

## 常用句式：嵌套从句版（改写，非原文）

| 功能 | 嵌套从句句式 |
| --- | --- |
| 动态查询选型 | **When** filters are optional and numerous, imperative QueryBuilder code **that** adds clauses only **when** needed is clearer **than** a SQL string **that** encodes every branch. |
| 声明式局限 | Declarative SQL becomes a liability **when** you are not writing one query, **but** a function **that** assembles hundreds of lines of SQL. |
| 发现误判 | `EXPLAIN ANALYZE` reveals bad plans **by comparing** actual rows **to** estimates, **which** often diverge **when** statistics on low-selectivity columns are stale. |
| 两步修复 | The fix is two-step: refresh statistics **so that** the optimizer can re-evaluate, **and only if** that fails, add a documented `FORCE INDEX` hint **that** CI continues **to monitor**. |
| 多源整合 | A GraphQL gateway fans out parallel calls **that** each data source executes, **then** assembles the response **while** a correlation ID **that** every log carries makes cross-source tracing possible. |
| 分层策略 | Aggregated queries use the unified layer, **whereas** simple lookups **that** hit one source stay on native APIs **so that** abstraction does not tax the common case. |
| 低选择性 | Indexes on columns **that** have low selectivity may trigger lookups **that** cost more **than** a full table scan **when** too many rows match. |

---

## 老师可能追问 — 嵌套从句回答

| 老师问 | 你可以答 |
| --- | --- |
| 声明式和命令式区别？ | Declarative SQL states **what** you want, **whereas** imperative builders show **how** conditions are added step by step **when** the user selects them. |
| 何时用 QueryBuilder？ | **When** a report has many optional filters **that** combine at runtime, **because** each filter is easier **to test** **than** one giant SQL template. |
| EXPLAIN vs EXPLAIN ANALYZE？ | `EXPLAIN` shows the plan **that** the optimizer intends, **whereas** `EXPLAIN ANALYZE` runs the query and reports actual rows **that** reveal whether the estimate was wrong. |
| 50% 差距什么意思？ | **If** actual rows scanned exceed the estimate by more than fifty percent, we suspect the optimizer misjudged selectivity, **which** often points to stale statistics or a bad index choice. |
| FORCE INDEX vs USE INDEX？ | `USE INDEX` suggests an index **that** the optimizer may still ignore, **whereas** `FORCE INDEX` almost always forces the engine **to use** the named index. |
| 为什么简单查询不走 GraphQL？ | **Because** a gateway adds latency and debugging steps **that** are unnecessary **when** one native API can fetch the row directly. |
| correlation ID 干什么用？ | It is an ID **that** the gateway generates **so that** logs from MySQL, MongoDB, and ES can be stitched into one trace **when** a report fails. |

---

## 跟读练习：五段 B2 嵌套从句（课前朗读 2 遍）

**Part 1 — 声明式 vs 命令式**

> **Although** our team relies on SQL for most queries, a report page **where** users can pick a dozen optional filters is not a good fit for pure declarative SQL, **because** you end up maintaining a function **that** assembles a huge string rather than one statement **that** expresses the intent. **That** is why we use a QueryBuilder **that** chains `.where()`, `.filter()`, and `.paginate()`, **adding** each clause **only when** the user selects it, **which** keeps every filter independently testable and the logic easier **to read** over time.

**Part 2 — 优化器误判与修复**

> **When** a query on `orders` filters by `status`, a column **that** has only five values and therefore low selectivity, the optimizer may choose a plan **that** scans far more rows **than** filtering first by `create_time`. We run `EXPLAIN ANALYZE` and compare actual rows **to** estimates; **if** the gap exceeds fifty percent, we refresh statistics **so that** the optimizer can re-evaluate, **and only then** do we add a `FORCE INDEX` hint **that** we document and monitor through CI **because** data distribution **that** changes over time can turn yesterday's fix into tomorrow's regression.

**Part 3 — 低选择性与回表**

> A low-selectivity index on `status` may match a large fraction of the table, **and when** the query needs columns **that** are not stored in the index, the engine performs a lookup back to the clustered index for every matching row — **a pattern that** creates heavy random I/O. **That** is why a composite index **that** puts `create_time` first often works better, **because** the more selective column narrows the range **before** `status` is applied to a much smaller set.

**Part 4 — 多数据源整合**

> Our aggregated reports go through a GraphQL gateway **that** splits one frontend query into parallel calls to MySQL, MongoDB, and Elasticsearch, **then** assembles the response into a single payload. **Although** this gives the client one clean endpoint, debugging is harder **because** failures must be traced across three backends, **which** is why we inject a correlation ID **that** every downstream log carries **so that** we can stitch the full call chain together **when** something breaks.

**Part 5 — 分层与工程原则**

> We do not force every query through the gateway: simple lookups **that** hit only one data source still use native APIs, **whereas** complex reports **that** need fields from three stores use the unified path. **The** principle is **to choose** the style and layer **that** fit the scenario, **and then** manage the cost — whether that cost is unreadable dynamic SQL, an index hint **that** may age badly, or an abstraction layer **whose** debugging overhead is only worth paying for aggregated queries.

---

## 附录：嵌套从句工具箱

| 从句类型 | 常用引导词 | 练法 |
| --- | --- | --- |
| **定语从句（限定）** | that, which, who, whose, where | 修饰名词：*a QueryBuilder **that** adds clauses only when needed* |
| **定语从句（非限定）** | , which / , who | 补充信息：*…fifty percent, **which** signals a bad plan* |
| **时间 / 条件状语** | when, before, after, if, unless | *|**When** filters are dynamic, imperative code is clearer* |
| **原因 / 结果状语** | because, since, so that | *…hard **because** you must trace every branch* |
| **对比 / 让步状语** | although, whereas, while | *|**Although** SQL is declarative, dynamic reports need builders* |
| **嵌套技巧** | 从句套从句 | 主句 → 定语从句里再套 that/when/which |

**拆句口诀：** 先找主句主干 → 标出每个 that/which/when/because 引导的从句 → 从外往里读 → 再试着合并回去。

---

**课前最少记：** 动态报表 → QueryBuilder · 误判信号 → EXPLAIN ANALYZE 实际 vs 预估 >50% · 修复 → 更新统计 → FORCE INDEX + 注释 + CI · 多源 → GraphQL 并行 + correlation ID · 简单单源走原生 API · *Choose the style for the scene; manage the cost of each tool.*
