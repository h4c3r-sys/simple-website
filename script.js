document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const setupScreen = document.getElementById('setup-screen');
    const gameScreen = document.getElementById('game-screen');
    const endScreen = document.getElementById('end-screen');
    const p1Prompt = document.getElementById('p1-prompt');
    const p2Prompt = document.getElementById('p2-prompt');
    const startPrompt = document.getElementById('start-prompt');
    const messageArea = document.getElementById('message-area');
    const p1Track = document.getElementById('p1-track');
    const p2Track = document.getElementById('p2-track');
    const endMessage = document.getElementById('end-message');
    const playAgainBtn = document.getElementById('play-again-btn');
    const difficultyBtns = document.querySelectorAll('.difficulty-btn');
    const lengthBtns = document.querySelectorAll('.length-btn');
    const gameMusic = document.getElementById('game-music');
    const musicSelection = document.getElementById('music-selection');
    const sfxCountdown = document.getElementById('sfx-countdown');
    const sfxKeyPress = document.getElementById('sfx-keypress');
    const sfxWin = document.getElementById('sfx-win');
    const sfxLose = document.getElementById('sfx-lose');

    // Game State
    let player1_key = null;
    let player2_key = null;
    let player1_position = 0;
    let player2_position = 0;
    let player1_penaltyTimer = null;
    let player2_penaltyTimer = null;
    let penaltyTime = 2000; // Default Easy
    let gameState = "setup";
    let p1KeyDown = false;
    let p2KeyDown = false;
    let trackMin = -30;
    let trackMax = 30;

    const scenarios = {
        'UV': {
            'both_win': "Ultraviolet Victory!",
            'both_lose': "Violet Demise."
        },
        'IO': {
            'both_win': "I/O Error: Success!",
            'both_lose': "Binary Sunset."
        }
    };

    // Scenario State
    let player1_finished = false;
    let player2_finished = false;
    let player1_outcome = null; // 'win' or 'loss'
    let player2_outcome = null; // 'win' or 'loss'
    let first_finisher = null; // 1 or 2
    let first_finisher_outcome = null; // 'win' or 'loss'

    // --- Helper Functions ---
    function isValidKey(key) {
        return key.length === 1 && key >= 'A' && key <= 'Z';
    }

    function playSound(sfx) {
        try {
            sfx.currentTime = 0;
            sfx.play();
        } catch (error) {
            console.error("SFX could not be played.", error);
        }
    }

    function speak(text) {
        try {
            const utterance = new SpeechSynthesisUtterance(text);
            window.speechSynthesis.speak(utterance);
        } catch (error) {
            console.error("Speech synthesis failed.", error);
        }
    }

    function generateRandomTitle() {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        let title = '';
        for (let i = 0; i < 6; i++) {
            title += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return title;
    }

    // --- Game Flow ---

    function resetGame() {
        gameMusic.pause();
        gameMusic.currentTime = 0;
        // Reset variables
        player1_key = null;
        player2_key = null;
        player1_position = 0;
        player2_position = 0;
        clearTimeout(player1_penaltyTimer);
        clearTimeout(player2_penaltyTimer);
        player1_penaltyTimer = null;
        player2_penaltyTimer = null;
        penaltyTime = 2000;
        gameState = "setup";
        p1KeyDown = false;
        p2KeyDown = false;
        trackMin = -30;
        trackMax = 30;

        // Reset Scenario State
        player1_finished = false;
        player2_finished = false;
        player1_outcome = null;
        player2_outcome = null;
        first_finisher = null;
        first_finisher_outcome = null;


        // Reset UI
        setupScreen.classList.remove('hidden');
        gameScreen.classList.add('hidden');
        endScreen.classList.add('hidden');
        p1Prompt.textContent = "Player 1: Press Your Key";
        p2Prompt.textContent = "Player 2: (Waiting...)";
        startPrompt.classList.add('hidden');
        messageArea.textContent = '';
        p1Track.innerHTML = '';
        p2Track.innerHTML = '';
        document.getElementById('easy-btn').classList.add('active');
        document.querySelectorAll('.difficulty-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('easy-btn').classList.add('active');
        document.querySelectorAll('.length-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('short-track').classList.add('active');


        // Re-attach setup listener
        document.addEventListener('keydown', setupKeyListener);
        document.removeEventListener('keydown', raceKeyListener);
        document.removeEventListener('keyup', raceKeyUpListener);
    }

    function checkSecretEnding() {
        const combo = [player1_key, player2_key].sort().join('');
        const secrets = {
            'FL': "Lost and Found",
            'AZ': "From A to Z",
            'MW': "Wumbo",
            'GG': "Good Game",
            'FF': "Pay Respects"
        };
        if (secrets[combo]) {
            gameState = "finished";
            setupScreen.classList.add('hidden');
            endScreen.classList.remove('hidden');
            endMessage.textContent = `Secret Ending: ${secrets[combo]}`;
            speak(`Secret Ending: ${secrets[combo]}`);
            return true;
        }
        return false;
    }

    function startCountdown() {
        const selectedMusic = musicSelection.querySelector('input[name="music"]:checked').value;
        gameMusic.src = selectedMusic;

        setupScreen.classList.add('hidden');
        gameScreen.classList.remove('hidden');
        generateTracks();

        setTimeout(() => {
            messageArea.textContent = '3';
            speak('3');
            playSound(sfxCountdown);
        }, 0);
        setTimeout(() => {
            messageArea.textContent = '2';
            speak('2');
            playSound(sfxCountdown);
        }, 1000);
        setTimeout(() => {
            messageArea.textContent = '1';
            speak('1');
            playSound(sfxCountdown);
        }, 2000);
        setTimeout(() => {
            messageArea.textContent = 'GO!';
            speak('Go!');
            try {
                gameMusic.play();
            } catch (error) {
                console.log("Music could not be played.", error);
            }
            placePlayers();
            gameState = "racing";
            document.removeEventListener('keydown', setupKeyListener);
            document.addEventListener('keydown', raceKeyListener);
            document.addEventListener('keyup', raceKeyUpListener);
            startPenaltyTimer(1);
            startPenaltyTimer(2);
        }, 3000);
        setTimeout(() => {
            messageArea.textContent = 'SPAM!';
            speak('Spam!');
        }, 3500);
    }

    function generateTracks() {
        p1Track.innerHTML = '';
        p2Track.innerHTML = '';
        for (let i = trackMin; i <= trackMax; i++) {
            const cell1 = document.createElement('div');
            cell1.classList.add('cell');
            cell1.textContent = i;
            cell1.dataset.pos = i;
            if (i === 0) cell1.classList.add('zero-cell');
            p1Track.appendChild(cell1);

            const cell2 = document.createElement('div');
            cell2.classList.add('cell');
            cell2.textContent = i;
            cell2.dataset.pos = i;
            if (i === 0) cell2.classList.add('zero-cell');
            p2Track.appendChild(cell2);
        }
        scrollToPosition(p1Track, 0);
        scrollToPosition(p2Track, 0);
    }

    function placePlayers() {
        const p1Avatar = document.createElement('div');
        p1Avatar.id = 'p1-avatar';
        p1Avatar.textContent = player1_key;
        p1Track.querySelector('[data-pos="0"]').appendChild(p1Avatar);

        const p2Avatar = document.createElement('div');
        p2Avatar.id = 'p2-avatar';
        p2Avatar.textContent = player2_key;
        p2Track.querySelector('[data-pos="0"]').appendChild(p2Avatar);
    }

    function scrollToPosition(track, position) {
        const cell = track.querySelector(`[data-pos="${position}"]`);
        if (cell) {
            const trackRect = track.parentElement.getBoundingClientRect();
            const cellRect = cell.getBoundingClientRect();
            const scrollLeft = cell.offsetLeft - (trackRect.width / 2) + (cellRect.width / 2);
            track.parentElement.scrollLeft = scrollLeft;
        }
    }

    function startPenaltyTimer(playerNumber) {
        if (gameState !== "racing") return;

        if (playerNumber === 1) {
            clearTimeout(player1_penaltyTimer);
            player1_penaltyTimer = setTimeout(() => penalizePlayer(1), penaltyTime);
        } else {
            clearTimeout(player2_penaltyTimer);
            player2_penaltyTimer = setTimeout(() => penalizePlayer(2), penaltyTime);
        }
    }

    function penalizePlayer(playerNumber) {
        if (gameState !== "racing") return;

        if (playerNumber === 1) {
            player1_position--;
            movePlayer(1);
            if (player1_position === trackMin) {
                playerFinished(1, 'loss');
            } else {
                startPenaltyTimer(1); // Restart the timer
            }
        } else {
            player2_position--;
            movePlayer(2);
            if (player2_position === trackMin) {
                playerFinished(2, 'loss');
            } else {
                startPenaltyTimer(2);
            }
        }
    }

    function playerFinished(playerNumber, outcome) {
        if (playerNumber === 1 && !player1_finished) {
            player1_finished = true;
            player1_outcome = outcome;
            clearTimeout(player1_penaltyTimer);
            if (!first_finisher) {
                first_finisher = 1;
                first_finisher_outcome = outcome;
            }
        } else if (playerNumber === 2 && !player2_finished) {
            player2_finished = true;
            player2_outcome = outcome;
            clearTimeout(player2_penaltyTimer);
            if (!first_finisher) {
                first_finisher = 2;
                first_finisher_outcome = outcome;
            }
        }
        checkIfBothFinished();
    }

    function checkIfBothFinished() {
        if (player1_finished && player2_finished) {
            gameState = "finished";
            gameMusic.pause();
            gameMusic.currentTime = 0;
            document.removeEventListener('keydown', raceKeyListener);
            document.removeEventListener('keyup', raceKeyUpListener);

            if (!checkForScenarioEnding()) {
                // Default to original win/loss behavior based on the first finisher
                if (first_finisher_outcome === 'win') {
                    showWinScreen(first_finisher);
                } else {
                    showShameScreen(first_finisher);
                }
            }
        }
    }

    function checkForScenarioEnding() {
        const combo = [player1_key, player2_key].sort().join('');
        const scenario = scenarios[combo];
        if (!scenario) return false;

        let outcome_key = null;
        if (player1_outcome === 'win' && player2_outcome === 'win') {
            outcome_key = 'both_win';
        } else if (player1_outcome === 'loss' && player2_outcome === 'loss') {
            outcome_key = 'both_lose';
        }

        if (outcome_key && scenario[outcome_key]) {
            const msg = `Scenario Ending: ${scenario[outcome_key]}`;
            gameScreen.classList.add('hidden');
            endScreen.classList.remove('hidden');
            endMessage.textContent = msg;
            speak(msg);
            return true;
        }

        return false;
    }

    function movePlayer(playerNumber) {
        if (playerNumber === 1) {
            const avatar = document.getElementById('p1-avatar');
            const newCell = p1Track.querySelector(`[data-pos="${player1_position}"]`);
            if (avatar && newCell) {
                newCell.appendChild(avatar);
                scrollToPosition(p1Track, player1_position);
            }
        } else {
            const avatar = document.getElementById('p2-avatar');
            const newCell = p2Track.querySelector(`[data-pos="${player2_position}"]`);
            if (avatar && newCell) {
                newCell.appendChild(avatar);
                scrollToPosition(p2Track, player2_position);
            }
        }
    }

    function showWinScreen(winnerPlayerNumber) {
        gameState = "finished";
        playSound(sfxWin);
        gameMusic.pause();
        gameMusic.currentTime = 0;
        clearTimeout(player1_penaltyTimer);
        clearTimeout(player2_penaltyTimer);
        document.removeEventListener('keydown', raceKeyListener);
        document.removeEventListener('keyup', raceKeyUpListener);

        const winnerKey = winnerPlayerNumber === 1 ? player1_key : player2_key;
        const title = generateRandomTitle();
        const msg = `Congratulations ${winnerKey}! You won and earned the title of ${title}!`;

        gameScreen.classList.add('hidden');
        endScreen.classList.remove('hidden');
        endMessage.textContent = msg;
        speak(msg);
    }

    function showShameScreen(loserPlayerNumber) {
        gameState = "finished";
        playSound(sfxLose);
        gameMusic.pause();
        gameMusic.currentTime = 0;
        clearTimeout(player1_penaltyTimer);
        clearTimeout(player2_penaltyTimer);
        document.removeEventListener('keydown', raceKeyListener);
        document.removeEventListener('keyup', raceKeyUpListener);

        const loserKey = loserPlayerNumber === 1 ? player1_key : player2_key;
        const msg = `Shame, ${loserKey}! You reached the anti-finish line.`;

        gameScreen.classList.add('hidden');
        endScreen.classList.remove('hidden');
        endMessage.textContent = msg;
        speak(msg);
    }

    // --- Event Listeners ---
    const setupKeyListener = (e) => {
        if (gameState !== "setup") return;
        const key = e.key.toUpperCase();

        if (!player1_key) {
            if (isValidKey(key)) {
                player1_key = key;
                p1Prompt.textContent = `Player 1: ${player1_key}`;
                p2Prompt.textContent = "Player 2: Press Your Key";
            }
        } else if (!player2_key) {
            if (isValidKey(key) && key !== player1_key) {
                player2_key = key;
                p2Prompt.textContent = `Player 2: ${player2_key}`;
                if (!checkSecretEnding()) {
                    startPrompt.classList.remove('hidden');
                }
            }
        } else if (key === 'ENTER') {
            gameState = "countdown";
            startCountdown();
        }
    };

    const raceKeyListener = (e) => {
        if (gameState !== "racing") return;
        const key = e.key.toUpperCase();

        if (key === player1_key && !p1KeyDown) {
            p1KeyDown = true;
            player1_position++;
            playSound(sfxKeyPress);
            movePlayer(1);
            startPenaltyTimer(1);
            if (player1_position === trackMax) {
                playerFinished(1, 'win');
            }
        } else if (key === player2_key && !p2KeyDown) {
            p2KeyDown = true;
            player2_position++;
            playSound(sfxKeyPress);
            movePlayer(2);
            startPenaltyTimer(2);
            if (player2_position === trackMax) {
                playerFinished(2, 'win');
            }
        }
    };

    const raceKeyUpListener = (e) => {
        if (gameState !== "racing") return;
        const key = e.key.toUpperCase();
        if (key === player1_key) {
            p1KeyDown = false;
        } else if (key === player2_key) {
            p2KeyDown = false;
        }
    };

    difficultyBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            difficultyBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            if (btn.id === 'easy-btn') penaltyTime = 2000;
            if (btn.id === 'medium-btn') penaltyTime = 1000;
            if (btn.id === 'hard-btn') penaltyTime = 500;
            if (btn.id === 'extreme-btn') penaltyTime = 100;
        });
    });

    lengthBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            lengthBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            if (btn.id === 'short-track') {
                trackMin = -30;
                trackMax = 30;
            }
            if (btn.id === 'medium-track') {
                trackMin = -100;
                trackMax = 100;
            }
            if (btn.id === 'long-track') {
                trackMin = -200;
                trackMax = 200;
            }
        });
    });

    playAgainBtn.addEventListener('click', resetGame);

    // Initial setup
    document.addEventListener('keydown', setupKeyListener);
});