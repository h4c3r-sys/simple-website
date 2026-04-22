# Notes for AI Assistants (Cursor / Antigravity)

When assisting with bug fixes, feature development, or maintenance on this repository, please adhere to the following strict guidelines. This application is designed to emulate the exact microservice architecture of Discord, employing high-security End-to-End Encryption.

## 1. Tech Stack Overview
- **Database:** ScyllaDB (Used for massive scalability, matching Discord's persistence layer).
- **Frontend:** React (Handling client-side E2EE encryption/decryption, UI).
- **Backend Services:**
  - `backend/gateway` (Elixir): Handles persistent WebSocket connections and real-time event dispatching.
  - `backend/api` (Go): The main REST API handling CRUD operations (Users, Servers, Channels).
  - `backend/encryption` (Rust): Key distribution and verification microservice.
  - `backend/worker` (Python): Background tasks and processing.
  - `backend/native` (C++): High-performance native bindings / connectors.

## 2. Core Principles
- **End-to-End Encryption (E2EE):** The backend MUST NEVER see plaintext messages. All encryption (AES-256-GCM) and key exchanges (X25519) must occur on the client side (React). The backend only stores and forwards ciphertext.
- **Microservice Networking:** Services communicate with each other via internal Docker networks. External clients only interact with the React frontend, the Go API (via REST), and the Elixir Gateway (via WebSockets).
- **State Management:** WebSockets (Elixir) are stateless regarding data storage; all persistent data must be routed to the Go API or directly to ScyllaDB.

## 3. Bug Fixing Protocol
1. **Identify the Service:** Trace the bug to the specific language/service layer. (e.g., Is it a real-time issue? Check Elixir. Is it an encryption key mismatch? Check React/Rust).
2. **Review Logs:** Instruct the user to check Docker container logs (`docker logs <container_name>`) before proposing sweeping code changes.
3. **Database Schema:** ScyllaDB requires specific querying patterns (partition keys vs. clustering keys). Do not attempt to write complex relational `JOIN` queries.
4. **Security First:** Never propose changes that downgrade cryptographic standards or expose keys to the backend.

Keep these principles in mind when modifying code in this repository.
