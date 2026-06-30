import { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Paramètres par défaut avec la nouvelle IP et le nom du modèle
  const [serverUrl, setServerUrl] = useState('http://100.75.233.27:11434');
  const [modelName, setModelName] = useState('phi3-financial');

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(() => { scrollToBottom(); }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input.trim() };
    const chatHistory = [...messages, userMessage];
    
    setMessages(chatHistory);
    setInput('');
    setIsLoading(true);

    const baseUrl = serverUrl.replace(/\/$/, "");
    const apiUrl = `${baseUrl}/api/chat`; // Retour sur l'endpoint chat

    const requestBody = {
      model: modelName,
      messages: chatHistory, // L'endpoint chat attend un tableau d'objets "messages"
      stream: false
    };

    // --- DEBUT DES LOGS DE DEBUG ---
    console.log("🚀 [DEBUG] 1. URL appelée :", apiUrl);
    console.log("📦 [DEBUG] 2. Payload JSON envoyé à Ollama :", requestBody);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      console.log("🌐 [DEBUG] 3. Statut HTTP reçu :", response.status, response.statusText);

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status} - ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log("✅ [DEBUG] 4. Données JSON reçues du serveur :", data);

      // L'endpoint chat renvoie la réponse dans message.content
      const aiResponse = data.message?.content || "Réponse vide de l'IA.";
      setMessages(prev => [...prev, { role: 'assistant', content: aiResponse }]);

    } catch (error) {
      console.error("❌ [DEBUG] 5. Erreur critique attrapée :", error);
      console.error("❌ [DEBUG] Type d'erreur :", error.name);
      console.error("❌ [DEBUG] Message d'erreur :", error.message);
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Erreur : Impossible de joindre le serveur. Regarde la console (F12) pour les logs de debug. Détail : ${error.message}`,
        isError: true 
      }]);
    } finally {
      setIsLoading(false);
      console.log("🏁 [DEBUG] 6. Fin de la tentative de requête.");
      // --- FIN DES LOGS DE DEBUG ---
    }
  };

  const handleReset = () => {
    setMessages([]);
    console.clear(); 
    console.log("🧹 [DEBUG] Historique effacé.");
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

        {/* Barre de saisie style "Pill" */}
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
                <option value="phi3-financial">phi3-financial</option>
                <option value="medical_model">Médical</option>
              </select>

              <select 
                className="pill-select" 
                value={serverUrl} 
                onChange={(e) => setServerUrl(e.target.value)}
              >
                <option value="http://100.75.233.27:11434">Ollama Distant</option>
                <option value="http://localhost:11434">Ollama Local</option>
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