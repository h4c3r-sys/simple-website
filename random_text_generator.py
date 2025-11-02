import random
import string
import time
import requests
import argparse

def check_word(word, lang='en'):
    """Checks if a word is a valid English word using the Free Dictionary API."""
    if len(word) < 2:  # No need to check single letters or empty strings
        return False
    try:
        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return False

def mode_one():
    """Generates and prints an endless stream of random characters."""
    print("Starting Mode 1... Press Ctrl+C to stop.")
    char_set = string.ascii_letters + string.digits + string.punctuation + ' '
    try:
        while True:
            random_char = random.choice(char_set)
            print(random_char, end='', flush=True)
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nMode 1 stopped.")

def mode_two(limit, lang='en'):
    """Generates a specific number of random characters, finds words, and saves them."""
    print(f"Starting Mode 2 for {limit} characters...")
    char_set = string.ascii_letters + string.digits + string.punctuation + ' '
    found_words_count = 0
    current_word = ""
    generated_text = ""

    with open("found_words.txt", "w") as f:
        for _ in range(limit):
            char = random.choice(char_set)
            generated_text += char
            if char.isalpha():
                current_word += char.lower()
            else:
                if check_word(current_word, lang):
                    found_words_count += 1
                    f.write(current_word + "\n")
                    print(f"\nFound word: {current_word}")
                current_word = ""

    # Check the last word, in case the generation ends with a word
    if check_word(current_word, lang):
        with open("found_words.txt", "a") as f:
            f.write(current_word + "\n")
        found_words_count += 1

    print(f"\nGenerated text: {generated_text}")
    print(f"Mode 2 finished. Found {found_words_count} words. See found_words.txt for the full list.")

def mode_three(lang='en'):
    """Generates endless random characters and finds words in real-time."""
    print("Starting Mode 3... Press Ctrl+C to stop.")
    char_set = string.ascii_letters + string.digits + string.punctuation + ' '
    found_words_count = 0
    current_word = ""

    try:
        with open("found_words_live.txt", "w") as f:
            while True:
                char = random.choice(char_set)
                print(char, end='', flush=True)
                time.sleep(0.01)

                if char.isalpha():
                    current_word += char.lower()
                else:
                    if check_word(current_word, lang):
                        found_words_count += 1
                        f.write(current_word + "\n")
                        f.flush()
                        print(f"\nFound word: {current_word} (Total: {found_words_count})")
                    current_word = ""
    except KeyboardInterrupt:
        # Check the last word before exiting
        if check_word(current_word, lang):
             with open("found_words_live.txt", "a") as f:
                f.write(current_word + "\n")
                found_words_count += 1
                print(f"\nFound one last word before stopping: {current_word}")

        print(f"\nMode 3 stopped. Found a total of {found_words_count} words.")

def mode_four():
    """Generates a cipher puzzle and displays it with the solution."""
    print("Starting Mode 4: Cipher Puzzle")

    # Create a random mapping from numbers to letters
    letters = list(string.ascii_lowercase)
    random.shuffle(letters)
    # Create a reverse mapping for encoding
    reverse_cipher = {letter: num for num, letter in zip(range(1, 27), letters)}

    # Hardcoded list of words
    words = ["python", "jules", "cipher", "random", "developer"]
    secret_word = random.choice(words)

    # Encode the secret word
    encoded_word = [str(reverse_cipher[letter]) for letter in secret_word]

    # Display the puzzle and solution
    print(f"Your puzzle is: {' '.join(encoded_word)}")
    print("Try to solve it! The solution is below.")
    print("-" * 20)
    print("Solution:")
    print(f"The secret word was: {secret_word}")
    print("Cipher Key:")
    # Create the forward cipher for displaying the key
    cipher = {num: letter for letter, num in reverse_cipher.items()}
    for number in sorted(cipher.keys()):
        print(f"{number}: {cipher[number]}")

def main():
    parser = argparse.ArgumentParser(description="Generate and analyze random text.")
    parser.add_argument("mode", type=int, choices=[1, 2, 3, 4], help="The mode to run.")
    parser.add_argument("-l", "--limit", type=int, help="The number of characters to generate in Mode 2.")
    parser.add_argument("--lang", type=str, default="en", help="The language to check for words in (e.g., en, es, fr).")
    args = parser.parse_args()

    if args.mode == 1:
        mode_one()
    elif args.mode == 2:
        if args.limit:
            mode_two(args.limit, args.lang)
        else:
            print("Mode 2 requires a limit. Use -l or --limit to specify the number of characters.")
    elif args.mode == 3:
        mode_three(args.lang)
    elif args.mode == 4:
        mode_four()

if __name__ == "__main__":
    main()
