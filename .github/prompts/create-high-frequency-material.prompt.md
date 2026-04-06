---
name: "Create High-Frequency Material"
description: "Create high-frequency vocabulary training material from a short article with original text, words, phrases, pronunciation practice, and grammar patterns"
argument-hint: "Paste a short article and any requirements"
agent: "agent"
---
Create a new file under `高频1000词/` using the workspace instructions for this repository.

Requirements:

- Treat the learner as someone who can read but speaks with great difficulty.
- Build vocabulary training material, not a topic script and not a post-lesson note.
- Follow the required high-frequency vocabulary material structure from [copilot-instructions](../copilot-instructions.md).
- Keep the original article or dialogue in the file.
- Focus on high-frequency or highly reusable words and phrases.
- Make pronunciation practice a major part of the material.
- Highlight good sentence patterns and grammar structures that are worth reusing.
- Keep the output compact, repeatable, and easy to review many times.
- Use a numeric filename prefix like `1_`, `2_`, `3_` instead of a date prefix unless the user explicitly asks otherwise.

The user's message after invoking this prompt contains the article and any extra requirements.
Use that input directly to produce the new file.
