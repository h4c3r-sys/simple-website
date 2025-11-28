import re
import pandas as pd
import numpy as np
import os
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import openai
import google.generativeai as genai

# Basic seed list of spam words to help the bootstrap process.
# These act as a "heuristic" to identify initial spam messages,
# allowing the ML model to learn *other* associated words.
SEED_SPAM_WORDS = {
    "nitro", "steam", "gift", "free", "discord", "airdrop", "crypto", "bitcoin",
    "giveaway", "claim", "month", "premium", "click", "link", "hack", "cheat",
    "password", "login", "verify", "support", "urgent", "winner", "congratulations",
    "won", "selected", "offer", "limited", "expires", "bank", "account", "transfer",
    "invest", "earning", "profit", "partners", "collaboration", "dm", "promotion"
}

class SpamAnalyzer:
    """
    Handles the logic for identifying spam keywords from message history.
    Supports a hybrid approach:
    1. Heuristics (Cold Start): Uses seed words/links to guess what is spam.
    2. Analysis: Uses either LLMs (OpenAI/Gemini) or local TF-IDF to find distinctive keywords.
    """
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        # Add common discord filler/slang to stop words so they aren't flagged
        self.stop_words.update(['im', 'dont', 'cant', 'http', 'https', 'www', 'com', 'net', 'org'])

        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")

    def preprocess(self, text):
        """Basic text cleaning: lowercase, remove URLs, remove special chars."""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = " ".join(text.split())
        return text

    def analyze_and_suggest_bans(self, messages_df):
        """
        Analyzes a DataFrame of messages and returns a list of suggested ban words.

        Strategy:
        1. Preprocess text.
        2. Assign a 'Spam Score' based on heuristics (links + seed words).
        3. Split data into 'Likely Spam' and 'Likely Ham' (Clean).
        4. Use ML (LLM or TF-IDF) to find words unique to the 'Likely Spam' set.
        """
        if messages_df.empty:
            return []

        logging.info(f"Starting analysis on {len(messages_df)} messages.")

        # 1. Preprocess
        messages_df['clean_text'] = messages_df['content'].apply(self.preprocess)
        messages_df = messages_df[messages_df['clean_text'].str.strip().astype(bool)]

        if messages_df.empty:
            return []

        # 2. Heuristic Labeling (Common to both methods)
        # We need this because we don't have a pre-labeled dataset (0=ham, 1=spam).
        # We guess labels to bootstrap the learning process.
        def simple_spam_score(row):
            text = row['clean_text']
            content = row['content'].lower()
            score = 0

            # Links are high risk in cold DMS/spam channels
            if "http" in content or "www." in content:
                score += 2

            # Check for matches against our hardcoded seed list
            tokens = set(text.split())
            matches = tokens.intersection(SEED_SPAM_WORDS)
            score += len(matches) * 1.5

            # Low entropy check: Spam often repeats the same char or has low vocabulary variety
            if len(text) > 0 and len(set(text)) / len(text) < 0.5:
                score += 2
            return score

        messages_df['spam_score'] = messages_df.apply(simple_spam_score, axis=1)

        # Determine the cutoff for what we consider "Spam" for this training run.
        # We take the top 10% most suspicious messages, or at least those with a score > 3.
        threshold = max(messages_df['spam_score'].quantile(0.90), 3.0)

        spam_msgs = messages_df[messages_df['spam_score'] >= threshold]
        ham_msgs = messages_df[messages_df['spam_score'] < threshold]

        logging.info(f"Identified {len(spam_msgs)} potential spam messages and {len(ham_msgs)} clean messages.")

        if spam_msgs.empty:
            logging.info("No potential spam found via heuristics. Returning empty.")
            return []

        # 3. Choose Analysis Method
        # Prioritize OpenAI -> Gemini -> Local
        if self.openai_key:
            logging.info("Using OpenAI for analysis.")
            try:
                return self.analyze_with_openai(spam_msgs, ham_msgs)
            except Exception as e:
                logging.error(f"OpenAI analysis failed: {e}. Falling back to local.")

        if self.gemini_key:
            logging.info("Using Gemini for analysis.")
            try:
                return self.analyze_with_gemini(spam_msgs, ham_msgs)
            except Exception as e:
                logging.error(f"Gemini analysis failed: {e}. Falling back to local.")

        logging.info("Using local TF-IDF analysis.")
        return self.analyze_local(spam_msgs, ham_msgs, messages_df)

    def analyze_local(self, spam_msgs, ham_msgs, all_msgs):
        """
        Legacy TF-IDF logic.
        Calculates Term Frequency-Inverse Document Frequency.
        Then calculates a ratio: (Score in Spam) / (Score in Ham).
        Words with a high ratio are spam indicators.
        """
        vectorizer = TfidfVectorizer(stop_words=list(self.stop_words), min_df=2, max_features=1000)
        try:
            # Fit vocabulary on all data
            all_corpus = all_msgs['clean_text'].tolist()
            X = vectorizer.fit_transform(all_corpus)
            feature_names = np.array(vectorizer.get_feature_names_out())

            # Calculate scores for Spam group
            spam_corpus = spam_msgs['clean_text'].tolist()
            if not spam_corpus: return []
            X_spam = vectorizer.transform(spam_corpus)
            spam_tfidf_sum = np.asarray(X_spam.sum(axis=0)).flatten()

            # Calculate scores for Ham group
            ham_corpus = ham_msgs['clean_text'].tolist()
            if not ham_corpus:
                ham_tfidf_sum = np.zeros_like(spam_tfidf_sum)
            else:
                X_ham = vectorizer.transform(ham_corpus)
                ham_tfidf_sum = np.asarray(X_ham.sum(axis=0)).flatten()

            # Normalize by size of group to be fair
            spam_tfidf_norm = spam_tfidf_sum / (len(spam_msgs) + 1)
            ham_tfidf_norm = ham_tfidf_sum / (len(ham_msgs) + 1)

            # The Magic Ratio: How much more frequent is this word in Spam vs Ham?
            ratio = spam_tfidf_norm / (ham_tfidf_norm + 0.0001)

            words_df = pd.DataFrame({
                'word': feature_names,
                'spam_score': spam_tfidf_norm,
                'ratio': ratio
            })

            # Filter: Must actually appear in spam, and be distinctive
            words_df = words_df[words_df['spam_score'] > 0.01]
            words_df['final_metric'] = words_df['ratio'] * words_df['spam_score']

            return words_df.sort_values(by='final_metric', ascending=False).head(30)['word'].tolist()
        except ValueError as e:
            logging.error(f"Error during vectorization: {e}")
            return []

    def _prepare_llm_prompt(self, spam_msgs, ham_msgs):
        """
        Constructs a prompt for the LLM.
        We provide samples of what we think is spam vs normal chat,
        and ask the LLM to use its vast training data to pick out the best keywords.
        """
        # Sample messages to fit in context window
        spam_sample = spam_msgs.sample(n=min(15, len(spam_msgs)))['content'].tolist()
        ham_sample = ham_msgs.sample(n=min(15, len(ham_msgs)))['content'].tolist()

        prompt = (
            "I have two lists of Discord messages. One list contains potential spam/scam messages, "
            "and the other contains normal user conversation.\n\n"
            "--- POTENTIAL SPAM ---\n" + "\n".join([f"- {m}" for m in spam_sample]) + "\n\n"
            "--- NORMAL CHAT ---\n" + "\n".join([f"- {m}" for m in ham_sample]) + "\n\n"
            "Task: Identify 10 to 20 specific keywords or short phrases (1-2 words) that are highly indicative of the spam messages "
            "but rarely appear in normal chat. Focus on scam triggers like 'nitro', 'claim', specific domains, or urgency words. "
            "Return ONLY the list of words separated by commas, no other text."
        )
        return prompt

    def analyze_with_openai(self, spam_msgs, ham_msgs):
        client = openai.OpenAI(api_key=self.openai_key)
        prompt = self._prepare_llm_prompt(spam_msgs, ham_msgs)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful data analyst bot."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3
        )
        content = response.choices[0].message.content
        return [w.strip().lower() for w in content.split(',') if w.strip()]

    def analyze_with_gemini(self, spam_msgs, ham_msgs):
        genai.configure(api_key=self.gemini_key)
        # Switch to gemini-2.0-flash as gemini-pro is deprecated/unavailable
        # or use gemini-1.5-flash as a safe fallback
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception:
             logging.warning("gemini-2.0-flash not found, falling back to gemini-1.5-flash")
             model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = self._prepare_llm_prompt(spam_msgs, ham_msgs)

        try:
            response = model.generate_content(prompt)
            content = response.text
            return [w.strip().lower() for w in content.split(',') if w.strip()]
        except Exception as e:
            # Helpful debug info for user
            logging.error(f"Gemini generation failed: {e}")
            logging.info("Attempting to list available models for debugging...")
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        logging.info(f"Available model: {m.name}")
            except Exception as list_err:
                logging.error(f"Could not list models: {list_err}")
            raise e
