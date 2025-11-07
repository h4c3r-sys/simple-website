// --- DOM Elements ---
const questionElement = document.getElementById('question');
const answerElement = document.getElementById('answer');
const submitElement = document.getElementById('submit');
const feedbackElement = document.getElementById('feedback');
const languageSelect = document.getElementById('language-select');

// --- State ---
let internalScore = 0;
let currentQuestion = null;
const MATH_API_URL = 'https://math.oglimmer.de/v1/calc?expression=';
let TRANSLATE_API_URL = 'https://translate.argosopentech.com/';

// --- Internationalization (i18n) ---
const translations = {
    en: { title: "Ultra Mega Math Quiz", submit_button: "Submit", correct_feedback: "Correct!", incorrect_feedback: "Incorrect. A similar question will be generated.", placeholder: "Your answer...", },
    es: { title: "Ultra Mega Concurso de Matemáticas", submit_button: "Enviar", correct_feedback: "¡Correcto!", incorrect_feedback: "Incorrecto. Se generará una pregunta similar.", placeholder: "Tu respuesta...", }
};
const defaultLanguages = [ { code: 'en', name: 'English' }, { code: 'es', name: 'Español' }, { code: 'fr', name: 'Français' }, { code: 'de', name: 'Deutsch' }, { code: 'zh', name: '中文' }];

async function getSupportedLanguages() { try { const response = await fetch(TRANSLATE_API_URL + 'languages'); if (!response.ok) throw new Error('API down'); const languages = await response.json(); populateLanguageDropdown(languages); } catch (error) { console.error('Language API error, using fallback:', error); populateLanguageDropdown(defaultLanguages); } }
function populateLanguageDropdown(languages) { languageSelect.innerHTML = ''; languages.forEach(lang => { const option = document.createElement('option'); option.value = lang.code; option.textContent = lang.name; if (lang.code === 'en') option.selected = true; languageSelect.appendChild(option); }); }
async function translateText(text, targetLang) { if (targetLang === 'en') return text; const key = Object.keys(translations.en).find(k => translations.en[k] === text); if (key && translations[targetLang] && translations[targetLang][key]) return translations[targetLang][key]; try { const response = await fetch(TRANSLATE_API_URL + 'translate', { method: 'POST', body: JSON.stringify({ q: text, source: 'en', target: targetLang }), headers: { 'Content-Type': 'application/json' }, }); if (!response.ok) throw new Error('Translate API failed'); const data = await response.json(); return data.translatedText; } catch (error) { console.error('Translation error:', error); return text; } }
async function translateUI(lang) { for (const el of document.querySelectorAll('[data-translate]')) { const key = el.getAttribute('data-translate'); el.textContent = await translateText(translations.en[key], lang); } answerElement.placeholder = await translateText(translations.en.placeholder, lang); }

// --- Question Generation Engine ---
const rand = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
const questionLibrary = {
    arithmetic: [
        { level: 0, template: 'a + b', vars: { a: [1, 10], b: [1, 10] } },
        { level: 5, template: 'a - b', vars: { a: [10, 30], b: [1, 20] } },
        { level: 10, template: 'a * b', vars: { a: [2, 12], b: [2, 12] } },
        { level: 15, template: 'a / b', generator: () => { const b = rand(2, 15); return { a: b * rand(2, 10), b: b }; } },
        { level: 20, template: 'a + b * c', vars: { a: [1, 15], b: [2, 8], c: [2, 8] } },
        { level: 25, template: '(a + b) * c', vars: { a: [1, 10], b: [1, 10], c: [2, 6] } },
        { level: 30, template: 'a / b + c', generator: () => { const b = rand(2, 10); return { a: b * rand(2, 10), b: b, c: rand(1, 20) }; } },
        { level: 35, template: 'a^2 + b^2', vars: { a: [3, 10], b: [3, 10] } },
    ],
    algebra: [
        { level: 40, template: 'a*x + b = c', solveFor: 'x', generator: () => { const a = rand(2, 10); const x = rand(1, 8); const b = rand(-10, 10); return { a, x, b, c: a * x + b }; } },
        { level: 45, template: 'a*(x+b) = c', solveFor: 'x', generator: () => { const a = rand(2, 8); const x = rand(1, 6); const b = rand(-5, 5); return {a, x, b, c: a*(x+b)}; }},
        { level: 50, template: '(x+a)(x+b) = 0', solveFor: 'x', isMultiAnswer: true, generator: () => { const a = rand(-8, 8); let b = rand(-8, 8); while (a === b) { b = rand(-8, 8); } return { a, b, x: [-a, -b] }; } },
        { level: 55, template: 'sqrt(x) = a', solveFor: 'x', generator: () => { const a = rand(3,12); return { a, x: a*a }; }},
        { level: 60, template: 'log_a(b)', generator: () => { const a = 2; const b = Math.pow(a, rand(2,5)); return {a, b, answer: Math.log(b)/Math.log(a) }; }},
    ],
    geometry: [
        { level: 65, template: 'Area of square with side a', vars: { a: [5, 20] }, answerExpr: 'a*a' },
        { level: 70, template: 'Area of rectangle with sides a and b', vars: { a: [5, 20], b: [5, 20] }, answerExpr: 'a*b' },
        { level: 75, template: 'Area of circle with radius r (pi=3.14)', vars: { r: [3, 15] }, answerExpr: '3.14*r*r' },
    ],
    trigonometry: [
        { level: 80, template: 'sin(a)', isFixed: true, generator: () => { const angles = {0:0, 30:0.5, 90:1}; const a = Object.keys(angles)[rand(0,2)]; return { text: `sin(${a} degrees)`, answer: angles[a] }; }},
        { level: 85, template: 'cos(a)', isFixed: true, generator: () => { const angles = {0:1, 60:0.5, 90:0}; const a = Object.keys(angles)[rand(0,2)]; return { text: `cos(${a} degrees)`, answer: angles[a] }; }},
    ],
    calculus: [
        { level: 90, template: 'd/dx (x^n)', solveFor: 'f\'(x)', generator: () => { const n = rand(2, 8); return { text: `d/dx (x^${n})`, answer: `${n}*x^${n-1}` }; }},
        { level: 95, template: 'd/dx (a*x^n)', solveFor: 'f\'(x)', generator: () => { const a = rand(2,10); const n = rand(2, 5); return { text: `d/dx (${a}x^${n})`, answer: `${a*n}*x^${n-1}` }; }},
        { level: 100, template: 'integral(a*x^n, dx)', solveFor: 'F(x)', generator: () => { const a = rand(2,10); const n = rand(2,5); return { text: `integral(${a}x^${n} dx)`, answer: `${a/(n+1)}*x^${n+1}+C` }; }},
    ],
};

function generateQuestion() { const available = []; for (const cat in questionLibrary) { for (const q of questionLibrary[cat]) { if (internalScore >= q.level) { available.push(q); } } } const template = available[rand(0, available.length - 1)]; if (template.isFixed) { const qData = template.generator(); return { text: `\\(${qData.text}\\)`, answerExpression: qData.answer }; } let vars = template.generator ? template.generator() : {}; if (!template.generator) { for (const v in template.vars) { vars[v] = rand(template.vars[v][0], template.vars[v][1]); } } let questionText = template.template; let answerExpression = template.answerExpr || template.template; for (const v in vars) { questionText = questionText.replace(new RegExp(v, 'g'), vars[v]); answerExpression = answerExpression.replace(new RegExp(v, 'g'), vars[v]); } if (template.solveFor) { if (template.isMultiAnswer) { return { text: `Solve for ${template.solveFor}: \\(${questionText.replace('*', '\\times')}\\)`, answerExpression: vars[template.solveFor] }; } return { text: `Solve for ${template.solveFor}: \\(${questionText.replace('*', '\\times')}\\)`, answerExpression: vars[template.solveFor] }; } return { text: `\\(${questionText.replace('*', '\\times')}\\)`, answerExpression: answerExpression }; }

async function displayQuestion() { currentQuestion = generateQuestion(); questionElement.innerHTML = currentQuestion.text; if (window.MathJax) { MathJax.typesetPromise([questionElement]); } feedbackElement.textContent = ''; }
async function checkAnswer() { const userAnswer = answerElement.value.trim().toLowerCase().replace(/\s/g, ''); const lang = languageSelect.value; const correctAnswer = await getCorrectAnswer(currentQuestion.answerExpression); if (Array.isArray(correctAnswer)) { if (correctAnswer.map(String).includes(userAnswer)) { handleCorrectAnswer(lang); } else { handleIncorrectAnswer(lang); } } else { if (userAnswer == correctAnswer) { handleCorrectAnswer(lang); } else { handleIncorrectAnswer(lang); } } }
async function getCorrectAnswer(expression) { if (typeof expression === 'number' || Array.isArray(expression)) return expression; if (typeof expression === 'string' && !/[\+\-\*\/]/.test(expression)) return expression; try { const response = await fetch(MATH_API_URL + encodeURIComponent(expression)); const data = await response.json(); return data.result; } catch (error) { console.error("Math API Error:", error); return "Error"; } }
async function handleCorrectAnswer(lang) { internalScore++; feedbackElement.textContent = await translateText(translations.en.correct_feedback, lang); feedbackElement.style.color = 'green'; answerElement.value = ''; setTimeout(displayQuestion, 1000); }
async function handleIncorrectAnswer(lang) { feedbackElement.textContent = await translateText(translations.en.incorrect_feedback, lang); feedbackElement.style.color = 'red'; answerElement.value = ''; setTimeout(displayQuestion, 2000); }

submitElement.addEventListener('click', checkAnswer);
answerElement.addEventListener('keyup', (e) => { if (e.key === 'Enter') checkAnswer(); });
languageSelect.addEventListener('change', (e) => translateUI(e.target.value));

getSupportedLanguages();
displayQuestion();
