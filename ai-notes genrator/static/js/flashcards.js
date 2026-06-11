let currentIndex = 0;

const flashcard =
    document.getElementById("flashcard");

// Flip on click
flashcard.addEventListener("click", () => {
    flashcard.classList.toggle("flipped");
});

function updateCard() {

    if (!flashcards || flashcards.length === 0) {
        return;
    }

    const card = flashcards[currentIndex];

    document.getElementById("question").innerText =
        card.question;

    document.getElementById("answer").innerText =
        card.answer;

    // Progress text
    document.getElementById("progressText").innerText =
        `Card ${currentIndex + 1} of ${flashcards.length}`;

    // Card counter
    document.getElementById("cardCounter").innerText =
        `Card ${currentIndex + 1} of ${flashcards.length}`;

    // Progress bar
    const progress =
        ((currentIndex + 1) / flashcards.length) * 100;

    document.getElementById("progressBar").style.width =
        progress + "%";

    // Remove flip when changing cards
    flashcard.classList.remove("flipped");

    // Enable/Disable buttons
    const prevBtn =
        document.querySelector(".btn-secondary");

    const nextBtn =
        document.querySelector(".btn-primary");

    prevBtn.disabled = currentIndex === 0;

    nextBtn.disabled =
        currentIndex === flashcards.length - 1;

    // Completion message
    const msg =
        document.getElementById("completedMsg");

    msg.style.display = "none";
}

function nextCard() {

    if (currentIndex < flashcards.length - 1) {

        currentIndex++;
        updateCard();

    } else {

        document.getElementById(
            "completedMsg"
        ).style.display = "block";
    }
}

function previousCard() {

    if (currentIndex > 0) {

        currentIndex--;
        updateCard();
    }
}

// Keyboard navigation
document.addEventListener("keydown", function (event) {
    if (event.key === "ArrowRight") nextCard();
    if (event.key === "ArrowLeft") previousCard();
});

// Load first card on page load
updateCard();
