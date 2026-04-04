---
name: "Create English Topic"
description: "Create a beginner-friendly speaking topic from raw material for a one-to-one English lesson"
argument-hint: "Paste source material and any lesson requirements"
agent: "agent"
---
Create a new topic file under `topics/` using the workspace instructions for this repository.

Requirements:

- Treat the learner as someone who can read but speaks with great difficulty.
- Build a speaking-training topic, not a reading summary.
- Follow the required topic structure from [copilot-instructions](../copilot-instructions.md).
- Use simple spoken English with concise Chinese support where helpful.
- If the user provides a target date or title, use it in the filename.
- If the user provides an existing draft path, keep the source draft intact unless explicitly told to overwrite it.

The user's message after invoking this prompt contains the source material and any extra lesson requirements.
Use that input directly to produce the new topic file.
