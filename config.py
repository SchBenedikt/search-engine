import os
import logging
from dotenv import load_dotenv

# .env-Datei laden
load_dotenv()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Konfigurationseinstellungen
class Config:
    DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'defaultsecretkey_change_this_in_production')
    PORT = int(os.environ.get('PORT', 5560))
    RESULTS_PER_PAGE = int(os.environ.get('RESULTS_PER_PAGE', 10))
    
    # API-Schlüssel
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    GOOGLE_CX = os.environ.get('GOOGLE_CX')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', os.environ.get('GOOGLE_GENAI_API_KEY'))
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# Funktionen zum Lesen und Aktualisieren der .env-Datei
def get_env_variables():
    """Reads values from the .env file"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    env_vars = {}
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars

def update_env_file(updates):
    """Updates the .env file with new values"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    
    # Read current environment variables from the file
    current_env = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            current_env = f.readlines()
    
    # Create a map for easy access to current values
    updated_lines = []
    updated_keys = set()
    
    # Update existing lines
    for line in current_env:
        line = line.rstrip('\n')
        # Keep comments and empty lines
        if not line or line.startswith('#'):
            updated_lines.append(line)
            continue
            
        if '=' in line:
            key = line.split('=', 1)[0].strip()
            if key in updates:
                updated_lines.append(f"{key}={updates[key]}")
                updated_keys.add(key)
            else:
                updated_lines.append(line)
    
    # Add new values that are not already in the file
    for key, value in updates.items():
        if key not in updated_keys:
            updated_lines.append(f"{key}={value}")
    
    # Write the file back with updated values
    with open(env_path, 'w') as f:
        for line in updated_lines:
            f.write(line + '\n')
