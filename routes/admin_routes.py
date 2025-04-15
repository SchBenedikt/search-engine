from flask import render_template, request, jsonify
import json
import os
import logging
from config import get_env_variables, update_env_file
from database import get_db_config, save_db_config, get_type_synonyms

def init_admin_routes(app):
    """
    Initialisiert alle administrativen Routen für die Anwendung.
    """
    
    @app.route('/settings', methods=['GET'])
    def settings():
        type_synonyms = get_type_synonyms()
        # API-Konfigurationen aus der .env-Datei lesen
        env_vars = get_env_variables()
        
        # Übergibt die Synonyme und API-Konfigurationen an das Template
        return render_template('settings.html', 
                               type_synonyms=json.dumps(type_synonyms, indent=2),
                               google_api_key=env_vars.get('GOOGLE_API_KEY', ''),
                               google_cx=env_vars.get('GOOGLE_CX', ''),
                               gemini_api_key=env_vars.get('GEMINI_API_KEY', ''),
                               results_per_page=os.environ.get('RESULTS_PER_PAGE', '10'))
    
    @app.route('/save-settings', methods=['POST'])
    def save_settings():
        data = request.get_json()
        db_url = data.get('db_url')
        db_name = data.get('db_name', 'search_engine')
        db_username = data.get('db_username')
        db_password = data.get('db_password')
        
        # Extract API configurations from form data
        google_api_key = data.get('google_api_key', '')
        google_cx = data.get('google_cx', '')
        gemini_api_key = data.get('gemini_api_key', '')
        results_per_page = data.get('results_per_page', '10')
        
        # Save type synonyms if provided
        type_synonyms = data.get('type_synonyms')
        if type_synonyms:
            try:
                # Expects a valid JSON string
                parsed = json.loads(type_synonyms)
                with open('type_synonyms.json', 'w') as f:
                    json.dump(parsed, f)
            except Exception as e:
                logging.error(f"Error saving type synonyms: {e}")
                return jsonify({'success': False, 'message': 'Error saving type synonyms'})
        
        # Save API configurations to .env file
        try:
            env_updates = {}
            if google_api_key:
                env_updates['GOOGLE_API_KEY'] = google_api_key
            if google_cx:
                env_updates['GOOGLE_CX'] = google_cx
            if gemini_api_key:
                env_updates['GEMINI_API_KEY'] = gemini_api_key
            if results_per_page:
                env_updates['RESULTS_PER_PAGE'] = results_per_page
            
            # Update .env file
            if env_updates:
                update_env_file(env_updates)
                # Update current environment variables
                for key, value in env_updates.items():
                    os.environ[key] = value
        except Exception as e:
            logging.error(f"Error saving .env file: {e}")
            return jsonify({'success': False, 'message': f'Error saving .env file: {str(e)}'})
                
        if db_url:
            connections = get_db_config()
            connections.append({'url': db_url, 'name': db_name, 'username': db_username, 'password': db_password})
            save_db_config(connections)
            return jsonify({'success': True})
        return jsonify({'success': True})
    
    @app.route('/get-db-connections', methods=['GET'])
    def get_db_connections():
        connections = get_db_config()
        return jsonify({'connections': connections})
    
    @app.route('/delete-db-connection', methods=['POST'])
    def delete_db_connection():
        try:
            os.remove('db_config.json')
            logging.info('Deleted db_config.json file')
            return jsonify({'success': True})
        except FileNotFoundError:
            logging.warning('db_config.json file not found')
            return jsonify({'success': False, 'message': 'File not found'})
        except Exception as e:
            logging.error(f'Error deleting db_config.json file: {e}')
            return jsonify({'success': False, 'message': 'Error deleting file'})
    
    @app.route('/delete-db-connection/<int:index>', methods=['POST'])
    def delete_single_db_connection(index):
        try:
            connections = get_db_config()
            if 0 <= index < len(connections):
                removed = connections.pop(index)
                save_db_config(connections)
                logging.info(f"Removed connection: {removed}")
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'message': 'Index out of range'})
        except Exception as e:
            logging.error(f'Error deleting connection: {e}')
            return jsonify({'success': False, 'message': 'Internal error'})
