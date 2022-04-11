import docx2txt
import nltk
import requests
 
nltk.download('stopwords')
 
 
def extract_text_from_docx(docx_path):
    txt = docx2txt.process(docx_path)
    if txt:
        return txt.replace('\t', ' ')
    return None
 
 
def skill_exists(skill):
    url = f'https://api.apilayer.com/skills?q={skill}&amp;count=1'
    headers = {'apikey': 'tegtTot9eJxbtD7lxSoZPnGgR08dYYzo'}
    response = requests.request('GET', url, headers=headers)
    result = response.json()
 
    if response.status_code == 200:
        return len(result) > 0 and result[0].lower() == skill.lower()
    raise Exception(result.get('message'))
 
 
def extract_skills(input_text):
    stop_words = set(nltk.corpus.stopwords.words('english'))
    word_tokens = nltk.tokenize.word_tokenize(input_text)

    filtered_tokens = [w for w in word_tokens if w not in stop_words]

    filtered_tokens = [w for w in word_tokens if w.isalpha()]

    bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))
 
    found_skills = set()

    for token in filtered_tokens:
        if skill_exists(token.lower()):
            found_skills.add(token)
 
    for ngram in bigrams_trigrams:
        if skill_exists(ngram.lower()):
            found_skills.add(ngram)
 
    return found_skills
 
 
if __name__ == '__main__':
    text = extract_text_from_docx('resume.docx')
    skills = extract_skills(text)
 
    print(skills)