const chatBox =
    document.getElementById("chatBox");

const answerInput =
    document.getElementById("answerInput");

const topicInput =
    document.getElementById("topic");

let history = [];

function formatMessage(text) {

    return text
        .replace(/\n/g, "<br>")
        .replace(
            /## Feedback/g,
            "<h5>📊 Feedback</h5>"
        )
        .replace(
            /## Next Question/g,
            "<h5>❓ Next Question</h5>"
        );
}
function addMessage(text, sender) {

    const div =
        document.createElement("div");

    div.className =
        sender === "user"
        ? "user-msg"
        : "bot-msg";

    div.innerHTML =
    formatMessage(text);

    chatBox.appendChild(div);

    chatBox.scrollTop =
        chatBox.scrollHeight;
}

async function startInterview() {

    const topic =
        topicInput.value.trim();

    if (!topic) {

        alert("Enter interview topic");

        return;
    }

    addMessage(
        "Interview started for: " + topic,
        "bot"
    );

    const response = await fetch(
        "/mock-interview",
        {
            method: "POST",

            headers: {
                "Content-Type":
                "application/json"
            },

            body: JSON.stringify({

                topic: topic,

                answer:
                "Start the interview",

                history: []
            })
        }
    );

    const data =
        await response.json();

    addMessage(data.reply, "bot");
}

async function sendAnswer() {

    const answer =
        answerInput.value.trim();

    if (!answer) return;

    addMessage(answer, "user");

    answerInput.value = "";

    const topic =
        topicInput.value.trim();

    history.push({
        question: "Previous Question",
        answer: answer
    });

    const response = await fetch(
        "/mock-interview",
        {
            method: "POST",

            headers: {
                "Content-Type":
                "application/json"
            },

            body: JSON.stringify({

                topic: topic,

                answer: answer,

                history: history
            })
        }
    );

    const data =
        await response.json();

    addMessage(data.reply, "bot");
    speakAI(data.reply);
}
function startVoiceInput() {

    if (!('webkitSpeechRecognition' in window)) {

        alert(
            "Voice recognition supported only in Chrome."
        );

        return;
    }

    const recognition =
        new webkitSpeechRecognition();

    recognition.lang = "en-US";

    recognition.continuous = false;

    recognition.interimResults = false;

    recognition.start();

    recognition.onstart = function() {

        addMessage(
            "🎤 Listening...",
            "bot"
        );
    };

    recognition.onresult = function(event) {

        const transcript =
            event.results[0][0].transcript;

        answerInput.value = transcript;

        addMessage(
            "🎤 " + transcript,
            "user"
        );

        sendAnswer();
    };

    recognition.onerror = function(event) {

        alert(
            "Voice recognition error: "
            + event.error
        );
    };
}
function speakAI(text) {

    speechSynthesis.cancel();

    const speech =
        new SpeechSynthesisUtterance();

    speech.text = text;

    speech.lang = "en-US";

    speech.rate = 1;

    speech.pitch = 1;

    speech.volume = 1;

    window.speechSynthesis.speak(speech);
}