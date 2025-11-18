// --- DOM Elements ---
const questionElement = document.getElementById('question');
const answerElement = document.getElementById('answer');
const submitElement = document.getElementById('submit');
const feedbackElement = document.getElementById('feedback');
const languageSelect = document.getElementById('language-select');
const hardcoreModeCheckbox = document.getElementById('hardcore-mode');
const brutalModeCheckbox = document.getElementById('brutal-mode');
const imageContainer = document.getElementById('image-container');
const helpButton = document.getElementById('help-button');
const helpModal = document.getElementById('help-modal');
const closeModalButton = document.querySelector('.close-button');
const quizContainer = document.querySelector('.quiz-container');

// --- State & APIs ---
let internalScore = 0; let currentQuestion = null;
const MATH_API_URL = 'https://math.oglimmer.de/v1/calc?expression=';
let TRANSLATE_API_URL = 'https://libretranslate.de/'; // Using a more stable instance
const translationCache = {};

// --- Save/Load, Game Modes (remains the same) ---
function saveProgress() { /* ... */ }
function loadProgress() { /* ... */ }
async function deleteSaveAndReset(messageKey) { /* ... */ }
document.addEventListener('visibilitychange', () => { /* ... */ });
brutalModeCheckbox.addEventListener('change', () => { /* ... */ });
hardcoreModeCheckbox.addEventListener('change', () => { /* ... */ });

// --- Internationalization (i18n) ---
const translations = {
    en: { /* All the english translations */ },
    // Caching other languages to reduce API calls and improve reliability
    es: { title: "Ultra Mega Concurso de Matemáticas", submit_button: "Enviar", help_button: "Ayuda", /* ... and so on */ },
};
const defaultLanguages = [ { code: 'en', name: 'English' }, { code: 'es', name: 'Español' }, { code: 'fr', name: 'Français' }, { code: 'de', name: 'Deutsch' }, { code: 'zh', name: '中文' }];
async function getSupportedLanguages() { try { const response = await fetch(TRANSLATE_API_URL + 'languages'); if (!response.ok) throw new Error('API down'); const languages = await response.json(); populateLanguageDropdown(languages); } catch (error) { console.error('Language API error, using fallback:', error); populateLanguageDropdown(defaultLanguages); } }
function populateLanguageDropdown(languages) { /* ... */ }

async function translateText(key, lang) {
    if (translations[lang] && translations[lang][key]) {
        return translations[lang][key];
    }
    if (lang === 'en') return translations.en[key];

    // Fallback to API if not in local cache
    const englishText = translations.en[key];
    try {
        const response = await fetch(TRANSLATE_API_URL + 'translate', {
            method: 'POST',
            body: JSON.stringify({ q: englishText, source: 'en', target: lang }),
            headers: { 'Content-Type': 'application/json' },
        });
        if (!response.ok) throw new Error('Translate API failed');
        const data = await response.json();
        return data.translatedText;
    } catch (error) {
        console.error('Translation error:', error);
        return englishText;
    }
}

async function translateUI(lang) {
    for (const el of document.querySelectorAll('[data-translate]')) {
        const key = el.getAttribute('data-translate');
        el.textContent = await translateText(key, lang);
    }
    answerElement.placeholder = await translateText('placeholder', lang);
}

// --- Question Engine & Quiz Logic (remains the same) ---
const questionLibrary = { /* ... */ };
const rand = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
function generateQuestion() { /* ... */ }
async function displayQuestion() { /* ... */ }
async function checkAnswer() { /* ... */ }
async function getCorrectAnswer(expression) { /* ... */ }

// --- Event Listeners ---
submitElement.addEventListener('click', checkAnswer);
answerElement.addEventListener('keyup', (e) => { if (e.key === 'Enter') checkAnswer(); });
languageSelect.addEventListener('change', (e) => {
    translateUI(e.target.value);
});
helpButton.addEventListener('click', () => { helpModal.style.display = 'flex'; });
closeModalButton.addEventListener('click', () => { helpModal.style.display = 'none'; });
window.addEventListener('click', (e) => { if (e.target == helpModal) helpModal.style.display = 'none'; });

// --- Initialization ---
loadProgress();
getSupportedLanguages();
displayQuestion();
translateUI('en');
