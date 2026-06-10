import { useState, useRef, useEffect } from "react";
import { MessageSquare, X, Send, Sparkles, Heart, Bot, HelpCircle, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { db } from "@/lib/db-store";

interface Message {
  role: "user" | "model";
  text: string;
}

const PRESETS = [
  "Explain what Arrhythmia means",
  "What is the QRS, PR, and QT interval?",
  "Suggest precautions for Tachycardia",
  "Explain heart attack risk factors"
];

export function AiAssistant() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "model",
      text: "Hello! I am CardioPredict AI, your cardiology explanation assistant. I can interpret heart disease predictions, explain complex ECG intervals, suggest cardiovascular precautions, or answer general cardiac health questions."
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;

    const newMsgs = [...messages, { role: "user" as const, text }];
    setMessages(newMsgs);
    setInput("");
    setLoading(true);

    const apiKey = import.meta.env.VITE_GEMINI_API_KEY;

    db.logQuery(
      `SELECT * FROM perplexity_agent_api WHERE prompt = '${text.substring(0, 30).replace(/'/g, "''")}...';`,
      "Invoked Perplexity Agent / Gemini AI Explainer"
    );

    if (!apiKey) {
      // Simulate responses if API Key is not loaded
      setTimeout(() => {
        let reply = "Here is a professional summary of your query regarding cardiovascular health:\n\n";
        if (text.toLowerCase().includes("arrhythmia")) {
          reply += "Arrhythmia refers to a group of conditions where the heartbeat is irregular, too fast (tachycardia), or too slow (bradycardia). It is caused by disturbances in the heart's electrical conduction system. In our DBMS records, a patient's QRS duration or PR interval can help flag potential conduction blocks.\n\nPrecautions: Limit caffeine/alcohol, monitor heart rate, and schedule an ECG review.";
        } else if (text.toLowerCase().includes("interval") || text.toLowerCase().includes("qrs")) {
          reply += "ECG waveforms contain critical intervals:\n- **QRS Duration**: Represents ventricular depolarization. Normal range is 0.08s - 0.10s. Prolonged QRS (>0.12s) can indicate bundle branch block.\n- **PR Interval**: Time from atrial depolarization to ventricular depolarization. Normal range is 0.12s - 0.20s.\n- **QT Interval**: Time for ventricular depolarization and repolarization. Normal is usually < 0.44s.";
        } else {
          reply += "Cardiovascular health is governed by blood pressure, cardiac output, and sinus rhythm. Please review your ECG analytics dashboard to monitor historical intervals and AI risk indices.\n\nPrecautions: Eat a heart-healthy diet, exercise regularly as directed, and avoid smoking.";
        }
        setMessages([...newMsgs, { role: "model" as const, text: reply }]);
        setLoading(false);
      }, 1000);
      return;
    }

    try {
      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [
              {
                parts: [
                  {
                    text: `You are CardioPredict AI, an advanced SaaS healthcare cardiology assistant. Analyze this inquiry professionally, provide patient-friendly summaries, explain heart disease (Arrhythmia, Tachycardia, Bradycardia, Atrial Fibrillation, Myocardial Infarction risk), interpret ECG parameters (QRS duration, PR interval, QT interval, heart rate) if asked, and outline clinical precautions.
                    
                    USER INQUIRY: "${text}"
                    
                    IMPORTANT CRITICAL RULE: Add this medical disclaimer at the absolute bottom of your response: "Disclaimer: This is an AI-generated educational assistant and not professional medical advice. Always consult a certified cardiologist for diagnostics."`
                  }
                ]
              }
            ]
          })
        }
      );

      const data = await response.json();
      const reply = data.candidates?.[0]?.content?.parts?.[0]?.text || "Unable to retrieve AI analysis. Please verify network settings.";
      setMessages([...newMsgs, { role: "model" as const, text: reply }]);
    } catch (err: any) {
      console.error(err);
      toast.error("Failed to query Gemini API");
      setMessages([
        ...newMsgs,
        {
          role: "model",
          text: "I encountered a communication error with the AI system. Please verify your connection or VITE_GEMINI_API_KEY in .env."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-5 right-5 z-40 pointer-events-auto">
      {/* Floating Chat Button */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="h-14 w-14 rounded-full gradient-primary text-primary-foreground shadow-glow flex items-center justify-center cursor-pointer hover:scale-105 transition-transform animate-ecg-pulse border border-primary/20 relative"
          title="Clinical AI Chatbot"
        >
          <Bot className="h-6 w-6" />
          <span className="absolute -top-1 -right-1 flex h-4 w-4">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00ff66] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-4 w-4 bg-[#00ff66] border-2 border-background text-[8px] font-bold text-black items-center justify-center">AI</span>
          </span>
        </button>
      )}

      {/* Glassmorphic Chat Window */}
      {open && (
        <div className="w-80 md:w-96 h-[480px] rounded-2xl border border-border bg-card/90 backdrop-blur-xl flex flex-col shadow-2xl overflow-hidden animate-fade-in-up">
          {/* Header */}
          <div className="gradient-primary p-4 flex items-center justify-between text-primary-foreground">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-white/20 flex items-center justify-center">
                <Heart className="h-4.5 w-4.5 text-white animate-pulse" />
              </div>
              <div>
                <div className="font-bold text-sm leading-tight flex items-center gap-1">
                  CardioPredict AI <Sparkles className="h-3 w-3 text-[#00ff66]" />
                </div>
                <div className="text-[10px] text-white/70">Google Gemini Explainer</div>
              </div>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="text-white/80 hover:text-white p-1 hover:bg-white/10 rounded-lg transition-colors cursor-pointer"
            >
              <X className="h-4.5 w-4.5" />
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-xl px-3.5 py-2 text-xs leading-relaxed whitespace-pre-wrap ${
                    m.role === "user"
                      ? "bg-primary text-primary-foreground rounded-tr-none shadow"
                      : "bg-muted text-foreground rounded-tl-none border border-border"
                  }`}
                >
                  {m.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-muted text-muted-foreground rounded-xl rounded-tl-none px-4 py-2 border border-border text-xs flex items-center gap-2">
                  <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
                  Analyzing clinical metrics...
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Quick Presets */}
          {messages.length === 1 && (
            <div className="px-4 py-2 border-t border-border bg-muted/40">
              <div className="text-[9px] uppercase tracking-wider text-muted-foreground font-semibold flex items-center gap-1 mb-1.5">
                <HelpCircle className="h-3 w-3" /> Quick Inquiries
              </div>
              <div className="flex flex-wrap gap-1.5">
                {PRESETS.map((p) => (
                  <button
                    key={p}
                    onClick={() => sendMessage(p)}
                    className="text-[10px] bg-card hover:bg-primary/10 hover:text-primary transition-colors border border-border px-2 py-1 rounded-md text-left text-muted-foreground cursor-pointer"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Warning Banner */}
          <div className="px-4 py-1.5 bg-yellow-500/10 dark:bg-yellow-500/5 text-[9px] text-yellow-600 dark:text-yellow-400 border-t border-border/50 text-center leading-normal">
            “AI assistant for educational purposes. Not clinical advice.”
          </div>

          {/* Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              sendMessage(input);
            }}
            className="p-3 border-t border-border bg-card/60 flex gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about ECG waveform, predictions..."
              className="flex-1 h-9 px-3 rounded-lg bg-background border border-input text-xs focus:outline-none focus:ring-2 focus:ring-ring text-foreground"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="h-9 w-9 rounded-lg gradient-primary text-primary-foreground shadow flex items-center justify-center disabled:opacity-60 cursor-pointer flex-shrink-0"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
