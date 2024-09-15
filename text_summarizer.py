from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from heapq import nlargest

def summarize_text(text, num_sentences=5):
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)
    
    # Remove stopwords and punctuation
    stop_words = set(stopwords.words('english') + list('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'))
    words = [word.lower() for sentence in sentences for word in sentence.split() if word.lower() not in stop_words]
    
    # Calculate word frequencies
    freq = FreqDist(words)
    
    # Score sentences based on word frequencies
    sentence_scores = {}
    for sentence in sentences:
        for word in sentence.split():
            if word.lower() in freq:
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = freq[word.lower()]
                else:
                    sentence_scores[sentence] += freq[word.lower()]
    
    # Get the top N sentences
    summary_sentences = nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    
    # Join the sentences and return the summary
    return ' '.join(summary_sentences)

def generate_bullet_points(text, num_points=5):
    summary = summarize_text(text, num_points)
    sentences = sent_tokenize(summary)
    return '\n'.join([f"• {sentence}" for sentence in sentences])