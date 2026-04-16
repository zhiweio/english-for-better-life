---
name: "Create English Note"
description: "Create a post-lesson English review note with pronunciation practice from free talk output, vocabulary, phrases, and short sentences"
argument-hint: "Paste lesson output, phrases, short sentences, and any note requirements"
agent: "agent"
---
Create a new note file under `notes/` using the workspace instructions for this repository.

Requirements:

- Treat the learner as someone who can read but speaks with great difficulty.
- Build a review note, not a transcript and not a topic script.
- Follow the required note structure from [copilot-instructions](../copilot-instructions.md).
- Cover all usable user-provided words, phrases, and short sentences somewhere in the note.
- If the user provides an explicit review list, treat that list as mandatory coverage, not optional reference.
- Exact duplicates can be merged, but do not silently drop usable items.
- If an item is unclear, weak, or still wrong, place it in `Fixes and Upgrades` or `Check Next Time` instead of omitting it.
- Use concise Chinese support where it lowers the speaking barrier.
- Keep the note compact, reusable, and easy to review before the next class.
- Make pronunciation practice a major part of the note.
- Highlight stress, rhythm, linking, or difficult sounds in a simple beginner-friendly way.
- Prefer easy pronunciation hints such as `re-MOTE`, `con-CISE`, or short Chinese reminders instead of heavy IPA.
- If a topic file is provided, use it only as background. The note may include free-talk output that is only loosely related to the topic.
- If the raw output contains duplicates, spelling errors, or broken phrases, clean them up when the intended meaning is clear.
- Before finishing, check that every usable input item appears in at least one section of the note.

The user's message after invoking this prompt contains the lesson output and any extra requirements.
Use that input directly to produce the new note file.
