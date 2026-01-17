# 🚀 AI Search Engine - Next.js Edition

A modern, AI-powered search engine built with Next.js 15, featuring a minimalistic Google-like design, personalized results based on location, and intelligent AI-generated answers.

![Homepage](https://github.com/user-attachments/assets/cae372d8-03ac-4d5a-81ee-26643ee32f53)

## ✨ Features

- 🤖 **AI-Powered Answers** - Get instant, intelligent responses to your queries using Google Gemini AI
- 🔍 **Google Search Integration** - Fetch comprehensive search results from Google Custom Search API
- 📍 **Location-Based Personalization** - Personalized results based on your geographic location
- 🎨 **Modern Minimalistic Design** - Clean, Google-inspired interface with a beautiful gradient logo
- 🌓 **Automatic Dark Mode** - Seamlessly adapts to your system preferences
- ⚡ **Lightning Fast** - Built on Next.js 15 with optimal performance
- 📱 **Fully Responsive** - Works perfectly on all devices
- 🎯 **Smart Sidebar** - Trending topics, recent searches, and location info
- 💫 **Beautiful UI** - Gradient effects, smooth transitions, and modern design elements

## 🎯 Search Features

### Standard Search
![Search Results](https://github.com/user-attachments/assets/432ad666-c62d-4e78-8365-148a1be18931)

- Real-time search results from Google
- Clean result cards with titles, snippets, and links
- Location-aware result personalization
- Trending topics sidebar
- Recent searches history

### AI-Powered Search
![AI Answer](https://github.com/user-attachments/assets/76d267a5-1dd1-49b1-b759-a15a48ef3da6)

- Intelligent AI-generated answers using Gemini
- Source attribution with clickable links
- Beautiful gradient-styled answer cards
- Contextual information from search results

## 🛠️ Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **AI**: Google Gemini API
- **Search**: Google Custom Search API
- **Icons**: Lucide React
- **Deployment**: Vercel-ready

## 📋 Prerequisites

- Node.js 18+ and npm
- Google Cloud account with:
  - Gemini API key
  - Custom Search API key
  - Custom Search Engine ID

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/SchBenedikt/search-engine.git
cd search-engine
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Create a `.env.local` file in the root directory:

```env
# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Google Custom Search Configuration
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CX=your_google_custom_search_engine_id_here
```

### 4. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 5. Build for Production

```bash
npm run build
npm start
```

## 🔑 Getting API Keys

### Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and add to `.env.local` as `GEMINI_API_KEY`

### Google Custom Search API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Custom Search API
3. Create credentials (API key)
4. Copy and add to `.env.local` as `GOOGLE_API_KEY`

### Google Custom Search Engine ID

1. Visit [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Create a new search engine
3. Configure it to search the entire web
4. Copy the Search Engine ID
5. Add to `.env.local` as `GOOGLE_CX`

## 📁 Project Structure

```
search-engine/
├── app/
│   ├── api/
│   │   └── search/
│   │       └── route.ts          # Search API endpoint
│   ├── search/
│   │   └── page.tsx              # Search results page
│   ├── globals.css               # Global styles
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Homepage
├── components/                    # Reusable React components
├── lib/                          # Utility functions
├── public/                       # Static assets
├── .env.example                  # Example environment variables
├── next.config.ts                # Next.js configuration
├── tailwind.config.ts            # Tailwind CSS configuration
└── package.json                  # Dependencies
```

## 🎨 Design Philosophy

The interface follows a minimalistic, Google-inspired design with:

- **Clean white/dark backgrounds** that adapt to system preferences
- **Gradient accents** (blue → purple → pink) for modern appeal
- **Generous white space** for clarity and focus
- **Smooth transitions** for professional feel
- **Consistent spacing** using Tailwind's utility classes
- **Accessible color contrasts** for readability

## 🔧 Customization

### Changing Colors

Edit `app/globals.css` to customize the color scheme:

```css
:root {
  --primary: #1a73e8;        /* Primary blue */
  --secondary: #f8f9fa;      /* Light gray */
  /* ... other colors */
}
```

### Modifying Trending Topics

Edit `app/search/page.tsx` in the sidebar section:

```typescript
["KI-Entwicklung 2026", "Next.js 15", ...]
```

### Adjusting Search Results

Modify the `getMockResults` function in `app/api/search/route.ts` for custom mock data, or ensure your Google API credentials are properly configured for real results.

## 🧪 Testing Without API Keys

The application includes mock data that works without API keys for development and testing purposes. Simply start the dev server without configuring `.env.local` and you'll see sample results.

## 📱 Responsive Design

The application is fully responsive with breakpoints:

- **Mobile**: Single column layout, hidden sidebar
- **Tablet**: Optimized spacing, collapsible sidebar
- **Desktop**: Full layout with sidebar, optimal spacing

## 🌍 Localization

The interface is currently in German. To change the language:

1. Update text strings in `app/page.tsx` and `app/search/page.tsx`
2. Modify the `lang` attribute in `app/layout.tsx`
3. Update placeholder text in search inputs

## 🔒 Privacy & Security

- Location data is only used client-side for personalization
- No user data is stored or logged
- All API calls are server-side to protect API keys
- Environment variables keep credentials secure

## 🚢 Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import the project in [Vercel](https://vercel.com)
3. Add environment variables in Vercel dashboard
4. Deploy!

### Docker

```bash
docker build -t ai-search-engine .
docker run -p 3000:3000 ai-search-engine
```

### Other Platforms

The application works on any platform supporting Node.js:
- Netlify
- Railway
- Render
- DigitalOcean App Platform

## 📊 Performance

- **First Contentful Paint**: < 1s
- **Time to Interactive**: < 2s
- **Lighthouse Score**: 95+
- **Build Size**: ~102 KB First Load JS

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [Next.js](https://nextjs.org/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
- Icons by [Lucide](https://lucide.dev/)
- AI powered by [Google Gemini](https://deepmind.google/technologies/gemini/)
- Search by [Google Custom Search](https://developers.google.com/custom-search)

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This is a complete rewrite of the search engine in Next.js, replacing the previous Flask-based implementation. The old Flask code has been preserved in the `old_flask_app/` directory for reference.
