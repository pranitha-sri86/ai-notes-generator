// static/js/quiz.js

let currentQuestion = 0;
let score = 0;

// quizQuestions must be defined in quiz.html
// Example:
// <script>
// const quizQuestions = {{ questions | tojson | safe }};
// </script>

const userAnswers = new Array(quizQuestions.length).fill(null);

function loadQuestion() {

    if (!quizQuestions || quizQuestions.length === 0) {
        document.getElementById("question").innerText =
            "No quiz questions available.";
        return;
    }

    const q = quizQuestions[currentQuestion];

    document.getElementById("question").innerText = q.question;

    document.getElementById("progress").innerText =
        `Question ${currentQuestion + 1} of ${quizQuestions.length}`;

    let html = "";

    Object.entries(q.options).forEach(([key, value]) => {

        const selected =
            userAnswers[currentQuestion] === key
                ? "selected"
                : "";

        html += `
            <div class="option ${selected}"
                 onclick="selectOption(this, '${key}')">

                <span class="option-key">${key}</span>
                ${value}
            </div>
        `;
    });

    document.getElementById("options").innerHTML = html;

    // Button visibility
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");

    if (prevBtn) {
        prevBtn.style.display =
            currentQuestion === 0 ? "none" : "inline-block";
    }

    if (nextBtn) {
        nextBtn.innerText =
            currentQuestion === quizQuestions.length - 1
                ? "Finish Quiz"
                : "Next";
    }
}

function selectOption(element, option) {

    document.querySelectorAll(".option").forEach(el => {
        el.classList.remove("selected");
    });

    element.classList.add("selected");

    userAnswers[currentQuestion] = option;
}

function nextQuestion() {

    if (userAnswers[currentQuestion] === null) {
        alert("Please select an answer before continuing.");
        return;
    }

    if (currentQuestion < quizQuestions.length - 1) {
        currentQuestion++;
        loadQuestion();
    } else {
        showResults();
    }
}

function prevQuestion() {

    if (currentQuestion > 0) {
        currentQuestion--;
        loadQuestion();
    }
}

function showResults() {

    score = 0;

    quizQuestions.forEach((question, index) => {
        if (userAnswers[index] === question.answer) {
            score++;
        }
    });

    const total = quizQuestions.length;
    const percent = Math.round((score / total) * 100);

    document.getElementById("quizSection").style.display = "none";
    document.getElementById("resultBox").style.display = "block";

    document.getElementById("scoreCircle").innerText =
        `${score}/${total}`;

    document.getElementById("scoreText").innerText =
        `You scored ${percent}%`;

    // Optional feedback message
    const feedback = document.getElementById("feedback");

    if (feedback) {

        let message = "";

        if (percent >= 90) {
            message = "Excellent work!";
        }
        else if (percent >= 75) {
            message = "Great job!";
        }
        else if (percent >= 50) {
            message = "Good effort. Keep practicing.";
        }
        else {
            message = "Review the topic and try again.";
        }

        feedback.innerText = message;
    }
}

// Start quiz
if (typeof quizQuestions !== "undefined" &&
    quizQuestions.length > 0) {

    loadQuestion();

} else {

    console.error("quizQuestions is empty or undefined");
}