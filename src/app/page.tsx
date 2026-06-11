import { prisma } from "@/lib/prisma";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";

export const revalidate = 0; // Dynamic page

export default async function HomePage() {
  const threads = await prisma.thread.findMany({
    orderBy: { updatedAt: 'desc' },
    include: {
      author: true,
      _count: {
        select: { posts: true }
      }
    }
  });

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h2>Latest Discussions</h2>
        <Link href="/new-thread">
          <button className="retro-button">Post New Thread</button>
        </Link>
      </div>

      <div className="forum-panel">
        <div className="forum-header" style={{ display: 'flex' }}>
          <div style={{ flex: 1 }}>Thread Title</div>
          <div style={{ width: '150px', textAlign: 'center' }}>Replies / Views</div>
          <div style={{ width: '200px' }}>Last Post</div>
        </div>

        {threads.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center', color: 'var(--muted-foreground)' }}>
            No threads found. Be the first to start a discussion!
          </div>
        ) : (
          threads.map(thread => (
            <div key={thread.id} className="forum-row" style={{ padding: '10px 15px', backgroundColor: 'var(--card)' }}>
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <Link href={`/thread/${thread.id}`} style={{ fontWeight: 'bold', color: 'var(--primary)', textDecoration: 'none', fontSize: '15px' }}>
                  {thread.title}
                </Link>
                <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', marginTop: '4px' }}>
                  Started by <b>{thread.author.username}</b>, {formatDistanceToNow(new Date(thread.createdAt))} ago
                </div>
              </div>
              <div style={{ width: '150px', textAlign: 'center', fontSize: '12px', color: 'var(--muted-foreground)', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <div>Replies: {Math.max(0, thread._count.posts - 1)}</div>
                <div>Views: {thread.views}</div>
              </div>
              <div style={{ width: '200px', fontSize: '11px', color: 'var(--muted-foreground)', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                {formatDistanceToNow(new Date(thread.updatedAt))} ago
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
