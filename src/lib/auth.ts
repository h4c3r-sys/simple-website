import { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { prisma } from "@/lib/prisma";
import bcrypt from "bcryptjs";

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.username) return null;

        const user = await prisma.user.findUnique({
          where: { username: credentials.username },
        });

        if (user && user.password && credentials.password) {
          const isValid = await bcrypt.compare(credentials.password, user.password);
          if (isValid) {
            return {
              id: user.id,
              name: user.username,
              role: user.role,
              pfpUrl: user.pfpUrl,
            };
          }
        } else if (!user && !credentials.password) {
          // Anonymous login flow (no password provided)
          // We can optionally create a user dynamically or handle anonymous session differently.
          // For now, let's just say if it's an existing anon user, they might not have a password.
        }

        return null;
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = (user as any).role;
        token.pfpUrl = (user as any).pfpUrl;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).id = token.sub;
        (session.user as any).role = token.role;
        (session.user as any).pfpUrl = token.pfpUrl;
      }
      return session;
    },
  },
  pages: {
    signIn: "/login",
  },
  session: {
    strategy: "jwt",
  },
  secret: process.env.NEXTAUTH_SECRET || "fallback-secret-key-change-in-prod",
};
