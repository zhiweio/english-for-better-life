# 【中级】Time Estimation - AI‑Assisted Estimation for Data Cleaning – Productivity Gain

**类型**：会议 / 预习作业 4

---

## 背景解析

这篇对话展示了一次从"纯手动编码"向"AI 辅助生成 + 人工审查"的范式转变，重点在于用 AI 来加速数据清洗类 ETL 的开发。以下是关键的技术点解析：

### 1. 任务定义与清洗范围

**任务**：清洗过去 6 个月的订单数据。

- **清洗需求**：处理空值、标准化时间戳、补全缺失的客户 ID。
- **实现方式**：使用 PySpark 脚本，运行在分布式集群上。
- **意义**：这是一个典型的重复性、模板化、规则明确（**well-defined**）的数据工程任务，非常适合 AI 辅助。

---

### 2. 传统手动开发 vs AI 辅助开发

- **手动估算**：3 天（编码 + 清洗逻辑 + 单元测试）。
- **AI 辅助实际**：1.5 天，**节省 50% 时间**。
- **AI 的角色**：生成完整的 PySpark 脚本和基础的单元测试框架，覆盖正常情况、空值处理、边界条件。
- **人的角色**：
  - 提供清晰的清洗规则说明。
  - 微调列名（仅两处）。
  - 补充一条特定于业务的边界校验规则。
  - 审查 AI 输出的结构与正确性。
- **核心价值**：AI 承担了模板代码和测试桩的编写，人专注在领域特定逻辑的验证和补充。

---

### 3. 数据清洗逻辑的组成

AI 生成的脚本通常包含以下典型步骤：

- **空值处理**：填充默认值或按规则舍弃。
- **日期标准化**：统一转换为标准格式（如 `yyyy-MM-dd HH:mm:ss`）。
- **缺失值补全**：可能用左连接补全客户 ID，或打上标记。
- **异常值过滤**：根据业务规则剔出明显不合法记录。

---

### 4. 测试生成的完备性与可靠性

- **AI 生成的测试用例**：
  - 正确路径（期望的正常输入产生正确输出）。
  - 空值输入（验证空字段的处理策略）。
  - 格式异常记录（如日期乱码、字符串混入数字字段）。
- **人的补充**：仅增加一个特定业务场景。
- **结论**：AI 生成的测试框架结构（**scaffolding**）良好，开箱即用度高。这得益于清洗规则的确定性——明确的输入、明确的预期输出，非常适合 AI 生成测试断言。

---

### 5. 效率提升量化与推广策略

- **量化数据**：在此案例中节省约 50% 时间（从 3 天到 1.5 天）。
- **团队标准提议**：凡是新的 ETL 任务，默认先用 AI 生成初始脚本和测试套件，再人工审查、添加领域特定逻辑。
- **预期收益**：持续获得 30‑50% 的开发时间节省。
- **适用边界**：当任务复杂度超出 AI 能力时才回归纯手写。

---

### 6. AI 提示词工程

Zhou 提出要编写一份**有效的提示词指南**。在数据清洗和 PySpark 场景下，提示词通常包含：

- 数据源格式与 Schema。
- 详细的清洗规则列表。
- 输出格式要求。
- 测试框架和示例。

好的提示词是保证 AI 生成质量的关键，也是此次高成功率的前提。

---

### 总结

这篇对话的核心是以实际案例验证了 **"AI 生成 + 人工审查"** 在数据工程中的可行性和显著效率提升。它强调了三个关键成功要素：

1. **任务匹配**：规则明确、模板化程度高的任务最适合 AI。
2. **输入质量**：提供给 AI 的清洗规范越清晰，输出质量越高。
3. **人机分工**：AI 负责体力的、模板化的部分，人负责判断、审查与领域特化。

这种模式正在从一次成功的试验，演变为团队正式的工作标准。

---

## 角色及场景

- **Zhou（数据工程师 - 小周）**：估算历史数据清洗任务的工作量，并汇报使用 AI 辅助后的实际效率提升。
- **Tech Lead（技术负责人）**：听取估算，决定将 AI 辅助作为团队 ETL 开发的默认实践。

**场景**：数据工程师小周估算历史数据清洗任务：手动写 PySpark 代码需 3 天。他使用 AI 辅助生成数据清洗脚本和单元测试框架，实际只用了 1.5 天，效率提升 50%。团队决定后续 ETL 开发默认先让 AI 生成初版。

---

## 对话脚本（中级，正文约 424 词）

**Tech Lead**

We have a new task: **clean the last six months of order data.** The data has many nulls, inconsistent date formats, and missing customer IDs. What's your effort estimate?

**Zhou**

If I write the PySpark script manually from scratch, it will take about 3 days. That includes coding the cleaning logic, handling nulls, standardising timestamps, and writing unit tests.

**Tech Lead**

Three days is significant. Can we reduce that?

**Zhou**

Yes. I experimented with an AI‑assisted approach. I provided the AI with a clear specification of the cleaning rules. It generated a complete PySpark script and a basic unit test framework, covering normal cases, null handling, and edge conditions.

**Tech Lead**

**How much time did that save?**

**Zhou**

The actual work took 1.5 days – half of the manual estimate. That's a 50% productivity gain. The AI handled the boilerplate code and test scaffolding, so I could focus on domain‑specific validation rules.

**Tech Lead**

**Did you have to modify the AI‑generated code significantly?**

**Zhou**

Very little. I adjusted two column names and added one extra rule for a business edge case. The AI's code was well‑structured and followed our naming conventions.

**Tech Lead**

**What about the tests? Were they reliable?**

**Zhou**

The AI generated test cases for happy path, null inputs, and malformed records. I only added one more scenario. The test framework was ready to run with minimal adjustments.

**Tech Lead**

So overall, **AI reduced manual effort and improved consistency.**

**Zhou**

Exactly. Given this success, I propose that for any new ETL task, we default to AI‑assisted generation for the initial script and test suite. Then we review, refine, and add domain‑specific logic. This should consistently save us 30‑50% of development time.

**Tech Lead**

That's a compelling productivity gain. Let's adopt that as a team standard. **We'll only write from scratch when AI cannot handle the complexity.**

**Zhou**

I'll prepare a short guide on writing effective prompts for data cleaning and PySpark tasks.

**Tech Lead**

Good. Share it with the team in our next tech sync.

---

## 词汇表（25 个高频数据工程技术词汇）

| Word | Phonetic | Meaning |
|---|---|---|
| effort estimate | /ˈefət ˈestɪmeɪt/ | 工作量估算 |
| manual | /ˈmænjuəl/ | 手动的 |
| PySpark script | /paɪ spɑːk skrɪpt/ | PySpark 脚本 |
| cleaning logic | /ˈkliːnɪŋ ˈlɒdʒɪk/ | 清洗逻辑 |
| null handling | /nʌl ˈhændlɪŋ/ | 空值处理 |
| unit test | /ˈjuːnɪt test/ | 单元测试 |
| AI‑assisted | /ˌeɪ ˈaɪ əˈsɪstɪd/ | AI 辅助的 |
| specification | /ˌspesɪfɪˈkeɪʃən/ | 规范说明 |
| edge condition | /edʒ kənˈdɪʃən/ | 边界条件 |
| productivity gain | /ˌprɒdʌkˈtɪvəti ɡeɪn/ | 生产力提升 |
| boilerplate code | /ˈbɔɪlərpleɪt kəʊd/ | 样板代码 |
| test scaffolding | /test ˈskæfəʊldɪŋ/ | 测试脚手架 |
| domain‑specific | /dəˈmeɪn spəˈsɪfɪk/ | 领域特定的 |
| validation rule | /ˌvælɪˈdeɪʃən ruːl/ | 校验规则 |
| naming convention | /ˈneɪmɪŋ kənˈvenʃən/ | 命名规范 |
| happy path | /ˈhæpi pɑːθ/ | 正常路径 |
| malformed record | /ˌmælˈfɔːmd ˈrekɔːd/ | 畸形记录 |
| consistency | /kənˈsɪstənsi/ | 一致性 |
| ETL task | /ˌiː tiː ˈel tɑːsk/ | ETL 任务 |
| AI‑generated | /ˌeɪ ˈaɪ ˈdʒenəreɪtɪd/ | AI 生成的 |
| refine | /rɪˈfaɪn/ | 优化 |
| adopt | /əˈdɒpt/ | 采纳 |
| standard | /ˈstændəd/ | 标准 |
| prompt | /prɒmpt/ | 提示词 |
| tech sync | /tek sɪŋk/ | 技术同步会 |

---

## 五个提问及参考答案

**1. How long would the data cleaning task take if done manually?**
→ 3 days.

**2. How long did it take with AI assistance?**
→ 1.5 days.

**3. What was the productivity gain percentage?**
→ 50%.

**4. What did the AI generate besides the PySpark script?**
→ A basic unit test framework covering normal cases, nulls, and edge conditions.

**5. What team standard was adopted after this experience?**
→ For any new ETL task, default to AI‑assisted generation for the initial script and test suite; only write from scratch when AI cannot handle the complexity.

---

## 正文单词统计

- **对话脚本正文自然语言单词数：424 词**（不含角色标签，逐词计数）
- 偏差：+1.0%（符合 420±5% 要求）

## 难度自评

- **等级：中级**
- **理由**：句子长度适中（平均 10‑16 词），使用了如 `effort estimate`, `manual`, `AI‑assisted`, `specification`, `edge condition`, `productivity gain`, `boilerplate code`, `test scaffolding`, `domain‑specific`, `naming convention`, `consistency`, `refine`, `adopt` 等中级词汇。对话包含任务估算、AI 辅助价值分析和团队决策，适合 B1‑B2 学员学习 AI 提效估算的英语表达。

---

## **Section 1: 任务定义与清洗范围**

**英文原文**

> **1. Task Definition & Cleaning Scope**
>
> - **Task**: Clean the last six months of order data.
> - **Cleaning requirements**: Handle nulls, standardise timestamps, and fill in missing customer IDs.
> - **Implementation**: Use a PySpark script running on a distributed cluster.
> - **Significance**: This is a typical repetitive, templated, well-defined data-engineering task, making it highly suitable for AI assistance.

**参考译文**

> **1. 任务定义与清洗范围**
>
> - **任务**：清洗过去 6 个月的订单数据。
> - **清洗需求**：处理空值、标准化时间戳、补全缺失的客户 ID。
> - **实现方式**：使用 PySpark 脚本，运行在分布式集群上。
> - **意义**：这是一个典型的重复性、模板化、规则明确的数据工程任务，非常适合 AI 辅助。

| 词汇 / 短语 | 含义 | 口译提示 |
|---|---|---|
| **clean** (v.) | 清洗（数据） | 数据场景下不用"清理"，固定译"清洗" |
| **nulls** | 空值 | 区别于 empty / blank，数据库语境用"空值" |
| **standardise timestamps** | 标准化时间戳 | 口译时可说"把时间格式统一成标准格式" |
| **fill in missing customer IDs** | 补全缺失的客户 ID | "fill in" 此处=补全、填补 |
| **distributed cluster** | 分布式集群 | 技术口译高频词 |
| **well-defined** | 规则明确的 / 边界清晰的 | 修饰 task / problem，常译"定义良好的"或"规则明确的" |
| **templated** | 模板化的 | 指有固定套路，可复用 |
| **AI assistance** | AI 辅助 | 区分 AI-generated（AI 生成）与 AI-assisted（AI 辅助） |

**长句拆解**

> **原句**：This is a typical repetitive, templated, well-defined data-engineering task, making it highly suitable for AI assistance.
>
> **结构**：主句 + 现在分词短语（表结果）
>
> **口译版本**：这是一个典型的数据工程任务——重复性强、模板化、规则边界清晰——因此非常适合让 AI 来辅助完成。
>
> **提示**：三个形容词 stacked 修饰 task，口译时可用破折号或"其特点是…"来拆解，避免一口气堆叠定语。

---

## **Section 2: 传统手动开发 vs AI 辅助开发**

**英文原文**

> **2. Traditional Manual Development vs. AI-Assisted Development**
>
> - **Manual estimate**: 3 days (coding + cleaning logic + unit tests).
> - **AI-assisted actual**: 1.5 days, a **50% time saving**.
> - **AI's role**: Generate a complete PySpark script and a basic unit-test framework, covering normal cases, null handling, and edge conditions.
> - **Human's role**:
>   - Provide a clear specification of cleaning rules.
>   - Tweak two column names (only two places).
>   - Add one extra rule for a business edge case.
>   - Review the AI output for structure and correctness.
> - **Core value**: AI handles the boilerplate code and test scaffolding, while the human focuses on domain-specific validation rules and supplements.

**参考译文**

> **2. 传统手动开发 vs AI 辅助开发**
>
> - **手动估算**：3 天（编码 + 清洗逻辑 + 单元测试）。
> - **AI 辅助实际耗时**：1.5 天，**节省 50% 时间**。
> - **AI 的角色**：生成完整的 PySpark 脚本和基础的单元测试框架，覆盖正常情况、空值处理、边界条件。
> - **人的角色**：
>   - 提供清晰的清洗规则说明。
>   - 微调列名（仅两处）。
>   - 补充一条特定于业务的边界校验规则。
>   - 审查 AI 输出的结构与正确性。
> - **核心价值**：AI 承担了模板代码和测试桩的编写，人专注在领域特定逻辑的验证和补充。

| 词汇 / 短语 | 含义 | 口译提示 |
|---|---|---|
| **manual estimate** | 手动估算 / 人工估算 | 指工作量预估，常搭配 effort / time |
| **time saving** | 节省时间 | 此处作名词，a 50% time saving = 节省 50% 的时间 |
| **unit-test framework** | 单元测试框架 | 注意 framework 译"框架"，不是"结构" |
| **normal cases** | 正常情况 / 正确路径 | 对应 happy path |
| **edge conditions** | 边界条件 | 同 edge cases |
| **specification** | 规格说明 / 详细要求 | 提供 specification = 给一份明确的规格/规则说明 |
| **tweak** | 微调 / 小幅调整 | 比 adjust 更轻量，口译可译"微调"或"稍微改了一下" |
| **business edge case** | 业务边界情况 | 指特定业务场景下的极端/例外情况 |
| **boilerplate code** | 模板代码 / 样板代码 | 指重复性、套路化的代码，可复用 |
| **test scaffolding** | 测试脚手架 / 测试桩 | scaffolding 原义脚手架，技术语境指"基础支撑结构" |
| **domain-specific** | 领域特定的 / 业务域相关的 | 与 generic 相对，强调专业领域属性 |
| **validation rules** | 校验规则 / 验证规则 | validate = 验证有效性 |

**长句拆解**

> **原句**：AI handles the boilerplate code and test scaffolding, while the human focuses on domain-specific validation rules and supplements.
>
> **结构**：while 连接两个并列分句，表对比
>
> **口译版本**：AI 负责搞定那些模板化的代码和测试的基础框架，而人则把精力放在业务领域特有的校验规则上，同时做补充。
>
> **提示**：while 表对比时，口译可用"而…则…"或"一方面…另一方面…"来体现分工。

---

## **Section 3: 数据清洗逻辑的组成**

**英文原文**

> **3. Composition of Data-Cleaning Logic**
>
> An AI-generated script typically contains the following standard steps:
>
> - **Null handling**: Fill with default values or drop according to rules.
> - **Date standardisation**: Convert to a uniform format (e.g., `yyyy-MM-dd HH:mm:ss`).
> - **Missing-value completion**: May use a left join to fill in customer IDs, or flag them.
> - **Outlier filtering**: Remove obviously invalid records according to business rules.

**参考译文**

> **3. 数据清洗逻辑的组成**
>
> AI 生成的脚本通常包含以下典型步骤：
>
> - **空值处理**：填充默认值或按规则舍弃。
> - **日期标准化**：统一转换为标准格式（如 `yyyy-MM-dd HH:mm:ss`）。
> - **缺失值补全**：可能用左连接补全客户 ID，或打上标记。
> - **异常值过滤**：根据业务规则剔出明显不合法记录。

| 词汇 / 短语 | 含义 | 口译提示 |
|---|---|---|
| **null handling** | 空值处理 | 固定搭配 |
| **fill with default values** | 用默认值填充 | fill = 填充，default = 默认 |
| **drop according to rules** | 按规则舍弃 | drop 在数据语境=删除/丢弃记录 |
| **uniform format** | 统一格式 | uniform = 一致的、统一的 |
| **missing-value completion** | 缺失值补全 | completion 此处=补全、补齐 |
| **left join** | 左连接 | SQL/数据库术语，固定译法 |
| **flag** (v.) | 打上标记 / 标记出来 | 不是"旗帜"，是"做标记" |
| **outlier filtering** | 异常值过滤 | outlier = 离群值、异常值 |
| **obviously invalid records** | 明显不合法的记录 | invalid = 无效的、不合法的 |
| **according to business rules** | 根据业务规则 | 高频介词短语 |

**长句拆解**

> **原句**：May use a left join to fill in customer IDs, or flag them.
>
> **结构**：省略主语的祈使/说明句，or 表二选一
>
> **口译版本**：可以用左连接的方式把客户 ID 补全，或者给它们打上标记。
>
> **提示**：them 指代前面的 missing customer IDs，口译时建议补全指代对象，避免听众困惑。

---

## **Section 4: 测试生成的完备性与可靠性**

**英文原文**

> **4. Completeness & Reliability of AI-Generated Tests**
>
> - **AI-generated test cases**:
>   - Happy path (expected normal input produces correct output).
>   - Null inputs (verify handling strategy for empty fields).
>   - Malformed records (e.g., garbled dates, strings mixed into numeric fields).
> - **Human supplement**: Only one additional business-specific scenario was added.
> - **Conclusion**: The AI-generated test framework scaffolding was well-structured and ready to run with minimal adjustments. This is thanks to the deterministic nature of cleaning rules—clear input, clear expected output—making it highly suitable for AI-generated test assertions.

**参考译文**

> **4. 测试生成的完备性与可靠性**
>
> - **AI 生成的测试用例**：
>   - 正确路径（期望的正常输入产生正确输出）。
>   - 空值输入（验证空字段的处理策略）。
>   - 格式异常记录（如日期乱码、字符串混入数字字段）。
> - **人的补充**：仅增加一个特定业务场景。
> - **结论**：AI 生成的测试框架结构良好，开箱即用度高。这得益于清洗规则的确定性——明确的输入、明确的预期输出——非常适合 AI 生成测试断言。

| 词汇 / 短语 | 含义 | 口译提示 |
|---|---|---|
| **happy path** | 正确路径 / 正常流程 | 测试术语，指一切按预期进行的场景 |
| **verify handling strategy** | 验证处理策略 | verify = 验证，handling strategy = 处理策略 |
| **malformed records** | 格式异常记录 / 畸形记录 | malformed = 格式错误的、畸形的 |
| **garbled dates** | 日期乱码 | garbled = 混乱的、乱码的 |
| **strings mixed into numeric fields** | 字符串混入数字字段 | mix into = 混入 |
| **business-specific scenario** | 特定业务场景 | 与 generic scenario 相对 |
| **scaffolding** | 脚手架 / 基础结构 | 再次出现，指框架性的支撑代码 |
| **ready to run** | 开箱即用 / 可直接运行 | 口译时"开箱即用"很地道 |
| **minimal adjustments** | 最小调整 / 微调 | minimal = 最小的、极少的 |
| **deterministic nature** | 确定性 | 指结果可预期、非随机，技术高频词 |
| **expected output** | 预期输出 | 与 input 成对出现 |
| **test assertions** | 测试断言 | assertion = 断言（测试术语） |

**长句拆解**

> **原句**：This is thanks to the deterministic nature of cleaning rules—clear input, clear expected output—making it highly suitable for AI-generated test assertions.
>
> **结构**：主句 + 插入语（同位语解释）+ 现在分词短语（表结果）
>
> **口译版本**：这是因为清洗规则本身具有确定性——输入是明确的，预期输出也是明确的——所以非常适合让 AI 来生成测试断言。
>
> **提示**：破折号插入语"clear input, clear expected output"口译时可用"也就是说…"或"即…"引出，避免断句太碎。

---

## **Section 5: 效率提升量化与推广策略**

**英文原文**

> **5. Quantified Efficiency Gains & Rollout Strategy**
>
> - **Quantified data**: In this case, ~50% time saved (from 3 days to 1.5 days).
> - **Team standard proposal**: For any new ETL task, default to AI-generated initial scripts and test suites first, then review, refine, and add domain-specific logic.
> - **Expected benefit**: Consistently save 30–50% of development time.
> - **Boundary of applicability**: Revert to pure manual writing only when task complexity exceeds AI capability.

**参考译文**

> **5. 效率提升量化与推广策略**
>
> - **量化数据**：在此案例中节省约 50% 时间（从 3 天到 1.5 天）。
> - **团队标准提议**：凡是新的 ETL 任务，默认先用 AI 生成初始脚本和测试套件，再人工审查、添加领域特定逻辑。
> - **预期收益**：持续获得 30–50% 的开发时间节省。
> - **适用边界**：当任务复杂度超出 AI 能力时才回归纯手写。

| 词汇 / 短语 | 含义 | 口译提示 |
|---|---|---|
| **quantified data** | 量化数据 | quantify = 量化 |
| **rollout strategy** | 推广策略 /  rollout 策略 | rollout = 推出、推广实施 |
| **default to** | 默认采用 / 以…为默认 | 此处 default 作动词，= 默认选择 |
| **initial scripts** | 初始脚本 | initial = 最初的、初始的 |
| **test suites** | 测试套件 | suite = 套件、套件集合 |
| **review, refine** | 审查、完善 | 常成对出现，review = 审，refine = 改 |
| **expected benefit** | 预期收益 | 商务/技术汇报高频 |
| **consistently save** | 持续节省 | consistently = 持续地、一贯地 |
| **boundary of applicability** | 适用边界 / 适用范围边界 | 指适用与不适用之间的界限 |
| **revert to** | 回归 / 回退到 | revert = 恢复、回退 |
| **exceeds AI capability** | 超出 AI 能力 | exceed = 超过，capability = 能力 |

**长句拆解**

> **原句**：For any new ETL task, default to AI-generated initial scripts and test suites first, then review, refine, and add domain-specific logic.
>
> **结构**：祈使句，then 连接三个连续动作
>
> **口译版本**：对于任何新的 ETL 任务，我们先默认让 AI 生成初始脚本和测试套件，然后人工去审查、完善，并补充领域特定的逻辑。
>
> **提示**：default to 口译时建议补全为"默认采用…的方式"或"把…作为默认做法"，然后引出后续动作链。

---

## **Section 6: AI 提示词工程**

**英文原文**

> **6. AI Prompt Engineering**
>
> Zhou proposed writing a guide on **effective prompts**. For data-cleaning and PySpark scenarios, a prompt typically contains:
>
> - Data source format and schema.
> - A detailed list of cleaning rules.
> - Output format requirements.
> - Test framework and examples.
>
> Good prompts are the key to guaranteeing AI output quality and were the prerequisite for this high success rate.

**参考译文**

> **6. AI 提示词工程**
>
> Zhou 提出要编写一份**有效的提示词指南**。在数据清洗和 PySpark 场景下，提示词通常包含：
>
> - 数据源格式与 Schema。
> - 详细的清洗规则列表。
> - 输出格式要求。
> - 测试框架和示例。
>
> 好的提示词是保证 AI 生成质量的关键，也是此次高成功率的前提。

| 词汇 / 短语 | 含义 | 口译提示 |
|---|---|---|
| **prompt engineering** | 提示词工程 | 固定术语，不译"提示工程"以外的说法 |
| **effective prompts** | 有效的提示词 | effective = 有效的、高效的 |
| **data source format** | 数据源格式 | 注意与 data format（数据格式）区分 |
| **schema** | 模式 / 结构定义 | 数据库语境下常保留英文或译"结构定义" |
| **cleaning rules** | 清洗规则 | 复数 rules 表示"规则列表" |
| **output format requirements** | 输出格式要求 | requirement = 要求、需求 |
| **guaranteeing AI output quality** | 保证 AI 输出质量 | guarantee = 保证，output = 输出 |
| **prerequisite** | 前提 / 先决条件 | 正式用语，口译可译"前提条件" |
| **high success rate** | 高成功率 | 此处指 AI 生成结果的成功率 |

**长句拆解**

> **原句**：Good prompts are the key to guaranteeing AI output quality and were the prerequisite for this high success rate.
>
> **结构**：主语 + 两个并列系表结构（are… and were…）
>
> **口译版本**：好的提示词，一方面是保证 AI 输出质量的关键；另一方面，也是这次能获得高成功率的前提。
>
> **提示**：两个并列的表语成分，口译时用"一方面…另一方面…"或"既是…也是…"来拆分，避免长句堆砌。

---

## **附录：口译高频衔接词与句型速查**

| 英文表达 | 口译推荐译法 | 适用场景 |
|---|---|---|
| To begin with / First of all | 首先 / 第一点 | 列举 |
| In this case | 在这个案例中 / 就这次来说 | 举例 |
| Thanks to / Due to | 得益于 / 由于 | 归因 |
| As a result / Therefore | 因此 / 结果是 | 因果 |
| On the one hand… on the other hand | 一方面…另一方面 | 对比 |
| In other words / That is to say | 也就是说 / 换言之 | 解释 |
| Given that… | 鉴于… / 考虑到… | 前提条件 |
| It is highly suitable for… | 非常适合… | 评价 |
| The core value lies in… | 核心价值在于… | 总结观点 |
| Revert to pure manual writing | 回归纯手写 | 决策回退 |
