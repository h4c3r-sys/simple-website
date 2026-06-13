import { prisma } from "@/lib/prisma";
import { notFound } from "next/navigation";
import Image from "next/image";
import { formatDistanceToNow } from "date-fns";
import ReplyForm from "./ReplyForm";

export default async function ThreadPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const thread = await prisma.thread.findUnique({
    where: { id },
    include: {
      posts: {
        orderBy: { createdAt: 'asc' },
        include: { author: true }
      }
    }
  });

  if (!thread) {
    notFound();
  }

  return (
    <div>
      <div style={{ marginBottom: '15px' }}>
        <h2 style={{ margin: '0 0 5px 0' }}>{thread.title}</h2>
        <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>
          Thread Views: {thread.views}
        </div>
      </div>

      <div className="forum-panel">
        <div className="forum-header">Replies</div>
        {thread.posts.map((post, index) => (
          <div key={post.id} className="forum-row">
            <div className="user-block">
              <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '10px', color: post.author.role === 'ADMIN' ? 'red' : 'inherit', textShadow: post.author.role === 'ADMIN' ? '0 0 5px rgba(255,0,0,0.3)' : 'none' }}>
                <span className="online-status"></span>
                {post.author.username}
              </div>
              <div className="avatar-container">
                <Image
                  src={post.author.pfpUrl || '/pfps/default.png'}
                  alt={post.author.username}
                  fill
                  style={{ objectFit: 'cover' }}
                  unoptimized
                />
              </div>
              <div style={{ fontSize: '11px', fontWeight: 'bold', color: 'var(--primary)' }}>
                {post.author.role === 'FAKE' ? 'Veteran Member' : post.author.role === 'ADMIN' ? 'Administrator' : 'Member'}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', marginTop: '5px' }}>
                Posts: {Math.floor(Math.random() * 5000) + 10}
              </div>
              <div style={{ marginTop: '10px', fontSize: '11px', fontWeight: 'bold', color: 'green' }}>
                Rep: +{post.likes} / -{post.dislikes}
              </div>
              {post.author.aboutMe && (
                <div className="user-bio">
                  {post.author.aboutMe}
                </div>
              )}
            </div>
            <div className="post-content-block">
              <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', borderBottom: '1px solid var(--border)', paddingBottom: '5px', marginBottom: '15px' }}>
                Posted {formatDistanceToNow(new Date(post.createdAt))} ago {index === 0 && ' (Original Post)'}
              </div>
              <div className="post-text">
                {post.content}
              </div>
              <div className="post-signature">
                "Code is poetry." - Generated automatically by {post.author.username}
              </div>
            </div>
          </div>
        ))}
      </div>

      <ReplyForm threadId={thread.id} />
    </div>
  );
}
