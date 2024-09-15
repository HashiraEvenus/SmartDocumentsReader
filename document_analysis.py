import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textstat import flesch_reading_ease
import requests

nltk.download('punkt')
nltk.download('stopwords')

def extract_keywords(text, num_keywords=10):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text.lower())
    filtered_words = [word for word in word_tokens if word.isalnum() and word not in stop_words]
    freq_dist = nltk.FreqDist(filtered_words)
    return freq_dist.most_common(num_keywords)

def calculate_readability(text):
    return flesch_reading_ease(text)

def check_plagiarism(text, api_key):
    url = "https://api.copyleaks.com/v3/plagiarism/check"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "text": text
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None