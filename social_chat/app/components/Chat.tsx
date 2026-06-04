"use client";

import { useState, useRef, useEffect } from "react";
import { Send, User, Bot, Loader2, Info, Upload, CheckCircle2 } from "lucide-react";

interface Source {
  platform: string;
  date: string;
  excerpt: string;
  source_file: string;
  relevance_score: number;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! Ask me anything about the ingested social data.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setMessages((prev) => [
      ...prev,
      { role: "user", content: `Uploaded file: ${file.name}` }
    ]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `✅ ${data.message} It will be available for search in a few moments once embedding finishes.` }
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "❌ Failed to upload file." }
      ]);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage.content }),
      });

      if (!res.ok) {
        throw new Error("Failed to fetch response");
      }

      const data = await res.json();
      const assistantMessage: Message = {
        role: "assistant",
        content: data.answer,
        sources: data.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error connecting to the backend. Make sure the FastAPI server is running." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[80vh] w-full max-w-4xl mx-auto bg-white border border-gray-300 rounded-lg shadow-sm overflow-hidden text-black">
      {/* Header */}
      <div className="p-4 border-b border-gray-300 bg-gray-50 flex flex-col gap-1">
        <h2 className="text-lg font-bold text-black flex items-center gap-2">
          <Bot className="w-5 h-5 text-black" />
          Social Knowledge Base
        </h2>

      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-white">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
              msg.role === "user" ? "bg-black" : "bg-gray-200"
            }`}>
              {msg.role === "user" ? <User size={16} className="text-white"/> : <Bot size={16} className="text-black"/>}
            </div>
            
            <div className={`flex flex-col max-w-[80%] ${msg.role === "user" ? "items-end" : "items-start"}`}>
              <div className={`p-3 rounded-lg text-sm leading-relaxed ${
                msg.role === "user" 
                  ? "bg-black text-white" 
                  : "bg-gray-100 text-black border border-gray-200"
              }`}>
                {msg.content}
              </div>

              {/* Citations / Sources */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 space-y-2 w-full">
                  <div className="text-xs font-bold text-gray-500 flex items-center gap-1">
                    <Info size={12} /> Sources Cited:
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {msg.sources.map((src, i) => (
                      <div key={i} className="group relative">
                        <div className="bg-gray-50 border border-gray-300 rounded-md px-2 py-1 text-xs text-gray-700 cursor-help hover:bg-gray-200 transition-colors">
                          <span className="font-bold text-black">[{i + 1}]</span> {src.platform} &bull; {src.date ? src.date.split('T')[0] : 'Unknown'}
                        </div>
                        {/* Tooltip on hover */}
                        <div className="absolute bottom-full mb-1 left-0 w-64 p-2 bg-black border border-gray-800 rounded-md text-xs text-white opacity-0 group-hover:opacity-100 transition-opacity z-10 pointer-events-none shadow-lg">
                          <div className="font-bold text-gray-300 mb-1">Excerpt:</div>
                          <p className="italic">"{src.excerpt}"</p>
                          <div className="mt-1 text-gray-400 text-[10px]">File: {src.source_file}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center shrink-0">
              <Bot size={16} className="text-black"/>
            </div>
            <div className="p-3 rounded-lg bg-gray-100 border border-gray-200">
              <Loader2 className="w-4 h-4 text-black animate-spin" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-gray-50 border-t border-gray-300">
        <form onSubmit={handleSubmit} className="relative flex items-center gap-2">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            className="hidden"
            accept=".csv,.json,.html"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading || isLoading}
            className="p-3 bg-gray-200 hover:bg-gray-300 text-black rounded-md transition-colors disabled:opacity-50 flex-shrink-0"
            title="Upload Data Export"
          >
            {isUploading ? <Loader2 size={18} className="animate-spin" /> : <Upload size={18} />}
          </button>
          
          <div className="relative flex-1">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your social data..."
              className="w-full bg-white border border-gray-300 rounded-md py-3 pl-4 pr-12 text-sm text-black placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-black transition-all"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-black hover:bg-gray-800 text-white rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={16} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
