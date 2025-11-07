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
let TRANSLATE_API_URL = 'https://translate.argosopentech.com/';

// --- Save/Load & Game Modes ---
// Manages the user's progress using localStorage for persistence.
function saveProgress() { if (!localStorage.getItem('hardcoreReset')) localStorage.setItem('quizProgress', internalScore.toString()); }
function loadProgress() { if (localStorage.getItem('hardcoreReset') === 'true') { localStorage.removeItem('quizProgress'); localStorage.removeItem('hardcoreReset'); internalScore = 0; return; } const savedScore = localStorage.getItem('quizProgress'); if (savedScore) internalScore = parseInt(savedScore, 10); }

// Resets the user's progress. Sets a tamper-evident flag to prevent save restoration.
async function deleteSaveAndReset(messageKey) {
    localStorage.removeItem('quizProgress');
    localStorage.setItem('hardcoreReset', 'true');
    internalScore = 0;

    quizContainer.style.animation = 'flash-red 0.5s';
    setTimeout(() => quizContainer.style.animation = '', 500);

    const lang = languageSelect.value;
    feedbackElement.innerHTML = `<span style="color: purple; font-weight: bold;">${await translateText(translations.en[messageKey], lang)}</span>`;

    submitElement.disabled = true;
    answerElement.disabled = true;

    setTimeout(() => window.location.reload(), 3000);
}

// Event listener for tab/window switching to enforce hardcore modes.
document.addEventListener('visibilitychange', () => { if (document.hidden && (hardcoreModeCheckbox.checked || brutalModeCheckbox.checked)) deleteSaveAndReset('cheating_feedback'); });

// Logic to ensure Brutal Mode implies Hardcore Mode.
brutalModeCheckbox.addEventListener('change', () => { if (brutalModeCheckbox.checked) hardcoreModeCheckbox.checked = true; });
hardcoreModeCheckbox.addEventListener('change', () => { if (!hardcoreModeCheckbox.checked) brutalModeCheckbox.checked = false; });

// --- Internationalization (i18n) ---
const translations = { /* ... same as before ... */ };
const defaultLanguages = [ /* ... same as before ... */ ];
async function getSupportedLanguages() { /* ... same as before ... */ }
function populateLanguageDropdown(languages) { /* ... same as before ... */ }
async function translateText(text, targetLang) { /* ... same as before ... */ }
async function translateUI(lang) { /* ... same as before ... */ }

// --- Question Engine & Quiz Logic ---
const questionLibrary = { /* ... same as before ... */ };
const rand = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
function generateQuestion() { /* ... same as before ... */ }
async function displayQuestion() { /* ... same as before ... */ }
async function checkAnswer() {
    const userAnswer = answerElement.value.trim();
    const correctAnswer = await getCorrectAnswer(currentQuestion.answerExpression);
    const lang = languageSelect.value;
    const isCorrect = userAnswer == correctAnswer;

    if (isCorrect) {
        internalScore++;
        saveProgress();
        feedbackElement.textContent = await translateText(translations.en.correct_feedback, lang);
        feedbackElement.style.color = 'green';
    } else {
        if (brutalModeCheckbox.checked) {
            await deleteSaveAndReset('wrong_answer_feedback_brutal');
            return;
        }
        feedbackElement.textContent = await translateText(translations.en.incorrect_feedback, lang);
        feedbackElement.style.color = 'red';
    }
    answerElement.value = '';
    setTimeout(displayQuestion, isCorrect ? 1000 : 2000);
}
async function getCorrectAnswer(expression) { /* ... same as before ... */ }

// --- Event Listeners ---
submitElement.addEventListener('click', checkAnswer);
answerElement.addEventListener('keyup', (e) => { if (e.key === 'Enter') checkAnswer(); });
languageSelect.addEventListener('change', (e) => translateUI(e.target.value));
helpButton.addEventListener('click', () => { helpModal.style.display = 'flex'; });
closeModalButton.addEventListener('click', () => { helpModal.style.display = 'none'; });
window.addEventListener('click', (e) => { if (e.target == helpModal) helpModal.style.display = 'none'; });

// --- Initialization ---
loadProgress();
getSupportedLanguages();
displayQuestion();
translateUI('en');
