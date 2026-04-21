# Hosting and Deployment Guide

This guide explains how to host your private, highly secure chat application using Docker. It also includes an overview of the advanced encryption algorithms utilized in this application.

## 1. Hosting Requirements
- A server or Virtual Private Server (VPS) running Linux (Ubuntu 22.04 LTS recommended).
- Docker and Docker Compose installed.
- At least 8GB RAM (ScyllaDB and Elixir/Rust/Go microservices require significant memory).
- A domain name (optional but recommended for SSL/TLS).

## 2. Deployment Steps

### Step 1: Install Docker
If you are starting on a fresh server, install Docker:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### Step 2: Clone the Repository
Clone the codebase to your server:
```bash
git clone <your-repo-url> chat-app
cd chat-app
```

### Step 3: Configure Environment Variables
Create a `.env` file in the root directory (where `docker-compose.yml` is located) and set your secure secrets:
```env
# Example .env configuration
DB_KEYSPACE=discord_clone
JWT_SECRET=generate_a_very_long_random_string_here
```

### Step 4: Run Docker Compose
Start all microservices and the ScyllaDB database using Docker Compose in detached mode:
```bash
docker-compose up -d --build
```
This command will pull the required base images, build the Go, Rust, Elixir, Python, and React applications, and network them together securely.

### Step 5: Verify Running Services
Check that all containers are healthy:
```bash
docker-compose ps
```

---

## Explanation of Encryption Algorithms

This application uses End-to-End Encryption (E2EE), meaning the backend databases and microservices **cannot read your messages**. Only the sender and the recipient(s) possess the keys to decrypt the message payloads.

We achieve this "immunity" to data breaches by utilizing two state-of-the-art cryptographic algorithms:

### 1. Key Exchange: X25519 (Elliptic Curve Diffie-Hellman)
- **What it is:** X25519 is an elliptic curve used in the Diffie-Hellman (ECDH) key agreement protocol.
- **How it works:** When you want to chat with a friend, both of your devices generate a mathematically linked pair of keys (a Public Key and a Private Key). You exchange Public Keys over the internet. Using your friend's Public Key and your Private Key, your device calculates a "Shared Secret." Your friend's device does the same math using your Public Key and their Private Key, arriving at the *exact same Shared Secret*.
- **Why it's secure:** Even if an attacker intercepts the Public Keys in transit, the underlying elliptic curve mathematics makes it practically impossible to calculate the Shared Secret without the Private Keys (which never leave your device).

### 2. Message Encryption: AES-256-GCM
- **What it is:** Advanced Encryption Standard with a 256-bit key in Galois/Counter Mode. This is military-grade encryption used by governments and financial institutions worldwide.
- **How it works:** Once X25519 generates the Shared Secret, this secret is used to derive an AES-256 key. Every time you send a message, AES scrambles your plaintext into unreadable ciphertext.
- **Why GCM (Galois/Counter Mode) is crucial:** GCM doesn't just encrypt the data; it also provides **Authentication**. It generates an authentication tag that guarantees the message has not been tampered with in transit. If an attacker tries to alter even a single byte of the encrypted message, the decryption process will fail and reject the message, protecting you from manipulation attacks.

Combined, these algorithms ensure that your private communications remain strictly private.
