import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Attempt to download required NLTK resources
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

def clean_text(text: str) -> str:
    """
    Cleans text by lowercasing, removing punctuation, 
    removing stopwords, and normalizing whitespace.
    """
    if not text:
        return ""
    
    # 1. Lowercase
    text = text.lower()
    
    # 2. Remove URLs, emails, etc (basic)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    
    # 3. Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # 4. Tokenize
    try:
        tokens = word_tokenize(text)
    except:
        # Fallback if punkt is not available
        tokens = text.split()
        
    # 5. Remove stopwords
    try:
        stop_words = set(stopwords.words('english'))
    except:
        # Fallback stopwords
        stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        
    filtered_tokens = [word for word in tokens if word not in stop_words and word.isalpha()]
    
    # 6. Normalize whitespace
    cleaned_text = ' '.join(filtered_tokens)
    
    return cleaned_text
