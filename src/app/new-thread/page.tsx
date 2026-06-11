"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function NewThreadPage() {
  const [topic, setTopic] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const router = useRouter();

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);

    try {
      const res = await fetch("/api/generate-thread", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
      });

      const data = await res.json();
      if (data.success && data.threadId) {
        router.push(`/thread/${data.threadId}`);
      } else {
        alert("Error generating thread: " + data.error);
      }
    } catch (error) {
      alert("Failed to reach server");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="forum-panel" style={{ maxWidth: '600px', margin: '40px auto' }}>
      <div className="forum-header">Create New AI Discussion Thread</div>
      <div style={{ padding: '20px', backgroundColor: 'var(--card)' }}>
        <p style={{ fontSize: '13px', marginBottom: '20px' }}>
          Enter a programming topic below. Our AI engine will automatically generate a highly realistic, multi-user forum discussion covering the topic to help with your research.
        </p>

        <form onSubmit={handleGenerate}>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '5px' }}>Topic / Question:</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., How to implement WebSockets in Node.js"
              style={{ width: '100%', padding: '8px', border: '1px solid var(--border)', borderRadius: '3px', boxSizing: 'border-box' }}
              required
            />
          </div>
          <button type="submit" className="retro-button" disabled={isGenerating}>
            {isGenerating ? "Generating Simulation..." : "Generate Thread"}
          </button>
        </form>
      </div>
    </div>
  );
}
