"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useState, useEffect, Suspense, useCallback } from "react";
import { Search, MapPin, Clock, TrendingUp, Sparkles, ExternalLink } from "lucide-react";
import Link from "next/link";

interface SearchResult {
  title: string;
  link: string;
  snippet: string;
  displayLink: string;
}

interface AIAnswer {
  answer: string;
  sources: string[];
}

function SearchPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const query = searchParams.get("q") || "";
  const aiMode = searchParams.get("ai") === "true";
  
  const [searchQuery, setSearchQuery] = useState(query);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [aiAnswer, setAiAnswer] = useState<AIAnswer | null>(null);
  const [loading, setLoading] = useState(true);
  const [userLocation, setUserLocation] = useState<string>("");

  useEffect(() => {
    // Get user location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation(`${position.coords.latitude.toFixed(2)}, ${position.coords.longitude.toFixed(2)}`);
        },
        () => {
          setUserLocation("Standort nicht verfügbar");
        }
      );
    }
  }, []);

  const performSearch = useCallback(async (searchQuery: string, withAI: boolean) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(searchQuery)}&ai=${withAI}&location=${encodeURIComponent(userLocation)}`);
      const data = await response.json();
      
      if (data.results) {
        setResults(data.results);
      }
      if (data.aiAnswer) {
        setAiAnswer(data.aiAnswer);
      }
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setLoading(false);
    }
  }, [userLocation]);

  useEffect(() => {
    if (query) {
      performSearch(query, aiMode);
    }
  }, [query, aiMode, performSearch]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[var(--background)]">
      {/* Header with Search */}
      <header className="sticky top-0 z-50 bg-[var(--background)] border-b border-[var(--border)] shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center gap-6">
            {/* Logo */}
            <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent whitespace-nowrap">
              AI Search
            </Link>

            {/* Search Bar */}
            <form onSubmit={handleSearch} className="flex-1 max-w-3xl">
              <div className="relative flex items-center bg-[var(--card)] border border-[var(--border)] rounded-full px-4 py-2 hover:shadow-md transition-shadow">
                <Search className="w-4 h-4 text-[var(--muted-foreground)] mr-3" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Suchen..."
                  className="flex-1 bg-transparent outline-none text-[var(--foreground)] text-sm"
                />
              </div>
            </form>

            {/* Nav Items */}
            <div className="hidden md:flex items-center gap-4">
              <button className="text-sm text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors">
                Einstellungen
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
        <div className="flex gap-6">
          {/* Main Results */}
          <main className="flex-1 min-w-0">
            {/* Search Info */}
            <div className="mb-4 flex items-center gap-4 text-sm text-[var(--muted-foreground)]">
              <span>Ergebnisse für: <strong className="text-[var(--foreground)]">{query}</strong></span>
              {userLocation && (
                <span className="flex items-center gap-1">
                  <MapPin className="w-3 h-3" />
                  {userLocation}
                </span>
              )}
            </div>

            {/* AI Answer */}
            {aiAnswer && (
              <div className="mb-6 p-6 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30 rounded-xl border border-[var(--border)]">
                <div className="flex items-start gap-3 mb-3">
                  <Sparkles className="w-5 h-5 text-purple-600 mt-1" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-2">KI-Antwort</h3>
                    <p className="text-[var(--foreground)] leading-relaxed">{aiAnswer.answer}</p>
                  </div>
                </div>
                {aiAnswer.sources.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-[var(--border)]">
                    <p className="text-xs text-[var(--muted-foreground)] mb-2">Quellen:</p>
                    <div className="flex flex-wrap gap-2">
                      {aiAnswer.sources.map((source, idx) => (
                        <a
                          key={idx}
                          href={source}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline"
                        >
                          Quelle {idx + 1}
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Loading State */}
            {loading && (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-[var(--muted)] rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-[var(--muted)] rounded w-1/2 mb-2"></div>
                    <div className="h-3 bg-[var(--muted)] rounded w-full"></div>
                  </div>
                ))}
              </div>
            )}

            {/* Search Results */}
            {!loading && results.length > 0 && (
              <div className="space-y-6">
                {results.map((result, idx) => (
                  <article key={idx} className="group">
                    <div className="mb-1">
                      <a
                        href={result.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-sm text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
                      >
                        <span>{result.displayLink}</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                    <h2 className="mb-2">
                      <a
                        href={result.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xl text-blue-600 hover:underline group-hover:text-blue-700 transition-colors"
                      >
                        {result.title}
                      </a>
                    </h2>
                    <p className="text-sm text-[var(--foreground)] leading-relaxed">
                      {result.snippet}
                    </p>
                  </article>
                ))}
              </div>
            )}

            {/* No Results */}
            {!loading && results.length === 0 && (
              <div className="text-center py-12">
                <p className="text-[var(--muted-foreground)]">
                  Keine Ergebnisse gefunden für &quot;{query}&quot;
                </p>
                <p className="text-sm text-[var(--muted-foreground)] mt-2">
                  Versuchen Sie es mit anderen Suchbegriffen
                </p>
              </div>
            )}
          </main>

          {/* Sidebar */}
          <aside className="hidden lg:block w-80 space-y-6">
            {/* Quick Info Card */}
            <div className="p-5 bg-[var(--card)] border border-[var(--border)] rounded-xl">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Trending
              </h3>
              <div className="space-y-3">
                {["KI-Entwicklung 2026", "Next.js 15", "Quantencomputer", "Klimawandel", "Raumfahrt"].map((term, idx) => (
                  <button
                    key={idx}
                    onClick={() => router.push(`/search?q=${encodeURIComponent(term)}`)}
                    className="block w-full text-left text-sm text-[var(--foreground)] hover:text-blue-600 transition-colors"
                  >
                    {idx + 1}. {term}
                  </button>
                ))}
              </div>
            </div>

            {/* Recent Searches */}
            <div className="p-5 bg-[var(--card)] border border-[var(--border)] rounded-xl">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Letzte Suchen
              </h3>
              <div className="space-y-2 text-sm text-[var(--muted-foreground)]">
                <p>Keine letzten Suchen</p>
              </div>
            </div>

            {/* Location Info */}
            {userLocation && (
              <div className="p-5 bg-[var(--card)] border border-[var(--border)] rounded-xl">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  Ihr Standort
                </h3>
                <p className="text-sm text-[var(--muted-foreground)]">{userLocation}</p>
                <p className="text-xs text-[var(--muted-foreground)] mt-2">
                  Wird für personalisierte Ergebnisse verwendet
                </p>
              </div>
            )}
          </aside>
        </div>
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Laden...</div>}>
      <SearchPageContent />
    </Suspense>
  );
}
