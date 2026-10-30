"""
Medical Domain Guard for AISIA — AI_Based_Strategic_Intelligence_Assistant
Validates that queries are medical in nature and rejects non-medical requests.
"""

import re
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ── Medical keyword sets ─────────────────────────────────────────────────────

MEDICAL_KEYWORDS = {
    # Anatomy and physiology
    "heart", "brain", "lung", "liver", "kidney", "blood", "bone", "muscle",
    "nerve", "artery", "vein", "cell", "tissue", "organ", "spine", "skull",
    "stomach", "intestine", "pancreas", "thyroid", "adrenal", "pituitary",
    "lymph", "immune", "skin", "eye", "ear", "nose", "throat", "mouth",
    "chest", "abdomen", "pelvis", "femur", "tibia", "humerus", "cortex",
    "neuron", "synapse", "hormone", "enzyme", "protein", "dna", "rna",
    "chromosome", "gene", "metabolism", "respiration", "circulation",
    "digestion", "excretion", "reproduction", "homeostasis", "anatomy",
    "physiology", "histology", "pathology", "embryology",

    # Conditions and diseases
    "diabetes", "hypertension", "cancer", "tumor", "infection", "disease",
    "syndrome", "disorder", "condition", "illness", "symptoms", "diagnosis",
    "prognosis", "treatment", "therapy", "surgery", "procedure", "covid",
    "pneumonia", "asthma", "copd", "stroke", "seizure", "epilepsy",
    "alzheimer", "parkinson", "depression", "anxiety", "schizophrenia",
    "arthritis", "osteoporosis", "anemia", "leukemia", "lymphoma",
    "melanoma", "hepatitis", "cirrhosis", "nephritis", "dialysis",
    "cardiac", "cardiovascular", "myocardial", "infarction", "arrhythmia",
    "hypertrophy", "edema", "inflammation", "fibrosis", "necrosis",
    "sepsis", "shock", "fracture", "dislocation", "sprain", "laceration",
    "abrasion", "burn", "wound", "ulcer", "abscess", "cyst", "polyp",

    # Symptoms
    "pain", "fever", "nausea", "vomiting", "diarrhea", "fatigue", "weakness",
    "dizziness", "headache", "rash", "swelling", "bleeding", "breathless",
    "dyspnea", "cough", "sputum", "palpitation", "syncope", "jaundice",
    "pallor", "cyanosis", "edema", "ascites", "pruritus", "insomnia",
    "tachycardia", "bradycardia", "hypotension", "tachypnea",

    # Medications and pharmacology
    "medication", "drug", "medicine", "tablet", "capsule", "injection",
    "dose", "dosage", "pharmacology", "antibiotic", "antiviral", "antifungal",
    "analgesic", "antipyretic", "anti-inflammatory", "antihypertensive",
    "antidiabetic", "antidepressant", "anxiolytic", "anticoagulant",
    "antiplatelet", "diuretic", "bronchodilator", "corticosteroid",
    "chemotherapy", "immunotherapy", "vaccine", "aspirin", "ibuprofen",
    "paracetamol", "metformin", "insulin", "warfarin", "statins",
    "beta blocker", "ace inhibitor", "arb", "ssri", "nsaid", "opioid",

    # Medical procedures and tests
    "mri", "ct scan", "x-ray", "ultrasound", "ecg", "ekg", "blood test",
    "biopsy", "endoscopy", "colonoscopy", "mammogram", "pap smear",
    "surgery", "operation", "transplant", "dialysis", "chemotherapy",
    "radiotherapy", "physiotherapy", "occupational therapy", "cpr",
    "intubation", "ventilator", "catheter", "stent", "pacemaker",
    "prosthetic", "defibrillator", "anesthesia", "sedation",

    # Medical fields
    "medical", "clinical", "healthcare", "health", "doctor", "physician",
    "nurse", "pharmacist", "surgeon", "cardiologist", "neurologist",
    "oncologist", "pediatrician", "psychiatrist", "dermatologist",
    "ophthalmologist", "orthopedic", "gynecologist", "obstetrician",
    "endocrinologist", "gastroenterologist", "pulmonologist", "urologist",
    "nephrologist", "rheumatologist", "infectious", "emergency", "hospital",
    "clinic", "ward", "icu", "icu", "emergency room", "er",

    # Medical research
    "clinical trial", "randomized", "placebo", "control group", "cohort",
    "evidence", "guideline", "protocol", "pubmed", "lancet", "nejm",
    "who", "cdc", "fda", "nih", "systematic review", "meta-analysis",

    # Nutrition and prevention
    "nutrition", "diet", "vitamin", "mineral", "supplement", "calorie",
    "obesity", "bmi", "weight", "exercise", "prevention", "screening",

    # ICD/coding related
    "icd", "icd-10", "diagnosis code", "procedure code",
}

# ── Domains that indicate NON-medical queries ────────────────────────────────

REJECTED_DOMAIN_PATTERNS = [
    # Finance and markets
    r'\b(stock|equity|bond|crypto|bitcoin|forex|currency|market cap|ipo|hedge fund|portfolio|investment|trading|nasdaq|nyse|dow jones|s&p|etf|mutual fund|dividend|earnings|revenue|profit|loss|balance sheet|p/e ratio|yfinance|ticker symbol)\b',
    # Geopolitics and military
    r'\b(war|military|weapon|missile|tank|soldier|army|navy|air force|intelligence|cia|nsa|pentagon|nato|defcon|sanctions|geopolitical|diplomatic|embassy|treaty|espionage|surveillance|reconnaissance|osint|threat assessment|strategic intelligence|conflict zone|terrorist)\b',
    # Programming and technology (general)
    r'\b(python code|java code|javascript|typescript|html|css|sql query|algorithm|data structure|machine learning model|neural network architecture|api design|software development|coding|programming|debugging|git|docker|kubernetes|aws|azure|gcp)\b',
    # Sports
    r'\b(football|soccer|basketball|cricket|tennis|olympic|championship|tournament|player stats|nfl|nba|mlb|nhl|fifa|ipl|fantasy sports)\b',
    # Entertainment
    r'\b(movie|film|actor|actress|director|music album|song lyrics|netflix|hollywood|bollywood|video game|anime|manga)\b',
]

# ── Emergency / life-threatening symptom patterns ────────────────────────────

EMERGENCY_PATTERNS = [
    r'\b(chest pain|crushing chest|heart attack|cardiac arrest)\b',
    r'\b(stroke|facial droop|arm weakness|speech difficulty|sudden numbness|facial paralysis)\b',
    r'\b(overdose|drug overdose|poisoning|toxic ingestion)\b',
    r'\b(severe allergic|anaphylaxis|anaphylactic shock)\b',
    r'\b(suicidal|suicide attempt|self harm|self-harm|want to die|kill myself)\b',
    r'\b(severe bleeding|blood loss|hemorrhage|uncontrolled bleeding)\b',
    r'\b(difficulty breathing|can\'t breathe|not breathing|respiratory arrest)\b',
    r'\b(loss of consciousness|unconscious|unresponsive|fainted)\b',
    r'\b(severe head injury|traumatic brain|brain bleed)\b',
    r'\b(septic shock|organ failure)\b',
    r'\b(high fever.*child|febrile seizure|infant.*fever)\b',
]

EMERGENCY_MESSAGE = (
    "⚠️ URGENT MEDICAL ATTENTION REQUIRED\n\n"
    "The symptoms or situation you described may indicate a medical emergency. "
    "Please take the following steps IMMEDIATELY:\n\n"
    "🚨 Call emergency services (911 in the US, 112 in Europe, 108 in India) or\n"
    "🏥 Go to the nearest Emergency Room immediately.\n\n"
    "Do not wait for online information in a potential emergency situation. "
    "AISIA can provide educational context after you are safe, but emergency care "
    "professionals must be involved immediately.\n\n"
    "This platform is for educational and informational purposes only — "
    "it is NOT a substitute for emergency medical care."
)


@dataclass
class DomainValidationResult:
    is_medical: bool
    confidence: float          # 0.0 to 1.0
    detected_domains: list     # list of detected medical domains
    rejection_reason: Optional[str] = None
    is_emergency: bool = False
    emergency_message: Optional[str] = None


class MedicalDomainGuard:
    """
    Validates that incoming queries are medical in nature.
    Enforces domain restriction for AISIA.
    """

    def validate(self, query: str) -> DomainValidationResult:
        """
        Validate whether a query is medical in nature.

        Returns a DomainValidationResult with:
        - is_medical: True if the query should be processed
        - confidence: confidence score for the classification
        - rejection_reason: explanation if rejected
        - is_emergency: True if emergency patterns detected
        - emergency_message: emergency guidance if applicable
        """
        query_lower = query.lower().strip()

        if not query_lower or len(query_lower) < 5:
            return DomainValidationResult(
                is_medical=False,
                confidence=1.0,
                detected_domains=[],
                rejection_reason="Query is too short. Please provide a detailed medical question."
            )

        # 1. Check for non-medical domains first
        for pattern in REJECTED_DOMAIN_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                logger.info(f"Domain guard: Rejected non-medical query. Pattern matched: {pattern[:50]}")
                return DomainValidationResult(
                    is_medical=False,
                    confidence=0.95,
                    detected_domains=[],
                    rejection_reason=(
                        "AISIA is exclusively a medical AI platform. This query appears to be about "
                        "a non-medical topic (finance, military, general technology, or other domains). "
                        "Please ask a medical, healthcare, or biomedical science question."
                    )
                )

        # 2. Check for emergency patterns
        is_emergency = False
        for pattern in EMERGENCY_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                is_emergency = True
                logger.warning(f"Domain guard: Emergency pattern detected in query")
                break

        # 3. Count medical keyword hits
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        medical_hits = query_words.intersection(MEDICAL_KEYWORDS)

        # Also check multi-word phrases
        multi_word_medical = [
            "blood pressure", "blood sugar", "blood test", "heart rate", "blood count",
            "clinical trial", "medical history", "side effect", "drug interaction",
            "patient care", "treatment plan", "laboratory test", "vital signs",
            "immune system", "nervous system", "digestive system", "respiratory system",
            "urinary tract", "thyroid function", "liver function", "kidney function",
            "bone density", "body mass", "blood glucose", "cholesterol level",
        ]
        phrase_hits = sum(1 for phrase in multi_word_medical if phrase in query_lower)

        total_hits = len(medical_hits) + phrase_hits

        # 4. Classify
        detected_domains = _detect_medical_domain(query_lower, medical_hits)

        if total_hits >= 1 or is_emergency:
            # Medical query accepted
            confidence = min(0.99, 0.5 + (total_hits * 0.1))
            return DomainValidationResult(
                is_medical=True,
                confidence=confidence,
                detected_domains=detected_domains,
                is_emergency=is_emergency,
                emergency_message=EMERGENCY_MESSAGE if is_emergency else None
            )

        # Borderline — check for health-related intent words
        health_intent_words = [
            "what is", "how does", "symptoms of", "causes of", "treatment for",
            "cure for", "prevent", "risk of", "effect of", "study on",
        ]
        for intent in health_intent_words:
            if intent in query_lower:
                # Give benefit of the doubt if it looks like an information-seeking query
                # about a specific topic — but it must have some medical context
                return DomainValidationResult(
                    is_medical=False,
                    confidence=0.7,
                    detected_domains=[],
                    rejection_reason=(
                        "Your query does not appear to be about a medical topic. "
                        "AISIA handles medical and healthcare questions only — such as diseases, "
                        "symptoms, medications, anatomy, clinical guidelines, and medical research. "
                        "Please rephrase your question with a medical focus."
                    )
                )

        return DomainValidationResult(
            is_medical=False,
            confidence=0.8,
            detected_domains=[],
            rejection_reason=(
                "AISIA is a medical AI platform for healthcare and biomedical questions. "
                "Your query does not appear to be about a medical topic. "
                "Examples of accepted queries: 'What are the symptoms of Type 2 diabetes?', "
                "'How does metformin work?', 'What is the treatment for hypertension?'"
            )
        )


def _detect_medical_domain(query_lower: str, medical_hits: set) -> list:
    """Detect which specific medical domains are relevant to the query."""
    domains = []

    domain_keywords = {
        "Cardiology": ["heart", "cardiac", "cardiovascular", "arrhythmia", "myocardial", "angina", "coronary"],
        "Neurology": ["brain", "neuron", "stroke", "seizure", "epilepsy", "alzheimer", "parkinson", "nerve"],
        "Oncology": ["cancer", "tumor", "malignant", "chemotherapy", "lymphoma", "leukemia", "melanoma"],
        "Pharmacology": ["drug", "medication", "dose", "pharmacology", "antibiotic", "side effect", "interaction"],
        "Endocrinology": ["diabetes", "insulin", "thyroid", "hormone", "adrenal", "pituitary", "pancreas"],
        "Pulmonology": ["lung", "breathing", "asthma", "copd", "pneumonia", "respiratory"],
        "Gastroenterology": ["stomach", "intestine", "liver", "hepatitis", "cirrhosis", "colonoscopy"],
        "Anatomy": ["anatomy", "bone", "muscle", "tissue", "organ", "cell", "physiology"],
        "Psychiatry": ["depression", "anxiety", "schizophrenia", "psychiatric", "mental health"],
        "Infectious Disease": ["infection", "bacteria", "virus", "antibiotic", "sepsis", "covid"],
        "General Medicine": ["fever", "pain", "symptoms", "diagnosis", "treatment", "clinical"],
    }

    for domain, keywords in domain_keywords.items():
        if any(kw in query_lower or kw in medical_hits for kw in keywords):
            domains.append(domain)

    return domains[:3]  # Return top 3 detected domains


# Singleton instance
medical_domain_guard = MedicalDomainGuard()
