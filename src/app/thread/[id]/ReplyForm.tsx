"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function ReplyForm({ threadId }: { threadId: string }) {
  const [content, setContent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    setIsSubmitting(true);
    try {
      const res = await fetch("/api/post-reply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ threadId, content }),
      });

      if (res.ok) {
        setContent("");
        router.refresh();
      } else {
        alert("Failed to post reply.");
      }
    } catch (e) {
      alert("Error posting reply.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="forum-panel" style={{ marginTop: '20px' }}>
      <div className="forum-header">Quick Reply</div>
      <div style={{ padding: '15px', backgroundColor: 'var(--card)' }}>
        <form onSubmit={handleSubmit}>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            style={{ width: '100%', minHeight: '100px', padding: '10px', border: '1px solid var(--border)', borderRadius: '3px', boxSizing: 'border-box', fontFamily: 'inherit', resize: 'vertical' }}
            placeholder="Type your reply here..."
            required
          />
          <div style={{ marginTop: '10px' }}>
            <button type="submit" className="retro-button" disabled={isSubmitting}>
              {isSubmitting ? "Posting..." : "Post Quick Reply"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
