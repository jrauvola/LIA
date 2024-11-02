import re

class TextFeatureExtractor:
    def __init__(self):
        # Filler words list
        self.filler_words = [
            "um", "uhm", "uh", "uhh", "er", "err", "ah", "ahh", "like", "you know",
            "sort of", "kind of", "kinda", "sorta", "basically", "literally", "actually",
            "so", "well", "I mean", "you see", "right", "okay", "ok", "yeah", "yea",
            "you know what I mean", "I guess", "just", "stuff", "things", "whatever",
            "anyway", "anyhow", "honestly", "truthfully", "frankly",
            "uh-huh", "huh", "hmm", "mhm", "y'know", "ya know", "dunno", "gonna",
            "wanna", "gotta", "lemme", "gimme", "ain't", "innit",
            "like, you know", "right?", "you know what I'm saying", "obviously",
            "um, you know", "like, totally", "uh-oh", "nope", "meh", "basically",
            "kinda sorta", "I mean, like", "you see what I mean", "you know what I'm talking about",
            "it's like", "for real", "I guess you could say", "you know what I'm saying",
            "I suppose", "to be honest", "like, whatever",
            "ehm", "erm", "mmm", "urm", "umm", "uuh", "yknow", "y'see", "yunno"
        ]

        # Quantifier words list
        self.quantifiers = [
            "all", "another", "any", "both", "each", "either", "enough", "every",
            "few", "fewer", "little", "less", "many", "more", "much", "neither",
            "no", "several", "some", "a few", "a little", "a lot of", "lots of",
            "most", "plenty", "numerous", "countless", "abundant",
            "scarce", "ample", "sufficient", "inadequate", "various",
            "myriad", "copious", "sparse", "plentiful", "negligible",
            "majority", "minority", "handful", "fraction", "bulk",
            "mass", "multitude", "scarcity", "abundance", "profusion",
            "dearth", "surfeit", "paucity", "plurality", "multiplicity",
            "best", "bunch", "ton", "unique"
        ]

        # Compile regex patterns
        self.filler_pattern = r'\b(' + '|'.join(map(re.escape, self.filler_words)) + r')\b'
        self.quantifier_pattern = r'\b(' + '|'.join(map(re.escape, self.quantifiers)) + r')\b'

    def extract_features(self, text):
        """Extract text features from the given text"""
        try:
            # Convert text to lowercase for consistent matching
            text = text.lower()

            # Count total words (splitting on whitespace)
            total_words = len(text.split())

            # Count filler words
            filler_count = len(re.findall(self.filler_pattern, text))

            # Count quantifier words
            quantifier_count = len(re.findall(self.quantifier_pattern, text))

            # Calculate percentages (avoid division by zero)
            filler_pct = (filler_count / total_words * 100) if total_words > 0 else 0
            quantifier_pct = (quantifier_count / total_words * 100) if total_words > 0 else 0

            return {
                'quantifier_words_pct': float(quantifier_pct),
                'filler_nonfluency_pct': float(filler_pct),
                'word_count': total_words
            }

        except Exception as e:
            print(f"Error extracting text features: {str(e)}")
            return {
                'quantifier_words_pct': 0.0,
                'filler_nonfluency_pct': 0.0,
                'word_count': 0
            }


def initialize_text_features():
    """Initialize the text_features list with empty dictionaries"""
    return [{
        'quantifier_words_pct': 0.0,
        'filler_nonfluency_pct': 0.0,
        'word_count': 0
    } for _ in range(5)]


def update_text_features(interview_instance, text, answer_index):
    """Update the text_features list in the interview instance"""
    if not hasattr(interview_instance, 'text_features') or not interview_instance.text_features:
        interview_instance.text_features = initialize_text_features()

    extractor = TextFeatureExtractor()
    features = extractor.extract_features(text)
    if features:
        interview_instance.text_features[answer_index] = features
        return True
    return False