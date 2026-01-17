import { NextRequest, NextResponse } from "next/server";
import { GoogleGenerativeAI } from "@google/generative-ai";

// Initialize Gemini AI
const genAI = process.env.GEMINI_API_KEY 
  ? new GoogleGenerativeAI(process.env.GEMINI_API_KEY)
  : null;

interface SearchResult {
  title: string;
  link: string;
  snippet: string;
  displayLink: string;
}

// Google Custom Search API
async function googleSearch(query: string, location?: string): Promise<SearchResult[]> {
  const apiKey = process.env.GOOGLE_API_KEY;
  const cx = process.env.GOOGLE_CX;

  if (!apiKey || !cx) {
    console.warn("Google API credentials not configured, returning mock results");
    return getMockResults(query);
  }

  try {
    // Add location context to query if available
    const enhancedQuery = location && location !== "Standort nicht verfügbar" 
      ? `${query} near ${location}`
      : query;

    const url = `https://www.googleapis.com/customsearch/v1?key=${apiKey}&cx=${cx}&q=${encodeURIComponent(enhancedQuery)}&num=10`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Google API error: ${response.status}`);
    }

    const data = await response.json();
    
    if (!data.items) {
      return [];
    }

    return data.items.map((item: {
      title: string;
      link: string;
      snippet?: string;
      displayLink?: string;
    }) => ({
      title: item.title,
      link: item.link,
      snippet: item.snippet || "",
      displayLink: item.displayLink || new URL(item.link).hostname,
    }));
  } catch (error) {
    console.error("Google search error:", error);
    return getMockResults(query);
  }
}

// Generate AI answer using Gemini
async function generateAIAnswer(query: string, context: SearchResult[]): Promise<string> {
  if (!genAI) {
    return `Basierend auf Ihrer Suchanfrage "${query}" habe ich relevante Informationen gefunden. Die Ergebnisse unten bieten detaillierte Informationen zu Ihrem Thema.`;
  }

  try {
    const model = genAI.getGenerativeModel({ model: "gemini-pro" });
    
    const contextText = context
      .slice(0, 3)
      .map((r) => `${r.title}: ${r.snippet}`)
      .join("\n\n");

    const prompt = `Beantworte die folgende Frage präzise und informativ auf Deutsch. Nutze den folgenden Kontext aus den Suchergebnissen:

Frage: ${query}

Kontext aus Suchergebnissen:
${contextText}

Gib eine klare, prägnante Antwort in 2-4 Sätzen. Sei sachlich und hilfreich.`;

    const result = await model.generateContent(prompt);
    const response = await result.response;
    return response.text();
  } catch (error) {
    console.error("AI answer generation error:", error);
    return `Basierend auf Ihrer Suchanfrage "${query}" habe ich relevante Informationen gefunden. Die Ergebnisse unten bieten detaillierte Informationen zu Ihrem Thema.`;
  }
}

// Mock results for testing without API keys
function getMockResults(query: string): SearchResult[] {
  const mockData = [
    {
      title: `${query} - Wikipedia`,
      link: `https://de.wikipedia.org/wiki/${encodeURIComponent(query)}`,
      snippet: `${query} ist ein umfassendes Thema mit vielen Aspekten. Dieser Artikel bietet einen detaillierten Überblick über die wichtigsten Informationen und historischen Hintergründe.`,
      displayLink: "de.wikipedia.org",
    },
    {
      title: `Alles über ${query} | Fachportal`,
      link: `https://example.com/${encodeURIComponent(query)}`,
      snippet: `Entdecken Sie umfassende Informationen zu ${query}. Unser Portal bietet Expertenwissen, aktuelle Entwicklungen und praktische Tipps für Einsteiger und Fortgeschrittene.`,
      displayLink: "example.com",
    },
    {
      title: `${query}: Aktuelle News und Trends 2026`,
      link: `https://news.example.com/${encodeURIComponent(query)}`,
      snippet: `Die neuesten Nachrichten und Entwicklungen zu ${query}. Bleiben Sie auf dem Laufenden mit unseren täglichen Updates und Expertenanalysen.`,
      displayLink: "news.example.com",
    },
    {
      title: `${query} - Ratgeber und Tipps`,
      link: `https://ratgeber.example.com/${encodeURIComponent(query)}`,
      snippet: `Praktische Tipps und Tricks zu ${query}. Unser Ratgeber hilft Ihnen, das Beste aus Ihrem Interesse zu machen und häufige Fehler zu vermeiden.`,
      displayLink: "ratgeber.example.com",
    },
    {
      title: `Forum: ${query} Diskussion`,
      link: `https://forum.example.com/${encodeURIComponent(query)}`,
      snippet: `Tauschen Sie sich mit anderen Interessierten über ${query} aus. Stellen Sie Fragen, teilen Sie Erfahrungen und lernen Sie von der Community.`,
      displayLink: "forum.example.com",
    },
  ];

  return mockData;
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const query = searchParams.get("q");
    const aiMode = searchParams.get("ai") === "true";
    const location = searchParams.get("location") || "";

    if (!query) {
      return NextResponse.json(
        { error: "Query parameter is required" },
        { status: 400 }
      );
    }

    // Perform search
    const results = await googleSearch(query, location);

    // Generate AI answer if requested
    let aiAnswer = null;
    if (aiMode && results.length > 0) {
      const answer = await generateAIAnswer(query, results);
      aiAnswer = {
        answer,
        sources: results.slice(0, 3).map((r) => r.link),
      };
    }

    return NextResponse.json({
      query,
      results,
      aiAnswer,
      location,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("Search API error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
