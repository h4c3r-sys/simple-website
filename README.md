# AI Business Market Analyzer

A powerful hybrid tool (Web UI + Python Backend) to generate business ideas and analyze their market viability using Google's Gemini AI, web search, social media signals, and email feedback.

## Features

1.  **Generate Business Ideas**: Enter a niche (e.g., "Sustainable Coffee"), and the AI will analyze current trends and social discourse to propose a unique business model.
2.  **Analyze Market**: Enter a specific business idea, and the tool will:
    *   Search the web for competitors.
    *   Scan social media (Reddit/Twitter/Instagram) for sentiment.
    *   (Optional) Check your email inbox for customer feedback.
    *   Synthesize all data into a comprehensive report.
3.  **Email Campaign Manager**:
    *   Send bulk emails from an Excel list.
    *   Check your inbox for responses and use AI to summarize the feedback.

## Setup & Deployment

### Prerequisites
*   Docker & Docker Compose installed.
*   **Google Gemini API Key** (Get it from Google AI Studio).
*   (Optional) SMTP/IMAP credentials if using the email features.

### Running with Docker

1.  **Clone the repository.**
2.  **Set Environment Variables**:
    *   Create a `.env` file or modify `docker-compose.yml`.
    *   `GEMINI_API_KEY`: Required for AI.
    *   `EMAIL_USER`, `EMAIL_PASSWORD`, `EMAIL_HOST`: Required for email.

3.  **Run the container**:
    ```bash
    docker-compose up --build
    ```

4.  **Access the App**:
    *   Open your browser to `http://localhost:8000`.

### Manual Run (No Docker)

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the server:
    ```bash
    uvicorn backend.main:app --reload
    ```
