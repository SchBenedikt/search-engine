import os
import logging
from google import genai
from google.genai import types
from utils.text_utils import generate_fallback_search_terms

# Function to generate AI response using Google's Gemini model with the correct API
def generate_ai_response(query):
    if not query or query == "#all":
        return "", []
    
    try:
        # Create a client with API key
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_GENAI_API_KEY"))
        )
        
        model = "gemini-2.0-flash"  # Using a faster model for quick responses
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=f"Please answer to this: {query}. Please show your sources."),
                ],
            ),
        ]
        
        # Enable Google Search tool
        tools = [
            types.Tool(google_search=types.GoogleSearch())
        ]
        
        # Define default system instruction for the AI
        lang = os.environ.get('SEARCH_LANG', 'de-DE')  # Default to German if not specified
        default_system_instruction = f"Bitte antworte in {lang}. Zeige Quellen, wenn du im Internet suchst. Du bist ein Assitant für eine Suchmaschine und zeigst bei einer Anfrage so viele Informationen wie möglich"
        
        # Get custom system instruction from query if present (format: #system:instruction)
        system_instruction = default_system_instruction
        if "#system:" in query:
            parts = query.split("#system:", 1)
            if len(parts) > 1:
                query = parts[0].strip()
                # Override default with custom system instruction
                system_instruction = parts[1].strip()
                # Update the user content with the modified query (without the system instruction)
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=f"Please answer this question: {query}. Please show your sources."),
                        ],
                    ),
                ]
        
        generate_content_config = types.GenerateContentConfig(
            tools=tools,
            response_mime_type="text/plain",  # Use supported MIME type
            system_instruction=system_instruction,  # Always add system instruction
        )
        
        # Generate content using the model
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        # Extract citation sources from response if available
        sources = []
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'citation_metadata') and candidate.citation_metadata:
                if hasattr(candidate.citation_metadata, 'citations'):
                    for citation in candidate.citation_metadata.citations:
                        if hasattr(citation, 'uri') and citation.uri:
                            source = {
                                'uri': citation.uri,
                                'title': citation.title if hasattr(citation, 'title') else "Source"
                            }
                            sources.append(source)
        
        return response.text, sources  # Return both the text and sources
    except Exception as e:
        logging.error(f"Error generating AI response: {e}")
        return "Sorry, I couldn't generate a response at this time.", []

def generate_related_search_terms(query):
    """
    Generates related search terms for a given query using the Gemini AI.
    Falls back to rule-based suggestions if the API key is missing.
    Returns a list of related search terms.
    """
    if not query or query == "#all":
        return []
    
    # Check if Gemini API key is available
    api_key = os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_GENAI_API_KEY"))
    if not api_key:
        # Fallback to rule-based related terms when API key is missing
        return generate_fallback_search_terms(query)
    
    try:
        # Create a client with API key
        client = genai.Client(api_key=api_key)
        
        model = "gemini-2.0-flash"  # Using a faster model for quick responses
        
        # Create a prompt that asks for related search terms
        prompt = f"""Based on the search query "{query}", provide exactly 6 related search terms that users might be interested in.
        These should be highly relevant to the original query but add useful variations or specifications.
        Format your response as a simple list of terms only, one per line, with no explanations or numbering.
        Do not repeat the exact original query in your suggestions."""
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
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
        
        # Parse the response into a list of search terms
        related_terms = []
        if response.text:
            # Split by newlines and clean up
            related_terms = [term.strip() for term in response.text.split('\n') if term.strip()]
            # Limit to 6 terms
            related_terms = related_terms[:6]
            
        return related_terms
    except Exception as e:
        logging.error(f"Error generating related search terms: {e}")
        return generate_fallback_search_terms(query)

def chat_with_ai_about_website(website_content, user_message, url):
    """
    Generates an AI response about the content of a website.
    """
    try:
        # Create a client with API key
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_GENAI_API_KEY"))
        )
        
        model = "gemini-2.0-flash"  # Using a more capable model for content analysis
        
        # Parse the domain for context
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        # Create a prompt that provides the website content and sets context
        system_prompt = f"""Sie sind ein hilfreicher KI-Assistent, der Fragen über den Inhalt einer Website beantwortet.
        
        Die Frage des Benutzers bezieht sich auf den Inhalt der Website: {domain}
        
        Bitte beantworten Sie die Frage basierend auf diesen Website-Inhalten. Wenn die Antwort nicht in den Website-Inhalten zu finden ist, sagen Sie ehrlich, dass Sie die Information dort nicht finden können.
        
        Website-Inhalte:
        {website_content[:50000]}
        """
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=system_prompt),
                ],
            ),
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=user_message),
                ],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
            system_instruction=system_prompt
        )
        
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=user_message),
                    ],
                ),
            ],
            config=generate_content_config,
        )
        
        # Extract and return the text response
        ai_response = response.text
        
        return ai_response
    except Exception as e:
        logging.error(f"Error generating AI response for website content: {str(e)}")
        raise Exception(f"Fehler bei der KI-Antwort: {str(e)}")
