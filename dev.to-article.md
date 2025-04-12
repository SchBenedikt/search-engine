Hello everyone,# Moderne Suchmaschine: Die nächste Generation mit KI, Wikipedia & mehrIch freue mich, euch die neuesten Funktionen und Verbesserungen meiner benutzerdefinierten Suchmaschine vorstellen zu können. Seit dem letzten Update wurden zahlreiche innovative Features implementiert, die das Nutzererlebnis entscheidend verbessern und die Suchmaschine zu einem noch mächtigeren Werkzeug machen.![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/yd3a10hjzvmhc8c38vt7.png)## 1. Google AI Integration: Leistungsstarke ZusammenfassungenDie größte Neuerung ist die Integration von **Google's Gemini AI** (gemini-2.0-flash) anstelle des zuvor verwendeten Llama-Modells. Die neue KI-Lösung bietet mehrere entscheidende Vorteile:- **Schnellere Antwortzeiten** durch optimierte Verarbeitung- **Quellenangaben für Informationen** - die KI gibt an, woher sie ihre Informationen bezieht- **Intelligente Zusammenfassungen** zu Suchanfragen, die automatisch in der ausgewählten Sprache erstellt werden```client = genai.Client(    api_key=os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_GENAI_API_KEY")))```Die KI-Antworten werden asynchron geladen, um die Suchgeschwindigkeit nicht zu beeinträchtigen, und bieten einen "Show more"-Button für längere Antworten.## 2. Wikipedia-Integration mit Knowledge PanelsEin weiteres Highlight ist die **automatische Erkennung von Entitäten** und die Anzeige relevanter Wikipedia-Informationen direkt neben den Suchergebnissen:- Automatische Erkennung von Begriffen, die potenzielle Entitäten sein könnten- Kompakte Zusammenfassungen des Wikipedia-Artikels- Passende Bilder, wenn verfügbar- Links zum vollständigen Wikipedia-Artikel

Diese Knowledge Panels erscheinen in der ausgewählten Sprache, mit direkten Links zu den entsprechenden Wikipedia-Sprachversionen (Deutsch, Englisch, Französisch, Spanisch, Italienisch).

![Knowledge Panel Beispiel](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/kox15wp7qbbmnoxpu9xn.png)

## 3. Website-Zusammenfassungen auf Abruf

Mit der neuen Vorschaufunktion können Nutzer jetzt:

- Durch **Rechtsklick auf ein Suchergebnis** eine kurze KI-generierte Zusammenfassung der Webseite anzeigen lassen
- Zeit sparen, indem sie den Inhalt einer Seite verstehen, ohne sie besuchen zu müssen
- Formatierte Markdown-Zusammenfassungen mit hervorgehobenen Schlüsselbegriffen erhalten

Die Zusammenfassungen werden intelligent erstellt: Falls der Inhalt nicht direkt zugänglich ist, analysiert die KI die URL-Struktur, um eine hilfreiche Kontextinformation zu liefern.

## 4. Google-Integration & hybride Suchergebnisse

Die Suchmaschine kombiniert jetzt intelligent eigene und Google-Suchergebnisse:

- **Automatische Mischung** der lokalen Datenbank mit Google-Ergebnissen im Verhältnis 2:3
- Deduplizierung, damit keine identischen Ergebnisse angezeigt werden
- Klare Kennzeichnung von Google-Ergebnissen mit einem "Google"-Badge
- Optimierte Balance zwischen lokalen und externen Ergebnissen

```python
ratio_google = 3
ratio_local = 2
```

Diese hybride Suche bietet eine beeindruckende Kombination aus eigenen indexierten Inhalten und der Breite von Google-Ergebnissen.

## 5. Verbesserte Landing Page & Benutzerfreundlichkeit

Das Design wurde grundlegend überarbeitet:

- **Moderne Landing Page** mit klarem, fokussiertem Design
- **Instrument Sans** als neue Standard-Schriftart für bessere Lesbarkeit
- **Automatische Spracherkennung** und Anpassung der Suchmaschine an die Benutzersprache
- Integration mit weiteren Suchmaschinen (Google, Bing, DuckDuckGo, Ecosia, Perplexity)

## 6. Automatische Spracherkennung & mehrsprachige Unterstützung

Die Suchmaschine unterstützt jetzt mehrere Sprachen vollständig:

- Benutzeroberfläche und Ergebnisse können in verschiedenen Sprachen angezeigt werden
- KI-Antworten und Zusammenfassungen werden automatisch in der gewählten Sprache generiert
- Wikipedia-Panels verlinken zur entsprechenden Sprachversion
- Sprachfilter für Suchergebnisse

## Wie die Suche technisch funktioniert

Die Suche arbeitet mit einem mehrschichtigen Ansatz:

1. **Lokale Datenbanksuche**: 
   - Abfrage der MongoDB-Datenbanken mit Textindizes
   - Normalisierung von URLs für Deduplizierung
   - Typerkennung und -filterung durch Synonymgruppen

2. **Google-Integration**:
   - Parallele Abfrage der Google Custom Search API
   - Intelligente Gewichtung und Mischung der Ergebnisse
   - Score-Boost für relevante Ergebnisse

3. **Ergebnisverarbeitung**:
   - Automatische Deduplizierung von URLs
   - Paginierung der Ergebnisse für bessere Performance
   - Lazy-Loading von Favicons für schnellere Anzeige

4. **KI-Unterstützung**:
   - Asynchrones Laden von KI-Antworten
   - Wikipedia-Entitätserkennung
   - Website-Zusammenfassungen auf Anfrage

Durch die Kombination dieser Technologien bietet die Suchmaschine eine leistungsstarke Alternative zu herkömmlichen Suchmaschinen mit praktischen KI-Features.

## Weitere Verbesserungen

- **Reaktionsschnelleres Interface** durch optimiertes Laden und serverseitige Verarbeitung
- **Verbesserte Einstellungsseite** zur Verwaltung mehrerer Datenbankverbindungen
- **Integrierte Vorschläge** und Autocompletion für Suchanfragen
- **Ergebnis-Paginierung** für bessere Navigation bei vielen Ergebnissen

{% embed https://github.com/SchBenedikt/search-engine %}

Was haltet ihr von den neuen Funktionen? Welche würdet ihr als nächstes sehen wollen? Lasst es mich in den Kommentaren wissen!

![Beispiel für die Suchoberfläche](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/obk7u92f8nb3toues4wn.png)