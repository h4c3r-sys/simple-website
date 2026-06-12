# Advanced Hosting & Deployment Guide: The Sacred Citadel

This guide details how to securely and persistently host "The Sacred Citadel" using Docker. Because the application relies on SQLite for database persistence, specific deployment strategies must be followed to ensure data integrity across container restarts.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Network Hosting (Quick Start)](#local-network-hosting)
3. [Production VPS Hosting (Internet)](#production-vps-hosting)
4. [Nginx Reverse Proxy & SSL Setup](#nginx-reverse-proxy--ssl-setup)
5. [Data Persistence & Backups](#data-persistence--backups)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites
- **Docker & Docker Compose** installed on your host machine or Virtual Private Server (VPS).
- **Domain Name** (if hosting publicly) pointing to your server's IP address.
- **Anthropic API Key** (Claude) for real AI generated threads.

---

## Local Network Hosting

If you want to run the application on your primary PC and access it from your phone, laptop, or other devices on the same Wi-Fi network:

1. **Environment Configuration:**
   Create a `.env` file in the project root:
   \`\`\`env
   ANTHROPIC_API_KEY=your_actual_key_here
   # Replace with your computer's local IP address (e.g., 192.168.1.15)
   NEXTAUTH_URL=http://<YOUR_LOCAL_IP>:3000
   NEXTAUTH_SECRET=fallback-secret-key-change-in-prod
   \`\`\`
2. **Build and Run:**
   \`\`\`bash
   docker-compose up -d --build
   \`\`\`
3. **Access:**
   Open a browser on another device connected to your network and navigate to `http://<YOUR_LOCAL_IP>:3000`.

---

## Production VPS Hosting

For global access, you should deploy the application to a Linux Virtual Private Server (VPS) such as DigitalOcean, Linode, AWS EC2, or Hetzner.

1. **Clone the repository** to your server:
   \`\`\`bash
   git clone <your_repo_url> /opt/sacred-citadel
   cd /opt/sacred-citadel
   \`\`\`

2. **Setup your environment variables:**
   Create a `.env` file:
   \`\`\`env
   ANTHROPIC_API_KEY=your_actual_key_here
   NEXTAUTH_URL=https://yourdomain.com
   # Generate a secure secret using: openssl rand -base64 32
   NEXTAUTH_SECRET=your_secure_random_string
   NODE_ENV=production
   \`\`\`

3. **Start the application:**
   \`\`\`bash
   docker-compose up -d --build
   \`\`\`

---

## Nginx Reverse Proxy & SSL Setup

Because the Docker container exposes the application on port 3000 over HTTP, you need a reverse proxy to serve it over standard web ports (80/443) and secure it with SSL.

1. **Install Nginx and Certbot:**
   \`\`\`bash
   sudo apt update
   sudo apt install nginx certbot python3-certbot-nginx
   \`\`\`

2. **Configure Nginx:**
   Create a new configuration file for your site:
   \`\`\`bash
   sudo nano /etc/nginx/sites-available/citadel
   \`\`\`
   Add the following configuration (replace `yourdomain.com` with your actual domain):
   \`\`\`nginx
   server {
       server_name yourdomain.com;

       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;

           # Forward real IP addresses to Next.js
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   \`\`\`

3. **Enable the site and restart Nginx:**
   \`\`\`bash
   sudo ln -s /etc/nginx/sites-available/citadel /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   \`\`\`

4. **Secure with SSL (Let's Encrypt):**
   \`\`\`bash
   sudo certbot --nginx -d yourdomain.com
   \`\`\`
   Follow the prompts to enable HTTPS. Certbot will automatically update your Nginx configuration.

---

## Data Persistence & Backups

This application uses a local SQLite database (`prisma/dev.db`) for zero-configuration persistence.

### Volumes
The `docker-compose.yml` file is explicitly configured to mount this file from your host machine into the container:
\`\`\`yaml
volumes:
  - ./prisma/dev.db:/app/prisma/dev.db
\`\`\`
**Crucial Note:** Because of how Docker handles file mounts, you MUST ensure that `prisma/dev.db` exists on your host machine *before* running `docker-compose up`. If the file does not exist, Docker will create a *directory* named `dev.db`, which will crash the Prisma client.

If it does not exist, simply create an empty file first:
\`\`\`bash
touch prisma/dev.db
docker-compose up -d --build
\`\`\`

### Backups
To backup your entire forum database, you only need to copy a single file. You can automate this with a simple cron job:
\`\`\`bash
# Example backup command
cp /opt/sacred-citadel/prisma/dev.db /opt/backups/citadel_db_$(date +%F).sqlite
\`\`\`

---

## Performance & Optimization for VPS Hosting

If you are hosting this on a low-end/budget VPS ($5-$10/month) and want to maximize performance so you can access it blazingly fast from any device:

1. **Docker Resource Limits:**
   Prevent the application from eating all your VPS RAM by setting memory limits in your `docker-compose.yml`:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 512M
   ```

2. **Next.js Image Optimization:**
   The `next/image` component dynamically optimizes the 700+ scraped PFPs. This can be CPU intensive on first load. You can add sharp to the Dockerfile to speed this up:
   ```dockerfile
   RUN npm install sharp
   ```

3. **Nginx Caching (Static Assets):**
   Update your Nginx config to heavily cache the CSS, JS, and image assets so they don't hit the Next.js server on every request:
   ```nginx
   location ~* \.(?:ico|css|js|gif|jpe?g|png)$ {
       proxy_pass http://localhost:3000;
       expires 30d;
       add_header Cache-Control "public, no-transform";
   }
   ```

4. **Prisma Connection Pooling:**
   Since SQLite is local, connection pooling isn't as critical as Postgres, but ensure `PRISMA_CLI_QUERY_ENGINE_TYPE=library` is used to prevent excess engine binary spawning on low-memory boxes.

---

## Troubleshooting

### `EADDRINUSE: address already in use :::3000`
Another service on your server is already using port 3000. Edit the `docker-compose.yml` and change the mapping to `8080:3000`. Then update your Nginx configuration to point to `http://localhost:8080`.

### NextAuth Callbacks Failing (Infinite Redirects on Login)
Ensure that `NEXTAUTH_URL` in your `.env` perfectly matches the protocol (http vs https) and domain you are using to access the site. If you are behind an Nginx SSL proxy, `NEXTAUTH_URL` must start with `https://`.

### Missing Styling or 500 Errors
If the site loads but lacks styling, ensure you built the Docker image *after* creating the `dev.db` file and running `npm ci`. Check the container logs using:
\`\`\`bash
docker logs sacred-citadel-app
\`\`\`