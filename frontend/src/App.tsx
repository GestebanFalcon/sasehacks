import { useState, useRef } from "react";
import "./index.css";
import { ChatWindow, type Message } from "./ChatWindow";

type WsDataType = { error?: string, event?: string, [key: string]: any };

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
  const wsRef = useRef<WebSocket | null>(null)

  const isValidUrl = (value: string) => {
    try {
      new URL(value.startsWith("http") ? value : `https://${value}`);
      return true;
    } catch {
      return false;
    }
  };

  const postInit = async (trimmed: string) => {

    const res = await fetch(`http://localhost:8000/ask-deepseek?url=${url}`, {
      method: "POST"
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const data = await res.json();

    console.log(data);

    // Parse response body for content property
    // The backend returns { "success": true, "response": content }
    const responseContent = data.response || "No response content received";

    // Create new message with response content
    setMessages([
      {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: responseContent,
        timestamp: new Date(),
      },
    ]);
  }


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

    try {
      // Post to localhost:8000/ask-deepseek endpoint

      const ws = new WebSocket("ws://localhost:8000/chat");
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("opened n shi")
        ws.send(JSON.stringify({
          event: "init",
          url: trimmed
        }));
      }
      ws.onclose = (event) => {
        console.log(event.code);
        if (event) {
          throw new Error(`Websocket Error! - idk`);
        }
        console.log("closed n shi <3")
      }

      ws.onmessage = (message) => {
        const { event, error, ...data }: WsDataType = JSON.parse(message.data);
        if (error) {
          throw new Error(`Websocket Error! - ${error}`)
        }
        if (event == "init") {
          const { response }: { response?: string } = data;
          console.log(`Response received: ${response}`);
          if (!response) return; // impossible. for compiler

          setMessages([
            {
              id: `assistant-${Date.now()}`,
              role: "assistant",
              content: response,
              timestamp: new Date(),
            },
          ])
          setPhase("chat");
          //TODO: align with actual database message and send the full message data.
        }
        if (event == "new_message") {
          console.log("got new message")
          // if (messages.length < 1)
          // throw new Error("Logic Error! - New message without init, how did this happen!?")
          const { response }: { response?: string } = data;
          console.log(response);
          if (!response) return;
          setMessages((prev) => [...prev, {
            ...prev[0]!, //Fuck you it clearly exists i length checked. ts getting reworked anyways
            content: response,
            timestamp: new Date()
          }])
        }

      }

    } catch (error) {
      console.error("Error calling backend API:", error);
      // Fall back to mock data if backend call fails
      setMessages([
        {
          id: "init-1",
          role: "assistant",
          content: MOCK_INITIAL_REPLY(trimmed),
          timestamp: new Date(),
        },
      ]);
      setPhase("chat");
    }
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
    setMessages((prev) => [...prev, userMsg]);
    if (!wsRef.current) {
      setMessages((prev) => [...prev, assistantMsg]);
      return;
    }

    const ws = wsRef.current;
    ws.send(JSON.stringify({
      event: "re_prompt",
      data: content
    }));


  };

  const handleReset = () => {
    setUrl("");
    setUrlError("");
    setPhase("input");
    setMessages([]);
  };

  return (
    <div className="min-h-screen min-w-256 flex flex-col items-center bg-[#242424] px-4 py-10 relative overflow-hidden">
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
