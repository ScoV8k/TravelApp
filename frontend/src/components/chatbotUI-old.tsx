"use client"

import { useState } from "react";

export const ChatBotUi = () => {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await fetch("http://127.0.0.1:8001/generuj/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      const data = await response.json();

      const botMessage = { sender: "bot", text: data.response };
      setMessages((prev) => [...prev, userMessage, botMessage]);
    } catch (error) {
      console.error("Error:", error);
    }

    setInput("");
  };

  return (
    <div className="chat-bot-ui">
      <header className="header">
        <h1 className="title">Ask our AI anything</h1>
      </header>

      <main className="chat-container">
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-message ${msg.sender}`}>
              {msg.text}
            </div>
          ))}
        </div>

        <div className="input-container">
          <input
            type="text"
            className="chat-input"
            placeholder="Ask me anything..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button className="send-button" onClick={sendMessage}>
            ➤
          </button>
        </div>
      </main>
    </div>
  );
};
