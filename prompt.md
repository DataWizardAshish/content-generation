# CONTEXT

You are updating prompts.py for SHRUTI, a Ramayan quiz app. The 
current prompts produce 2 fields per question: question + explanation. 
We need to upgrade the pipeline to produce 5 fields per question to 
support an immersive narrative experience instead of an exam-style quiz.

The 5 required fields are:
1. scene_setup — 1-2 sentence narrative setup BEFORE the question
2. question — the MCQ stem (existing, refine slightly)
3. narrative_continuation — replaces "explanation" — past-tense story 
   prose that confirms the answer AND continues the narrative
4. deep_context — 10-15 sentence "Know More" expansion with cultural, 
   symbolic, or historical depth
5. forward_hook — 1 sentence teasing what comes next, creating 
   forward momentum

Plus existing fields: 4 options, correct_answer, source_quote, 
difficulty, story_phase, narrative_arc, chapter_title, 
engagement_score, is_daily_insight.

# CURRENT FILE LOCATION

backend/services/prompts.py

# OBJECTIVE

Rewrite prompts.py to:
- Produce all 5 narrative fields with high quality
- Use GPT-5 best practices: concise system prompts, structured 
  outputs via JSON schema, in-context examples, field-specific guidance
- Maintain the existing 3-stage pipeline (Generate → Validate → 
  Self-Critique)
- Add validation for the new fields (deep_context must cite source, 
  scene_setup must be present-tense, etc.)
- Add self-critique scoring on enrichment depth, not just engagement

# DESIGN PRINCIPLES (NON-NEGOTIABLE)

These rules govern every prompt change:

1. Each field has a distinct voice:
   - scene_setup: PRESENT TENSE, sensory, cinematic, draws reader in
   - question: NEUTRAL TENSE, specific, self-contained
   - narrative_continuation: PAST TENSE, story prose, ends with hook
   - deep_context: REFLECTIVE TONE, factual depth, teaches symbolism
   - forward_hook: PRESENT/FUTURE TENSE, 1 sentence, creates pull

2. Use few-shot examples for every field. Examples beat rules.

3. Strict JSON output via OpenAI's response_format with json_schema.

4. Grounding rule extends: every factual claim in deep_context must 
   trace to source passage OR be marked as "general Vedic context" 
   if it's well-known cultural background (e.g., "agni-sakshi 
   tradition" doesn't need passage citation, but "Sugriva had been 
   hiding for 7 years" does).

5. Reject any output where deep_context introduces specific facts 
   (numbers, names, events) not in the passage.

# ACCEPTANCE CRITERIA

## Phase 1 — Refactor structure

a) Add a constants section at top:
   - GPT_MODEL = "gpt-5"  (or whatever production model)
   - GENERATION_TEMPERATURE = 0.8
   - VALIDATION_TEMPERATURE = 0.1
   - CRITIQUE_TEMPERATURE = 0.3

b) Define JSON schemas as Python dicts at top of file:
   - QUESTION_GENERATION_SCHEMA (single question structure)
   - GENERATION_BATCH_SCHEMA (array of questions)
   - VALIDATION_SCHEMA
   - CRITIQUE_SCHEMA

c) Helper functions for OpenAI API calls:
   - call_generation(chapter_text, num_questions, chapter_title, 
     episode_metadata) -> dict
   - call_validation(chapter_text, questions) -> dict
   - call_critique(questions) -> dict

   Each helper passes proper response_format, temperature, and 
   system prompt.

## Phase 2 — Rewrite system prompts

Replace existing 3 system prompts with upgraded versions:

a) GENERATION_SYSTEM_PROMPT
   - Concise principle-based opening (5-6 lines)
   - Field-by-field voice guidance with 1 example each
   - Grounding rule explicit
   - Distractor quality rule
   - Story phase mapping (existing) preserved
   - End with: "Respond ONLY with the JSON matching the schema."

b) VALIDATION_SYSTEM_PROMPT
   - Validate each of 5 narrative fields against its rules
   - scene_setup: must be present tense, must not contain spoilers 
     for the question's answer
   - narrative_continuation: must end with forward momentum, must 
     not start with "the answer is"
   - deep_context: any specific fact must trace to passage; general 
     Vedic/cultural context is acceptable; flag specific unsourced facts
   - forward_hook: must be 1 sentence, must create curiosity
   - Output structured per-field validation, not just one approve/reject

c) CRITIQUE_SYSTEM_PROMPT
   - Score on 3 axes now (not 1):
     - engagement_score (1-10): would the reader pause?
     - enrichment_score (1-10): does the user learn something they 
       didn't know — cultural depth, symbolism, lesser-known fact?
     - narrative_flow_score (1-10): does scene_setup → question → 
       narrative_continuation → forward_hook flow naturally?
   - is_daily_insight_candidate = (engagement >= 8 AND enrichment >= 8)
   - Provide 1-line specific suggestion when any score is below 7

## Phase 3 — Add few-shot examples

Embed 2 high-quality examples directly in GENERATION_SYSTEM_PROMPT 
showing all 5 fields produced for sample passages. The examples are 
provided below in the "EXAMPLES TO EMBED" section of this prompt.

## Phase 4 — Build prompt functions

Update or replace these functions:

a) build_generation_prompt(chapter_text, num_questions, 
   chapter_title, episode_metadata)
   - episode_metadata is a new optional dict containing 
     episode_name, episode_subtitle, emotional_tone, narrative_arc
   - When provided, the generator can use it to align tone of 
     scene_setup with episode mood

b) build_validation_prompt(chapter_text, questions_json)
   - Now validates 5 fields instead of 2

c) build_critique_prompt(questions_json)
   - Returns 3 scores + suggestion per question

## Phase 5 — Add tests

Create tests/test_prompts.py with:

a) test_generation_schema_compliance — generate 3 questions, 
   assert all 5 narrative fields present and non-empty

b) test_scene_setup_is_present_tense — generate 5 questions, 
   verify scene_setup uses present-tense verbs (heuristic: 
   contains "is", "stands", "moves", "approaches" etc.)

c) test_narrative_continuation_has_forward_pull — verify it 
   doesn't end mid-thought, doesn't start with "The answer"

d) test_deep_context_word_count — should be 150-250 words

e) test_forward_hook_is_single_sentence — count periods/exclamations

f) Mock OpenAI calls with sample fixture responses to keep tests 
   fast and deterministic

# DO NOT DO

- Do not change the existing 3-stage pipeline architecture
- Do not remove existing fields (question, options, correct_answer, 
  source_quote, etc.)
- Do not introduce new external dependencies beyond openai SDK
- Do not hardcode model name in functions — use module-level constant
- Do not change generation_runs audit log schema (separate concern)
- Do not modify the Streamlit UI in this prompt — that's separate

# DELIVERABLES

1. Fully rewritten backend/services/prompts.py
2. tests/test_prompts.py with mocked OpenAI responses
3. backend/services/llm_client.py — thin wrapper if not already 
   present, with retry logic and structured output handling
4. Migration note in README explaining what changed and why

# STARTING POINT

Before writing code:
1. View current prompts.py
2. View current LLM client / OpenAI call site (likely in 
   services/generation.py)
3. Confirm openai SDK version (we need >= 1.40 for structured 
   outputs)
4. Propose your file structure plan as numbered list
5. Wait for my approval before writing code

# EXAMPLES TO EMBED

The two examples below MUST be embedded verbatim in 
GENERATION_SYSTEM_PROMPT under a "## EXAMPLES" section. Use them as 
few-shot anchors so GPT-5 understands the voice and depth required.

[INSERT EXAMPLES BELOW HERE]

Begin by viewing the current files and proposing your plan.

Examples :

{
  "scene_setup": "Pampa's water laps quietly against the shore. A suspicious king has finally chosen to trust. Two grieving men — one who lost a kingdom, one who lost a wife — stand ready to bind their fates.",
  
  "question": "Why does Hanuman drop his wanderer's disguise before lighting the sacred fire?",
  
  "options": {
    "A": "To honor Rama's royal birth",
    "B": "Because hidden identities cannot witness a sacred oath",
    "C": "Because Sugriva commanded him to reveal himself",
    "D": "To intimidate any spies watching from the forest"
  },
  
  "correct_answer": "B",
  
  "source_quote": "In wanderer's weed disguised no more, / His proper form Hanúmán wore. / Then, wood with wood engendering, came / Neath his deft hands the kindled flame.",
  
  "narrative_continuation": "The alliance had just become real. Rama pressed Sugriva's hand and drew his new ally to his heart. In that charged moment, Hanuman cast off the wanderer's garb — for in Vedic tradition, no oath sworn before Agni could be witnessed by hidden faces. Trust had to stand uncovered. Only then did he kindle the sacred fire, friction of wood against wood, and crown it with sweet flowers. And in the flames that now burned between Rama and Sugriva, the path to Lanka was finally lit.",
  
  "deep_context": "Hanuman's disguise had a purpose, not vanity. Sugriva had been hiding on Mount Rishyamukha for years, fearing his brother Vali's wrath, and when two armed strangers appeared at Pampa, he could not be sure they weren't Vali's agents. He sent his minister Hanuman in a wanderer's form to test them — to hear how they spoke, what they knew, whether their grief was real. Only after Hanuman heard Rama speak with grace and pain did he reveal his true mantri form and bring them to Sugriva. The fire that follows is no decoration. In the Vedic tradition, agni-sakshi — fire as witness — was the most sacred form of oath. Marriages, treaties, alliances all required it, because Agni alone could carry truth between the human and divine worlds. By kindling Agni between Rama and Sugriva, Hanuman was not just lighting a fire; he was invoking the same cosmic witness that had bound Rama and Sita years before in Mithila. Two of the most consequential bonds in Rama's life were sealed before the same divine flame.",
  
  "forward_hook": "Now Sugriva will tell his story — of a brother who became an enemy. And Rama will have to make a choice that will haunt him for the rest of the epic.",
  
  "difficulty": "medium",
  "story_phase": "Search for Sita",
  "engagement_score": 9,
  "enrichment_score": 9,
  "narrative_flow_score": 9,
  "is_daily_insight_candidate": true
}


2.
{
  "scene_setup": "Night thickens in the cursed forest of Tataka. A boy of sixteen stands beside an old sage, bow not yet drawn. He has never killed before — and the thing rushing toward him through the trees is no ordinary enemy.",
  
  "question": "What sound first dismays Tataka before Rama's arrow strikes her?",
  
  "options": {
    "A": "The chanting of Vishvamitra's mantra",
    "B": "The clanging of Rama's bowstring",
    "C": "Lakshman's war cry",
    "D": "The roar of fire from the sage's yajna"
  },
  
  "correct_answer": "B",
  
  "source_quote": "The clanging of the cord dismayed / The monstrous fiend, who, wild with ire, / Rushed forward with a scream of fire.",
  
  "narrative_continuation": "Rama raised his bow and laid an arrow on the silken braid. Before the shaft flew, it was the sound itself — the sharp twang of the drawn cord splitting the forest silence — that struck Tataka first. The demoness, more accustomed to terrified prey than challenge, screamed in fury and rushed forward wild with rage. The arrow followed swift through the air. She fell, and with her fell life and rage together. The boy who had never killed had crossed his first threshold — and the world he would walk in had just changed shape.",
  
  "deep_context": "Tataka's killing is a moment Valmiki dwells on for a reason. Rama hesitated before this act — he had been raised never to harm a woman, and Tataka, despite her demonic form, had once been a beautiful yakshi cursed by Sage Agastya for her cruelty. Vishvamitra had to argue Rama into the killing, citing the dharma that protects sages and the principle that one who has abandoned dharma loses the protection that gender or birth would otherwise grant. The clanging of the bowstring carries weight in Vedic warfare: a kshatriya's bow was considered to have a voice, and that voice could itself be a weapon — both warning and declaration. Many epic battles in the Mahabharata also describe enemies dismayed by the sound of a bow before any arrow flies. This was Rama's first kill, and it was sanctioned by his guru, witnessed by his brother, and bounded by dharma — but it was also the moment innocence ended. The astras Vishvamitra would soon teach him existed because he had now proven he could kill when righteousness required it.",
  
  "forward_hook": "Vishvamitra reaches into his memory now, and from it draws weapons that have not been seen on earth in ages.",
  
  "difficulty": "easy",
  "story_phase": "Early Life of Rama",
  "engagement_score": 8,
  "enrichment_score": 9,
  "narrative_flow_score": 9,
  "is_daily_insight_candidate": true
}

Example 3 — Episode 22 "Ram Kills Bali" — Question 1 (Kishkindha Kanda, Sarga 16)Source passage excerpt:

"Then Ráma to a tree applied / His arrow tipped with iron tried, / And, drawing back the cord, let fly / The shaft that made the tree-tops cry. / Through Báli's mighty chest it sped / And from his back came forth wide. / Earth shook beneath the giant form / Cast prostrate, like a tree by storm."
Generated 5 fields:json{
  "scene_setup": "Sugriva's voice has just risen in challenge from the clearing below. Vali emerges, his crown still warm with rage, and the two brothers crash together for the second time. But this time, hidden behind a sal tree, an exiled prince watches with a drawn bow.",
  
  "question": "From where does Rama release the arrow that strikes Vali down?",
  
  "options": {
    "A": "From an open hilltop above the battlefield",
    "B": "From behind a tree, hidden from Vali's sight",
    "C": "Standing openly beside Sugriva",
    "D": "From a chariot driven by Lakshman"
  },
  
  "correct_answer": "B",
  
  "source_quote": "Then Ráma to a tree applied / His arrow tipped with iron tried, / And, drawing back the cord, let fly / The shaft that made the tree-tops cry.",
  
  "narrative_continuation": "Rama drew the cord against the tree's trunk, steadying the iron-tipped shaft. The arrow flew. It pierced Vali's mighty chest and emerged from his back, and the great king of Kishkindha fell like a sal tree felled by storm. The earth shook beneath him. But the moment the dying king saw who had loosed the arrow — and from where — his fall became something more terrible than death. He had been struck from concealment, from behind, by the prince who was supposed to be the very embodiment of dharma.",
  
  "deep_context": "Rama's choice to shoot from hiding is one of the most debated moments in the entire Ramayan. Critics across centuries — from Vali himself in the next sarga to modern scholars — have asked the same question: how can dharma's avatar kill from concealment? Vali was not in single combat with Rama; he was fighting his brother Sugriva. The Vedic code of yuddha dharma demanded that warriors face one another openly, that arrows fly between equals who could see each other. Rama appears to break this code. Valmiki does not look away from this difficulty. He places the entire next sarga in Vali's voice — a dying king's dharmic prosecution of the man who killed him. Vali is not portrayed as a villain in this moment; he is portrayed as a wounded king with legitimate grievance. This is the brilliance of the Ramayan: it does not protect its hero from accusation. It forces Rama to answer.",
  
  "forward_hook": "Now Vali turns his head, and from the dust of the battlefield, the dying king begins to speak.",
  
  "difficulty": "medium",
  "story_phase": "Search for Sita",
  "engagement_score": 9,
  "enrichment_score": 10,
  "narrative_flow_score": 9,
  "is_daily_insight_candidate": true
}Example 4 — Episode 22 "Ram Kills Bali" — Question 2 (Kishkindha Kanda, Sarga 17-18)Notice how this question's scene_setup continues directly from Question 1's forward_hook.Source passage excerpt:

"What cause, O chief of Raghu's line, / What motive led that hand of thine, / When I, intent on other foe, / Was wholly heedless of the blow? / Hast thou not heard from many a sage / The duty of a kshatriya's rage? / What of thy fame, O prince, will men / Speak in the ages yet to ken?"
Generated 5 fields:json{
  "scene_setup": "Vali turns his head from the dust. Blood darkens his lion-mane. The dying king does not weep, does not beg — he speaks instead like a magistrate, and the prince who killed him from concealment must now stand trial before he stands free.",
  
  "question": "What does the dying Vali primarily accuse Rama of having violated?",
  
  "options": {
    "A": "The bond of friendship with Sugriva",
    "B": "The duty of a kshatriya — the warrior's code of fair combat",
    "C": "The promise of safe passage through Kishkindha",
    "D": "The sage Matanga's curse boundary"
  },
  
  "correct_answer": "B",
  
  "source_quote": "Hast thou not heard from many a sage / The duty of a kshatriya's rage? / What of thy fame, O prince, will men / Speak in the ages yet to ken?",
  
  "narrative_continuation": "Vali did not curse. He prosecuted. Why, he asked, when he was intent on another foe, wholly heedless, had Rama struck him from hiding? Had Rama not heard from many a sage the duty of a kshatriya's rage — that warriors face each other openly, that arrows are not loosed from concealment against the unarmed-toward-thee? What, the dying king asked, would men speak of Rama's fame in ages yet to come? It was not the wound that wounded Vali most. It was the silence of dharma in the man he had thought was its very form.",
  
  "deep_context": "Vali's accusation is structured as a formal kshatriya legal complaint, not a lament. He cites three specific principles of yuddha dharma: that combat must be between willing opponents, that strikes from concealment are forbidden, and that interfering in another's combat violates the code of equals. Each of these has roots in the Dharmashastras and would be expanded centuries later in the Mahabharata's war ethics. Vali also raises a deeper question — the question of legacy. In the Vedic worldview, a king's kirti (renown) was understood to outlive his body, and any stain on it would echo through the ages. Vali is essentially asking Rama: 'You have killed me, but what have you done to your own name?' This is one of the few moments in Indian literature where the slain accuses the slayer not of cruelty but of ethical failure. Rama's coming reply will become one of the most analyzed dharmic arguments in Hindu philosophy — invoked even today in debates about ends, means, and the limits of righteous action.",
  
  "forward_hook": "Rama listens fully. Then he begins to answer — and the reply will not be what Vali expected.",
  
  "difficulty": "hard",
  "story_phase": "Search for Sita",
  "engagement_score": 10,
  "enrichment_score": 10,
  "narrative_flow_score": 10,
  "is_daily_insight_candidate": true
}