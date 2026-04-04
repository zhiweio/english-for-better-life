# Talk-to-Data English Speaking Topic Pack

## Goal of This Pack

This pack is for a one-hour one-to-one English lesson.
The topic is my Talk-to-Data project.
The main goal is not to sound perfect.
The main goal is to keep talking, explain my project clearly, and answer simple follow-up questions.

This pack uses simple spoken English at about B1 level.
Technical words stay professional when needed.

## Core Topic

How a business question becomes a safe data answer in Talk-to-Data.

## One-Sentence Version

Talk-to-Data is a system that lets business users ask questions in natural language, and the backend turns the question into a safe SQL query, runs it, and returns results with explanations.

## One-Minute Version

My project is called Talk-to-Data. It is an AI data system for business users. Many users want data, but they cannot write SQL. Our system lets them ask questions in natural language, like "What was last month's GMV by brand?" Then the backend understands the question, finds the right tables and metrics, generates SQL, checks safety rules, runs the query, and returns the result. I think the most important part is that it is not only smart, but also safe and governed.

## Two-Minute Opening

Today I want to talk about a project I work on called Talk-to-Data.
It is a backend system for data analysis.
The main idea is simple: business users want answers from data, but many of them do not know SQL.
So we build a system that lets them ask questions in natural language.

For example, a user can ask, "What was last month's GMV by brand?"
Our system will understand the question, find the correct data assets, generate SQL, check security and business rules, run the query, and return the result.

This project is not only about AI.
It is also about safety, governance, and reliability.
We do not want the model to guess.
We want the system to use the right metadata, follow the right business rules, and block risky queries.

I like this project because it combines several parts together.
It has natural language understanding, data retrieval, SQL generation, security checks, and result presentation.
So it is a good example of how AI can help in enterprise data work.

## Suggested 60-Minute Lesson Flow

### Part 1. Warm-up: 5 minutes

Use these easy opening lines:

My topic today is a project I work on.
It is called Talk-to-Data.
It is an AI system for data questions.
I want to explain what problem it solves and how the backend works.

### Part 2. Project Introduction: 8 minutes

Main points:

- What the project is
- Who uses it
- Why it is useful

### Part 3. Main System Flow: 15 minutes

Main points:

- User asks a question
- System understands the question
- System retrieves metadata
- System generates SQL
- System checks safety
- System runs the query
- System returns the answer

### Part 4. Key Backend Design: 12 minutes

Main points:

- Why we use multiple agents or modules
- Why retrieval matters
- Why guardrails matter

### Part 5. Safety and Governance: 10 minutes

Main points:

- Permission control
- PII protection
- SQL validation
- Business rules

### Part 6. Personal Work and Reflection: 5 minutes

Main points:

- What I work on
- What is difficult
- What I learned

### Part 7. Free Q&A: 5 minutes

Use short answers first.
Then add more detail if the teacher asks.

## Main Speaking Outline

### 1. What Is Talk-to-Data?

Talk-to-Data is an enterprise data assistant.
It helps business users ask questions in natural language.
They do not need to write SQL by themselves.
The backend system understands the question and turns it into a safe data query.

It is useful because many business users know the business well, but they are not good at SQL.
They want fast answers, not a technical tool.
So our project tries to reduce the gap between business language and data language.

Short answer if I get stuck:

It is a natural-language data query system.
Users ask questions in plain language, and the system returns safe data answers.

### 2. What Problem Does It Solve?

In many companies, data is hard to use.
Business users often need help from data analysts.
This makes the process slow.
Also, business words and database words are often different.
For example, a user may say "sales," but in the system there may be different metrics like GMV or net revenue.

Another problem is safety.
Even if AI can generate SQL, it may generate the wrong SQL.
It may use the wrong table, the wrong column, or break a security rule.
So the real problem is not only understanding the question.
The real problem is giving a correct and safe answer.

Short answer if I get stuck:

It solves two problems.
First, business users cannot easily use data.
Second, AI-generated SQL must be controlled carefully.

### 3. Who Uses This System?

The main users are business users, analysts, and managers.
They want quick answers from data.
They may ask about sales, channels, brands, trends, or KPI changes.

There are also technical users behind the system.
Data teams define metadata, business terms, rules, and permissions.
So the end users ask questions, but the system is supported by governance work from data teams.

Short answer if I get stuck:

The front users are business users.
The support users are data and governance teams.

### 4. The Main Example Question

The example I like to use is:

What was last month's GMV by brand?

I use this example because it is simple but complete.
It has a metric, which is GMV.
It has a time range, which is last month.
And it has a dimension, which is brand.
So it is a very good example to explain the whole system flow.

## Full Script: The Question Journey

### Step 1. The User Asks a Question

First, the user sends a question in natural language.
For example, the user asks, "What was last month's GMV by brand?"

This looks simple for a human.
But for a backend system, this question has many hidden parts.
The system needs to know what GMV means, what last month means, and which brand field should be used.

### Step 2. The System Understands the Question

Then the system tries to understand the question.
It identifies the intent.
It extracts the metric, the time range, and the grouping field.
In this case, the metric is GMV, the time range is last month, and the grouping field is brand.

This step is important because natural language is often unclear.
Sometimes users use business words, not technical words.
So the system must translate business meaning into a structured form.

Short version:

At this step, the system changes a human question into a machine-friendly structure.

### Step 3. The System Chooses a Route

After that, the system decides what kind of workflow to use.
Some questions are simple KPI lookups.
Some are normal SQL questions.
Some are complex analysis tasks.
Some are only business knowledge questions.

For my example, the system usually chooses a normal query path.
It is not too simple, because it needs grouping.
But it is not a very deep analysis either.

Why is routing important?
Because not every question needs the same cost and the same process.
Good routing makes the system faster and more stable.

Short version:

The router decides which path is best for the question.

### Step 4. The System Retrieves the Right Metadata

This is one of the most important steps.
Before generating SQL, the system must find the right metadata.
It needs the correct table, the correct columns, the metric definition, and maybe some business rules.

In our project, retrieval is not only keyword search.
It uses a hybrid method.
It can use relational metadata, vector search, and graph relationships.
This helps the system find relevant assets more accurately.

For example, if the user asks about GMV, the system can find the GMV metric definition.
Then it can find which table contains the data and what business rules are connected to that metric.

Short version:

Retrieval means the system finds the right data context before writing SQL.

### Step 5. The System Generates SQL

After retrieval, the system generates SQL.
But it does not generate SQL in an empty space.
It uses the retrieved metadata as context.
So the SQL is grounded in real tables, real columns, and real rules.

For the example question, the SQL may group by brand and sum the GMV for the last month.
I do not need to explain every SQL detail in class.
I only need to say that the system turns the user question into an executable query.

Short version:

The SQL generator writes a query based on the question and the metadata context.

### Step 6. The System Checks Safety and Rules

This is my favorite part of the project.
The system does not trust generated SQL directly.
It checks the SQL before execution.

There are several kinds of checks.
First, it checks syntax.
Second, it checks policy rules, for example whether the query is read-only.
Third, it may check cost or execution risk.
Also, it can enforce business rules and permission rules.

For example, if a metric should only include completed orders, the system should keep that rule.
If a user tries to access sensitive data, the system should block it.

Short version:

The system has guardrails, so the SQL must be safe, valid, and allowed.

### Step 7. The System Runs the Query

If the SQL passes all checks, the system runs it on the data platform.
Then it gets the result rows and columns.
It may also record execution time and other metadata.

This step sounds simple, but it is important to separate query generation from query execution.
That separation makes the system safer.

Short version:

Only validated SQL can reach the execution layer.

### Step 8. The System Returns the Result

Finally, the system returns the result to the user.
Sometimes it is only a table.
Sometimes it also includes a chart or a short insight summary.

So the full process is not only question to SQL.
It is question to understanding, then retrieval, then validation, then execution, and finally explanation.

Short version:

The final answer is not only data.
It is also an easier business explanation.

## Why the Backend Design Matters

### A. Why We Do Not Use One Single Agent

In my opinion, one single AI agent is not enough for this kind of system.
The reason is that the job is too complex.
The system needs to understand language, retrieve data context, generate SQL, check safety, and sometimes explain results.

If one model does everything, it is harder to control quality.
So we split the work into different stages or modules.
This design is easier to debug, test, and improve.

Short answer:

We split the task because each step has a different job and a different risk.

### B. Why Retrieval Is So Important

A lot of people think the core problem is SQL generation.
But I think retrieval is even more important.
If the system finds the wrong table or wrong metric, even perfect SQL is still wrong.

So retrieval gives the system grounding.
It reduces hallucination and gives business context.

Short answer:

Bad retrieval leads to bad SQL.
Good retrieval gives the model the right context.

### C. Why Guardrails Are So Important

Guardrails are necessary because enterprise data is sensitive.
The system should not expose PII.
It should not allow risky SQL.
It should not break business rules.

So in this project, safety is not an extra feature.
It is part of the core design.

Short answer:

The system must be smart, but it must also be safe and controllable.

## Safety and Governance Section

When I talk about safety, I usually mention four points.

First, user permissions matter.
Different users should see different data.

Second, sensitive data must be protected.
If some columns contain private information, the system should hide or mask them.

Third, generated SQL must follow policy rules.
For example, it should be read-only.

Fourth, business rules matter.
A metric may have a specific definition, and the system should follow that definition.

I think this part is very important in enterprise systems.
Without governance, AI may be fast, but it may also be dangerous.

Short version:

Governance means the system follows permissions, privacy rules, SQL policy, and business definitions.

## My Personal Work

You can choose one of these versions.

### Version A. General Version

In this project, I focus mainly on backend design and implementation.
I care a lot about how the system moves from user question to safe execution.
I also pay attention to system structure, data flow, and reliability.

### Version B. More Technical Version

In this project, I work on backend architecture, agent flow, and system integration.
I am interested in how to connect natural language understanding, metadata retrieval, SQL generation, and validation in one stable pipeline.

### Version C. Safer Version If I Do Not Want Too Much Detail

I mainly work on the backend side.
I help design and improve the workflow, so the system can answer questions more accurately and more safely.

## What Is Difficult in This Project?

One difficulty is ambiguity.
Users often ask short questions, but the meaning is not complete.
For example, they may say "sales," but they do not say whether they mean GMV or net revenue.

Another difficulty is balancing intelligence and control.
We want the system to be flexible, but we also want strong guardrails.

A third difficulty is context quality.
If metadata is weak or inconsistent, the system becomes weaker.
So the AI part and the governance part must work together.

Short version:

The biggest challenge is making the system both smart and safe.

## What I Learned from This Project

This project taught me that AI alone is not enough.
Good system design needs retrieval, validation, governance, and clear boundaries.

It also taught me that enterprise projects are not only about model quality.
They are also about permissions, correctness, observability, and user trust.

Finally, I learned that good architecture should make complex things easier to understand and easier to improve.

Short version:

I learned that a useful AI system needs both intelligence and engineering discipline.

## Teacher Follow-up Questions and Model Answers

### 1. Why is this project useful?

It is useful because business users can get answers from data more easily.
They do not need to write SQL, and they can ask questions in natural language.

Longer answer:

It improves efficiency.
It can reduce the communication cost between business teams and data teams.
It also makes data access more user-friendly.

### 2. Why not just use ChatGPT directly on the database?

Because direct access is risky.
A general model may use the wrong tables, break security rules, or expose sensitive data.
Our system adds metadata grounding, routing, validation, and governance.

### 3. What is the most important technical part?

For me, the most important part is the combination of retrieval and guardrails.
Retrieval gives the right context, and guardrails reduce risk.

### 4. What does governance mean in your project?

In this project, governance means permissions, privacy protection, business rules, and controlled SQL behavior.
It means the system follows company rules, not only user requests.

### 5. What happens if the user asks an unclear question?

If the question is unclear, the system can ask for clarification.
For example, it can ask which metric the user means or which time period the user wants.

### 6. What happens if the generated SQL is wrong?

The system checks the SQL before execution.
If the SQL fails validation, it should not run directly.
In some cases, the system can try again with better context or repair logic.

### 7. Why do you talk so much about safety?

Because enterprise data can be sensitive.
If the system is fast but unsafe, users will not trust it.
Trust is very important in data systems.

### 8. What is one thing you are proud of in this project?

I am proud that the system is designed not only to generate answers, but also to control risk.
I think that makes it more practical for real business use.

### 9. Is this project only about SQL?

No, not really.
SQL is one important part, but the project also includes language understanding, retrieval, governance, validation, and result explanation.

### 10. What part do you want to improve in the future?

I want to improve accuracy, especially in ambiguous cases.
I also want to improve the user experience, so follow-up questions and explanations feel more natural.

## Short Answer and Long Answer Pairs

### Q: What does your system do?

Short answer:

It lets users ask data questions in natural language.

Long answer:

It lets business users ask questions in natural language, and the backend turns those questions into safe SQL queries and returns data results.

### Q: What is special about your backend?

Short answer:

It is not only smart, but also safe.

Long answer:

The backend does more than generate SQL. It also understands the question, retrieves the right metadata, validates the SQL, enforces rules, and protects sensitive data.

### Q: Why is the project difficult?

Short answer:

Because natural language is ambiguous.

Long answer:

The project is difficult because user questions are often incomplete or ambiguous, and the system must still return correct and safe results.

## Transition Sentences

Use these sentences to move from one part to another.

Let me start with the basic idea.

Now I want to explain the main workflow.

After that, I can talk about the backend design.

Another important point is safety.

From my point of view, retrieval is a key part.

If I explain it in a simple way, it works like this.

Let me give a concrete example.

There is also one challenge I want to mention.

Finally, I want to talk about what I learned.

## Listening Rescue Phrases

Use these when you do not catch the teacher's question.

Sorry, could you say that again?

Sorry, could you speak a little more slowly?

Do you mean the product side or the technical side?

Could you repeat the last part?

Let me make sure I understand your question.

If I understand correctly, you are asking about the backend flow, right?

Can I answer that in a simple way first?

## Time-Buying Phrases

Use these when you need a few seconds to think.

That is a good question.

Let me think for a second.

I would explain it like this.

There are two points I want to mention.

In a simple way, I would say this.

From the backend perspective, the key point is this.

## Repair Phrases When You Make a Mistake

Sorry, let me say that again.

What I mean is this.

Let me correct that.

I used the wrong word.

To be more precise, I mean the metadata layer, not the data table itself.

## Vocabulary Bank

### Core Project Words

- natural language: normal human language
- query: a request for data
- metric: a business measurement, like GMV
- dimension: a way to group data, like brand or region
- retrieval: finding the right data context
- metadata: data that describes data
- governance: rules and control for data use
- guardrails: safety checks
- validation: checking whether something is correct
- execution: running the query
- insight: a useful finding from data

### Useful Technical Words

- pipeline: a series of steps
- route: the chosen path in the system
- intent: what the user really wants
- context: the information around the task
- grounded: based on real data definitions
- permission: what a user is allowed to access
- sensitive data: private or risky data
- reliable: stable and trustworthy
- ambiguity: unclear meaning

## Easy Explanations for Important Technical Terms

### Agent

An agent is a part of the system that does one job.

### SQL Generation

SQL generation means the system writes a database query from a natural language question.

### Retrieval

Retrieval means the system finds the right tables, columns, metrics, and rules before generating SQL.

### Guardrails

Guardrails are checks that stop wrong or risky SQL.

### Governance

Governance means the system follows company rules about data definitions, permissions, and privacy.

## Pronunciation Focus Words

Practice these slowly:

- architecture
- retrieval
- governance
- validation
- permission
- sensitive
- execution
- reliable
- ambiguity
- enterprise

## Emergency Script When I Feel Nervous

If I feel nervous, I can use this shorter script.

My project is called Talk-to-Data.
It helps business users ask data questions in natural language.
The backend understands the question, finds the right metadata, generates SQL, checks safety, and returns the result.
I think the most important part is that the system is not only smart, but also safe.
It follows permissions, business rules, and privacy rules.
That is why I think this project is meaningful.

## Optional Practice Questions for Homework

Answer these aloud in English.

1. What is Talk-to-Data, and why is it useful?
2. What happens after the user asks a question?
3. Why is retrieval important before SQL generation?
4. Why are guardrails necessary in enterprise data systems?
5. What is the biggest challenge in your project?
6. What did you learn from this project?

## Final Closing

To summarize, Talk-to-Data is a system that turns natural language questions into safe data answers.
What makes it interesting is not only the AI part, but also the backend design behind it.
The system needs to understand the question, retrieve the right context, generate SQL, enforce rules, and return useful results.
For me, this project is a good example of how AI and engineering can work together in a practical business system.