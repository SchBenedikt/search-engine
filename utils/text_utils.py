import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Stelle sicher, dass die notwendigen NLTK-Ressourcen heruntergeladen sind
try:
    nltk.download('punkt')
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english')).union(set(stopwords.words('german')))
    stemmer = PorterStemmer()
except LookupError as e:
    nltk.download('punkt')
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english')).union(set(stopwords.words('german')))
    stemmer = PorterStemmer()

def preprocess_query(query):
    """
    Verarbeitet eine Suchanfrage, um Stopwörter zu entfernen und Wörter zu stemmen.
    """
    words = nltk.word_tokenize(query)
    if not words:
        return ''
    if len(words) > 1:
        processed_words = [stemmer.stem(word) for word in words[:-1] if word.lower() not in stop_words]
        processed_words.append(words[-1])  # Add the last word without stemming
    else:
        processed_words = [words[0]] if words[0].lower() not in stop_words else []
    return ' '.join(processed_words)

def preprocess_query_for_search(query):
    """
    Gibt sowohl die Originalanfrage als auch die verarbeitete Anfrage zurück.
    """
    original_query = query  # Keep the original query
    processed_query = preprocess_query(query)  # Process for search
    return original_query, processed_query

def generate_fallback_search_terms(query):
    """
    Generiert verwandte Suchbegriffe ohne KI-API, basierend auf einfachen Mustern.
    """
    query = query.lower().strip()
    
    # Common suffixes to add to search queries
    common_suffixes = [
        "installation", "tutorial", "guide", "download", "alternatives", "vs", 
        "how to use", "setup", "configuration", "examples", "pricing"
    ]
    
    # Common prefixes to add to search queries
    common_prefixes = [
        "best", "how to", "what is", "why use", "compare", "install"
    ]
    
    results = []
    
    # Add some suffixes
    for suffix in common_suffixes[:3]:
        if f"{query} {suffix}" != query:
            results.append(f"{query} {suffix}")
    
    # Add some prefixes
    for prefix in common_prefixes[:3]:
        if f"{prefix} {query}" != query:
            results.append(f"{prefix} {query}")
    
    # If we don't have enough suggestions, add more generic ones
    if len(results) < 6:
        if "open source" not in query and len(results) < 6:
            results.append(f"{query} open source")
        if "alternative" not in query and len(results) < 6:
            results.append(f"{query} alternatives")
        if "review" not in query and len(results) < 6:
            results.append(f"{query} review")
    
    # Return up to 6 suggestions
    return results[:6]
