import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from nltk.corpus import stopwords
import logging

# Basic seed list of spam words to help the bootstrap process
# These are words commonly found in scams, spam, and malicious links.
SEED_SPAM_WORDS = {
    "nitro", "steam", "gift", "free", "discord", "airdrop", "crypto", "bitcoin",
    "giveaway", "claim", "month", "premium", "click", "link", "hack", "cheat",
    "password", "login", "verify", "support", "urgent", "winner", "congratulations",
    "won", "selected", "offer", "limited", "expires", "bank", "account", "transfer",
    "invest", "earning", "profit", "partners", "collaboration", "dm", "promotion"
}

class SpamAnalyzer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        # Add common discord filler
        self.stop_words.update(['im', 'dont', 'cant', 'http', 'https', 'www', 'com', 'net', 'org'])

    def preprocess(self, text):
        """Basic text cleaning."""
        if not text:
            return ""
        # Lowercase
        text = text.lower()
        # Remove URLs (but we note them elsewhere)
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove special chars and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Remove extra spaces
        text = " ".join(text.split())
        return text

    def analyze_and_suggest_bans(self, messages_df):
        """
        Analyzes a DataFrame of messages and returns a list of suggested ban words.
        messages_df columns: ['content', 'is_bot', 'author_id']
        """
        if messages_df.empty:
            return []

        logging.info(f"Starting analysis on {len(messages_df)} messages.")

        # 1. Preprocess
        messages_df['clean_text'] = messages_df['content'].apply(self.preprocess)

        # Filter out empty messages
        messages_df = messages_df[messages_df['clean_text'].str.strip().astype(bool)]

        if messages_df.empty:
            return []

        # 2. Heuristic Labeling (The "Cold Start" problem)
        # We try to identify "potential spam" messages based on seed words and patterns (like links).
        # We assume messages with links + seed words are likely spam.

        def simple_spam_score(row):
            text = row['clean_text']
            content = row['content'].lower()
            score = 0

            # Check for links
            if "http" in content or "www." in content:
                score += 2

            # Check for seed words
            tokens = set(text.split())
            matches = tokens.intersection(SEED_SPAM_WORDS)
            score += len(matches) * 1.5

            # Check for excessive repetition (common in spam)
            if len(text) > 0 and len(set(text)) / len(text) < 0.5: # Low entropy
                score += 2

            # Check for "rapid fire" / bot behavior (handled better if we had time delta,
            # but here we rely on content)

            return score

        messages_df['spam_score'] = messages_df.apply(simple_spam_score, axis=1)

        # Define threshold for "Likely Spam" vs "Likely Ham"
        # Top 10% of spam scores or score > X
        threshold = messages_df['spam_score'].quantile(0.90)
        # Ensure threshold is at least some minimum to avoid flagging normal convos as spam in clean servers
        threshold = max(threshold, 3.0)

        spam_msgs = messages_df[messages_df['spam_score'] >= threshold]
        ham_msgs = messages_df[messages_df['spam_score'] < threshold]

        logging.info(f"Identified {len(spam_msgs)} potential spam messages and {len(ham_msgs)} clean messages.")

        if spam_msgs.empty:
            return []

        # 3. TF-IDF Analysis to find words unique to the "Spam" set
        # We want words that are frequent in Spam but rare in Ham.

        vectorizer = TfidfVectorizer(stop_words=list(self.stop_words), min_df=2, max_features=1000)

        try:
            # Fit on all data to get vocabulary
            all_corpus = messages_df['clean_text'].tolist()
            X = vectorizer.fit_transform(all_corpus)
            feature_names = np.array(vectorizer.get_feature_names_out())

            # Transform just the spam messages
            spam_corpus = spam_msgs['clean_text'].tolist()
            if not spam_corpus:
                 return []

            X_spam = vectorizer.transform(spam_corpus)

            # Sum tf-idf scores for each word in spam corpus
            spam_tfidf_sum = np.asarray(X_spam.sum(axis=0)).flatten()

            # Transform just the ham messages
            ham_corpus = ham_msgs['clean_text'].tolist()
            if not ham_corpus:
                # If everything is spam (unlikely), just take top spam words
                ham_tfidf_sum = np.zeros_like(spam_tfidf_sum)
            else:
                X_ham = vectorizer.transform(ham_corpus)
                ham_tfidf_sum = np.asarray(X_ham.sum(axis=0)).flatten()

            # 4. Calculate a "Spamminess" Ratio
            # (Spam Score) / (Ham Score + epsilon)
            # We want words that have high weight in spam and low weight in ham.

            # Normalize to account for different dataset sizes
            spam_tfidf_norm = spam_tfidf_sum / (len(spam_msgs) + 1)
            ham_tfidf_norm = ham_tfidf_sum / (len(ham_msgs) + 1)

            ratio = spam_tfidf_norm / (ham_tfidf_norm + 0.0001) # Avoid div by zero

            # Create a dataframe of words and their scores
            words_df = pd.DataFrame({
                'word': feature_names,
                'spam_score': spam_tfidf_norm,
                'ham_score': ham_tfidf_norm,
                'ratio': ratio
            })

            # Filter for words that actually appear in spam
            words_df = words_df[words_df['spam_score'] > 0.01]

            # Sort by Ratio (most distinguishing for spam)
            # But also consider raw spam frequency (we don't want super rare words that happened to appear once in spam)
            words_df['final_metric'] = words_df['ratio'] * words_df['spam_score']

            suggested_df = words_df.sort_values(by='final_metric', ascending=False).head(30)

            suggestions = suggested_df['word'].tolist()

            # Filter out words that are already in SEED_SPAM_WORDS to avoid redundancy (optional,
            # but user might want to ban new words).
            # Actually, we should return them so the user can ban them if not already banned.

            return suggestions

        except ValueError as e:
            logging.error(f"Error during vectorization: {e}")
            return []
