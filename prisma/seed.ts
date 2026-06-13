import { prisma } from "../src/lib/prisma";
import bcrypt from "bcryptjs";

async function main() {
  const adminPassword = await bcrypt.hash("admin", 10);

  await prisma.user.upsert({
    where: { username: "admin" },
    update: {},
    create: {
      username: "admin",
      password: adminPassword,
      role: "ADMIN",
      pfpUrl: "/pfps/default.png",
    },
  });

  await prisma.settings.upsert({
    where: { id: "global" },
    update: {},
    create: {
      id: "global",
      theme: "classic-blue",
    },
  });

  console.log("Database seeded successfully!");
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
