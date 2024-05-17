import pandas as pd
import spacy as sp
import pypdf
import re
from collections import Counter
import PyPDF2 as pypdf
from io import BytesIO

nlp = sp.load("en_core_web_sm")

   
def clean_text(text):
    # input to function should be a string
    
    # Define regular expression pattern to match allowed characters
    pattern = re.compile(r'[^a-z0-9%./]+')
    # Remove unwanted characters from the text
    cleaned_text = re.sub(pattern, ' ', text.lower())
    return cleaned_text # string

def clean_resume_text(file):
    print("Parsing PDF...")

    #read in <FileStorage: 'JR_Tesla_Resume.pdf' ('application/pdf')>
    pdfReader = pypdf.PdfReader(BytesIO(file.read()))
    text = ""
    for page in pdfReader.pages:
        text += page.extract_text()
        # text here is raw resume text (string with no formatting)
    if text:
        # Clean the text
        cleaned_text = clean_text(text)
        return cleaned_text # string
    else:
        print("No text found on this page.")

def process_resume_text(cleaned_text, nlp):
    # lemmatization
    # Process the resume text
    doc = nlp(cleaned_text)

    # Lemmatization and Stemming
    lemmatized_words = [token.lemma_ for token in doc if not token.is_stop]
    
    # return entities, lemmatized_words, top_keywords
    return lemmatized_words # list

def remove_long_numbers(text):
    #remove phone numbers
    # Remove characters like ()-
    cleaned_text = re.sub(r'[-()]+', '', text)
    
    # Look for numbers separated by a space, and only remove that space between consecutive numbers
    cleaned_text = re.sub(r'(\d)\s+(\d)', r'\1\2', cleaned_text)
    
    # Delete numbers with at least 10 digits
    cleaned_text = re.sub(r'\b\d{10,}\b', '', cleaned_text)
    
    return cleaned_text # string

def censor_text(text, words):
    # remove user sensitive information
    # Lowercase both text and words for case-insensitive matching
    text_lower = text.lower()
    words_lower = [word.lower() for word in words]

    # Create a set of all possible combinations of words (including single words)
    all_combos = set()
    for word in words_lower:
        all_combos.add(word)
        for i in range(1, len(word)):
        all_combos.add(word[:i] + word[i:])  # Add all substrings

    censored_text = text_lower
    for combo in all_combos:
        # Replace all occurrences of the combination (case-insensitive)
        censored_text = censored_text.replace(combo, "")

    # Return the censored text with the original casing
    return ''.join([c if c.islower() else c.upper() for c in censored_text])

def remove_text_before_state(text):
    # remove text before first state instance, which is usually personal info
    # Define a dictionary mapping state abbreviations to their full names
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
    
def clean_text(uploaded_file):
    clean_text = clean_resume_text(uploaded_file)  
    clean_text = remove_long_numbers(clean_text)
    # clean_text = censor_text(clean_text)
    clean_text = remove_text_before_state(clean_text)
    lemmatized_words = process_resume_text(clean_text, nlp)
    return lemmatized_words