import { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const [serverUrl, setServerUrl] = useState('http://localhost:11434');
  const [modelName, setModelName] = useState('phi3_financial');

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(() => { scrollToBottom(); }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const baseUrl = serverUrl.replace(/\/$/, "");

    try {
      const response = await fetch(`${baseUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: modelName,
          messages: [...messages, userMessage],
          stream: false
        })
      });

      if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);
      
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.message.content }]);

    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Erreur de connexion sur ${baseUrl}. Vérifiez l'état du serveur.`,
        isError: true 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setMessages([]);
  };

  return (
    <div className="layout">
      {/* Sidebar épurée avec historique conservé */}
      <aside className="sidebar">
        <div className="sidebar-top">
          <div className="logo-area">
            <span className="logo-icon">💠</span> TechCorp
          </div>
          <button className="new-chat-btn" onClick={handleReset}>
            <span className="icon">＋</span> Nouvelle discussion
          </button>
        </div>

        <div className="sidebar-history">
          <h3 className="history-title">Récents</h3>
          <ul className="history-list">
            {/* Tâches issues du briefing de mission */}
            <li className="history-item">Analyse financière Q3</li>
            <li className="history-item">Test modèle médical exp...</li>
            <li className="history-item">Audit de sécurité infra</li>
          </ul>
        </div>
      </aside>

      <main className="main-content">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <h1 className="greeting">
              <span className="gradient-text">Bonjour, l'équipe.</span>
              <br />
              <span className="greeting-sub">Comment puis-je vous aider aujourd'hui ?</span>
            </h1>
          </div>
        ) : (
          <div className="messages-container">
            {messages.map((msg, index) => (
              <div key={index} className={`message-row ${msg.role}`}>
                <div className="avatar">
                  {msg.role === 'user' ? 'U' : '💠'}
                </div>
                <div className={`message-bubble ${msg.isError ? 'error-text' : ''}`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message-row assistant">
                <div className="avatar">💠</div>
                <div className="message-bubble typing">...</div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Barre de saisie style "Pill" (Bulle flottante) */}
        <div className="input-wrapper">
          <form onSubmit={handleSubmit} className="input-pill">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Demander à TechCorp AI..."
              disabled={isLoading}
              className="main-input"
            />
            
            <div className="selectors-group">
              <select 
                className="pill-select" 
                value={modelName} 
                onChange={(e) => setModelName(e.target.value)}
              >
                <option value="phi3_financial">Finance</option>
                <option value="medical_model">Médical</option>
              </select>

              <select 
                className="pill-select" 
                value={serverUrl} 
                onChange={(e) => setServerUrl(e.target.value)}
              >
                <option value="http://localhost:11434">Ollama</option>
                <option value="http://localhost:8000">Triton</option>
              </select>
            </div>

            <button type="submit" className="action-btn send-btn" disabled={isLoading || !input.trim()}>
              ➤
            </button>
          </form>
          <div className="disclaimer">
            Ce projet est un déploiement expérimental. L'IA peut faire des erreurs.
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;