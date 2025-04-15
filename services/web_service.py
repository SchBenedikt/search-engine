import logging
import requests
import re
import os
from bs4 import BeautifulSoup
import wikipedia

def fetch_and_extract_content(url):
    """
    Lädt den Inhalt einer Webseite und extrahiert den relevanten Text.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Use BeautifulSoup to extract content from <p> tags
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from all paragraph tags
        paragraphs = soup.find_all('p')
        
        # If no paragraphs found, use basic extraction as fallback
        if not paragraphs:
            # Basic HTML content extraction as fallback
            content = response.text
            content = re.sub(r'<[^>]+>', ' ', content)
            content = re.sub(r'\s+', ' ', content).strip()
        else:
            # Extract and join text from all paragraph tags
            p_contents = [p.get_text().strip() for p in paragraphs]
            content = "\n\n".join(p_contents)
            
        # Remove extra whitespace
        content = re.sub(r'\s{3,}', '\n\n', content).strip()
        
        # Truncate if too large
        max_length = 50000  # Approximate token limit for AI context
        if len(content) > max_length:
            content = content[:max_length] + "... [Content truncated due to length]"
        
        return content
    except Exception as e:
        logging.error(f"Error fetching content from {url}: {str(e)}")
        raise Exception(f"Fehler beim Abrufen des Website-Inhalts: {str(e)}")

def get_page_summary(url):
    """
    Holt und fasst den Inhalt einer Webseite zusammen.
    """
    try:
        # Fetch the webpage content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Extract content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(['script', 'style', 'meta', 'link', 'header', 'footer', 'nav']):
            script_or_style.decompose()
        
        # Get the page title
        title = soup.title.string if soup.title else "No title found"
        
        # Extract text from paragraphs, prioritizing main content
        paragraphs = []
        
        # Try to find main content area (common containers for main content)
        main_content = soup.find('main') or soup.find('article') or soup.find(id='content') or soup.find(class_='content')
        
        if main_content:
            paragraphs = [p.get_text().strip() for p in main_content.find_all('p') if p.get_text().strip()]
        
        # If no paragraphs found in main content, look in the whole document
        if not paragraphs:
            paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]
        
        # Limit to first few paragraphs for summary
        content = " ".join(paragraphs[:5])
        
        # Ensure content isn't too long
        if len(content) > 1000:
            content = content[:997] + "..."
        
        # If content is still short, add more text from headers
        if len(content) < 200:
            headers_text = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3']) if h.get_text().strip()]
            content = " ".join(headers_text + [content])
        
        # If we have a Gemini API key, generate a summary
        api_key = os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_GENAI_API_KEY"))
        summary = ""
        
        if api_key and content:
            try:
                # Create a client with API key
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=api_key)
                
                model = "gemini-2.0-flash"  # Using a faster model for summaries
                
                # Create prompt for summary
                prompt = f"""Bitte erstelle eine prägnante Zusammenfassung der folgenden Webseite. 
                Der Zusammenfassung sollte maximal 2-3 Sätze umfassen und die Hauptidee der Seite vermitteln.
                
                Webseite: {title}
                Inhalt: {content[:5000]}"""  # Limit content to 5000 chars for API
                
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)],
                    ),
                ]
                
                generate_content_config = types.GenerateContentConfig(
                    response_mime_type="text/plain",
                )
                
                # Generate content using the model
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=generate_content_config,
                )
                
                if response.text and len(response.text) > 5:  # Ensure we got a valid response
                    summary = response.text
                    logging.info(f"Generated AI summary for {url}")
            except Exception as e:
                logging.error(f"Error generating AI summary: {e}")
                summary = ""  # Reset summary if error occurs
        
        # If AI summary failed or no API key, use the first paragraph as summary
        if not summary and paragraphs:
            summary = paragraphs[0]
        else:
            summary = summary or "No summary available."
        
        return {
            'title': title,
            'summary': summary,
            'content': content
        }
    except Exception as e:
        logging.error(f"Error fetching page summary for {url}: {str(e)}")
        return {
            'title': "Error loading page",
            'summary': f"Error: {str(e)}",
            'content': ""
        }

def fetch_google_results(query):
    """
    Holt Suchergebnisse von der Google Custom Search API.
    """
    # Get API key and CX from environment variables
    import os
    api_key = os.environ.get('GOOGLE_API_KEY')
    cx = os.environ.get('GOOGLE_CX')
    if not api_key or not cx:
        logging.error('Google API key or CX is not set.')
        return []
    
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except requests.RequestException as e:
        logging.error(f'Error fetching Google search results: {e}')
        return []

def get_knowledge_panel(query, lang=None):
    """
    Versucht, Wikipedia-Informationen für eine Abfrage abzurufen, um sie in einem Knowledge Panel anzuzeigen.
    Gibt ein Wörterbuch mit Informationen oder None zurück, wenn keine passenden Informationen gefunden werden.
    """
    if not query or query.startswith('#'):
        return None
    
    # Set default language to English
    wikipedia_lang = 'en'
    
    # Set language based on the user's selected language
    if lang:
        if lang.startswith('de'):
            wikipedia_lang = 'de'
        elif lang.startswith('fr'):
            wikipedia_lang = 'fr'
        elif lang.startswith('es'):
            wikipedia_lang = 'es'
        elif lang.startswith('it'):
            wikipedia_lang = 'it'
    
    # Set Wikipedia language
    wikipedia.set_lang(wikipedia_lang)
    
    try:
        # Clean up the query - remove special characters and focus on key terms
        clean_query = re.sub(r'[^\w\s]', '', query).strip()
        
        # Skip short or common queries that are unlikely to be entities
        if len(clean_query.split()) <= 1 and len(clean_query) < 4:
            return None
            
        # Try to search Wikipedia for the term
        search_results = wikipedia.search(clean_query, results=1)
        if not search_results:
            return None
            
        # Get the first result
        page_title = search_results[0]
        
        try:
            # Get the Wikipedia page
            page = wikipedia.page(page_title, auto_suggest=False)
            
            # Extract relevant information
            summary = page.summary
            # Trim summary to a reasonable length if needed
            if len(summary) > 500:
                summary = summary[:500] + "..."
                
            # Create knowledge panel data
            knowledge_panel = {
                'title': page.title,
                'summary': summary,
                'url': page.url,
                'image_url': None,  # Default to None, we'll try to find an image
                'wiki_lang': wikipedia_lang  # Store the language used
            }
            
            # Try to get an image if available
            if page.images:
                for img in page.images:
                    # Look for images that might be relevant (avoid small icons, etc.)
                    if ('logo' in img.lower() or 
                        'photo' in img.lower() or 
                        'image' in img.lower() or 
                        'picture' in img.lower() or
                        page.title.lower() in img.lower()):
                        if not img.endswith('.svg') and not img.endswith('.gif'):
                            knowledge_panel['image_url'] = img
                            break
            
            return knowledge_panel
            
        except wikipedia.exceptions.DisambiguationError as e:
            # If we hit a disambiguation page, try the first option
            if e.options:
                try:
                    page = wikipedia.page(e.options[0], auto_suggest=False)
                    summary = page.summary
                    if len(summary) > 500:
                        summary = summary[:500] + "..."
                    
                    knowledge_panel = {
                        'title': page.title,
                        'summary': summary,
                        'url': page.url,
                        'image_url': None
                    }
                    
                    if page.images:
                        for img in page.images:
                            if ('logo' in img.lower() or 
                                'photo' in img.lower() or 
                                'image' in img.lower() or 
                                'picture' in img.lower() or
                                page.title.lower() in img.lower()):
                                if not img.endswith('.svg') and not img.endswith('.gif'):
                                    knowledge_panel['image_url'] = img
                                    break
                    
                    return knowledge_panel
                except Exception:
                    return None
    except Exception as e:
        logging.error(f"Knowledge panel error: {e}")
        return None
    
    return None

def get_github_organization(query):
    """
    Versucht, GitHub-Organisations- oder Benutzerinformationen für eine Abfrage abzurufen.
    Gibt ein Wörterbuch mit Informationen oder None zurück, wenn keine Übereinstimmung gefunden wird.
    """
    if not query or query.startswith('#'):
        return None
        
    # Clean up the query - remove special characters and spaces
    clean_query = re.sub(r'[^\w\s]', '', query).strip().lower().replace(' ', '')
    
    if not clean_query:
        return None
    
    try:
        headers = {}
        
        # Add GitHub token if available for better rate limits
        import os
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f"token {github_token}"
        
        # First check if it's an organization
        org_url = f"https://api.github.com/orgs/{clean_query}"
        org_response = requests.get(org_url, headers=headers)
        
        # If organization exists, use that data
        if org_response.status_code == 200:
            org_data = org_response.json()
            
            # Get basic organization information
            github_panel = {
                'name': org_data.get('name') or org_data.get('login'),
                'login': org_data.get('login'),
                'description': org_data.get('description') or "No description available",
                'url': org_data.get('html_url'),
                'avatar_url': org_data.get('avatar_url'),
                'public_repos': org_data.get('public_repos', 0),
                'followers': org_data.get('followers', 0),
                'blog': org_data.get('blog') or None,
                'location': org_data.get('location') or None,
                'created_at': org_data.get('created_at'),
                'type': 'Organization'
            }
            
            # Try to get repositories information
            try:
                repos_url = f"https://api.github.com/orgs/{clean_query}/repos?sort=updated&per_page=3"
                repos_response = requests.get(repos_url, headers=headers)
                if repos_response.status_code == 200:
                    repos_data = repos_response.json()
                    top_repos = []
                    for repo in repos_data[:3]:  # Get top 3 repos
                        top_repos.append({
                            'name': repo.get('name'),
                            'description': repo.get('description') or "No description available",
                            'url': repo.get('html_url'),
                            'stars': repo.get('stargazers_count', 0),
                            'forks': repo.get('forks_count', 0),
                            'updated_at': repo.get('updated_at')
                        })
                    github_panel['top_repos'] = top_repos
            except Exception as e:
                logging.error(f"Error fetching GitHub organization repositories: {e}")
                github_panel['top_repos'] = []
                
            return github_panel
            
        # If not an organization, try as a user
        user_url = f"https://api.github.com/users/{clean_query}"
        user_response = requests.get(user_url, headers=headers)
        
        # If user exists, use that data
        if user_response.status_code == 200:
            user_data = user_response.json()
            
            github_panel = {
                'name': user_data.get('name') or user_data.get('login'),
                'login': user_data.get('login'),
                'description': user_data.get('bio') or "No bio available",
                'url': user_data.get('html_url'),
                'avatar_url': user_data.get('avatar_url'),
                'public_repos': user_data.get('public_repos', 0),
                'followers': user_data.get('followers', 0),
                'blog': user_data.get('blog') or None,
                'location': user_data.get('location') or None, 
                'created_at': user_data.get('created_at'),
                'company': user_data.get('company') or None,
                'email': user_data.get('email') or None,
                'twitter_username': user_data.get('twitter_username') or None,
                'type': 'User'
            }
            
            # Get user's repositories sorted by last updated
            try:
                repos_url = f"https://api.github.com/users/{clean_query}/repos?sort=updated&per_page=3"
                repos_response = requests.get(repos_url, headers=headers)
                if repos_response.status_code == 200:
                    repos_data = repos_response.json()
                    top_repos = []
                    for repo in repos_data[:3]:  # Get top 3 most recently updated repos
                        top_repos.append({
                            'name': repo.get('name'),
                            'description': repo.get('description') or "No description available",
                            'url': repo.get('html_url'),
                            'stars': repo.get('stargazers_count', 0),
                            'forks': repo.get('forks_count', 0),
                            'updated_at': repo.get('updated_at')
                        })
                    github_panel['top_repos'] = top_repos
            except Exception as e:
                logging.error(f"Error fetching GitHub user repositories: {e}")
                github_panel['top_repos'] = []
                
            return github_panel
            
        # Neither organization nor user found
        return None
    except Exception as e:
        logging.error(f"GitHub panel error: {e}")
        return None
