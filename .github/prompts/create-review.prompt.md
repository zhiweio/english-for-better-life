---
name: "Create Cycle Review"
description: "Create a weekly or cycle English review from a teacher article, word list, Q&A, and practice priorities"
argument-hint: "Paste the cycle materials, such as article, word list, Q&A, corrections, and review requirements"
agent: "agent"
---
Create a new file under `review/` using the workspace instructions for this repository.

Requirements:

- Treat the learner as someone who can read but speaks with great difficulty.
- Build a cycle review, not a topic script, not a single-lesson note, and not a high-frequency article file.
- Follow the required review structure from [copilot-instructions](../copilot-instructions.md).
- Keep the teacher-provided article in the file, but clean obvious formatting or language noise when the intended meaning is clear.
- Cover all usable user-provided words, phrases, questions, answers, and correction points somewhere in the review.
- If the user provides an explicit review list, treat that list as mandatory coverage.
- Exact duplicates can be merged, but do not silently drop usable items.
- If an item is weak, unclear, or still wrong, place it in `Pronunciation and Speaking Fixes` or `Priority Practice Analysis` instead of omitting it.
- Make the learner's top practice priorities explicit, including why they matter and what to practice first.
- Use concise Chinese support where it lowers the speaking and review barrier.
- Keep the review compact, reusable, and suitable for repeated study across several days.
- Prefer a date-based or cycle-based filename unless the user explicitly asks for another naming style.

The user's message after invoking this prompt contains the cycle materials and any extra requirements.
Use that input directly to produce the new review file.