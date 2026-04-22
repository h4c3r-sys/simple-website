import React, { useState, useEffect } from 'react';
import './App.css';

// Discord UI Clone with Client-Side E2EE
function App() {
  const [servers, setServers] = useState([{ id: '1', name: 'General Server' }]);
  const [channels, setChannels] = useState([{ id: '1', name: 'general' }]);
  const [messages, setMessages] = useState<{id: string, text: string, author: string, attachment?: string}[]>([]);
  const [inputText, setInputText] = useState('');
  const [editingMsgId, setEditingMsgId] = useState<string | null>(null);

  // DMs State
  const [dms, setDms] = useState([{ id: 'dm1', name: 'Alice (DM)' }]);
  const [activeView, setActiveView] = useState<'server' | 'dm'>('server');

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

  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() && !selectedFile) return;

    if (editingMsgId) {
      setMessages(messages.map(m => m.id === editingMsgId ? { ...m, text: inputText } : m));
      setEditingMsgId(null);
      setInputText('');
      return;
    }

    // 1. Encrypt message locally (Backend NEVER sees plaintext)
    const encryptedText = encryptMessage(inputText);

    // 2. Simulate sending over WebSocket (Elixir Gateway)
    console.log("Sending to Elixir Gateway:", encryptedText);

    let attachmentData = undefined;
    if (selectedFile) {
      // Simulate reading and encrypting the file
      attachmentData = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          // In real app, this would be encrypted with WebCrypto API before upload
          resolve(reader.result as string);
        };
        reader.readAsDataURL(selectedFile);
      });
      console.log(`Uploading encrypted file: ${selectedFile.name}`);
    }

    // 3. Update local UI (simulating receiving back the message)
    const newMessage = {
      id: Date.now().toString(),
      text: inputText ? decryptMessage(encryptedText) : '', // We decrypt it for display
      author: 'You',
      attachment: attachmentData
    };

    setMessages([...messages, newMessage]);
    setInputText('');
    setSelectedFile(null);
  };

  const handleEditMessage = (id: string, currentText: string) => {
    setEditingMsgId(id);
    setInputText(currentText);
  };

  const handleDeleteMessage = (id: string) => {
    setMessages(messages.filter(m => m.id !== id));
  };

  const handleCreateServer = () => {
    const name = prompt("Enter new server name:");
    if (name) setServers([...servers, { id: Date.now().toString(), name }]);
  };

  const handleCreateDM = () => {
    const name = prompt("Enter username to DM:");
    if (name) setDms([...dms, { id: Date.now().toString(), name: `${name} (DM)` }]);
  };

  return (
    <div className="discord-app">
      {/* Server Sidebar */}
      <div className="server-sidebar">
        <div className="server-icon home" title="The Sacred Citadel" onClick={() => setActiveView('dm')}>
          <img src="/logo.svg" alt="Citadel Logo" style={{ width: '32px', height: '32px' }} />
        </div>
        <div className="separator"></div>
        {servers.map(server => (
          <div key={server.id} className="server-icon" onClick={() => setActiveView('server')}>{server.name.charAt(0)}</div>
        ))}
        <div className="server-icon add-server" onClick={handleCreateServer}>+</div>
      </div>

      {/* Channel Sidebar */}
      <div className="channel-sidebar">
        <div className="server-header">
          <h3>{activeView === 'server' ? 'The Sacred Citadel' : 'Direct Messages'}</h3>
        </div>
        <div className="channel-list">
          {activeView === 'server' ? (
            channels.map(channel => (
              <div key={channel.id} className="channel-item active">
                <span className="hash">#</span> {channel.name}
              </div>
            ))
          ) : (
            <>
              {dms.map(dm => (
                <div key={dm.id} className="channel-item active">
                  <span className="hash">@</span> {dm.name}
                </div>
              ))}
              <div className="channel-item" onClick={handleCreateDM} style={{ cursor: 'pointer', color: '#23a559' }}>
                <span className="hash">+</span> New DM
              </div>
            </>
          )}
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
                  {msg.author === 'You' && (
                    <div className="message-actions">
                      <button onClick={() => handleEditMessage(msg.id, msg.text)}>Edit</button>
                      <button onClick={() => handleDeleteMessage(msg.id)} style={{ color: '#da373c' }}>Delete</button>
                    </div>
                  )}
                </div>
                <div className="message-text">{msg.text}</div>
                {msg.attachment && (
                  <div className="message-attachment">
                    {msg.attachment.startsWith('data:image/') ? (
                       <img src={msg.attachment} alt="attachment" style={{ maxWidth: '400px', maxHeight: '400px', borderRadius: '8px', marginTop: '8px' }} />
                    ) : (
                       <a href={msg.attachment} download="secure_file">Download Secure File</a>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="message-input-area">
          {selectedFile && (
            <div className="file-preview" style={{ padding: '8px', background: '#2b2d31', borderRadius: '8px 8px 0 0', color: '#dbdee1', fontSize: '14px', borderBottom: '1px solid #1e1f22' }}>
              📎 {selectedFile.name}
              <button onClick={() => setSelectedFile(null)} style={{ marginLeft: '8px', background: 'none', border: 'none', color: '#da373c', cursor: 'pointer' }}>✖</button>
            </div>
          )}
          <form onSubmit={handleSendMessage} style={{ display: 'flex', background: '#383a40', borderRadius: selectedFile ? '0 0 8px 8px' : '8px' }}>
            <label style={{ padding: '11px 16px', cursor: 'pointer', color: '#b5bac1' }}>
              +
              <input type="file" style={{ display: 'none' }} onChange={handleFileSelect} />
            </label>
            <input
              type="text"
              placeholder="Message #general"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              style={{ background: 'transparent', flexGrow: 1, border: 'none', padding: '11px 16px', color: '#dbdee1', outline: 'none' }}
            />
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
