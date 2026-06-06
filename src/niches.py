"""Niche library — each niche has its own story guide, visuals, payoff style,
thumbnail style and recommended voice. Used to generate the best story per niche.
"""

DEFAULT_NICHE = "ai_horror"

NICHES = {
    "ai_horror": {
        "label": "AI Horror Stories ⭐⭐⭐⭐⭐",
        "guide": "Smart-home / AI technology turns sinister. Modern, believable, "
                 "eerie. The tech notices something the human can't.",
        "visuals": "dark moody photorealistic horror cinematography, smart devices "
                   "glowing in the dark, fog, low-key lighting, camera slow push-in",
        "thumb": "extreme close-up of a terrified person's face lit by a glowing "
                 "screen, dark room, the unseen threat behind them",
        "payoff": "a chilling twist that loops back to the first line",
        "voice": "am_michael", "speed": 0.92,
    },
    "tech_mystery": {
        "label": "Technology Gone Wrong / Mysteries ⭐⭐⭐⭐",
        "guide": "Everyday technology behaves impossibly. Build unease through small "
                 "wrong details that add up to something disturbing.",
        "visuals": "moody tech-noir cinematography, screens and devices, blue-cyan "
                   "light, shadows, slow camera moves",
        "thumb": "shocked face staring at a glowing phone/screen, dark, dramatic",
        "payoff": "an unsettling reveal that reframes everything",
        "voice": "am_adam", "speed": 0.95,
    },
    "true_crime": {
        "label": "True Crime Inspired Mysteries ⭐⭐⭐⭐⭐",
        "guide": "Fictional crime mystery in a realistic style. A detail that doesn't "
                 "add up, growing dread, a disturbing conclusion. (Fully fictional.)",
        "visuals": "gritty realistic cinematography, dim interiors, street lights, "
                   "rain, handheld feel, cold color grade",
        "thumb": "tense worried face, evidence/clue element, dark dramatic lighting",
        "payoff": "a dark twist or a chilling unanswered question",
        "voice": "am_michael", "speed": 0.95,
    },
    "security_cam": {
        "label": "Scary Security Camera Stories ⭐⭐⭐⭐⭐",
        "guide": "Story told around what a security/doorbell camera captured. The "
                 "camera sees something the person didn't — build to that moment.",
        "visuals": "security-camera / night-vision aesthetic, grainy, timestamp feel, "
                   "dark doorways, infrared green or low-light gray",
        "thumb": "night-vision style frame, a figure half-seen, a shocked face inset",
        "payoff": "the camera reveals the horrifying detail at the end",
        "voice": "am_michael", "speed": 0.93,
    },
    "survival_disaster": {
        "label": "Survival & Disaster Stories ⭐⭐⭐⭐⭐",
        "guide": "A person caught in a sudden disaster or survival situation. High "
                 "stakes, fast danger, split-second choices, a gripping escape.",
        "visuals": "epic dramatic cinematography, storms, fire, flood, collapsing "
                   "environments, dust, dynamic camera, high contrast",
        "thumb": "terrified face with disaster behind them (fire/storm/flood), epic",
        "payoff": "a tense survival twist — barely make it, or a gut-punch ending",
        "voice": "am_adam", "speed": 0.98,
    },
    "reddit_drama": {
        "label": "Reddit-Style Drama Stories ⭐⭐⭐⭐",
        "guide": "First-person dramatic confession / betrayal / revenge story like a "
                 "viral Reddit post. Relatable, emotional, satisfying turn.",
        "visuals": "cinematic real-life scenes, homes, phones, tense faces, warm-cool "
                   "contrast, shallow depth of field",
        "thumb": "emotional shocked face, dramatic real-life moment, bold",
        "payoff": "a satisfying revenge / karma / shocking reveal",
        "voice": "af_heart", "speed": 1.0,
    },
    "social_experiment": {
        "label": "Social Experiments ⭐⭐⭐⭐",
        "guide": "A 'what would people do' scenario that reveals something about human "
                 "nature. Curious setup, surprising human behavior.",
        "visuals": "documentary-style real scenes, public places, candid feel, natural light",
        "thumb": "surprised face + the experiment setup, bold and bright",
        "payoff": "a surprising lesson about how people really act",
        "voice": "am_adam", "speed": 1.0,
    },
    "historical_facts": {
        "label": "Crazy Historical Facts ⭐⭐⭐⭐",
        "guide": "Wild, little-known (plausible-sounding) historical facts that shock. "
                 "Each fact escalates; save the craziest for last.",
        "visuals": "cinematic historical reenactment, period settings, dramatic light, "
                   "film grain, epic wide shots",
        "thumb": "dramatic historical scene + a shocked expression, bold",
        "payoff": "the most mind-blowing fact saved for the final line",
        "voice": "am_adam", "speed": 1.0,
    },
    "unsolved_mystery": {
        "label": "Unsolved Mysteries ⭐⭐⭐⭐",
        "guide": "An eerie unsolved-style mystery. Lay out the strange facts, deepen "
                 "the puzzle, end on a haunting unanswered question.",
        "visuals": "moody documentary cinematography, archival feel, fog, dim lighting, "
                   "slow zooms on details",
        "thumb": "mysterious dark scene, a question-raising element, tense face",
        "payoff": "a haunting question that leaves them unsettled",
        "voice": "am_michael", "speed": 0.95,
    },
    "moral_rich_poor": {
        "label": "Rich vs Poor / Moral Stories ⭐⭐⭐⭐",
        "guide": "An emotional moral story with a clear contrast (rich vs poor, kind "
                 "vs cruel). Build empathy, then a satisfying just ending.",
        "visuals": "emotional cinematic scenes, contrast of wealth and poverty, warm "
                   "and cold tones, expressive faces",
        "thumb": "emotional contrast image + a moved/shocked face, bold",
        "payoff": "a heart-warming or karmic twist that rewards good / punishes bad",
        "voice": "af_heart", "speed": 1.0,
    },
    "paranormal": {
        "label": "Paranormal Mystery ⭐⭐⭐⭐",
        "guide": "A creeping paranormal encounter. Ordinary setting, small uncanny "
                 "signs, escalating dread, a terrifying supernatural reveal.",
        "visuals": "dark supernatural horror cinematography, shadows, candle/torch "
                   "light, mist, slow unsettling camera",
        "thumb": "terrified face, a ghostly shape behind them, dark and eerie",
        "payoff": "a terrifying paranormal twist that loops to the start",
        "voice": "am_michael", "speed": 0.9,
    },
    "workplace_drama": {
        "label": "Workplace Drama ⭐⭐⭐⭐",
        "guide": "A tense workplace betrayal / power-struggle / revenge story. "
                 "Relatable office stakes, sharp turns, satisfying payoff.",
        "visuals": "modern office cinematic scenes, glass, screens, tense faces, "
                   "cool corporate lighting, shallow focus",
        "thumb": "tense / shocked office worker face, dramatic, bold",
        "payoff": "a satisfying comeback / karma / twist",
        "voice": "af_heart", "speed": 1.0,
    },
}


def get(niche_id: str) -> dict:
    return NICHES.get(niche_id, NICHES[DEFAULT_NICHE])


def choices():
    """[(label, id), ...] for a Gradio dropdown."""
    return [(n["label"], nid) for nid, n in NICHES.items()]
