import re
import PyPDF2
from io import BytesIO
import spacy

nlp = spacy.load("en_core_web_sm")

def clean_and_process_resume(file):
    print("Parsing PDF...")

    # Read the PDF file
    pdfReader = PyPDF2.PdfReader(BytesIO(file.read()))
    text = ""
    for page in pdfReader.pages:
        text += page.extract_text()

    if text:
        # Clean the text
        cleaned_text = clean_text(text)
        cleaned_text = remove_long_numbers(cleaned_text)
        cleaned_text = remove_text_before_state(cleaned_text)

        # Process the cleaned text
        lemmatized_words = process_resume_text(cleaned_text, nlp)
        return lemmatized_words
    else:
        print("No text found on this page.")
        return []

def clean_text(text):
    # Define regular expression pattern to match allowed characters
    pattern = re.compile(r'[^a-z0-9%./]+')
    # Remove unwanted characters from the text
    cleaned_text = re.sub(pattern, ' ', text.lower())
    return cleaned_text

def remove_long_numbers(text):
    # Remove phone numbers
    # Remove characters like ()-
    cleaned_text = re.sub(r'[-()]+', '', text)

    # Look for numbers separated by a space, and only remove that space between consecutive numbers
    cleaned_text = re.sub(r'(\d)\s+(\d)', r'\1\2', cleaned_text)

    # Delete numbers with at least 10 digits
    cleaned_text = re.sub(r'\b\d{10,}\b', '', cleaned_text)

    return cleaned_text

def remove_text_before_state(text):
    # Remove text before first state instance, which is usually personal info
    state_abbr_to_name = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
        'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
        'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
        'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
        'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
        'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
    }

    # Create a regex pattern to match state abbreviations and full names
    state_pattern = r'\b(?:' + '|'.join(re.escape(state) for state in state_abbr_to_name.values()) + r'|' + \
                    '|'.join(re.escape(abbr) for abbr in state_abbr_to_name.keys()) + r')\b'

    # Find the first occurrence of a state or its abbreviation
    match = re.search(state_pattern, text)

    if match:
        # If a match is found, remove all text before it
        return text[match.start()+len(match.group()):]
    else:
        # If no match is found, return the original text
        return text

def process_resume_text(cleaned_text, nlp):
    # Lemmatization
    doc = nlp(cleaned_text)
    lemmatized_words = [token.lemma_ for token in doc if not token.is_stop]
    return " ".join(lemmatized_words)  # Join lemmatized words with space