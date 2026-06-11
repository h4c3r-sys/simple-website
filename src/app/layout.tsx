import React from "react";
import Link from "next/link";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export default async function Layout({ children }: { children: React.ReactNode }) {
  const session = await getServerSession(authOptions);

  // Fetch global settings for theme
  const settings = await prisma.settings.findUnique({
    where: { id: "global" }
  });

  const theme = settings?.theme || "classic-blue";

  return (
    <html lang="en" data-theme={theme}>
      <head>
        <title>The Sacred Citadel - AI Coding Forum</title>
      </head>
      <body>
        {/* Top Navbar / Header */}
        <div style={{ backgroundColor: 'var(--primary)', color: 'var(--primary-foreground)', padding: '5px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '13px' }}>
          <div>
            Welcome to <strong>The Sacred Citadel</strong>
          </div>
          <div>
            {session?.user ? (
              <span>
                Logged in as <b>{(session.user as any).name}</b> |{" "}
                {(session.user as any).role === "ADMIN" && (
                  <Link href="/admin" style={{ color: 'inherit', textDecoration: 'underline' }}>Admin CP</Link>
                )}
                {" | "}
                <Link href="/api/auth/signout" style={{ color: 'inherit', textDecoration: 'underline' }}>Logout</Link>
              </span>
            ) : (
              <span>
                <Link href="/login" style={{ color: 'inherit', textDecoration: 'underline' }}>Login / Register</Link>
              </span>
            )}
          </div>
        </div>

        {/* Banner Area */}
        <div style={{ padding: '20px', backgroundColor: 'var(--card)', borderBottom: '1px solid var(--border)', textAlign: 'center' }}>
          <h1 style={{ margin: 0, fontSize: '32px', color: 'var(--primary)', textShadow: '1px 1px 0px #fff' }}>The Sacred Citadel</h1>
          <p style={{ margin: '5px 0 0 0', color: 'var(--muted-foreground)' }}>Premium Programming Discussions since 2012</p>
        </div>

        {/* Translation Widget Container */}
        <div style={{ textAlign: 'right', padding: '10px 20px', backgroundColor: 'var(--muted)' }} id="google_translate_element"></div>

        {/* Main Content */}
        <main className="forum-container">
          {children}
        </main>

        <footer style={{ textAlign: 'center', padding: '20px', fontSize: '12px', color: 'var(--muted-foreground)', borderTop: '1px solid var(--border)', marginTop: '40px' }}>
          &copy; 2012-2026 The Sacred Citadel. All Rights Reserved.
        </footer>

        {/* Google Translate Script */}
        <script type="text/javascript" dangerouslySetInnerHTML={{
          __html: `
            function googleTranslateElementInit() {
              new google.translate.TranslateElement({pageLanguage: 'en'}, 'google_translate_element');
            }
          `
        }}></script>
        <script type="text/javascript" src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
      </body>
    </html>
  );
}
