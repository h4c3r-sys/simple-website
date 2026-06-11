import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import Anthropic from '@anthropic-ai/sdk';
import fs from 'fs';
import path from 'path';

// Note: Ensure ANTHROPIC_API_KEY is available in the environment variables
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || 'dummy_key',
});

// Helper to pick random PFP
function getRandomPfp() {
  const pfpDir = path.join(process.cwd(), 'public/pfps');
  if (fs.existsSync(pfpDir)) {
    const files = fs.readdirSync(pfpDir).filter(f => f.endsWith('.jpg') || f.endsWith('.png'));
    if (files.length > 0) {
      const randomFile = files[Math.floor(Math.random() * files.length)];
      return `/pfps/${randomFile}`;
    }
  }
  return '/pfps/default.png'; // Fallback
}

function getRandomInt(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export async function POST(req: Request) {
  try {
    const { topic } = await req.json();

    if (!topic) {
      return NextResponse.json({ error: "Topic is required" }, { status: 400 });
    }

    // Since we may not have a valid API key during development/testing inside this sandbox,
    // we use a robust mocking strategy if the key is "dummy_key" or missing.
    let threadData;

    if (!process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_API_KEY === 'dummy_key') {
      // Mock generation for sandbox testing
      threadData = {
        title: `Help needed with ${topic} in 2026`,
        question: `I've been trying to figure out ${topic} for the past few days, but I'm completely stuck. I tried reading the docs, but they are confusing. Does anyone have a good example or best practices for this?`,
        author: { username: `Coder_${Math.floor(Math.random() * 1000)}` },
        replies: [
          {
            content: `The easiest way to handle ${topic} is by using the new API methods introduced recently. Here is a quick snippet:\n\n\`\`\`javascript\nconst example = new Example();\nexample.init();\n\`\`\`\n\nHope this helps!`,
            author: { username: `TechGuru99` }
          },
          {
            content: `I disagree with @TechGuru99. You shouldn't do it that way because of performance overhead. Instead, try the low-level bindings. It's harder but way more scalable for ${topic}.`,
            author: { username: `OptimizationNerd` }
          },
          {
            content: `Thanks for the tips guys! I was having the same issue with ${topic}. +1 for the snippet.`,
            author: { username: `NoobDev42` }
          }
        ]
      };
    } else {
      // Real API Call to Claude
      const prompt = `
      You are an expert at simulating forum discussions.
      Create a highly realistic 2012-era programming forum thread about the topic: "${topic}".

      Respond ONLY with a JSON object in this exact format:
      {
        "title": "A catchy, realistic forum thread title",
        "question": "The main question asked by the original poster (OP), formatted with paragraphs. Make it look like a real user asking for help.",
        "author": {
          "username": "Creative OP Username",
          "aboutMe": "A short, realistic user bio (e.g. 'Just a guy coding in his basement since 1999', 'Frontend enthusiast', 'Linux power user')"
        },
        "replies": [
          {
            "content": "A reply from another user. Can include code snippets, agreements, disagreements, or advice. Include characteristic 2012 forum behavior (e.g., \"bump\", \"did you try searching first?\", emoticons).",
            "author": {
              "username": "Another Creative Username",
              "aboutMe": "A different realistic short bio for this user."
            }
          }
          // Include 3 to 5 replies from different unique users.
        ]
      }
      `;

      const msg = await anthropic.messages.create({
        model: "claude-3-5-sonnet-20241022",
        max_tokens: 1500,
        temperature: 0.8,
        system: "You output only valid JSON.",
        messages: [
          {
            role: "user",
            content: prompt
          }
        ]
      });

      const rawText = (msg.content[0] as any).text;
      // Basic extraction if Claude wraps it in markdown blocks
      const jsonStr = rawText.replace(/```json\n?|\n?```/g, '').trim();
      threadData = JSON.parse(jsonStr);
    }

    // Save generated thread to database

    // 1. Get or create OP user
    let opUser = await prisma.user.findUnique({ where: { username: threadData.author.username } });
    if (!opUser) {
      opUser = await prisma.user.create({
        data: {
          username: threadData.author.username,
          aboutMe: threadData.author.aboutMe || "Just a coder...",
          role: "FAKE",
          pfpUrl: getRandomPfp(),
        }
      });
    }

    // 2. Create Thread
    const newThread = await prisma.thread.create({
      data: {
        title: threadData.title,
        content: threadData.question,
        authorId: opUser.id,
        views: getRandomInt(50, 5000),
      }
    });

    // 3. Create OP's Post (the first post in the thread)
    await prisma.post.create({
      data: {
        content: threadData.question,
        threadId: newThread.id,
        authorId: opUser.id,
        likes: getRandomInt(1, 1000),
        dislikes: getRandomInt(0, 100),
      }
    });

    // 4. Create Replies
    for (const reply of threadData.replies) {
      let replyUser = await prisma.user.findUnique({ where: { username: reply.author.username } });
      if (!replyUser) {
        replyUser = await prisma.user.create({
          data: {
            username: reply.author.username,
            aboutMe: reply.author.aboutMe || "Just a coder...",
            role: "FAKE",
            pfpUrl: getRandomPfp(),
          }
        });
      }

      await prisma.post.create({
        data: {
          content: reply.content,
          threadId: newThread.id,
          authorId: replyUser.id,
          likes: getRandomInt(1, 1000),
          dislikes: getRandomInt(0, 100),
        }
      });
    }

    return NextResponse.json({ success: true, threadId: newThread.id });

  } catch (error) {
    console.error("Error generating thread:", error);
    return NextResponse.json({ error: "Failed to generate thread." }, { status: 500 });
  }
}
