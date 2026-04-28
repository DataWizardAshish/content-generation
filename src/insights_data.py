import json

INSIGHTS = [
    {
        "sequence_number": 1,
        "title": "Rama's Silent Resolve",
        "story_phase": "Exile Phase",
        "character": "Rama",
        "narrative": (
            "As the chariot wheels fade into silence, Rama does not look back at Ayodhya. "
            "His eyes hold no grief — only the clear flame of dharma. "
            "He has surrendered a kingdom, a throne, a father's dearest dream. "
            "This is not exile. This is his chosen path."
        ),
        "lesson": "Duty embraced willingly becomes freedom.",
    },
    {
        "sequence_number": 2,
        "title": "Sita's Unyielding Flame",
        "story_phase": "Sita Haran",
        "character": "Sita",
        "narrative": (
            "In the Ashoka grove, surrounded by rakshasas, Sita holds a blade of grass "
            "between herself and Ravana. She will not bend. "
            "She has no army, no weapon — only the fire of her own faithfulness. "
            "And that fire, Ravana cannot cross."
        ),
        "lesson": "The strongest fortress is an unbroken will.",
    },
    {
        "sequence_number": 3,
        "title": "Hanuman's Leap of Faith",
        "story_phase": "Search for Sita",
        "character": "Hanuman",
        "narrative": (
            "At the edge of the ocean, the vanaras despair. The sea is vast and Lanka unreachable. "
            "Then Hanuman remembers — not a plan, not a weapon, but who he is. "
            "He grows. He leaps. The sky bends around a servant's devotion."
        ),
        "lesson": "The one who truly serves finds strength they did not know they had.",
    },
    {
        "sequence_number": 4,
        "title": "Lakshmana's Chosen Exile",
        "story_phase": "Exile Phase",
        "character": "Lakshmana",
        "narrative": (
            "Lakshmana was not commanded to follow Rama into exile. He chose it — "
            "leaving behind his own palace, his own comfort, his own future. "
            "When Rama told him to stay, Lakshmana simply said: where Rama goes, there is home."
        ),
        "lesson": "True loyalty does not wait to be asked.",
    },
    {
        "sequence_number": 5,
        "title": "Ravana's Tragic Pride",
        "story_phase": "Lanka War",
        "character": "Ravana",
        "narrative": (
            "Every sage, every god, every omen warned Ravana to return Sita. He heard them all. "
            "He was the greatest scholar of the Vedas, the mightiest king of three worlds — "
            "and he chose pride over wisdom. Lanka burned because one man could not bow."
        ),
        "lesson": "Wisdom unused is the most dangerous kind of pride.",
    },
    {
        "sequence_number": 6,
        "title": "The First Sorrow",
        "story_phase": "Early Life of Rama",
        "character": "Valmiki",
        "narrative": (
            "Valmiki watched a hunter's arrow strike a krouncha bird mid-flight. Its mate screamed. "
            "From Valmiki's grief rose a curse — and then a verse. "
            "That verse became a couplet, and that couplet became the Ramayana. "
            "The first poem in human history was born from sorrow."
        ),
        "lesson": "From grief, if witnessed with enough stillness, something eternal can emerge.",
    },
    {
        "sequence_number": 7,
        "title": "Kaikeyi's Moment of Choice",
        "story_phase": "Exile Phase",
        "character": "Kaikeyi",
        "narrative": (
            "Manthara's words were poison, and Kaikeyi drank them willingly. "
            "She had been Dasharatha's most beloved queen — but in one night, "
            "she chose a crown for her son over a son's love for his mother. "
            "She got what she asked for, and spent the rest of her life unable to live with it."
        ),
        "lesson": "What we demand in fear rarely brings what we imagined.",
    },
]

PHASE_STORIES = [
    {
        "story_phase": "Early Life of Rama",
        "title": "The Making of a Prince",
        "shloka_watermark": "रामो विग्रहवान् धर्मः",
        "narrative": (
            "In the city of Ayodhya, where the Sarayu flows and dharma holds every household, "
            "a son is born to King Dasharatha after years of longing and prayer. "
            "Rama grows up in the warmth of a palace that loves him — and Valmiki knows what is coming. "
            "Vishvamitra arrives and asks for the young prince, and Dasharatha's joy turns pale with fear. "
            "What follows is Rama's first education — not in archery, but in the cost of righteousness. "
            "He defeats Tataka, earns the divine weapons, and at Mithila strings the bow of Shiva. "
            "The Bala Kanda is a long, gentle inhale before the epic's exhale."
        ),
        "key_events": json.dumps([
            "Birth of Rama and his brothers",
            "Vishvamitra requests Rama's help",
            "Rama defeats Tataka in the forest",
            "Rama strings the Shiva bow and wins Sita",
            "The wedding at Mithila",
        ]),
        "key_characters": json.dumps(["Rama", "Lakshmana", "Vishvamitra", "Sita", "Dasharatha", "Janaka"]),
        "mood": "wonder, innocence, and first duty",
    },
    {
        "story_phase": "Exile Phase",
        "title": "The Forest of Surrender",
        "shloka_watermark": "नहि कश्चित् क्षमां जेतुम् शक्तः",
        "narrative": (
            "A kingdom is given away and a son walks into the forest carrying only his bow, his wife, and his brother. "
            "Dasharatha dies of a broken heart before dawn. "
            "The Ayodhya Kanda is the Ramayana's deepest wound — the moment the epic stops being about a hero "
            "and starts being about grief. "
            "Bharata refuses the throne and places Rama's sandals upon it instead. "
            "And in the forest, Rama, Sita, and Lakshmana discover what it means to live without comfort, "
            "without certainty, without home."
        ),
        "key_events": json.dumps([
            "Kaikeyi's two boons send Rama into exile",
            "Rama's farewell to Ayodhya",
            "Death of Dasharatha",
            "Bharata's visit to Chitrakuta",
            "Life at Panchavati in the Dandaka forest",
        ]),
        "key_characters": json.dumps(["Rama", "Sita", "Lakshmana", "Kaikeyi", "Bharata", "Dasharatha"]),
        "mood": "grief, sacrifice, and steadfast dharma",
    },
    {
        "story_phase": "Sita Haran",
        "title": "The Moment Everything Changed",
        "shloka_watermark": "धर्मो रक्षति रक्षितः",
        "narrative": (
            "It begins with a golden deer. Sita sees it and is enchanted. "
            "Rama chases it into the forest, Lakshmana is tricked away by a false cry, "
            "and in the silence that follows, a hermit appears at the threshold of their hut. "
            "Ravana drops his disguise and takes what cannot be taken. "
            "The vulture Jatayu gives his life trying to stop what no one could stop. "
            "Sita falls into Lanka's shadow — and the Ramayana is never the same again."
        ),
        "key_events": json.dumps([
            "The golden deer of Maricha lures Rama away",
            "Ravana's disguise as an ascetic",
            "The Lakshmana Rekha and Sita's crossing",
            "Jatayu's battle with Ravana",
            "Sita's abduction and Rama's grief at Panchavati",
        ]),
        "key_characters": json.dumps(["Sita", "Rama", "Ravana", "Lakshmana", "Maricha", "Jatayu"]),
        "mood": "loss, betrayal, and grief so sharp it breaks the sky",
    },
    {
        "story_phase": "Search for Sita",
        "title": "Devotion That Moved Mountains",
        "shloka_watermark": "भक्तिः परमा शक्तिः",
        "narrative": (
            "Two exiled princes meet a dispossessed monkey king, and the most unlikely alliance "
            "in epic literature is forged at the shores of Pampa. "
            "The Kishkindha and Sundara Kandas are the Ramayana's heart of devotion — "
            "where Hanuman, the son of the wind, grows into the servant of servants. "
            "He leaps the ocean on faith alone. He finds Sita in Lanka's Ashoka grove — "
            "alone, unbowed, still holding the name of Rama like a flame. "
            "He burns Lanka. He returns. The search was always also a homecoming."
        ),
        "key_events": json.dumps([
            "Alliance forged with Sugriva at Pampa",
            "The killing of Vali",
            "Hanuman's leap across the ocean",
            "Sita found in the Ashoka grove",
            "Lanka burned by Hanuman's tail",
        ]),
        "key_characters": json.dumps(["Hanuman", "Rama", "Sugriva", "Sita", "Vali", "Angada"]),
        "mood": "devotion, courage, and the impossible made possible by love",
    },
    {
        "story_phase": "Lanka War",
        "title": "The War at the Edge of the World",
        "shloka_watermark": "शठे शाठ्यं समाचरेत्",
        "narrative": (
            "An army of vanaras builds a bridge of stones across the sea, "
            "and the Ramayana enters its great and terrible final act. "
            "The Yuddha Kanda is the longest kanda for a reason — because war is long, and grief is longer. "
            "Ravana sends his greatest warriors, and one by one they fall. "
            "When Lakshmana is struck down, the night becomes absolute darkness — "
            "but Hanuman flies to the Himalayas and carries back the healing dawn. "
            "The war ends not with triumph, but with the terrible weight of dharma fulfilled."
        ),
        "key_events": json.dumps([
            "The bridge of Rama built across the sea",
            "Kumbhakarna awakened and slain",
            "Lakshmana struck by Indrajit's Shakti weapon",
            "Hanuman's flight to the Himalayas for the sanjeevani herb",
            "Death of Ravana",
            "Sita's agni-pariksha",
        ]),
        "key_characters": json.dumps(["Rama", "Ravana", "Lakshmana", "Hanuman", "Indrajit", "Kumbhakarna", "Vibhishana"]),
        "mood": "valor, sacrifice, and the terrible weight of war",
    },
    {
        "story_phase": "Return and Reunion",
        "title": "The Long Road Home",
        "shloka_watermark": "सत्यं वद धर्मं चर",
        "narrative": (
            "The Pushpaka Vimana carries them through the sky, and Rama narrates every landmark "
            "of their exile as they pass over it — as if fixing each sorrow in memory before it can fade. "
            "The city celebrates. The king is crowned. And then the whispers begin. "
            "The Uttara Kanda does not offer easy comfort. "
            "Sita must prove herself again — and this time, the earth opens and takes her back. "
            "Rama rules Ayodhya for ten thousand years, and the absence of Sita "
            "is the silence that fills every chapter of that reign."
        ),
        "key_events": json.dumps([
            "Return to Ayodhya in the Pushpaka Vimana",
            "Coronation of Rama",
            "The whispers of the washerman",
            "Sita's second exile",
            "Sita's return to the earth",
        ]),
        "key_characters": json.dumps(["Rama", "Sita", "Hanuman", "Bharata", "Valmiki"]),
        "mood": "homecoming shadowed by sacrifice, joy threaded with loss",
    },
]
