import requests
import logging
from urllib.parse import quote_plus

def get_stackoverflow_panel(query):
    """
    Fetch Stack Overflow questions and answers related to the query.
    Uses the public Stack Exchange API without authentication.
    
    Args:
        query (str): The search query
    
    Returns:
        dict: Stack Overflow panel data or None if not available
    """
    try:
        # Clean and encode the query
        search_query = quote_plus(query)
        
        # Stack Exchange API endpoint for searching questions
        api_url = f"https://api.stackexchange.com/2.3/search?order=desc&sort=relevance&intitle={search_query}&site=stackoverflow"
        
        # Make the request - Stack Exchange API responses are compressed by default
        headers = {'Accept-Encoding': 'gzip'}
        response = requests.get(api_url, headers=headers)
        data = response.json()
        
        if not response.ok or 'items' not in data or not data['items']:
            return None
        
        # Get the top 5 questions
        top_questions = data['items'][:5]
        
        # Create panel data
        panel_data = {
            'title': f"Stack Overflow: {query}",
            'questions': []
        }
        
        for question in top_questions:
            q_data = {
                'title': question.get('title', ''),
                'link': question.get('link', ''),
                'score': question.get('score', 0),
                'answer_count': question.get('answer_count', 0),
                'is_answered': question.get('is_answered', False),
                'creation_date': question.get('creation_date', 0),
                'tags': question.get('tags', [])
            }
            panel_data['questions'].append(q_data)
        
        return panel_data
        
    except Exception as e:
        logging.error(f"Stack Overflow panel error: {e}")
        return None
