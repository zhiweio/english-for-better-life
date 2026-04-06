# API Documentation

## Material Goal

- 理解这篇关于编写 API 文档的短文
- 掌握 documentation 场景里的高频词、短语和表达
- 重点练习 endpoint、request body、response、rate limiting 等常见英语

## Quick Chinese Brief

这篇短文讲的是开发者写 password reset API 的文档。内容包括接口标题、endpoint、request body、success response、error responses、cURL 示例以及 rate limiting 说明。文档写得清楚，团队里的其他开发者就能更容易使用 API。

这类材料很适合练“解释接口”和“说明文档内容”。重点不是背所有 HTTP 细节，而是把最常见的文档表达练熟。

## Original Text

**Theme: Writing clear documentation for a new API**

I finished coding the password reset API. Now I need to write documentation. Good documentation helps other developers use my code without bothering me.

I open a Markdown file. I start with a title and a short description.

"# Password Reset API - allows users to reset forgotten passwords."

Then I document the first endpoint. I write the method, the path, and what it does.

"**POST /api/auth/reset-request** - sends a reset email to the user."

I show the request body:

```json
{
  "email": "user@example.com"
}
```

I show the success response:

```json
{
  "message": "Reset email sent",
  "resetId": "abc123"
}
```

I also list the error responses:

- `400` - email is missing or invalid
- `404` - email not found in our system
- `429` - too many requests, try again later

Next, I document the second endpoint.

"**POST /api/auth/reset-confirm** - actually changes the password."

Request body:

```json
{
  "token": "abc123",
  "new_password": "MyNewPass123"
}
```

Success response:

```json
{
  "message": "Password updated successfully"
}
```

Error responses:

- `401` - token expired or invalid
- `400` - weak password

I add a quick example using cURL so developers can test it easily.

```bash
curl -X POST https://api.example.com/auth/reset-request \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'
```

Finally, I write a short note about rate limiting: max 3 requests per hour per email.

I save the file as `password-reset-api.md` and commit it to the repo. I also add a link to this doc in the pull request.

Now anyone on the team can use my API without asking me. Documentation is not fun, but it is necessary.

## Core High-Frequency Words

### 1. documentation

English meaning:
written information that explains how something works

中文提示：文档，说明文档

Pronunciation hint:
doc-u-men-TA-tion

Useful line:

Good documentation saves time for the team.

### 2. endpoint

English meaning:
a specific API URL and action

中文提示：接口端点

Pronunciation hint:
END-point

Useful line:

This endpoint sends a reset email.

### 3. request body

English meaning:
the data sent in the request

中文提示：请求体

Pronunciation hint:
re-QUEST BO-dy

Useful line:

The request body only needs one field.

### 4. response

English meaning:
the data returned by the API

中文提示：响应

Pronunciation hint:
re-SPONSE

Useful line:

The success response includes a message.

### 5. token

English meaning:
a value used to verify or identify something

中文提示：令牌

Pronunciation hint:
TO-ken

Useful line:

The token is required for reset confirmation.

### 6. invalid

English meaning:
not correct or not accepted

中文提示：无效的

Pronunciation hint:
in-VAL-id

Useful line:

The email is missing or invalid.

### 7. expired

English meaning:
no longer valid because time is over

中文提示：过期的

Pronunciation hint:
ex-PIRED

Useful line:

The token may be expired.

### 8. commit

English meaning:
to save changes in Git

中文提示：提交代码

Pronunciation hint:
com-MIT

Useful line:

I committed the documentation to the repo.

### 9. necessary

English meaning:
needed and important

中文提示：必要的

Pronunciation hint:
NEC-es-sar-y

Useful line:

Documentation is necessary for teamwork.

## Useful Phrases and Collocations

### 1. write documentation

中文提示：写文档

Pronunciation hint:
WRITE doc-u-men-TA-tion

Useful line:

I need to write documentation for the API.

### 2. short description

中文提示：简短说明

Pronunciation hint:
SHORT de-SCRIP-tion

Useful line:

Start with a short description.

### 3. success response

中文提示：成功响应

Pronunciation hint:
suc-CESS re-SPONSE

Useful line:

The success response returns a message.

### 4. error responses

中文提示：错误响应

Pronunciation hint:
ER-ror re-SPON-ses

Useful line:

I listed the error responses clearly.

### 5. rate limiting

中文提示：限流

Pronunciation hint:
RATE LIM-it-ing

Useful line:

We need a note about rate limiting.

### 6. per hour

中文提示：每小时

Pronunciation hint:
per HOUR

Useful line:

The limit is three requests per hour.

### 7. add a link

中文提示：添加链接

Pronunciation hint:
ADD a LINK

Useful line:

I added a link to the document in the PR.

### 8. without asking me

中文提示：不用来问我

Pronunciation hint:
with-OUT ASK-ing me

Useful line:

Now the team can use the API without asking me.

### 9. password reset

中文提示：密码重置

Pronunciation hint:
PASS-word re-SET

Useful line:

I finished the password reset API.

## Pronunciation Focus

### 1. documentation

Stress hint:
doc-u-men-TA-tion

中文提醒：重点在 `TA`，长词先慢读。

Repeat drill:

Good documentation helps the team.

### 2. endpoint

Stress hint:
END-point

中文提醒：前重后轻，比较短，但要读稳。

Repeat drill:

This endpoint changes the password.

### 3. response

Stress hint:
re-SPONSE

中文提醒：重点在后面，是 API 文档里的高频词。

Repeat drill:

The response is clear and simple.

### 4. invalid

Stress hint:
in-VAL-id

中文提醒：重点在 `VAL`，结尾不要吞音。

Repeat drill:

The token is invalid.

### 5. rate limiting

Stress hint:
RATE LIM-it-ing

中文提醒：两个词都要清楚，尤其是 `RATE`。

Repeat drill:

We added a note about rate limiting.

### 6. necessary

Stress hint:
NEC-es-sar-y

中文提醒：重点在 `NEC`，节奏不要太快。

Repeat drill:

Documentation is necessary.

## Good Expressions and Grammar Patterns

### 1. I start with ...

Pattern:
I start with ...

中文说明：很适合描述写文档的第一步。

Model line:

I start with a title and a short description.

Drill:

I start with __________.

### 2. I write ...

Pattern:
I write ...

中文说明：适合逐步说明文档包含什么内容。

Model line:

I write the method, the path, and what it does.

Drill:

I write __________.

### 3. I also list ...

Pattern:
I also list ...

中文说明：适合补充错误码、限制条件等信息。

Model line:

I also list the error responses.

Drill:

I also list __________.

### 4. so ... can ...

Pattern:
..., so ... can ...

中文说明：用来说明写文档的目的。

Model line:

I add a cURL example so developers can test it easily.

Drill:

I add __________ so developers can __________.

### 5. ... is not fun, but it is necessary.

Pattern:
... is not fun, but it is necessary.

中文说明：很自然的总结句型。

Model line:

Documentation is not fun, but it is necessary.

Drill:

__________ is not fun, but it is necessary.

## Retelling and Output Drill

### 3-Line Retelling

The writer finished the password reset API and then wrote documentation for it.
The document includes endpoints, request bodies, responses, and error codes.
In the end, the writer adds a cURL example and shares the doc with the team.

### 5-Line Retelling

This article is about writing API documentation.
The writer documents two password reset endpoints.
The document shows request bodies, success responses, and error responses.
It also includes a cURL example and a note about rate limiting.
Now the team can use the API more easily without asking the writer.

### Output Prompts

- Why is good API documentation important?
- What information should an API document include?
- Why do examples and error codes help other developers?

## Review Task

### 1. Read Aloud

Read the `Original Text` aloud once slowly and once at a natural speed.

### 2. Pronunciation Practice

Read all items in `Pronunciation Focus` aloud 3 times.
Pay attention to stress and technical terms.

### 3. Phrase Reuse

Use these 5 phrases to make your own short lines:

- write documentation
- success response
- error responses
- rate limiting
- add a link

### 4. Retelling

First say the `3-Line Retelling`.
Then try the `5-Line Retelling` without looking at the text.