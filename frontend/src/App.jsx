
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  // Send message to backend
  async function handleSend() {
    if (!question.trim() || loading) return;

    const userQuestion = question.trim();

    setMessages((prev) => [
      ...prev,
      { role: "user", text: userQuestion }
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(
        "https://ai-resume-chatbot-1fl7.onrender.com/chat",
        // "http://127.0.0.1:8001/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            question: userQuestion
          })
        }
      );

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      // Create empty assistant message
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "" }
      ]);

      // Read streaming response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        const chunk = decoder.decode(value, {
          stream: true
        });

        setMessages((prev) => {
          const updated = [...prev];
          const lastIndex = updated.length - 1;

          updated[lastIndex] = {
            ...updated[lastIndex],
            text: updated[lastIndex].text + chunk
          };

          return updated;
        });
      }

      // Process remaining decoded text
      const remaining = decoder.decode();

      if (remaining) {
        setMessages((prev) => {
          const updated = [...prev];
          const lastIndex = updated.length - 1;

          updated[lastIndex] = {
            ...updated[lastIndex],
            text: updated[lastIndex].text + remaining
          };

          return updated;
        });
      }

    } catch (error) {
      console.error("Chat error:", error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Sorry, something went wrong. Please try again."
        }
      ]);

    } finally {
      setLoading(false);
    }
  }

  // Suggested questions
  const suggestions = [
    "What are your technical skills?",
    "Tell me about your projects.",
    "What is your educational background?",
    "Why should we hire you?"
  ];

  return (
    <div className="app">

      {/* Navbar */}
      <header className="navbar">
        <h2>Rani AI Resume</h2>
        <span>AI Assistant</span>
      </header>

      {/* Main Chat Container */}
      <main className="chat-container">

        {/* Welcome Section */}
        <div className="welcome">
          <h1>Hi, I'm Rani AI Assistant 👋</h1>

          <p>
            Ask me anything about Rani skills,
            education and projects.
          </p>

          {/* Suggested Questions */}
          {messages.length === 0 && (
            <div className="suggested-questions">

              {suggestions.map((item, index) => (
                <button
                  key={index}
                  onClick={() => setQuestion(item)}
                >
                  {item}
                </button>
              ))}

            </div>
          )}
        </div>

        {/* Chat Messages */}
        <div className="messages">

          {messages.map((msg, index) => (
            <div
              key={index}
              className={
                msg.role === "user"
                  ? "user-message"
                  : "assistant-message"
              }
            >
              {msg.role === "assistant" ? (
                <ReactMarkdown>
                  {msg.text}
                </ReactMarkdown>
              ) : (
                msg.text
              )}
            </div>
          ))}

          {/* Loading Indicator */}
          {loading && (
            <div className="assistant-message typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}

        </div>

        {/* Input Area */}
        <div className="input-area">

          <input
            type="text"
            placeholder="Ask something about Rani..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleSend();
              }
            }}
          />

          <button
            onClick={handleSend}
            disabled={loading || !question.trim()}
          >
            {loading ? "Please wait..." : "Send"}
          </button>

        </div>

        {/* Footer */}
        <p className="footer">
          Powered by AI · FastAPI · Groq
        </p>

      </main>
    </div>
  );
}

export default App;
