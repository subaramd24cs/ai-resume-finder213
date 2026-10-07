import pdfplumber
import docx2txt
import re

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
    except Exception as e:
        print("Error reading PDF:", e)
    return text

def extract_text_from_docx(docx_path):
    try:
        text = docx2txt.process(docx_path)
        return text
    except Exception as e:
        print("Error reading DOCX:", e)
        return ""

def extract_entities(text):
    # Basic Regex for email
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails = re.findall(email_pattern, text)
    email = emails[0] if emails else "Unknown Email"
    
    # Basic Regex for phone
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    phone = phones[0] if phones else "Unknown Phone"
    
    # Name extraction using SpaCy
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        nlp = None

    name = "Unknown Candidate"
    if nlp:
        # We only want to search the first 1000 characters for the name, usually at the top
        doc = nlp(text[:1000])
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Ensure it's not a common false positive word
                if len(ent.text.split()) > 1:
                    name = ent.text
                    break
    if name == "Unknown Candidate":
        # Fallback to basic heuristics
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:5]:
            if len(line.split()) <= 3 and all(word[0].isupper() for word in line.split() if word.isalpha()):
                name = line
                break

    # Mocking other sections based on keywords
    text_lower = text.lower()
    
    def extract_section(start_keywords, end_keywords=[]):
        start_idx = -1
        for kw in start_keywords:
            idx = text_lower.find(kw)
            if idx != -1:
                start_idx = idx
                break
        if start_idx == -1: return "Not explicitly found"
        
        end_idx = len(text_lower)
        for kw in end_keywords:
            idx = text_lower.find(kw, start_idx + 10)
            if idx != -1 and idx < end_idx:
                end_idx = idx
                
        return text[start_idx:end_idx].strip()[:200] + "..." # return a snippet

    education = extract_section(['education', 'academic background', 'university'])
    experience = extract_section(['experience', 'work history', 'employment'], ['education', 'skills', 'projects'])
    certifications = extract_section(['certifications', 'certificates'])
    projects = extract_section(['projects', 'personal projects'])

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "education": education,
        "experience": experience,
        "certifications": certifications,
        "projects": projects
    }

def parse_resume(file_path):
    ext = file_path.split('.')[-1].lower()
    text = ""
    if ext == 'pdf':
        text = extract_text_from_pdf(file_path)
    elif ext in ['doc', 'docx']:
        text = extract_text_from_docx(file_path)
        
    entities = extract_entities(text)
    entities["text"] = text
    return entities
