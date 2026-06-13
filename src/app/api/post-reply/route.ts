import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";

export async function POST(req: Request) {
  try {
    const session = await getServerSession(authOptions);
    const { threadId, content } = await req.json();

    if (!threadId || !content) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 });
    }

    let authorId;

    if (session && session.user) {
      authorId = (session.user as any).id;
    } else {
      // Anonymous posting - create a generic anon user or use a default
      let anonUser = await prisma.user.findUnique({ where: { username: "Anonymous" } });
      if (!anonUser) {
        anonUser = await prisma.user.create({
          data: {
            username: `Anonymous_${Math.floor(Math.random() * 10000)}`,
            role: "USER",
            pfpUrl: "/pfps/default.png",
          }
        });
      }
      authorId = anonUser.id;
    }

    const post = await prisma.post.create({
      data: {
        content,
        threadId,
        authorId,
      }
    });

    // Update thread's updatedAt to bubble it to the top
    await prisma.thread.update({
      where: { id: threadId },
      data: { updatedAt: new Date() }
    });

    return NextResponse.json({ success: true, post });
  } catch (error) {
    console.error("Error posting reply:", error);
    return NextResponse.json({ error: "Failed to post reply." }, { status: 500 });
  }
}
