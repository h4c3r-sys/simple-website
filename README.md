# Viral Product Hunter

A powerful tool to discover viral tech gadgets on social media, analyze their buying intent with AI, and automatically find suppliers on AliExpress.

## Features

-   **🔍 Trend Scanner:** Searches the web (TikTok, Instagram, Reddit) for viral tech trends.
-   **🤖 AI Analysis:** Uses Google Gemini AI to identify the product, estimate a "Hype Score" (0-100), and explain why it's viral.
-   **🛒 Auto-Sourcing:** Automatically finds "Buy Now" links on AliExpress for approved products.
-   **⚡ Modern UI:** Fast, dark-mode React dashboard.
-   **🐳 Dockerized:** Ready to deploy with one command.

## Quick Start (Docker)

The easiest way to run the app is with Docker Compose.

1.  **Clone the repository.**
2.  **Set your Gemini API Key:**
    Open `docker-compose.yml` and replace `${GEMINI_API_KEY}` with your key, or set it in your environment:
    ```bash
    export GEMINI_API_KEY="your_key_here"
    ```
3.  **Run the app:**
    ```bash
    docker-compose up --build
    ```
4.  **Open the dashboard:**
    Visit `http://localhost:5173` in your browser.

## Manual Setup

### Backend (Python/FastAPI)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="your_key_here"
uvicorn main:app --reload
```
The backend runs on `http://localhost:8000`.

### Frontend (React/Vite)

```bash
cd frontend
npm install
npm run dev
```
The frontend runs on `http://localhost:5173`.

## How It Works

1.  Click **"Scan for Viral Trends"**. The backend searches the web for current viral topics.
2.  **AI Analysis** processes the search results to filter out noise and identify actual products.
3.  Review the feed. If you see a product you like with a high Hype Score, click **"Approve"**.
4.  The system searches AliExpress and returns direct links to purchase the item.

## Tech Stack

-   **Backend:** FastAPI, DuckDuckGo Search, Google Generative AI (Gemini)
-   **Frontend:** React, Vite, Tailwind CSS
-   **Infrastructure:** Docker, Docker Compose
