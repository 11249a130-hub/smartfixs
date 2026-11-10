"""
SmartFix NLP & Machine Learning Engine
- Text preprocessing (tokenization, stop-words, cleaning)
- TF-IDF Feature Extraction
- Linear Support Vector Machine (Linear SVM) classification
- Facility / Asset Entity Recognition
- Urgency & Priority Detection with Safety Hazard Analysis
"""

import math
import re
from typing import Dict, List, Tuple, Any

# Optional scikit-learn / nltk import with graceful fallback
HAVE_SKLEARN = False
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import LinearSVC
    HAVE_SKLEARN = True
except Exception:
    HAVE_SKLEARN = False


# Comprehensive training dataset of college campus & hostel complaints
TRAINING_DATA = [
    # Electrical
    ("Ceiling fan is not spinning and making loud humming noise", "Electrical"),
    ("Tube light in room 204 is flickering continuously and turns off", "Electrical"),
    ("Switchboard near study table gives small electric shock when plugged in", "Electrical"),
    ("Power socket is burnt and melted after plugging laptop charger", "Electrical"),
    ("Geyser in hostel floor bathroom is not heating water at all", "Electrical"),
    ("MCB breaker trips immediately whenever the room light is turned on", "Electrical"),
    ("Exposed electrical wires hanging from the corridor ceiling", "Electrical"),
    ("Sparks coming out of the main distribution switchboard", "Electrical"),
    ("AC in seminar hall is not cooling and blowing warm air", "Electrical"),
    ("Regulator of ceiling fan is broken, running only at maximum speed", "Electrical"),
    ("Bathroom exhaust fan is jammed and producing burning smell", "Electrical"),
    ("Extension board socket has loose contact and sparks when touched", "Electrical"),
    ("Wall tube light starter is dead and blinking orange", "Electrical"),
    ("Geyser thermostat seems broken, boiling water violently with steam", "Electrical"),

    # Plumbing
    ("Washroom tap in room 102 is leaking water non stop", "Plumbing"),
    ("Bathroom flush tank lever is broken and water keeps overflowing", "Plumbing"),
    ("Washbasin drain pipe is completely choked and dirty water overflowing", "Plumbing"),
    ("Shower head is blocked with salt scale and no water coming out", "Plumbing"),
    ("Water cooler in hostel block B is not dispensing cold water and leaking", "Plumbing"),
    ("Hostel corridor pipeline is ruptured and flooding the staircase", "Plumbing"),
    ("Commode drainage is blocked causing severe foul smell and backup", "Plumbing"),
    ("RO water purifier filter is clogged and red light is blinking", "Plumbing"),
    ("Bathroom floor drain is clogged with hair and soap scum", "Plumbing"),
    ("Severe sewage water leak outside hostel wing A ground floor", "Plumbing"),
    ("Cold water tap handle snapped off and water is spraying everywhere", "Plumbing"),
    ("Geyser inlet pipe has pinhole leak spraying water on electric socket", "Plumbing"),

    # Furniture
    ("Study table drawer is broken and handle fell off", "Furniture"),
    ("Hostel cot wooden frame is cracked and wobbling when sitting", "Furniture"),
    ("Study chair backrest is detached and missing screws", "Furniture"),
    ("Mattress provided in room is completely torn with exposed metal springs", "Furniture"),
    ("Cupboard wardrobe door hinges are detached and door won't close", "Furniture"),
    ("Almirah lock cylinder is jammed and my key is stuck inside", "Furniture"),
    ("Bookshelf wall shelf collapsed in room 312", "Furniture"),
    ("Bed wooden plank is fractured from the middle", "Furniture"),
    ("Wheel of the revolving chair is broken and cannot roll", "Furniture"),
    ("Study table top laminate is peeled off with sharp splinters", "Furniture"),

    # Hostel Infrastructure
    ("Room window glass pane is cracked and rattling in heavy wind", "Hostel Infrastructure"),
    ("Main entrance door latch and deadbolt cannot be locked from outside", "Hostel Infrastructure"),
    ("Ceiling plaster in room 405 is peeling off and falling onto the floor", "Hostel Infrastructure"),
    ("Dampness and heavy fungal mold on room wall causing bad smell", "Hostel Infrastructure"),
    ("Balcony iron railing is rusted and loose, posing safety risk", "Hostel Infrastructure"),
    ("Mosquito net mesh on window is torn allowing insects into room", "Hostel Infrastructure"),
    ("Hostel room wooden door is swollen due to rain and won't shut", "Hostel Infrastructure"),
    ("Room tile on floor is chipped and sharp corner caused cut", "Hostel Infrastructure"),
    ("Corridor exit fire door is jammed shut and won't push open", "Hostel Infrastructure"),

    # IT & Classroom Equipment
    ("Classroom 301 ceiling projector is not turning on before seminar", "IT & Equipment"),
    ("Projector display is yellow and HDMI cable port is damaged", "IT & Equipment"),
    ("Sound amplifier in lecture hall 2 is giving loud screeching feedback", "IT & Equipment"),
    ("Podium microphone wire is cut and no sound in classroom speakers", "IT & Equipment"),
    ("Computer lab PC 14 power supply unit does not boot up", "IT & Equipment"),
    ("Hostel corridor Wi-Fi router access point has no internet LED", "IT & Equipment"),
    ("LAN port in room 210 is damaged and RJ45 clip does not lock", "IT & Equipment"),
    ("Smart board touch interactive sensor is not calibrated or responding", "IT & Equipment"),
    ("Computer monitor screen has heavy horizontal lines and flickering", "IT & Equipment"),

    # Safety & Hazard
    ("Sparks and smoke coming from hostel meter box on ground floor", "Safety & Hazard"),
    ("Fire extinguisher in chemistry lab is expired and pressure gauge is zero", "Safety & Hazard"),
    ("Burning plastic smell coming from corridor ceiling wiring conduit", "Safety & Hazard"),
    ("Live electrical cable exposed after rain near hostel walkway", "Safety & Hazard"),
    ("Gas smell detected near college mess kitchen cylinder bank", "Safety & Hazard"),
    ("Heavy water seepage dripping directly into the main electric panel", "Safety & Hazard"),
]

# Assets dictionary for entity identification
ASSET_KEYWORDS = {
    "Ceiling Fan": ["fan", "ceiling fan", "exhaust fan", "regulator", "blade", "humming fan"],
    "Tube Light / LED": ["tube light", "tubelight", "led", "bulb", "lamp", "lighting", "starter", "flickering light"],
    "Switchboard / Socket": ["switchboard", "socket", "plug", "switch", "extension board", "mcb", "breaker", "power outlet", "wiring", "wire"],
    "Geyser / Water Heater": ["geyser", "water heater", "thermostat", "immersion rod"],
    "Water Tap / Faucet": ["tap", "faucet", "valve", "spigot", "shower head", "shower"],
    "Washbasin / Sink": ["washbasin", "basin", "sink", "drain pipe"],
    "Flush Tank / Commode": ["flush", "commode", "toilet", "cistern", "flush tank", "urinal"],
    "Drainage & Sewage": ["drain", "drainage", "sewage", "sewer", "gutter", "blockage", "choked", "clogged", "overflowing"],
    "Water Cooler / RO": ["water cooler", "cooler", "ro", "purifier", "drinking water", "dispenser"],
    "Study Table / Desk": ["study table", "table", "desk", "drawer", "tabletop"],
    "Chair": ["chair", "revolving chair", "stool", "backrest", "seat"],
    "Bed / Cot": ["cot", "bed", "bunk bed", "plank", "frame"],
    "Mattress": ["mattress", "spring", "cushion", "bedding"],
    "Cupboard / Almirah": ["cupboard", "almirah", "wardrobe", "locker", "closet", "shelf", "bookshelf", "drawer"],
    "Door / Lock": ["door", "lock", "latch", "hinge", "handle", "deadbolt", "key"],
    "Window / Mesh": ["window", "glass pane", "mesh", "mosquito net", "curtain rod", "balcony railing"],
    "Air Conditioner (AC)": ["ac", "air conditioner", "split ac", "cooling", "compressor"],
    "Projector / Display": ["projector", "screen", "smart board", "hdmi", "vga"],
    "Audio / Microphone": ["microphone", "mic", "speaker", "amplifier", "podium", "sound"],
    "Computer / Lab PC": ["pc", "computer", "desktop", "monitor", "keyboard", "mouse", "cpu"],
    "Wi-Fi / LAN Network": ["wifi", "wi-fi", "router", "lan", "internet", "ethernet", "access point", "cable"],
    "Fire Safety Equipment": ["fire extinguisher", "fire alarm", "smoke detector", "hose"],
    "Electrical Panel / Meter": ["meter box", "electric panel", "transformer", "distribution board"]
}

# Critical Safety and Urgency trigger indicators
SAFETY_HAZARD_KEYWORDS = [
    "spark", "sparks", "smoke", "burning", "fire", "electric shock", "shock",
    "live wire", "exposed wire", "fire hazard", "gas smell", "gas leak",
    "flooding", "short circuit", "burst pipe", "flame", "exploded", "melted",
    "collapse", "cylinder", "dripping on electric"
]

HIGH_URGENCY_KEYWORDS = [
    "broken lock", "cannot lock", "stuck inside", "water overflowing", "no water",
    "completely blocked", "sewage", "foul smell", "geyser not heating", "heavy leak",
    "trips", "blackout", "urgent", "exam tomorrow", "presentation", "lecture"
]

STOP_WORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
    "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me",
    "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should",
    "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then",
    "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why",
    "with", "would", "you", "your", "yours", "yourself", "yourselves", "room", "hostel", "please", "kindly"
])


def clean_and_tokenize(text: str) -> List[str]:
    """Lowercase, remove punctuation, extract alphabetic tokens, filter stopwords."""
    text = text.lower()
    tokens = re.findall(r"\b[a-z]{2,}\b", text)
    filtered = [t for t in tokens if t not in STOP_WORDS]
    return filtered if filtered else tokens


class PurePythonTFIDFLinearSVM:
    """
    Self-contained, pure-Python TF-IDF vectorizer + One-vs-Rest Linear SVM (SGD)
    Provides zero-dependency NLP classification identical in concept to scikit-learn.
    """
    def __init__(self):
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.classes: List[str] = []
        self.weights: Dict[str, Dict[str, float]] = {}  # class -> {word: weight}
        self.biases: Dict[str, float] = {}

    def fit(self, texts: List[str], labels: List[str]):
        self.classes = sorted(list(set(labels)))
        doc_count = len(texts)
        doc_freq: Dict[str, int] = {}
        tokenized_corpus = []

        # 1. Build vocabulary and document frequencies
        for text in texts:
            tokens = set(clean_and_tokenize(text))
            tokenized_corpus.append(clean_and_tokenize(text))
            for tok in tokens:
                doc_freq[tok] = doc_freq.get(tok, 0) + 1

        self.vocabulary = {word: idx for idx, word in enumerate(sorted(doc_freq.keys()))}
        for word, df in doc_freq.items():
            # Smooth IDF formula: log((1 + N) / (1 + df)) + 1
            self.idf[word] = math.log((1 + doc_count) / (1 + df)) + 1.0

        # 2. Train One-vs-Rest Linear SVM via Pegasos SGD
        for cls in self.classes:
            w: Dict[str, float] = {w: 0.0 for w in self.vocabulary}
            bias = 0.0
            lambda_param = 0.001
            epochs = 40
            t = 0

            for epoch in range(epochs):
                for tokens, label in zip(tokenized_corpus, labels):
                    t += 1
                    eta = 1.0 / (lambda_param * t + 10.0)
                    y = 1.0 if label == cls else -1.0

                    # Compute TF-IDF vector for this document
                    tfidf_vec = self._compute_doc_tfidf(tokens)
                    score = bias + sum(w.get(term, 0.0) * val for term, val in tfidf_vec.items())

                    # Hinge loss subgradient step
                    if y * score < 1.0:
                        for term, val in tfidf_vec.items():
                            w[term] = (1.0 - eta * lambda_param) * w.get(term, 0.0) + eta * y * val
                        bias += eta * y * 0.2
                    else:
                        for term in tfidf_vec:
                            w[term] = (1.0 - eta * lambda_param) * w.get(term, 0.0)

            self.weights[cls] = w
            self.biases[cls] = bias

    def _compute_doc_tfidf(self, tokens: List[str]) -> Dict[str, float]:
        if not tokens:
            return {}
        tf: Dict[str, int] = {}
        for tok in tokens:
            if tok in self.vocabulary:
                tf[tok] = tf.get(tok, 0) + 1

        tfidf: Dict[str, float] = {}
        norm_sq = 0.0
        for tok, count in tf.items():
            val = (count / len(tokens)) * self.idf.get(tok, 1.0)
            tfidf[tok] = val
            norm_sq += val * val

        # L2 normalize
        norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
        return {k: v / norm for k, v in tfidf.items()}

    def predict(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        tokens = clean_and_tokenize(text)
        tfidf_vec = self._compute_doc_tfidf(tokens)

        scores: Dict[str, float] = {}
        for cls in self.classes:
            score = self.biases[cls] + sum(self.weights[cls].get(term, 0.0) * val for term, val in tfidf_vec.items())
            scores[cls] = score

        best_class = max(scores, key=scores.get)
        # Convert margin scores to pseudo-probabilities via softmax
        max_score = max(scores.values()) if scores else 0
        exp_scores = {k: math.exp(v - max_score) for k, v in scores.items()}
        total_exp = sum(exp_scores.values()) or 1.0
        probs = {k: round(v / total_exp, 3) for k, v in exp_scores.items()}
        confidence = probs.get(best_class, 0.85)

        return best_class, confidence, probs


class SmartFixNLPEngine:
    """
    Main NLP Pipeline combining:
    - Linear SVM classifier (Scikit-Learn or Pure Python fallback)
    - Asset & Facility Entity Extractor
    - Urgency & Priority Predictor (Emergency / High / Medium / Low)
    - SLA Deadline Estimator
    """
    def __init__(self):
        self.use_sklearn = HAVE_SKLEARN
        self.sklearn_pipeline = None
        self.pure_svm = None
        self._train_model()

    def _train_model(self):
        texts = [item[0] for item in TRAINING_DATA]
        labels = [item[1] for item in TRAINING_DATA]

        if self.use_sklearn:
            try:
                from sklearn.pipeline import Pipeline
                self.sklearn_pipeline = Pipeline([
                    ('tfidf', TfidfVectorizer(ngram_range=(1, 2), stop_words='english', min_df=1)),
                    ('svm', LinearSVC(C=1.0, random_state=42))
                ])
                self.sklearn_pipeline.fit(texts, labels)
            except Exception as e:
                self.use_sklearn = False

        if not self.use_sklearn or self.sklearn_pipeline is None:
            self.pure_svm = PurePythonTFIDFLinearSVM()
            self.pure_svm.fit(texts, labels)

    def extract_asset(self, text: str) -> str:
        """Identifies which facility or campus asset is referred to in the complaint text."""
        text_lower = text.lower()
        # Direct match on multi-word and single-word keywords
        matched_assets = []
        for asset_name, keywords in ASSET_KEYWORDS.items():
            for kw in keywords:
                # Use regex word boundaries for accurate matching
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, text_lower):
                    # prioritize longer keyword matches
                    matched_assets.append((len(kw), asset_name))

        if matched_assets:
            matched_assets.sort(key=lambda x: x[0], reverse=True)
            return matched_assets[0][1]

        # General fallbacks based on common words
        if "light" in text_lower or "lamp" in text_lower:
            return "Tube Light / LED"
        if "tap" in text_lower or "water" in text_lower:
            return "Water Tap / Faucet"
        if "fan" in text_lower:
            return "Ceiling Fan"
        if "chair" in text_lower:
            return "Chair"
        if "table" in text_lower or "desk" in text_lower:
            return "Study Table / Desk"

        return "General Campus Facility"

    def predict_priority(self, text: str, category: str) -> Tuple[str, str, int, bool]:
        """
        Determines priority level:
        Returns (priority_level, reason, sla_hours, is_safety_critical)
        Levels: Emergency (Urgent), High, Medium, Low
        """
        text_lower = text.lower()

        # Check for immediate safety hazard triggers
        for kw in SAFETY_HAZARD_KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                return (
                    "Emergency",
                    f"Immediate safety/hazard detected: '{kw}'. Potential risk to life or infrastructure.",
                    4,   # 4 hours SLA
                    True
                )

        if category == "Safety & Hazard":
            return (
                "Emergency",
                "Classified under Safety & Hazard. Requires immediate campus safety intervention.",
                4,
                True
            )

        # Check for high urgency keywords
        for kw in HIGH_URGENCY_KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                return (
                    "High",
                    f"High operational disruption detected ('{kw}').",
                    24,  # 24 hours SLA
                    False
                )

        # Category based defaults
        if category in ["Electrical", "Plumbing"]:
            return ("Medium", "Standard utility issue. Scheduled for maintenance technician inspection.", 48, False)
        elif category in ["Furniture", "Hostel Infrastructure"]:
            return ("Medium", "Standard room maintenance request.", 48, False)
        elif category == "IT & Equipment":
            return ("Medium", "Academic equipment maintenance request.", 36, False)

        return ("Low", "Routine maintenance item.", 72, False)

    def classify_complaint(self, text: str) -> Dict[str, Any]:
        """
        End-to-end NLP processing:
        - Category classification (Linear SVM + TF-IDF)
        - Asset detection
        - Priority & SLA prediction
        - Suggested staff role
        """
        if not text or not text.strip():
            return {
                "category": "Hostel Infrastructure",
                "confidence": 0.5,
                "asset": "General Campus Facility",
                "priority": "Low",
                "sla_hours": 72,
                "is_safety_critical": False,
                "priority_reason": "No complaint description provided.",
                "assigned_department": "Hostel Caretaker"
            }

        cleaned_tokens = clean_and_tokenize(text)

        # 1. Category Classification via SVM
        if self.use_sklearn and self.sklearn_pipeline is not None:
            category = self.sklearn_pipeline.predict([text])[0]
            # SVM decision function / confidence estimate
            try:
                decisions = self.sklearn_pipeline.decision_function([text])[0]
                max_dec = max(decisions)
                # Sigmoid approximation for confidence
                confidence = round(1.0 / (1.0 + math.exp(-max_dec)), 2)
            except Exception:
                confidence = 0.92
        else:
            category, confidence, _ = self.pure_svm.predict(text)

        # Safety override: if strong safety keyword exists, category should be Safety & Hazard
        text_lower = text.lower()
        for kw in ["spark", "fire", "smoke", "live wire", "exposed wire", "gas smell", "shock"]:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                category = "Safety & Hazard"
                confidence = 0.98
                break

        # 2. Asset / Facility Detection
        asset = self.extract_asset(text)

        # 3. Priority Prediction
        priority, priority_reason, sla_hours, is_safety_critical = self.predict_priority(text, category)

        # 4. Department / Staff mapping
        dept_map = {
            "Electrical": "Electrician",
            "Plumbing": "Plumber",
            "Furniture": "Carpenter",
            "Hostel Infrastructure": "Civil & Maintenance Crew",
            "IT & Equipment": "IT Systems Technician",
            "Safety & Hazard": "Emergency Quick Response Team"
        }
        suggested_staff = dept_map.get(category, "General Maintenance Staff")

        return {
            "category": category,
            "confidence": confidence,
            "asset": asset,
            "priority": priority,
            "sla_hours": sla_hours,
            "is_safety_critical": is_safety_critical,
            "priority_reason": priority_reason,
            "assigned_department": suggested_staff,
            "tokens": cleaned_tokens[:6]
        }


# Global engine instance
nlp_engine = SmartFixNLPEngine()

if __name__ == "__main__":
    # Quick self-test
    test_cases = [
        "Sparks coming out from the ceiling fan switchboard and smells like burning wire",
        "Water tap in floor 2 washroom is leaking continuously and basin is choked",
        "Wooden study table leg is broken and chair has no wheel",
        "Hostel room 304 window glass is cracked after rainstorm",
        "Projector in seminar hall 2 is not turning on and HDMI cable is loose"
    ]
    print("Testing SmartFix NLP Engine:")
    for tc in test_cases:
        res = nlp_engine.classify_complaint(tc)
        print(f"\nText: '{tc}'")
        print(f" -> Category: {res['category']} (Conf: {res['confidence']})")
        print(f" -> Asset: {res['asset']}")
        print(f" -> Priority: {res['priority']} | SLA: {res['sla_hours']} hrs | Critical: {res['is_safety_critical']}")
        print(f" -> Staff: {res['assigned_department']}")
