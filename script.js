document.addEventListener('DOMContentLoaded', () => {
    // Game state variables
    let karma = 0;
    let currentDay = 1;
    let scenarios = [];

    // DOM elements
    const karmaScoreElement = document.getElementById('karma-score');
    const karmaBarElement = document.getElementById('karma-bar');
    const dayCounterElement = document.getElementById('day-counter');
    const scenarioEmojiElement = document.getElementById('scenario-emoji');
    const scenarioTextElement = document.getElementById('scenario-text');
    const choice1Button = document.getElementById('choice-1');
    const choice2Button = document.getElementById('choice-2');
    const endingContainer = document.getElementById('ending-container');
    const endingTitleElement = document.getElementById('ending-title');
    const endingTextElement = document.getElementById('ending-text');
    const playAgainButton = document.getElementById('play-again-btn');

    let currentScenarios = [];

    // Function to start the game
    async function startGame() {
        currentDay = 1;
        karma = 0;
        updateKarma(0);
        dayCounterElement.textContent = `Day ${currentDay}`;

        // Hide ending, show scenario
        endingContainer.classList.add('hidden');
        document.getElementById('scenario-container').classList.remove('hidden');
        document.getElementById('choices-container').classList.remove('hidden');

        // Disable buttons while loading
        choice1Button.disabled = true;
        choice2Button.disabled = true;

        await fetchScenarios();
        shuffleScenarios();
        displayScenario(currentScenarios[currentDay - 1]);
    }

    // Fetch scenarios from JSON file
    async function fetchScenarios() {
        try {
            const response = await fetch('scenarios.json');
            scenarios = await response.json();
        } catch (error) {
            console.error('Error fetching scenarios:', error);
            // Handle error, maybe show a message to the user
        }
    }

    // Shuffle scenarios
    function shuffleScenarios() {
        currentScenarios = [...scenarios].sort(() => Math.random() - 0.5);
    }

    // Function to display a scenario
    function displayScenario(scenario) {
        scenarioEmojiElement.textContent = scenario.emoji;
        scenarioTextElement.textContent = scenario.dilemma;

        // Randomize choice order
        const choices = [...scenario.choices].sort(() => Math.random() - 0.5);

        choice1Button.textContent = choices[0].text;
        choice1Button.dataset.karma = choices[0].karma;
        choice2Button.textContent = choices[1].text;
        choice2Button.dataset.karma = choices[1].karma;

        // Re-enable buttons
        choice1Button.disabled = false;
        choice2Button.disabled = false;
    }

    // Function to handle a choice
    function handleChoice(karmaChange) {
        updateKarma(karmaChange);

        if (currentDay < 5) {
            currentDay++;
            dayCounterElement.textContent = `Day ${currentDay}`;
            displayScenario(currentScenarios[currentDay - 1]);
        } else {
            showEnding();
        }
    }

    // Function to update the karma score and bar
    function updateKarma(change) {
        karma += change;
        // Clamp karma between -100 and 100
        karma = Math.max(-100, Math.min(100, karma));

        karmaScoreElement.textContent = karma;

        // Update karma bar width
        const percentage = (karma + 100) / 200 * 100;
        karmaBarElement.style.width = `${percentage}%`;

        // Change karma bar color
        if (karma < 0) {
            karmaBarElement.style.backgroundColor = 'red';
        } else {
            karmaBarElement.style.backgroundColor = '#4caf50';
        }
    }

    // Function to show the ending
    function showEnding() {
        document.getElementById('scenario-container').classList.add('hidden');
        document.getElementById('choices-container').classList.add('hidden');
        endingContainer.classList.remove('hidden');

        if (karma >= 50) {
            endingTitleElement.textContent = "Good Ending";
            endingTextElement.textContent = "Your consistently kind and selfless choices have led to a life filled with joy, strong friendships, and great success. The world is a better place because of you.";
        } else if (karma <= -50) {
            endingTitleElement.textContent = "Bad Ending";
            endingTextElement.textContent = "Your selfish and unkind choices have led to a life of isolation, failure, and misery. You have pushed away those who cared about you and are left with nothing but regret.";
        } else {
            endingTitleElement.textContent = "Neutral Ending";
            endingTextElement.textContent = "You've lived an average, unremarkable life. You've had your moments of kindness and selfishness, but you never strayed too far from the middle of the road. Your life was neither extraordinary nor terrible.";
        }
    }

    // Event listeners
    choice1Button.addEventListener('click', (event) => {
        const karmaChange = parseInt(event.target.dataset.karma);
        handleChoice(karmaChange);
    });

    choice2Button.addEventListener('click', (event) => {
        const karmaChange = parseInt(event.target.dataset.karma);
        handleChoice(karmaChange);
    });

    playAgainButton.addEventListener('click', () => {
        startGame();
    });

    // Initial game start
    startGame();
});
