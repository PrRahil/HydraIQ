import spacy

# Load spaCy's model for semantic similarity
nlp = spacy.load("en_core_web_md")

# Groundwater-related phrases
groundwater_phrases = [
    "Groundwater Management",
    "Hydrogeological Scenario",
    "Water Level Data",
    "Water Quality",
    "Groundwater Resources",
    "Comprehensive Report",
    "Categorization of Areas",
    "Groundwater Assessment",
    "Ground water",
    "Aquifer",
    "Wells",
    "Subsurface water",
    "hydrology",
    "Groundwater flow",
    "Subsurface water",
    "Confined aquifer", "Unconfined aquifer", "Groundwater contamination", "Groundwater management",
    "Saltwater intrusion", "Aquifer depletion", "Groundwater recharge zone",
    "Water quality", "Water treatment",
    "Aquifer storage and recovery (ASR)", "NOC", "Groundwater Management", "pH Levels",
]

# Function to check relevance
def is_related_to_groundwater(question, threshold=0.4):
    question_doc = nlp(question)
    for phrase in groundwater_phrases:
        phrase_doc = nlp(phrase)
        if question_doc.similarity(phrase_doc) > threshold:
            return True
    return False
