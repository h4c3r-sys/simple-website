import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { revalidatePath } from "next/cache";

export default async function AdminPage() {
  const session = await getServerSession(authOptions);

  if (!session || (session.user as any).role !== "ADMIN") {
    redirect("/");
  }

  const settings = await prisma.settings.findUnique({
    where: { id: "global" }
  });

  async function updateTheme(formData: FormData) {
    "use server";
    const theme = formData.get("theme") as string;
    await prisma.settings.update({
      where: { id: "global" },
      data: { theme }
    });
    revalidatePath("/", "layout");
  }

  return (
    <div className="forum-panel" style={{ maxWidth: '600px', margin: '0 auto' }}>
      <div className="forum-header">Admin Control Panel</div>
      <div style={{ padding: '20px', backgroundColor: 'var(--card)' }}>
        <h2 style={{ marginTop: 0 }}>Site Settings</h2>

        <form action={updateTheme} style={{ marginTop: '20px' }}>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '5px' }}>Global Theme</label>
            <select
              name="theme"
              defaultValue={settings?.theme || "classic-blue"}
              style={{ width: '100%', padding: '8px', border: '1px solid var(--border)', borderRadius: '3px' }}
            >
              <option value="classic-blue">Classic Blue vBulletin (Default)</option>
              <option value="retro-so">Retro StackOverflow (2012)</option>
              <option value="dark-hacker">Dark Hacker / Terminal</option>
            </select>
          </div>
          <button type="submit" className="retro-button">Save Settings</button>
        </form>
      </div>
    </div>
  );
}
