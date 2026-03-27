FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (needed for building some python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (stopwords)
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"

COPY . .

# Command to run the bot
CMD ["python", "-m", "bot.main"]
