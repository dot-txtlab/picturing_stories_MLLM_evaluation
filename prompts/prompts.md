# MLLM Prompts

Exact prompts used to elicit model outputs. For one-shot prompting a fixed
demonstration pair (example image + output) was shown before the target image.
Model/API versions: GPT-4.1 (`gpt-4.1-2025-04-14`), Gemini 2.5 Flash,
Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`), Qwen3-VL-8B-Instruct,
LLaVA-1.6-Vicuna-13B (zero-shot only, due to input-length constraints).

---

## Task 1 — Scene Analysis (illustration, characters, setting, objects, intensity)

**Zero-shot prompt:**

```
You are given a children's book illustration. Analyze the image and answer the
following 5 questions based on the visual content only. Respond using the exact
JSON format provided.

1. Is there an illustration on this page? Answer 'Yes' or 'No'.
2. Who are the characters on the page? Choose all that apply from: ['Man',
   'Woman', 'Girl', 'Boy', 'Animal', 'Animate Object',
   'Mythical / Imaginary Being', 'Other', 'None']
3. Where is the scene set? Choose one: 'Indoors', 'Outdoors', or 'Both / Ambiguous'
4. What are the main objects in the scene? Choose all that apply from: ['Nature',
   'Architecture', 'Vehicles', 'Toys', 'Reading and Art',
   'Household items and tools', 'Other', 'None']
5. How emotionally intense is the scene? Rate from 1 (very calm) to 5 (very intense).

Respond in this exact JSON format (no explanations or extra commentary):
{
  "illustration_present": "",
  "characters": [],
  "scene_setting": "",
  "objects": [],
  "emotional_intensity":
}
```

**One-shot example output (shown with the example image before the target):**

```
{
  "illustration_present": "Yes",
  "characters": ["Woman", "Boy"],
  "scene_setting": "Indoors",
  "objects": ["Household items and tools"],
  "emotional_intensity": 2
}
```

---

## Task 2 — Action Classification

**Zero-shot prompt:**

```
You are given a children's book illustration.
The entity type is: <ENTITY_TYPE>.
There is exactly ONE such entity in the image. Your task is to identify ONLY the
behaviors performed by that entity.

What behaviors do you see?
Choose ALL that apply from the list below. Use the option text exactly (spelling).
Options:
- <action option 1>
- <action option 2>
...

Return VALID JSON only in this format:
{
  "actions": []
}
```

Action option list (21): sitting, standing, walking, talking, looking, pointing,
gesturing, holding hands or embracing (someone), being embraced, holding
(something not someone), giving, playing, working, eating/drinking, reading,
listening, crying, sleeping, moving actively (running, jumping, dancing,
climbing, flying, etc), animal noise, violent action.

**Entity selection (see also `code/06_actions_entity_selection` / paper Appendix B.2):**
one query was issued per image, for a single entity *type* verified as present in
the human annotation. In 97.4% of queried images that entity had exactly one
instance (n=1) in the human labels; the "exactly ONE such entity" instruction
reflects this selection rule.

**One-shot example output:**

```
{
  "actions": ["Holding something (not someone)", "Sitting", "Working"]
}
```

---

## Task 3 — Caption Generation

**Zero-shot prompt:**

```
Please write a caption for this children's book illustration. Include the key
characters, important objects, actions, and aspects of the setting. Write 1-2
full sentences, be descriptive and as objective as possible, and do not invent
story details that are not clearly visible in the image.
```

**One-shot example caption:**

```
Inside a room with a table and fireplace, a woman holds a broom while a boy
stands in front of her with one arm raised. Another child looks into the room
from behind an open door, and a birdcage hangs on the wall.
```
