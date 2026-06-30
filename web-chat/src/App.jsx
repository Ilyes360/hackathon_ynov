import { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  // 1. Initialisation : Charge depuis localStorage ou crée une session par défaut
  const [sessions, setSessions] = useState(() => {
    const saved = localStorage.getItem('techcorp_chat_sessions');
    return saved ? JSON.parse(saved) : [{ id: Date.now(), title: 'Discussion du jour', messages: [] }];
  });
  
  const [activeId, setActiveId] = useState(sessions[0].id);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [serverUrl, setServerUrl] = useState('http://100.75.233.27:11434');
  const [modelName, setModelName] = useState('phi3-financial');

  const messagesEndRef = useRef(null);

  // 2. Persistance : Sauvegarde dans localStorage à chaque modification de "sessions"
  useEffect(() => {
    localStorage.setItem('techcorp_chat_sessions', JSON.stringify(sessions));
  }, [sessions]);

  // Récupérer les messages de la session active
  const activeSession = sessions.find(s => s.id === activeId) || sessions[0];
  const messages = activeSession.messages;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(() => { scrollToBottom(); }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input.trim() };
    
    // Mettre à jour la session active avec le message utilisateur
    updateSessionMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${serverUrl.replace(/\/$/, "")}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: modelName,
          messages: [...messages, userMessage],
          stream: false
        })
      });

      const data = await response.json();
      const aiResponse = data.message?.content || "Réponse vide de l'IA.";
      
      updateSessionMessages([...messages, userMessage, { role: 'assistant', content: aiResponse }]);

    } catch (error) {
      updateSessionMessages([...messages, userMessage, { 
        role: 'assistant', 
        content: `Erreur : Impossible de joindre le serveur.`,
        isError: true 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const updateSessionMessages = (newMessages) => {
    setSessions(prev => prev.map(s => 
      s.id === activeId ? { ...s, messages: newMessages } : s
    ));
  };

  const handleNewChat = () => {
    const newSession = { id: Date.now(), title: 'Nouvelle discussion', messages: [] };
    setSessions([newSession, ...sessions]);
    setActiveId(newSession.id);
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-top">
          <div className="logo-area">💠 TechCorp</div>
          <button className="new-chat-btn" onClick={handleNewChat}>
            <span className="icon">＋</span> Nouvelle discussion
          </button>
        </div>

        <div className="sidebar-history">
          <h3 className="history-title">Historique</h3>
          <ul className="history-list">
            {sessions.map(session => (
              <li 
                key={session.id} 
                className={`history-item ${activeId === session.id ? 'active' : ''}`}
                onClick={() => setActiveId(session.id)}
              >
                {session.title || 'Discussion vide'}
              </li>
            ))}
          </ul>
        </div>
      </aside>

      <main className="main-content">
        <div className="messages-container">
            {messages.map((msg, index) => (
              <div key={index} className={`message-row ${msg.role}`}>
                <div className="avatar">{msg.role === 'user' ? 'U' : '💠'}</div>
                <div className={`message-bubble ${msg.isError ? 'error-text' : ''}`}>{msg.content}</div>
              </div>
            ))}
            {isLoading && <div className="message-row assistant"><div className="avatar">💠</div><div className="message-bubble typing">...</div></div>}
            <div ref={messagesEndRef} />
        </div>

        <div className="input-wrapper">
          <form onSubmit={handleSubmit} className="input-pill">
            <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Demander à TechCorp AI..." className="main-input" />
            <select className="pill-select" value={modelName} onChange={(e) => setModelName(e.target.value)}>
                <option value="phi3-financial">phi3-financial</option>
                <option value="medical_model">Médical</option>
            </select>
            <button type="submit" className="action-btn send-btn" disabled={isLoading}>➤</button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default App;