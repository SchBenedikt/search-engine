import logging
import time
from database import get_all_db_connections, get_type_synonyms
from utils.url_utils import normalize_url
from services.web_service import fetch_google_results

def search_databases(query, selected_type, selected_lang, page=1, per_page=10):
    """
    Sucht in allen verfügbaren Datenbanken nach Ergebnissen, die mit der Abfrage übereinstimmen.
    """
    start_time = time.time()
    results = []
    total_results = 0
    message = None

    try:
        dbs = get_all_db_connections()
        if not dbs:
            message = "No database connections available."
            return [], 0, time.time() - start_time, message

        # Merge categories from all DBs for type filtering
        synonyms = get_type_synonyms()
        consolidated = {}
        for db in dbs:
            all_types = db['meta_data'].distinct('type')
            for t in all_types:
                if t and t.strip() != '' and t.lower() != 'alle':
                    found = False
                    for canon, group in synonyms.items():
                        if t in group:
                            consolidated[canon] = group
                            found = True
                            break
                    if not found:
                        consolidated[t] = [t]
        categories = list(consolidated.keys())

        temp_results = []
        # Query each DB and merge results with total count
        for db in dbs:
            collection = db['meta_data']
            if query == "#all":
                base_filter = {"$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"url": {"$regex": query, "$options": "i"}}
                ]}
                if selected_type:
                    for canon, group in synonyms.items():
                        if selected_type in group:
                            selected_group = group
                            break
                    else:
                        selected_group = [selected_type]
                    base_filter = {"$and": [{"type": {"$in": selected_group}}, base_filter]}
                if selected_lang:
                    base_filter = {"$and": [{"page_language": selected_lang}, base_filter]}
                db_results = list(collection.find(base_filter))
                count = collection.count_documents(base_filter)
            elif query:
                search_query = {"$text": {"$search": query}}
                if selected_type:
                    for canon, group in synonyms.items():
                        if selected_type in group:
                            selected_group = group
                            break
                    else:
                        selected_group = [selected_type]
                    search_query = {"$and": [search_query, {"type": {"$in": selected_group}}]}
                if selected_lang:
                    search_query = {"$and": [search_query, {"page_language": selected_lang}]}
                count = collection.count_documents(search_query)
                db_results = list(collection.find(search_query, {"score": {"$meta": "textScore"}})
                                   .sort([("score", {"$meta": "textScore"})]))
            elif selected_type:
                for canon, group in synonyms.items():
                    if selected_type in group:
                        selected_group = group
                        break
                else:
                    selected_group = [selected_type]
                search_query = {"type": {"$in": selected_group}}
                if selected_lang:
                    search_query = {"$and": [search_query, {"page_language": selected_lang}]}
                count = collection.count_documents(search_query)
                db_results = list(collection.find(search_query))
            else:
                if selected_lang:
                    db_results = list(collection.aggregate([
                        {"$match": {"page_language": selected_lang}},
                        {"$sample": {"size": 10}}
                    ]))
                else:
                    db_results = list(collection.aggregate([{"$sample": {"size": 10}}]))
                count = len(db_results)

            total_results += count
            temp_results.extend(db_results)
        
        # Deduplicate results by normalized URL
        unique_results = []
        seen_urls = set()
        for item in temp_results:
            url = item.get("url")
            if url:
                normalized_url = normalize_url(url)
                if normalized_url and normalized_url not in seen_urls:
                    unique_results.append(item)
                    seen_urls.add(normalized_url)
        
        # If using text search, sort merged results by score
        if query:
            unique_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Fetch Google search results if query is provided (but not for #all)
        google_items = []
        if query and query != "#all":
            google_results = fetch_google_results(query)
            
            # Prepare Google results
            for idx, item in enumerate(google_results):
                url = item.get('link')
                if url:
                    normalized_url = normalize_url(url)
                    if normalized_url and normalized_url not in seen_urls:
                        # Less steep scaling of the score for better mixing
                        score_boost = 1000 - (idx * 10)  # Linear decrease from 1000
                        google_items.append({
                            'title': item.get('title'),
                            'url': url,
                            'description': item.get('snippet'),
                            'source': 'google',  # Markierung für Google-Ergebnisse
                            'score': score_boost
                        })
                        seen_urls.add(normalized_url)
        
        # Collect local results with their scores - with normalized URL check
        local_items = []
        
        for item in unique_results:
            url = item.get('url')
            if url:
                # URL was already normalized during the first deduplication
                # and is already included in seen_urls
                # Keep the original score but multiply by a factor
                score = item.get('score', 0) * 8
                local_items.append({
                    'title': item.get('title'),
                    'url': url,
                    'description': item.get('description', ''),
                    'source': 'local',
                    'score': score
                })
        
        # IMPROVED MIXING: Interleave Google and local results
        # But respect the scores - alternate top Google with top local results
        combined_results = []
        
        # Sort both lists by score
        google_items.sort(key=lambda x: x.get('score', 0), reverse=True)
        local_items.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Verbesserte Mischlogik: Priorisiert höhere Scores, wechselt aber Quellen ab,
        # um eine Blockbildung einer Quelle zu vermeiden, wenn die Scores sehr ähnlich sind.
        
        # Sortiere beide Listen nach Score
        google_items.sort(key=lambda x: x.get('score', 0), reverse=True)
        local_items.sort(key=lambda x: x.get('score', 0), reverse=True)

        google_idx, local_idx = 0, 0
        google_len, local_len = len(google_items), len(local_items)

        # Gewichtung für Google-Ergebnisse (z.B. 1.5 bedeutet, dass Google-Ergebnisse
        # tendenziell etwas höher gewichtet werden, wenn Scores nahe beieinander liegen)
        google_score_weight = 1.2

        while google_idx < google_len or local_idx < local_len:
            # Nächstes Google-Ergebnis und dessen Score (mit Gewichtung)
            google_score = (google_items[google_idx].get('score', 0) * google_score_weight
                            if google_idx < google_len else -1)
            
            # Nächstes lokales Ergebnis und dessen Score
            local_score = (local_items[local_idx].get('score', 0)
                           if local_idx < local_len else -1)

            # Wenn beide Listen noch Elemente haben
            if google_idx < google_len and local_idx < local_len:
                # Bevorzuge das Ergebnis mit dem höheren gewichteten Score
                if google_score >= local_score:
                    combined_results.append(google_items[google_idx])
                    google_idx += 1
                else:
                    combined_results.append(local_items[local_idx])
                    local_idx += 1
            # Wenn nur noch Google-Ergebnisse übrig sind
            elif google_idx < google_len:
                combined_results.append(google_items[google_idx])
                google_idx += 1
            # Wenn nur noch lokale Ergebnisse übrig sind
            elif local_idx < local_len:
                combined_results.append(local_items[local_idx])
                local_idx += 1
            else:
                # Sollte nicht passieren, aber als Absicherung
                break
        
        logging.info(f"Combined {len(combined_results)} results. Google items processed: {google_idx}, Local items processed: {local_idx}")

        # Aktualisiere die Gesamtanzahl der Ergebnisse
        total_results = len(combined_results)
        
        # Wende Paginierung an
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_results)
        
        # Sichere Indizes verwenden
        if start_idx < total_results:
            results = combined_results[start_idx:end_idx]
        else:
            results = []
    
    except Exception as e:
        logging.error(f'Search error: {e}')
        message = f"An error occurred during search: {str(e)}"
        results = []
        total_results = 0
    
    query_time = time.time() - start_time
    return results, total_results, query_time, message
