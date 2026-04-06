# Project Guidelines

## Purpose

This workspace is for building one-to-one English lesson materials.
The main outputs are topic scripts under `topics/`, post-lesson review notes under `notes/`, and short-article vocabulary training materials under `高频1000词/`.
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

## High-Frequency Vocabulary Material Rules

When the user provides a short article and asks to create vocabulary training material, create a new file in `高频1000词/` unless the user clearly asks to overwrite an existing file.
Use a sequence prefix in the filename such as `1_`, `2_`, `3_` instead of a date prefix.
If no sequence number is specified, use the next reasonable integer based on existing files in `高频1000词/`.

This material is not a topic script and not a post-lesson note.
Its job is to help the learner build automatic control of high-frequency words through short reading, phrase review, pronunciation practice, and repeatable output drills.

Preserve the original text in the file.
Then transform the text into compact practice material.

When organizing this kind of material:

- keep the original article clean and readable
- select high-frequency or highly reusable words first
- prefer words and phrases that are useful across many topics
- include pronunciation practice as a core section
- include good sentence patterns and grammar structures from the article
- keep the practice focused and repeatable rather than encyclopedic

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

## Required High-Frequency Vocabulary Material Structure

Unless the user asks for a different structure, every generated file under `高频1000词/` should follow this order:

1. Material Goal
State what the learner should be able to understand, pronounce, and say after studying the material.

2. Quick Chinese Brief
Summarize the short article in concise Chinese.

3. Original Text
Keep the original article or dialogue in clean form.

4. Core High-Frequency Words
Select 8 to 15 useful words from the text.
For each item, give:
- simple English meaning
- short Chinese explanation
- simple pronunciation hint when useful
- one short reusable sentence

5. Useful Phrases and Collocations
Select 6 to 12 phrases from the text.
For each item, give:
- short Chinese explanation
- simple pronunciation or rhythm hint when useful
- one short reusable sentence

6. Pronunciation Focus
Select 5 to 8 words or phrases that are especially worth speaking practice.
For each item, give:
- a simple stress hint in easy text form
- a short Chinese reminder about stress, linking, endings, or difficult sounds
- one short repeat drill

7. Good Expressions and Grammar Patterns
Select 3 to 6 useful sentence patterns or grammar structures from the text.
For each item, give:
- the pattern
- a short Chinese explanation
- one model sentence from or based on the text
- one substitution drill or mini transformation

8. Retelling and Output Drill
Give:
- a 3-line retelling
- a 5-line retelling
- 3 short output prompts the learner can answer orally

9. Review Task
Add a short review plan focused on reading aloud, pronunciation, phrase reuse, and short retelling.

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

## Writing Style for High-Frequency Vocabulary Materials

Keep the material compact and drill-friendly.
The learner should be able to review one file quickly and repeat it many times.

Prefer high-frequency usefulness over topic completeness.
Do not try to explain every difficult word in the source if it is not worth keeping.

Pronunciation should be practical.
Use easy stress marking and simple Chinese reminders instead of dense phonetic theory.

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
When generating a new high-frequency vocabulary material from a short article, prefer creating a dedicated file in `高频1000词/`.
If updating an existing topic, keep the structure clean and consistent.

## Prompt Handling

If the user asks to create a new topic from raw material, infer the structure from these instructions and produce the full topic file directly.
If the material is too long, first identify the main message, the likely lesson questions, and the most reusable speaking chunks.

If the user asks to create a new note from lesson output, infer the structure from these instructions and produce the full note file directly.
If the output is messy, normalize it into a clean review note instead of preserving raw order.
If pronunciation is relevant, highlight which words and phrases should be practiced aloud first.

If the user asks to create a new high-frequency vocabulary material from a short article, infer the structure from these instructions and produce the full file directly.
Keep the original text and turn it into reusable drills for vocabulary, phrases, pronunciation, and grammar patterns.
