# Project Guidelines

## Purpose

This workspace is for building one-to-one English lesson materials.
The main outputs are topic scripts under `topics/` and post-lesson review notes under `notes/`.
The learner is a beginner speaker.
Reading is acceptable, but listening and speaking are very weak.
The long-term training goal is to reach spoken B1 level.

## Topic Creation Rules

When the user provides raw material and asks to create or update a topic, create a new file in `topics/` unless the user clearly asks to overwrite an existing file.
If a date is known from the source or request, use it in the filename.
If no date is known, ask only if the filename matters; otherwise use a reasonable date-based name.

Do not copy the source article into a lesson format mechanically.
Transform the material into a speaking-training script.
The final topic should help the learner go from reading to speaking.

## Note Creation Rules

When the user provides post-lesson output and asks to create or update a note, create a new file in `notes/` unless the user clearly asks to overwrite an existing file.
If a date is known from the lesson or request, use it in the filename.
If no date is known, use a reasonable date-based filename.

The note is not a transcript.
The note is a review sheet for later speaking practice.
Its job is to turn messy class output into reusable speaking material.

Pronunciation is a key training target in notes.
When useful, the note should help the learner practice stress, rhythm, linking, and difficult sounds in words and phrases.

The source output may be loosely related to the topic because part of the lesson may be free talk.
Do not force the note to stay tightly aligned with the topic article.

When organizing a note from raw lesson output:

- deduplicate repeated items
- correct obvious spelling mistakes
- correct obvious phrase errors when the intended meaning is clear
- keep ambiguous items only if they are useful to review later
- convert raw fragments into short reusable spoken lines when possible
- keep the note compact and review-friendly
- prioritize items that are valuable for both speaking reuse and pronunciation practice

## Default Learner Profile

Assume these defaults unless the user says otherwise:

- The learner can read English materials.
- The learner cannot speak fluently and often cannot start answering.
- The learner needs heavy speaking scaffolding.
- The learner needs repeated sentence patterns, not open-ended abstract discussion.
- The learner benefits from short, usable spoken English rather than textbook writing.
- The learner wants long-term improvement toward B1, not one-time polished output.

## Required Topic Structure

Unless the user asks for a different structure, every generated topic should follow this training-first order:

1. Topic Target
State what the learner should be able to say after the lesson in simple terms.

2. Quick Chinese Brief
Summarize the material in concise Chinese so the learner knows the meaning before speaking.

3. Core Message in Easy English
Give 4 to 6 very short sentences that express the topic at A2-B1 speaking level.

4. Key Words and Chunks
Select 5 to 8 useful words or phrases from the source.
For each item, give:
- simple English meaning
- short Chinese explanation
- one highly reusable spoken sentence

5. Answer Ladder
For the most likely lesson questions, provide answers in three levels:
- Level 1: one short sentence
- Level 2: two to three connected sentences
- Level 3: a longer natural answer

6. Personal Expression Builder
Provide sentence frames with blanks the learner can fill using personal experience.
Prefer patterns such as:
- In my case, ...
- I usually ... when ...
- One reason is that ...
- I agree because ...

7. Guided Speaking Script
Write a short speakable script in simple, natural English.
It should sound like something a real learner can say, not an article summary.
Keep sentence length controlled.

8. Tutor Q&A Drill
List likely tutor questions and give model answers.
Questions should move from easy factual questions to personal opinion questions.

9. Listening-to-Speaking Rescue Lines
Provide short lines for when the learner gets stuck, such as asking for repetition, buying time, or restarting an answer.

10. Homework and Review
Add a short self-practice plan such as shadowing, retelling, and personal sentence substitution.

## Required Note Structure

Unless the user asks for a different structure, every generated note should follow this review-first order:

1. Note Goal
State what the learner should be able to reuse after reviewing the note.

2. Session Snapshot
Briefly record the source topic if given, the main free-talk themes, and what kind of class output this note keeps.

3. Keep First
Select 6 to 10 highest-value words, phrases, or short lines that the learner should review first.
Prefer items that are both reusable and worth practicing aloud.

4. Pronunciation Focus
Select 5 to 8 words or phrases that are worth pronunciation practice.
For each item, give:
- a simple stress hint in easy text form such as `re-MOTE` or `con-CISE`
- a short Chinese reminder about stress, linking, endings, or difficult sounds
- one short repeat drill or mini line for oral practice

5. Word Bank
Group useful words.
For each item, give:
- simple English meaning
- short Chinese explanation
- simple pronunciation hint when it is useful
- one short spoken example

6. Phrase Bank
Group useful spoken chunks.
For each item, give:
- short Chinese explanation
- simple pronunciation or rhythm hint when it is useful
- one short reusable sentence

7. Ready-to-Say Sentences
Write 6 to 10 short sentences the learner can actually say in future classes.
These can be related to the topic, free talk, learning process, listening problems, work, or class interaction.

8. Fixes and Upgrades
When the raw output contains rough or incorrect expressions, turn them into natural spoken English with short correction notes.

9. Check Next Time
Optional.
Keep only truly unclear items that should be confirmed in the next lesson.

10. Review Task
Add a short practice plan that helps the learner reuse the note orally.
This should usually include a pronunciation task, not only memorization.

## Writing Style for Topics

Use simple spoken English.
Prefer short sentences.
Avoid advanced vocabulary unless it comes from the source and is useful.
Avoid long paragraphs.
Avoid broad discussion questions without giving answer support.
Make the output easy to read aloud.

## Writing Style for Notes

Keep notes compact.
Prefer short sections and short lines.
Do not write long explanations.
The learner should be able to review the whole note quickly before the next class.

Prioritize reusability over completeness.
It is better to keep 12 useful items than 40 weak items.

Prefer simple pronunciation help over technical phonetics.
Usually use easy stress marking like `a-GILE`, `SPRINT`, `con-CISE`, or short Chinese reminders.
Do not overuse IPA unless the user explicitly wants it.

## Bilingual Support

Use English for the training content.
Use concise Chinese only where it lowers the speaking barrier, especially in:

- topic summary
- vocabulary support
- usage notes
- homework guidance

Do not turn the whole file into a full translation.

## Personalization Rules

When the source topic is general, still help the learner sound personal.
Add prompts that connect the material to:

- daily routine
- work or study pressure
- habits
- recent experiences
- simple opinions

If the user provides personal background, reflect it in the script.

## File Editing Rules

Preserve the user's source draft unless the user asks to replace it.
When generating a new topic from source material, prefer creating a dedicated file in `topics/`.
When generating a new note from class output, prefer creating a dedicated file in `notes/`.
If updating an existing topic, keep the structure clean and consistent.

## Prompt Handling

If the user asks to create a new topic from raw material, infer the structure from these instructions and produce the full topic file directly.
If the material is too long, first identify the main message, the likely lesson questions, and the most reusable speaking chunks.

If the user asks to create a new note from lesson output, infer the structure from these instructions and produce the full note file directly.
If the output is messy, normalize it into a clean review note instead of preserving raw order.
If pronunciation is relevant, highlight which words and phrases should be practiced aloud first.
