"use client";

import { signIn } from "next-auth/react";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await signIn("credentials", {
      username,
      password,
      redirect: false,
    });

    if (res?.error) {
      setError("Invalid username or password");
    } else {
      router.push("/");
      router.refresh();
    }
  };

  return (
    <div className="forum-panel" style={{ maxWidth: '400px', margin: '40px auto' }}>
      <div className="forum-header">Login to The Sacred Citadel</div>
      <div style={{ padding: '20px', backgroundColor: 'var(--card)' }}>
        {error && <div style={{ color: 'red', marginBottom: '10px', fontSize: '12px' }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 'bold', marginBottom: '5px' }}>Username:</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{ width: '100%', padding: '8px', border: '1px solid var(--border)', borderRadius: '3px', boxSizing: 'border-box' }}
              required
            />
          </div>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 'bold', marginBottom: '5px' }}>Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: '100%', padding: '8px', border: '1px solid var(--border)', borderRadius: '3px', boxSizing: 'border-box' }}
              required
            />
          </div>
          <button type="submit" className="retro-button" style={{ width: '100%' }}>Log in</button>
        </form>
        <div style={{ marginTop: '15px', fontSize: '12px', textAlign: 'center' }}>
          Don't have an account? <a href="/register" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>Register here</a>
        </div>
        <div style={{ marginTop: '10px', fontSize: '11px', textAlign: 'center', color: 'var(--muted-foreground)' }}>
          Tip: Admin credentials are admin / admin
        </div>
      </div>
    </div>
  );
}
