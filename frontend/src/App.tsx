import { useState } from "react";
import "./index.css";
import { ChatWindow, type Message } from "./ChatWindow";

// ─── Mock data returned by the dummy API ────────────────────────────────────
const MOCK_INITIAL_REPLY = (url: string): string =>
  `I've finished reviewing **${url}**. Here's a quick summary:\n\n` +
  `**Overall Score: 78 / 100**\n\n` +
  `Strengths:\n` +
  `• Clean semantic HTML structure\n` +
  `• Responsive layout detected\n` +
  `• HTTPS is enabled\n\n` +
  `Areas for improvement:\n` +
  `• Several images are missing alt text (accessibility)\n` +
  `• No meta description tag found\n` +
  `• Large JavaScript bundle detected — consider code splitting\n\n` +
  `Feel free to ask me anything about the results!`;

const MOCK_FOLLOW_UP = (userMsg: string): string =>
  `*(Simulated response to: "${userMsg}")*\n\nThis is placeholder output — real LLM responses will be wired in once the backend is connected. Stay tuned!`;

// ─── Main page ───────────────────────────────────────────────────────────────
export function App() {
  const [url, setUrl] = useState("");
  const [urlError, setUrlError] = useState("");
  const [phase, setPhase] = useState<"input" | "loading" | "chat">("input");
  const [messages, setMessages] = useState<Message[]>([]);

  const isValidUrl = (value: string) => {
    try {
      new URL(value.startsWith("http") ? value : `https://${value}`);
      return true;
    } catch {
      return false;
    }
  };

  const handleAnalyze = async () => {
    const trimmed = url.trim();
    if (!trimmed) {
      setUrlError("Please enter a website URL.");
      return;
    }
    if (!isValidUrl(trimmed)) {
      setUrlError("Please enter a valid URL (e.g. https://example.com).");
      return;
    }

    setUrlError("");
    setPhase("loading");

    // Call the dummy review API endpoint
    let reviewUrl = trimmed;
    try {
      const res = await fetch("/api/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: trimmed }),
      });
      const data = await res.json();
      reviewUrl = data.url ?? trimmed;
    } catch {
      // Server may not be running; fall through with mock data
    }

    setMessages([
      {
        id: "init-1",
        role: "assistant",
        content: MOCK_INITIAL_REPLY(reviewUrl),
        timestamp: new Date(),
      },
    ]);
    setPhase("chat");
  };

  const handleSend = (content: string) => {
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content,
      timestamp: new Date(),
    };
    const assistantMsg: Message = {
      id: `ai-${Date.now() + 1}`,
      role: "assistant",
      content: MOCK_FOLLOW_UP(content),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg, assistantMsg]);
  };

  const handleReset = () => {
    setUrl("");
    setUrlError("");
    setPhase("input");
    setMessages([]);
  };

  return (
    <div className="min-h-screen flex flex-col items-center bg-[#242424] px-4 py-10 relative overflow-hidden">
      {/* Subtle background glow */}
      <div className="pointer-events-none fixed inset-0 z-0">
        <div className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-violet-700/10 blur-[120px]" />
      </div>

      {/* ── Header ── */}
      <header className="z-10 text-center mb-10">
        <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
          WebSight
        </h1>
        <p className="text-white/50 mt-2 text-sm">
          Paste any website URL and let the AI review it for you
        </p>
      </header>

      {/* ── URL input card ── */}
      <div className="z-10 w-full max-w-2xl">
        <div className="bg-[#1c1c1e] border border-white/10 rounded-2xl p-6 shadow-xl">
          <label className="block text-sm font-medium text-white/70 mb-2">
            Website URL
          </label>
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30 text-sm select-none">
                🔗
              </span>
              <input
                type="text"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  if (urlError) setUrlError("");
                }}
                onKeyDown={(e) => e.key === "Enter" && phase === "input" && handleAnalyze()}
                placeholder="https://example.com"
                disabled={phase !== "input"}
                className="w-full bg-[#111] border border-white/15 rounded-xl pl-9 pr-4 py-3 text-sm text-white placeholder-white/25 outline-none focus:border-violet-500 transition-colors disabled:opacity-50"
              />
            </div>
            {phase === "input" && (
              <button
                onClick={handleAnalyze}
                className="bg-violet-600 hover:bg-violet-500 text-white px-6 py-3 rounded-xl text-sm font-semibold transition-colors whitespace-nowrap"
              >
                Analyze
              </button>
            )}
            {phase === "chat" && (
              <button
                onClick={handleReset}
                className="bg-[#2a2a2a] hover:bg-[#333] border border-white/10 text-white/70 px-5 py-3 rounded-xl text-sm font-semibold transition-colors whitespace-nowrap"
              >
                New URL
              </button>
            )}
          </div>
          {urlError && (
            <p className="text-red-400 text-xs mt-2">{urlError}</p>
          )}
        </div>

        {/* ── Loading state ── */}
        {phase === "loading" && (
          <div className="mt-6 bg-[#1c1c1e] border border-white/10 rounded-2xl p-8 flex flex-col items-center gap-4 shadow-xl">
            <div className="w-10 h-10 rounded-full border-2 border-violet-500 border-t-transparent animate-spin" />
            <div className="text-center">
              <p className="text-white/80 font-medium text-sm">Analyzing website…</p>
              <p className="text-white/40 text-xs mt-1">Calling review API for {url}</p>
            </div>
          </div>
        )}

        {/* ── Chat panel ── */}
        {phase === "chat" && (
          <div className="mt-6 bg-[#1c1c1e] border border-white/10 rounded-2xl shadow-xl flex flex-col overflow-hidden"
               style={{ height: "520px" }}>
            {/* Chat header */}
            <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10 bg-[#1a1a1c]">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-[0_0_6px_#34d399]" />
              <span className="text-sm font-medium text-white/80">
                WebSight AI — reviewing{" "}
                <span className="text-violet-400 truncate max-w-[300px] inline-block align-bottom">
                  {url}
                </span>
              </span>
            </div>

            {/* Chat body */}
            <ChatWindow messages={messages} onSend={handleSend} />
          </div>
        )}
      </div>

      {/* ── Footer ── */}
      <footer className="z-10 mt-auto pt-10 text-white/20 text-xs text-center">
        Visual prototype — no real API calls or LLM yet
      </footer>
    </div>
  );
}

export default App;
