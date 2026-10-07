# Data Warehouse Layering Review – ODS, DWD, DWS – Partitioning Strategy and Z-Order Optimization

**Source:** Meeting / Technical Design Review
**Level:** D2 / Intermediate
**Role:** Zhou (Data Engineer), Li (DBA / Data Architect)
**Estimated Words:** ~508

---

## Background

数据仓库 DWD 层分区设计评审会。Zhou 投屏展示订单主题的数仓分层方案，Li 在分区细节上发现隐患：按天分区导致单分区过大，改成小时分区又会引入小文件问题。经过讨论，他们决定采用按天分区加 Z-Order 排序的方案，并利用 Delta Lake 或 Iceberg 的 OPTIMIZE 命令来平衡写入性能与查询延迟。

---

## Role and Scenario

- **Zhou (Data Engineer):** 投屏展示订单主题的数仓分层方案，负责定义 ODS、DWD、DWS 各层的存储和处理逻辑。
- **Li (DBA / Data Architect):** 评审分区设计，指出按天分区的扫描量问题和小文件风险，提出引入 Z-Order 排序的优化方案。
- **Scene:** 数仓设计评审会。

---

## Technical Key Points

### 1. Data Warehouse Layering Architecture

对话中涉及四个经典层级：

- **ODS (Operational Data Store):** 原始数据原样摄入，保留完整粒度，用于回溯和审计。
- **DWD (Data Warehouse Detail):** 对 ODS 进行清洗、标准化（如统一数据类型、状态码），按主题建模，是数据仓库的核心明细层。
- **DWS (Data Warehouse Summary):** 对 DWD 做轻度聚合（如日汇总），供常用报表直接查询。
- **ADS (Application Data Store):** 面向具体报表或应用场景的结果表。

### 2. Partition Granularity Dilemma

| Approach | Advantage | Disadvantage |
|---|---|---|
| Daily partition | Few partitions, simple file management | 100M rows in a single partition — scan volume still massive even with partition pruning |
| Hourly partition | ~4M rows per partition, precise queries | 24 partitions/day → 240 small files (~few dozen MB each) |

- **Small-file problem:** Many tiny files overwhelm HDFS NameNode metadata management, and I/O scheduling overhead per read cancels the query performance gain.
- **Conclusion:** Simply adding more partition levels does not solve the performance problem.

### 3. Z-Order Sorting — Trading Storage Layout for Query Speed

Li 提出的方案是在日分区内部，对数据按 `user_id` 做 Z-Order 排序。

- **Principle:** Z-Order is a multi-dimensional clustering technique. It maps values from multiple columns (or just one) into a one-dimensional Z-value so that rows with similar values in those columns are stored physically together. After Z-Order on `user_id`, all orders for the same user are physically adjacent in Parquet files.
- **Effect:** Queries with `WHERE user_id = xxx` can skip large amounts of irrelevant data blocks using min/max statistics — achieving **finer-grained partition pruning** without creating extra partitions or small files.
- **Extra benefit:** Z-Order can optimize queries on multiple dimensions simultaneously (e.g., `user_id` and `order_id`), while partitioning only optimizes the partition key.

### 4. Async Optimization — Fast Writes, Fast Reads

- **Implementation:** Table formats like Delta Lake and Apache Iceberg support `OPTIMIZE ZORDER BY (user_id)`.
- **Execution strategy:** Do not sort on the fly during normal writes (ensures write speed). After the daily batch completes, run `OPTIMIZE` asynchronously in the background to reorder the day's partition.
- **Key benefit:** Write performance is unaffected, while query performance improves by an order of magnitude. File compaction also solves the small-file problem.

### 5. Why ODS Keeps Hourly Partitions

ODS 层使用小时分区防止背压，核心在于通过细粒度的分区将上游数据洪峰"化整为零"，保护下游处理环节：

1. **缩小事务粒度，避免写入瓶颈:** 小时分区将 24 小时的写入分散到独立分区，减少锁冲突和提交代价。单个小时失败只需重跑该小时数据。
2. **分区剪枝加速下游消费:** DWD 任务可以直接定位到某个小时分区，只扫描新增数据，处理量锐减，跟上上游节奏。
3. **削峰填谷，平滑负载:** 将波动的数据流分割成固定的数据块，让下游 ETL 的资源调配和预期执行时间变得稳定。

**一句话：ODS 的小时分区是用空间换时间——用更精细的物理目录划分换取下游秒级定位数据的能力，避免数据在管道中积压。**

### 6. Why 240 Small Files Per Day?

**240 = 24 (hourly partitions) × 10 (files per partition, assuming Spark parallelism).**

- Spark 的每个存活 Task 都会独立写出结果文件。假设每个小时分区由 10 个并行 Task 处理，每个 Task 写一个 `part-xxxxx.parquet` 文件，一个分区就产生 10 个小文件。
- 24 小时 × 10 个文件 = 240 个文件。
- 每个文件平均 ~40 万行、几十 MB，属于"小文件"。大量小文件压垮 HDFS NameNode 元数据，并且查询 I/O 调度开销巨大。

### 7. DWS Incremental Updates

使用 Iceberg 的 `MERGE INTO` 语句对日汇总数据进行增量更新，而非全量重刷，节约计算资源，提升时效性。

### 8. Operations Monitoring

需监控 `OPTIMIZE` 作业的执行时间，确保它在下一批次写入前完成，否则未优化的分区堆积，查询性能会退化。

---

## Summary

这套设计是典型的大型数仓分区优化思路：**当日分区粒度导致扫描效率下降时，不盲目增加分区层级（避免小文件灾难），而是引入 Z-Order 排序从物理布局上提升查询剪枝效率，再通过异步 OPTIMIZE 命令在不影响写入的前提下，实现文件合并与排序。** 最终形成"ODS 小时分区防反压，DWD 日分区 + Z-Order 加速查询"的稳健架构。

---

## Dialogue (~508 words)

**Zhou:**

I'll present the data warehouse design for the order theme. **The ODS layer ingests raw data as-is. The DWD layer performs standardisation—cleaning data types and normalising status codes—partitioned by day. Then DWS aggregates to daily summaries, and ADS serves the reports.**

**Li:**

Hold on. You're partitioning DWD by day. The order table gets 100 million rows per day, and analysts mainly query the last three days. A single daily partition would contain 100 million rows. Even with partition pruning, the scan volume is still massive. Have you considered multi-level partitioning?

**Zhou:**

**We could add hourly partitions.** Something like `dt=2024-01-01/hour=00`. That would give about 4 million rows per partition—much more precise queries.

**Li:**

That's true, but now you've created 24 partitions per day, and the Spark job would produce 240 small files per day—only a few dozen MB each. The small-file problem is worse than large partitions. The HDFS NameNode gets overloaded tracking all those files, and every read incurs an I/O scheduling overhead that eats up the query performance gain.

**Zhou:**

So we're stuck. **How do we balance precise querying without exploding the file count?**

**Li:**

**We keep daily partitions but introduce Z-Order sorting.** The order table is frequently queried by `order_id` but also by `user_id` for user-centric analysis. If we sort the data within each daily partition by `user_id` using Z-Order, the records for the same user become physically clustered. Queries filtering on `user_id` can then skip large chunks of files, achieving similar pruning effectiveness to hourly partitions without the small-file overhead.

**Zhou:**

Does Parquet itself support Z-Order?

**Li:**

Parquet alone doesn't, but Delta Lake and Apache Iceberg both support `OPTIMIZE ZORDER BY (user_id)`. After the daily write, we run the `OPTIMIZE` command to reorganise the files. **The write remains fast because we don't sort on the fly**, and **the async optimisation step improves read performance by an order of magnitude. No small files, no heavy scans.**

**Zhou:**

That makes sense. So the final design is: **ODS keeps hourly partitions for raw ingestion to prevent backpressure. DWD stays daily partitioned with Z-Order by `user_id`, and DWS daily aggregates use Iceberg's `MERGE INTO` for incremental updates**. I'll draft the new partitioning spec with file size estimates by tomorrow.

**Li:**

Good. Also monitor the `OPTIMIZE` job's execution time and make sure it completes before the next batch cycle. Otherwise, we'll have unoptimised partitions stacking up.

**Zhou:**

Understood. I'll add that to the runbook.

---

## Vocabulary (25 Terms)

| Vocabulary | Pronunciation (IPA) | Chinese Meaning |
|---|---|---|
| data warehouse | /ˈdeɪtə ˈweərhaʊs/ | 数据仓库 |
| ODS (Operational Data Store) | /ˌoʊ diː ˈes/ | 操作数据存储层 |
| DWD (Data Warehouse Detail) | /ˌdiː dʌbəljuː ˈdiː/ | 明细数据层 |
| DWS (Data Warehouse Summary) | /ˌdiː dʌbəljuː ˈes/ | 汇总数据层 |
| ADS (Application Data Store) | /ˌeɪ diː ˈes/ | 应用数据层 |
| partition | /pɑːrˈtɪʃən/ | 分区 |
| partition pruning | /pɑːrˈtɪʃən ˈpruːnɪŋ/ | 分区裁剪 |
| scan volume | /skæn ˈvɒljuːm/ | 扫描量 |
| multi-level partition | /ˈmʌlti ˈlevəl pɑːrˈtɪʃən/ | 多级分区 |
| small-file problem | /smɔːl faɪl ˈprɒbləm/ | 小文件问题 |
| HDFS NameNode | /ˌeɪtʃ diː ef ˈes ˈneɪm noʊd/ | HDFS 名称节点 |
| I/O scheduling overhead | /aɪ oʊ ˈʃedjuːlɪŋ ˈoʊvərhed/ | I/O 调度开销 |
| Z-Order | /zed ˈɔːrdər/ | Z-Order 排序 |
| physically clustered | /ˈfɪzɪkli ˈklʌstərd/ | 物理聚集 |
| pruning effectiveness | /ˈpruːnɪŋ ɪˈfektɪvnəs/ | 裁剪效率 |
| Delta Lake | /ˈdeltə leɪk/ | Delta Lake 数据湖 |
| Apache Iceberg | /əˈpætʃi ˈaɪsbɜːrɡ/ | Apache Iceberg 表格式 |
| OPTIMIZE command | /ˈɒptɪmaɪz kəˈmɑːnd/ | 优化命令 |
| incremental update | /ˌɪnkrəˈmentl ʌpˈdeɪt/ | 增量更新 |
| MERGE INTO | /mɜːrdʒ ˈɪntuː/ | 合并插入 |
| async optimisation | /eɪˈsɪŋk ˌɒptɪmaɪˈzeɪʃən/ | 异步优化 |
| backpressure | /ˈbækpreʃər/ | 背压 |
| batch cycle | /bætʃ ˈsaɪkəl/ | 批处理周期 |
| file size estimate | /faɪl saɪz ˈestɪmeɪt/ | 文件大小估算 |
| runbook | /ˈrʌnbʊk/ | 操作手册 |

---

## Reading Comprehension

1. **Why does Li think daily partitioning alone is insufficient for the order table?**

   **Answer:** Because a single daily partition holds 100 million rows, and even with partition pruning, the scan volume remains too large for queries that only need the last three days.

2. **What is the drawback of switching to hourly partitions?**

   **Answer:** It generates many small files (240 per day), which overloads HDFS NameNode and causes high I/O scheduling overhead, negating the query speed benefit.

3. **How does Z-Order sorting help without changing the partition granularity?**

   **Answer:** It clusters data by `user_id` within each daily partition, allowing queries filtering on `user_id` to skip large chunks of data, achieving similar pruning to hourly partitions but without creating small files.

4. **Which tools support Z-Order optimisation, and what command is used?**

   **Answer:** Delta Lake and Apache Iceberg support it via the `OPTIMIZE ZORDER BY (...)` command, which reorganises files after the daily write.

5. **What is the final storage strategy Zhou decides on for each layer?**

   **Answer:** ODS uses hourly partitions for raw ingestion; DWD uses daily partitions with Z-Order by `user_id` and asynchronous `OPTIMIZE`; DWS uses daily aggregates with `MERGE INTO` for incremental updates.

---

*Word count (dialogue): ~508 words*
*Level: Intermediate / D2*
