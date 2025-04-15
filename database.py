import json
import logging
from pymongo import MongoClient, TEXT

def get_db_config():
    """Lädt die Datenbankkonfiguration aus der Datei"""
    try:
        with open('db_config.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_db_config(connections):
    """Speichert die Datenbankkonfiguration in der Datei"""
    with open('db_config.json', 'w') as f:
        json.dump(connections, f)

def get_db_connection():
    """Erstellt eine Verbindung zur Datenbank mit den gespeicherten Konfigurationsdaten"""
    connections = get_db_config()
    if not connections:
        return None
    try:
        client = MongoClient(connections[0]['url'], username=connections[0].get('username'), password=connections[0].get('password'))
        db = client[connections[0]['name']]
        db['meta_data'].create_index([("title", TEXT), ("url", TEXT)])
        return db
    except Exception as e:
        logging.error(f'Error: {e}')
        return None

def get_all_db_connections():
    """Erstellt Verbindungen zu allen konfigurierten Datenbanken"""
    connections = get_db_config()
    dbs = []
    for conn in connections:
        try:
            client = MongoClient(conn['url'], username=conn.get('username'), password=conn.get('password'))
            db = client[conn['name']]
            db['meta_data'].create_index([("title", TEXT), ("url", TEXT)])
            dbs.append(db)
        except Exception as e:
            logging.error(f"Error connecting to {conn}: {e}")
    return dbs

def get_type_synonyms():
    """Lädt die Typ-Synonyme aus der Datei"""
    try:
        with open('type_synonyms.json', 'r') as f:
            return json.load(f)
    except Exception:
        return {}
