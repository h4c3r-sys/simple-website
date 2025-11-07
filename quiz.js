const questionElement = document.getElementById('question');
const answerElement = document.getElementById('answer');
const submitElement = document.getElementById('submit');
const scoreElement = document.getElementById('score');
const feedbackElement = document.getElementById('feedback'); // Added for feedback

let score = 0;
let correctAnswersInLevel = 0;
let level = 1;
const questionsPerLevel = 5;
let currentQuestion = null;

function generateQuestion(level) {
    let q = {};
    const rand = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
    const formatExpr = (num) => (num < 0 ? `(${num})` : num);

    if (level === 1) { q.text = `\\(${rand(1,10)} + ${rand(1,10)}\\)`; q.answer = [eval(q.text.replace(/\\\(|\\\)/g, ''))]; }
    else if (level === 2) { q.text = `\\(${rand(10,20)} - ${rand(1,9)}\\)`; q.answer = [eval(q.text.replace(/\\\(|\\\)/g, ''))]; }
    else if (level === 3) { q.text = `\\(${rand(2,10)} \\times ${rand(2,10)}\\)`; q.answer = [eval(q.text.replace(/\\\(|\\\)|\\times/g, '*'))]; }
    else if (level === 4) { const b = rand(2, 10); const a = b * rand(2, 10); q.text = `\\(${a} \\div ${b}\\)`; q.answer = [a/b]; }
    else if (level === 5) { q.text = `\\(${rand(-10,10)} + ${formatExpr(rand(-10,10))}\\)`; q.answer = [eval(q.text.replace(/\\\(|\\\)/g, ''))]; }
    else if (level === 6) { q.text = `\\(${rand(-10,10)} - ${formatExpr(rand(-10,10))}\\)`; q.answer = [eval(q.text.replace(/\\\(|\\\)/g, ''))]; }
    else if (level === 7) { q.text = `\\(${rand(-8,8)} \\times ${formatExpr(rand(-8,8))}\\)`; q.answer = [eval(q.text.replace(/\\\(|\\\)|\\times/g, '*'))]; }
    else if (level === 8) { const a = rand(2, 10); const b = rand(2, 3); q.text = `\\(${a}^${b}\\)`; q.answer = [Math.pow(a, b)]; }
    else if (level === 9) { const a = rand(2, 10); q.text = `\\(\\sqrt{${a*a}}\\)`; q.answer = [a]; }
    else if (level === 10) { const [a, b, c] = [rand(1,10), rand(2,5), rand(2,5)]; q.text = `\\(${a} + ${b} \\times ${c}\\)`; q.answer = [a + b * c]; }
    else if (level === 11) { const a = rand(2,10), x = rand(1,5), b = rand(1,10); q.text = `\\(${a}x + ${b} = ${a*x+b}\\)`; q.answer = [x]; }
    else if (level === 12) { const a = rand(-5,5) || 1, x = rand(-5,5), b = rand(-10,10); q.text = `\\(${a}x + ${b} = ${a*x+b}\\)`; q.answer = [x]; }
    else if (level === 13) { const x = rand(3,15); q.text = `If \\(x^2 = ${x*x}\\), what is \\(x\\)?`; q.answer = [x, -x]; }
    else if (level === 14) { const [a,b] = [3,4]; const c = Math.sqrt(a*a + b*b); q.text = `A right triangle has legs \\(${a}\\) and \\(${b}\\). Find the hypotenuse.`; q.answer = [c];}
    else if (level === 15) { const r = rand(2,10); q.text = `Area of a circle with radius \\(${r}\\)? (Use \\(\\pi=3.14\\))`; q.answer = [3.14*r*r];}
    else if (level === 16) { const [a,b,c,d] = [rand(1,5), rand(1,5), rand(1,5), rand(1,5)]; q.text = `\\((${a}x + ${b}) + (${c}x + ${d})\\)`; q.answer = [`${a+c}x + ${b+d}`];}
    else if (level === 17) { const [a,b] = [rand(2,6), rand(2,6)]; q.text = `\\((${a}x)(${b}x^2)\\)`; q.answer = [`${a*b}x^3`];}
    else if (level === 18) { const x = rand(2,4); q.text = `Solve for x: \\(2^x = ${Math.pow(2,x)}\\)`; q.answer = [x];}
    else if (level === 19) { const x = rand(2,4); q.text = `Solve for x: \\(\\log_2(${Math.pow(2,x)}) = x\\)`; q.answer = [x];}
    else if (level === 20) { q.text = `What is \\(\\sin(90^{\\circ})\\)?`; q.answer = [1];}
    else if (level === 21) { q.text = `What is \\(\\cos(0^{\\circ})\\)?`; q.answer = [1];}
    else if (level === 22) { const a = rand(3,8); q.text = `Find the derivative of \\(f(x) = x^${a}\\)`; q.answer = [`${a}x^${a-1}`, `${a}x^(${a-1})`];}
    else if (level === 23) { const a = rand(2,8); const c = rand(1,10); q.text = `Find the derivative of \\(f(x) = ${a}x + ${c}\\)`; q.answer = [a];}
    else if (level === 24) { const a = rand(2,10); q.text = `Calculate \\(\\int_{0}^{1} ${a}x \\,dx\\)`; q.answer = [a/2];}
    else if (level === 25) { q.text = `What is \\(i^2\\)?`; q.answer = [-1];}
    // ... keep adding levels
    else { q.text = "You are a true math genius! More levels coming soon."; q.answer = ["next"]; }

    // Ensure all answers are strings
    q.answer = q.answer.map(String);
    return q;
}

function displayQuestion() {
    currentQuestion = generateQuestion(level);
    questionElement.innerHTML = currentQuestion.text;
    if (window.MathJax) {
        MathJax.typesetPromise([questionElement]).catch(err => console.log('MathJax error: ' + err.message));
    }
    scoreElement.textContent = `Score: ${score} | Level: ${level}`;
    feedbackElement.textContent = ''; // Clear feedback
}

function checkAnswer() {
    const userAnswer = answerElement.value.trim().toLowerCase();
    if (currentQuestion.answer.includes(userAnswer)) {
        score++;
        correctAnswersInLevel++;
        if (correctAnswersInLevel >= questionsPerLevel) {
            level++;
            correctAnswersInLevel = 0;
        }
        answerElement.value = '';
        displayQuestion();
    } else {
        feedbackElement.textContent = "Incorrect. Please try again.";
        feedbackElement.style.color = 'red';
    }
}

submitElement.addEventListener('click', checkAnswer);
answerElement.addEventListener('keyup', function(event) {
    if (event.key === 'Enter') checkAnswer();
});

displayQuestion();
