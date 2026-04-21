"use client";
import React, { useState } from "react";
import ReactMarkdown from "react-markdown";

async function fetchAIResponse(question: string) {
  try {
    const res = await fetch("http://localhost:8000/query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });

    const data = await res.json();
    return data.answer;
  } catch (err) {
    console.error(err);
    return "Oops! Something went wrong.";
  }
}

function ChatPage() {
  const [messages, setMessages] = useState<{ role: string; text: string }[]>(
    [],
  );
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message
    setMessages([...messages, { role: "user", text: input }]);
    setInput("");

    // Fetch AI response
    setMessages((prev) => [...prev, { role: "ai", text: "Typing..." }]);
    const aiResponse = await fetchAIResponse(input);
    setMessages((prev) => [
      ...prev.slice(0, -1), // remove "..."
      { role: "ai", text: aiResponse },
    ]);
  };

  return (
    <div className="flex flex-col h-screen bg-zinc-50 font-sans text-black">
      {/* Chat Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-white shadow-md">
        <h1 className="text-xl font-semibold">AI Cybersecurity Chat</h1>
        <span className="text-sm text-gray-500">
          {messages.length} messages
        </span>
      </div>

      {/* Messages Area */}
      <div className="flex-1 p-6 overflow-y-auto space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {msg.role === "ai" && (
              <div className="shrink-0 w-8 h-8 bg-[#1a2337] text-white rounded-full flex items-center justify-center text-xs font-bold">
                AI
              </div>
            )}
            <div
              className={`px-4 py-2 w-fit max-w-5xl rounded-lg ${
                msg.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 text-black"
              }`}
            >
              <ReactMarkdown>{msg.text}</ReactMarkdown>
            </div>
            {msg.role === "user" && (
              <div className="shrink-0 w-8 h-8 bg-[#1a2337] text-white rounded-full flex items-center justify-center text-xs font-bold">
                You
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Input Area */}
      <div className="flex items-center p-4 bg-white shadow-inner">
        <input
          type="text"
          className="flex-1 px-4 py-2 border rounded-l-md border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Type your question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded-r-md hover:bg-blue-600 transition-colors"
          onClick={handleSend}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatPage;
