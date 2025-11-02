import random
import string
import time
import requests

def get_word_definition(word, lang='en'):
    """
    Retrieves the definition of a word using the Free Dictionary API.
    Returns the definition string if found, otherwise None.
    """
    if len(word) < 2:  # No need to check single letters or empty strings
        return None
    try:
        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word}")
        if response.status_code == 200:
            data = response.json()
            # Navigate through the JSON to find the first definition
            if data and isinstance(data, list):
                meanings = data[0].get('meanings')
                if meanings and isinstance(meanings, list):
                    definitions = meanings[0].get('definitions')
                    if definitions and isinstance(definitions, list):
                        definition = definitions[0].get('definition')
                        if definition:
                            return definition
            return "No definition found." # Word exists but no definition in expected format
        else:
            return None # Word not found
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

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

    with open("found_words.txt", "w", encoding="utf-8") as f:
        for _ in range(limit):
            char = random.choice(char_set)
            generated_text += char
            if char.isalpha():
                current_word += char.lower()
            else:
                definition = get_word_definition(current_word, lang)
                if definition:
                    found_words_count += 1
                    f.write(f"Word: {current_word}\n")
                    f.write(f"Definition: {definition}\n\n")
                    print(f"\nFound word: {current_word}")
                current_word = ""

    # Check the last word, in case the generation ends with a word
    definition = get_word_definition(current_word, lang)
    if definition:
        with open("found_words.txt", "a", encoding="utf-8") as f:
            f.write(f"Word: {current_word}\n")
            f.write(f"Definition: {definition}\n\n")
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
        with open("found_words_live.txt", "w", encoding="utf-8") as f:
            while True:
                char = random.choice(char_set)
                print(char, end='', flush=True)
                time.sleep(0.01)

                if char.isalpha():
                    current_word += char.lower()
                else:
                    definition = get_word_definition(current_word, lang)
                    if definition:
                        found_words_count += 1
                        f.write(f"Word: {current_word}\n")
                        f.write(f"Definition: {definition}\n\n")
                        f.flush()
                        print(f"\nFound word: {current_word} (Total: {found_words_count})")
                    current_word = ""
    except KeyboardInterrupt:
        # Check the last word before exiting
        definition = get_word_definition(current_word, lang)
        if definition:
             with open("found_words_live.txt", "a", encoding="utf-8") as f:
                f.write(f"Word: {current_word}\n")
                f.write(f"Definition: {definition}\n\n")
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
    while True:
        print("\nSelect a mode:")
        print("1. Generate endless random characters")
        print("2. Generate a specific number of random characters and find words")
        print("3. Generate endless random characters and find words in real-time")
        print("4. Cipher puzzle")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            mode_one()
        elif choice == '2':
            try:
                limit = int(input("Enter the number of characters to generate: "))
                lang = input("Enter the language for word checking (e.g., en, es, fr): ")
                mode_two(limit, lang)
            except ValueError:
                print("Invalid input for the character limit. Please enter a number.")
        elif choice == '3':
            lang = input("Enter the language for word checking (e.g., en, es, fr): ")
            mode_three(lang)
        elif choice == '4':
            mode_four()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
