# Hosting & Deployment Guide: The Sacred Citadel

This guide explains how to host "The Sacred Citadel" using Docker so you can access it from another PC or make it public on the internet.

## Prerequisites
- Docker and Docker Compose installed on your host machine.
- An Anthropic API Key (Claude) if you want real AI generations instead of the mock testing data.

## 1. Quick Start (Local Network Hosting)

If you just want to run it on your current PC and access it from your phone or laptop on the **same Wi-Fi network**:

1. Open a terminal in this project's root folder.
2. (Optional) Create a `.env` file and add your API key:
   \`\`\`
   ANTHROPIC_API_KEY=your_actual_key_here
   NEXTAUTH_URL=http://<YOUR_LOCAL_IP>:3000
   \`\`\`
   *(Replace `<YOUR_LOCAL_IP>` with your PC's local IP address, e.g., 192.168.1.10)*
3. Run the following command:
   \`\`\`bash
   docker-compose up -d --build
   \`\`\`
4. Open a browser on another device and go to `http://<YOUR_LOCAL_IP>:3000`.

## 2. Public Hosting (Internet)

If you want to host this on a VPS (like DigitalOcean, AWS, or Hetzner) to access it anywhere:

1. **Clone the repository** to your server.
2. **Setup your environment variables**:
   Create a `.env` file:
   \`\`\`
   ANTHROPIC_API_KEY=your_actual_key_here
   NEXTAUTH_URL=https://yourdomain.com
   NEXTAUTH_SECRET=generate_a_random_secure_string_here
   \`\`\`
3. **Start the application**:
   \`\`\`bash
   docker-compose up -d --build
   \`\`\`
4. **Setup Nginx & SSL (Recommended)**:
   Since the app runs on port 3000, you should use Nginx as a reverse proxy and attach a Let's Encrypt SSL certificate. A typical Nginx block looks like:
   \`\`\`nginx
   server {
       server_name yourdomain.com;
       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   \`\`\`
5. Use `certbot --nginx` to secure your domain.

## Database Note
This application uses a local SQLite database (`prisma/dev.db`) for zero-configuration persistence. The `docker-compose.yml` file is configured to map this file from your host machine into the container.
- If you move servers, simply copy the `prisma/dev.db` file to retain all your threads, users, and settings.
