import React, { useState, useEffect } from 'react';
import './App.css';

// Discord UI Clone with Client-Side E2EE
function App() {
  const [servers, setServers] = useState([{ id: '1', name: 'General Server' }]);
  const [channels, setChannels] = useState([{ id: '1', name: 'general' }]);
  const [messages, setMessages] = useState<{id: string, text: string, author: string}[]>([]);
  const [inputText, setInputText] = useState('');

  // Simulating fetching state from Go API
  useEffect(() => {
    // In real app, fetch from http://api:8080/api/servers
    console.log("Fetching servers from Go API...");
  }, []);

  // Simulating Client-Side E2EE
  const encryptMessage = (plaintext: string): string => {
    // This simulates AES-256-GCM encryption with X25519 keys
    // Real implementation would use Web Crypto API (SubtleCrypto)
    return `[ENCRYPTED_GCM]${btoa(plaintext)}`;
  };

  const decryptMessage = (ciphertext: string): string => {
    // Simulating decryption locally
    if (ciphertext.startsWith('[ENCRYPTED_GCM]')) {
      const base64 = ciphertext.replace('[ENCRYPTED_GCM]', '');
      return atob(base64);
    }
    return ciphertext;
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    // 1. Encrypt message locally (Backend NEVER sees plaintext)
    const encryptedText = encryptMessage(inputText);

    // 2. Simulate sending over WebSocket (Elixir Gateway)
    console.log("Sending to Elixir Gateway:", encryptedText);

    // 3. Update local UI (simulating receiving back the message)
    const newMessage = {
      id: Date.now().toString(),
      text: decryptMessage(encryptedText), // We decrypt it for display
      author: 'You'
    };

    setMessages([...messages, newMessage]);
    setInputText('');
  };

  return (
    <div className="discord-app">
      {/* Server Sidebar */}
      <div className="server-sidebar">
        <div className="server-icon home">D</div>
        <div className="separator"></div>
        {servers.map(server => (
          <div key={server.id} className="server-icon">{server.name.charAt(0)}</div>
        ))}
      </div>

      {/* Channel Sidebar */}
      <div className="channel-sidebar">
        <div className="server-header">
          <h3>Private Server</h3>
        </div>
        <div className="channel-list">
          {channels.map(channel => (
            <div key={channel.id} className="channel-item active">
              <span className="hash">#</span> {channel.name}
            </div>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="chat-area">
        <div className="chat-header">
          <h3><span className="hash">#</span> general</h3>
          <span className="e2ee-badge">🔒 End-to-End Encrypted</span>
        </div>

        <div className="message-list">
          <div className="message-container">
            <div className="avatar">S</div>
            <div className="message-content">
              <div className="message-header">
                <span className="author">System</span>
                <span className="timestamp">Today at 12:00 PM</span>
              </div>
              <div className="message-text">Welcome to your secure chat. Keys exchanged via X25519. Messages encrypted via AES-256-GCM.</div>
            </div>
          </div>

          {messages.map(msg => (
             <div key={msg.id} className="message-container">
              <div className="avatar">Y</div>
              <div className="message-content">
                <div className="message-header">
                  <span className="author">{msg.author}</span>
                  <span className="timestamp">Just now</span>
                </div>
                <div className="message-text">{msg.text}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="message-input-area">
          <form onSubmit={handleSendMessage}>
            <input
              type="text"
              placeholder="Message #general"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
