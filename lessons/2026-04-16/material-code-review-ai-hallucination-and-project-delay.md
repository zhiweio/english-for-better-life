# 【中级】Code Review - AI Hallucination & Project Delay

## 角色及场景

- **Tech Lead（技术主管）**：负责项目进度和技术决策，正在了解支付模块延期的原因。
- **Dev（开发人员）**：负责代码审查，发现了 AI 生成代码中的多处幻觉错误。

**场景**：团队使用 AI 辅助生成支付模块的核心代码。Dev 在代码审查中发现 AI 产生了多个幻觉问题，包括调用不存在的方法、错误的重试逻辑和安全漏洞，导致模块需要大量重写，项目延期两天。Dev 正在向 Tech Lead 解释具体情况。

## 对话脚本（中级难度）

**Tech Lead:**

Our payment module is two days behind schedule. What caused the delay?

**Dev:**

I discovered multiple **AI hallucinations** during the **code review** of the AI-generated code.

**Tech Lead:**

What exactly is an AI hallucination in the context of source code?

**Dev:**

It means the AI writes functions that call **non-existent methods** or contain **faulty logic**. For example, it used `finalizeTransaction()` - a method that doesn't exist anywhere in our **codebase**.

**Tech Lead:**

Why didn't the **compiler** catch that error?

**Dev:**

Because the AI also generated a fake **import statement** for a missing library. The compiler saw the import and assumed the method was valid.

**Tech Lead:**

That's a serious **logic error**. What other problems did you find?

**Dev:**

The AI implemented a **retry loop** without any waiting period. This creates a **busy-wait** that wastes **CPU cycles** and increases **latency** under heavy load.

**Tech Lead:**

Did our **unit tests** detect these issues before the review?

**Dev:**

No. The AI had written **misleading test mocks** that passed all **assertions**. The tests were green, but the code was fundamentally broken.

**Tech Lead:**

How many **critical issues** did you find in total?

**Dev:**

Eight critical issues across three **source files**. Two of them were **security vulnerabilities** - the AI omitted **input sanitization** in two **SQL queries**, creating **SQL injection** risks.

**Tech Lead:**

That could have caused a **data breach** in **production**. Have you fixed them?

**Dev:**

Yes, I rewrote those queries and added proper sanitization. However, the rework cost us two days.

**Tech Lead:**

What is your **recommendation** to prevent this from happening again?

**Dev:**

We should treat AI-generated code as a **rough draft** only. Always perform a **manual review** of the logic and **API calls**, and update our **code review checklist** to include common hallucination patterns.

**Tech Lead:**

Agreed. Let's document this and share it in the **retrospective meeting**.

## 词汇表（24个高频技术词汇）

| **词汇** | **释义** |
| -------- | -------- |
| AI hallucination | AI幻觉 |
| code review | 代码审查 |
| source code | 源代码 |
| non-existent methods | 不存在的方法 |
| faulty logic | 错误逻辑 |
| codebase | 代码库 |
| compiler | 编译器 |
| import statement | 导入语句 |
| logic error | 逻辑错误 |
| retry loop | 重试循环 |
| busy-wait | 忙等待 |
| CPU cycles | CPU周期 |
| latency | 延迟 |
| unit tests | 单元测试 |
| misleading test mocks | 误导性测试替身 |
| assertions | 断言 |
| critical issues | 严重问题 |
| source files | 源文件 |
| security vulnerabilities | 安全漏洞 |
| input sanitization | 输入过滤 |
| SQL queries | SQL查询 |
| SQL injection | SQL注入 |
| data breach | 数据泄露 |
| production | 生产环境 |
| recommendation | 建议 |
| rough draft | 草稿 |
| manual review | 人工审查 |
| API calls | API调用 |
| code review checklist | 代码审查清单 |
| retrospective meeting | 回顾会议 |

- ***What example does Dev give to explain AI hallucination?***

  参考答案：*The AI called a non-existent method `finalizeTransaction()` and generated a fake import statement for a missing library.*

- ***Why is a retry loop without waiting considered a problem?***

  参考答案：*It creates a busy-wait that wastes CPU cycles and increases latency.*

- ***Why did the unit tests not catch the AI hallucinations?***

  参考答案：*Because the AI also wrote misleading test mocks that passed all assertions, so the tests were verifying the wrong behavior.*

- ***What security vulnerabilities did the AI introduce?***

  参考答案：*The AI omitted input sanitization in SQL queries, creating SQL injection risks that could lead to a data breach.*

- ***What does Dev recommend to prevent similar delays in the future?***

  参考答案：*Treat AI-generated code as a rough draft only, always perform a manual review of logic and API calls, and update the code review checklist with hallucination patterns.*
