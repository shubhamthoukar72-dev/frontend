import { useEffect, useRef, useState } from "react";
import { Bot, MessageCircle, Send, Sparkles, X } from "lucide-react";
import { API_URL } from "../services/api";
import "./AIChatbot.css";

const welcomeMessage = {
  role: "assistant",
  content: "Hi! I can help with resumes, job searching, and interview preparation. What would you like help with?",
};

function AIChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([welcomeMessage]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");
  const conversationEndRef = useRef(null);

  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isOpen]);

  const sendMessage = async (event) => {
    event.preventDefault();
    const content = input.trim();
    if (!content || isSending) return;

    const conversation = [...messages, { role: "user", content }];
    const requestMessages = conversation
      .filter((message) => message !== welcomeMessage)
      .slice(-12);

    setMessages(conversation);
    setInput("");
    setIsSending(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/ai/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: requestMessages }),
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "The assistant could not respond.");
      }
      if (typeof data.reply !== "string" || !data.reply.trim()) {
        throw new Error("The assistant returned an empty response. Please try again.");
      }

      setMessages((current) => [
        ...current,
        { role: "assistant", content: data.reply },
      ]);
    } catch (sendError) {
      setError(sendError.message || "Unable to reach the assistant. Please try again.");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="ai-chatbot">
      {isOpen && (
        <section
          className="ai-chat-panel"
          aria-label="JobAI career assistant"
        >
          <header className="ai-chat-header">
            <div className="ai-chat-avatar"><Bot size={20} /></div>
            <div className="ai-chat-heading">
              <strong>JobAI Assistant</strong>
              <span><i /> AI career support</span>
            </div>
            <button
              type="button"
              className="ai-chat-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close chat"
            >
              <X size={19} />
            </button>
          </header>

          <div className="ai-chat-messages" role="log" aria-live="polite">
            {messages.map((message, index) => (
              <div
                className={`ai-chat-message ${message.role}`}
                key={`${message.role}-${index}`}
              >
                {message.content}
              </div>
            ))}
            {isSending && (
              <div className="ai-chat-message assistant ai-chat-typing" aria-label="Assistant is typing">
                <span /><span /><span />
              </div>
            )}
            <div ref={conversationEndRef} />
          </div>

          {error && <p className="ai-chat-error" role="alert">{error}</p>}

          <form className="ai-chat-form" onSubmit={sendMessage}>
            <label className="ai-chat-input-label" htmlFor="ai-chat-input">
              Message the JobAI assistant
            </label>
            <input
              id="ai-chat-input"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask a career question..."
              maxLength={2000}
              disabled={isSending}
            />
            <button
              type="submit"
              aria-label="Send message"
              disabled={!input.trim() || isSending}
            >
              <Send size={17} />
            </button>
          </form>
          <p className="ai-chat-disclaimer">AI responses can be inaccurate. Avoid sharing sensitive information.</p>
        </section>
      )}

      <button
        type="button"
        className={`ai-chat-toggle${isOpen ? " is-open" : ""}`}
        onClick={() => setIsOpen((open) => !open)}
        aria-label={isOpen ? "Close JobAI assistant" : "Open JobAI assistant"}
        aria-expanded={isOpen}
      >
        {isOpen ? <X size={23} /> : <MessageCircle size={23} />}
        {!isOpen && <span><Sparkles size={13} /> Ask AI</span>}
      </button>
    </div>
  );
}

export default AIChatbot;
