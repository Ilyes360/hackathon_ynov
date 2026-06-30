import { useState, useRef, useEffect, useCallback } from 'react';
import './App.css';
import { validateUserPrompt, checkResponseHeaders } from './security/validatePrompt';

const DEFAULT_SERVER = 'http://100.75.233.27:11434';
const DEFAULT_MODEL = 'phi3-financial';

function App() {
  const [sessions, setSessions] = useState(() => {
    try {
      const saved = localStorage.getItem('techcorp_chat_sessions');
      if (!saved) {
        return [{ id: Date.now(), title: 'Discussion du jour', messages: [] }];
      }
      const parsed = JSON.parse(saved);
      return Array.isArray(parsed) && parsed.length > 0
        ? parsed
        : [{ id: Date.now(), title: 'Discussion du jour', messages: [] }];
    } catch {
      return [{ id: Date.now(), title: 'Discussion du jour', messages: [] }];
    }
  });

  const [activeId, setActiveId] = useState(sessions[0].id);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [serverUrl, setServerUrl] = useState(DEFAULT_SERVER);
  const [modelName, setModelName] = useState(DEFAULT_MODEL);
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const messagesEndRef = useRef(null);

  const handleSaveTitle = (id) => {
    const title = editTitle.trim().replace(/<[^>]*>/g, '').slice(0, 80);
    if (title) {
      setSessions((prev) => prev.map((s) =>
        s.id === id ? { ...s, title } : s
      ));
    }
    setEditingSessionId(null);
  };

  useEffect(() => {
    localStorage.setItem('techcorp_chat_sessions', JSON.stringify(sessions));
  }, [sessions]);

  const activeSession = sessions.find((s) => s.id === activeId) || sessions[0];
  const messages = activeSession.messages;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  useEffect(() => { scrollToBottom(); }, [messages, isLoading]);

  const updateSessionMessages = (newMessages) => {
    setSessions((prev) => prev.map((s) => {
      if (s.id === activeId) {
        const updated = { ...s, messages: newMessages };
        // Si le titre actuel est générique ou vide, on le remplace par le début du premier message
        const isGeneric = s.title === 'Nouvelle discussion' || s.title === 'Discussion du jour' || !s.title;
        if (isGeneric && newMessages.length > 0) {
          const firstUserMsg = newMessages.find(m => m.role === 'user');
          if (firstUserMsg) {
            const content = firstUserMsg.content;
            const cleanTitle = content.length > 25 ? content.substring(0, 25) + '...' : content;
            updated.title = cleanTitle;
          }
        }
        return updated;
      }
      return s;
    }));
  };

  const checkConnection = useCallback(async () => {
    const baseUrl = serverUrl.replace(/\/$/, '');
    setConnectionStatus('checking');
    try {
      const res = await fetch(`${baseUrl}/api/tags`, { signal: AbortSignal.timeout(5000) });
      setConnectionStatus(res.ok ? 'connected' : 'disconnected');
    } catch {
      setConnectionStatus('disconnected');
    }
  }, [serverUrl]);

  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, [checkConnection]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const validation = validateUserPrompt(input.trim());
    if (!validation.isValid) {
      updateSessionMessages([
        ...messages,
        { role: 'user', content: input.trim() },
        { role: 'assistant', content: `Requete bloquee : ${validation.error}`, isError: true },
      ]);
      setInput('');
      return;
    }

    const userMessage = { role: 'user', content: validation.cleanPrompt };
    const chatHistory = [...messages, userMessage];
    updateSessionMessages(chatHistory);
    setInput('');
    setIsLoading(true);

    const baseUrl = serverUrl.replace(/\/$/, '');
    const apiUrl = `${baseUrl}/api/chat`;
    const requestBody = { model: modelName, messages: chatHistory, stream: false };

    if (import.meta.env.DEV) {
      console.log('[DEBUG] URL:', apiUrl);
      console.log('[DEBUG] Payload:', requestBody);
    }

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status} - ${response.statusText}`);
      }

      const suspiciousHeaders = checkResponseHeaders(response.headers);
      if (suspiciousHeaders.length > 0) {
        console.warn('[SECURITE] Headers suspects detectes:', suspiciousHeaders);
      }

      const data = await response.json();
      const aiResponse = data.message?.content || "Reponse vide de l'IA.";
      updateSessionMessages([...chatHistory, { role: 'assistant', content: aiResponse }]);
      setConnectionStatus('connected');
    } catch (error) {
      setConnectionStatus('disconnected');
      updateSessionMessages([
        ...chatHistory,
        {
          role: 'assistant',
          content: `Erreur : impossible de joindre le serveur (${error.message}).`,
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    const newSession = { id: Date.now(), title: 'Nouvelle discussion', messages: [] };
    setSessions([newSession, ...sessions]);
    setActiveId(newSession.id);
  };

  const statusLabel = {
    connected: 'Connecte',
    disconnected: 'Deconnecte',
    checking: 'Verification...',
  }[connectionStatus];

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-top">
          <div className="logo-area">
            <span className="logo-icon">💠</span> TechCorp
          </div>
          <div className={`connection-badge ${connectionStatus}`} title={serverUrl}>
            <span className="connection-dot" />
            {statusLabel}
          </div>
          <button className="new-chat-btn" onClick={handleNewChat}>
            <span className="icon">＋</span> Nouvelle discussion
          </button>
        </div>

        <div className="sidebar-history">
          <h3 className="history-title">Historique</h3>
          <ul className="history-list">
            {sessions.map((session) => (
              <li
                key={session.id}
                className={`history-item ${activeId === session.id ? 'active' : ''} ${editingSessionId === session.id ? 'editing' : ''}`}
                onClick={() => {
                  if (editingSessionId !== session.id) {
                    setActiveId(session.id);
                  }
                }}
                onDoubleClick={(e) => {
                  e.stopPropagation();
                  setEditingSessionId(session.id);
                  setEditTitle(session.title || '');
                }}
                title="Double-cliquez pour renommer"
              >
                {editingSessionId === session.id ? (
                  <div className="history-item-edit" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSaveTitle(session.id);
                        if (e.key === 'Escape') setEditingSessionId(null);
                      }}
                      autoFocus
                      className="rename-input"
                      maxLength={80}
                    />
                    <div className="edit-actions">
                      <button
                        className="edit-action-btn save"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSaveTitle(session.id);
                        }}
                        title="Enregistrer"
                      >
                        ✔️
                      </button>
                      <button
                        className="edit-action-btn cancel"
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingSessionId(null);
                        }}
                        title="Annuler"
                      >
                        ❌
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="history-item-content">
                    <span className="history-item-title">{session.title || 'Discussion vide'}</span>
                    <button
                      className="rename-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingSessionId(session.id);
                        setEditTitle(session.title || '');
                      }}
                      title="Renommer la discussion"
                    >
                      ✏️
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      </aside>

      <main className="main-content">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <h1 className="greeting">
              <span className="gradient-text">Bonjour, l'equipe.</span>
              <br />
              <span className="greeting-sub">Comment puis-je vous aider aujourd'hui ?</span>
            </h1>
          </div>
        ) : (
          <div className="messages-container">
            {messages.map((msg, index) => (
              <div key={index} className={`message-row ${msg.role}`}>
                <div className="avatar">{msg.role === 'user' ? 'U' : '💠'}</div>
                <div className={`message-bubble ${msg.isError ? 'error-text' : ''}`}>{msg.content}</div>
              </div>
            ))}
            {isLoading && (
              <div className="message-row assistant loading">
                <div className="avatar loading-avatar">💠</div>
                <div className="message-bubble typing-bubble">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        <div className="input-wrapper">
          <form onSubmit={handleSubmit} className="input-pill">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Demander a TechCorp AI..."
              disabled={isLoading}
              className="main-input"
              maxLength={1500}
            />
            <div className="selectors-group">
              <select className="pill-select" value={modelName} onChange={(e) => setModelName(e.target.value)}>
                <option value="phi3-financial">phi3-financial</option>
                <option value="medical_model">Medical</option>
              </select>
              <select className="pill-select" value={serverUrl} onChange={(e) => setServerUrl(e.target.value)}>
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
            Entrees filtrees (anti-injection). Historique stocke localement (localStorage).
            Ce projet est experimental — l'IA peut faire des erreurs.
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
