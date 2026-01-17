"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";

export default function HomePage() {
  const [query, setQuery] = useState("");
  const router = useRouter();

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4">
        <div className="text-sm flex gap-4">
          <a href="#" className="hover:underline text-[var(--secondary-foreground)]">Über uns</a>
          <a href="#" className="hover:underline text-[var(--secondary-foreground)]">Einstellungen</a>
        </div>
        <div className="flex items-center gap-4">
          <button className="text-sm hover:underline text-[var(--secondary-foreground)]">
            Anmelden
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 -mt-20">
        {/* Logo */}
        <div className="mb-8">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            AI Search
          </h1>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="w-full max-w-2xl">
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-full opacity-0 group-hover:opacity-20 transition-opacity blur-xl"></div>
            <div className="relative flex items-center bg-[var(--card)] border border-[var(--border)] rounded-full px-6 py-4 shadow-lg hover:shadow-xl transition-shadow">
              <Search className="w-5 h-5 text-[var(--muted-foreground)] mr-3" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Suchen Sie nach allem..."
                className="flex-1 bg-transparent outline-none text-[var(--foreground)] placeholder:text-[var(--muted-foreground)]"
                autoFocus
              />
            </div>
          </div>

          {/* Search Buttons */}
          <div className="flex items-center justify-center gap-4 mt-8">
            <button
              type="submit"
              className="px-6 py-3 bg-[var(--secondary)] hover:bg-[var(--border)] text-[var(--foreground)] rounded-lg transition-colors text-sm font-medium"
            >
              Suchen
            </button>
            <button
              type="button"
              onClick={() => {
                if (query.trim()) {
                  router.push(`/search?q=${encodeURIComponent(query.trim())}&ai=true`);
                }
              }}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg transition-colors text-sm font-medium"
            >
              AI-Antwort
            </button>
          </div>
        </form>

        {/* Quick Links */}
        <div className="mt-16 text-center">
          <p className="text-sm text-[var(--muted-foreground)] mb-4">Beliebte Suchanfragen:</p>
          <div className="flex flex-wrap gap-2 justify-center max-w-2xl">
            {["Wetter heute", "Nachrichten", "Wikipedia", "Programmierung", "KI-Technologie"].map((term) => (
              <button
                key={term}
                onClick={() => {
                  setQuery(term);
                  router.push(`/search?q=${encodeURIComponent(term)}`);
                }}
                className="px-4 py-2 bg-[var(--secondary)] hover:bg-[var(--border)] rounded-full text-sm transition-colors"
              >
                {term}
              </button>
            ))}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-6 px-6 border-t border-[var(--border)]">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-[var(--muted-foreground)]">
          <div className="flex gap-6">
            <a href="#" className="hover:underline">Impressum</a>
            <a href="#" className="hover:underline">Datenschutz</a>
            <a href="#" className="hover:underline">Nutzungsbedingungen</a>
          </div>
          <div>
            © 2026 AI Search Engine
          </div>
        </div>
      </footer>
    </div>
  );
}
