const chatMessages =
    document.getElementById("chatMessages");

const chatInput =
    document.getElementById("chatInput");

let chatHistory = [];

function appendMessage(message, sender) {

    const div = document.createElement("div");

    div.className =
        sender === "user"
            ? "chat-bubble user"
            : "chat-bubble bot";

    div.innerHTML = message.replace(/\n/g, "<br>");

    chatMessages.appendChild(div);

    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}

async function sendMessage() {

    const message = chatInput.value.trim();

    if (!message) return;

    appendMessage(message, "user");

    chatInput.value = "";

    const typing = document.createElement("div");

    typing.className = "chat-bubble bot";

    typing.id = "typing";

    typing.innerHTML = "Typing...";

    chatMessages.appendChild(typing);

    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                message: message,

                notes: NOTE_TEXT,

                language: NOTE_LANGUAGE,

                history: chatHistory
            })
        });

        const data = await response.json();

        document.getElementById("typing").remove();

        appendMessage(data.reply, "bot");

        chatHistory.push({
            user: message,
            bot: data.reply
        });

    } catch (error) {

        document.getElementById("typing").remove();

        appendMessage(
            "Error contacting AI assistant.",
            "bot"
        );
    }
}

chatInput.addEventListener("keypress", function(e) {

    if (e.key === "Enter") {

    e.preventDefault();

    sendMessage();
}
});

function readSummary() {

    const text =
        document.querySelector("#summary .note-content")
        ?.innerText
        ?.trim();

    if (!text) {
        alert("No summary found.");
        return;
    }

    // Stop previous speech
    speechSynthesis.cancel();

    const speech = new SpeechSynthesisUtterance();

    speech.text = text;

    speech.lang = "en-US";

    speech.rate = 1;

    speech.pitch = 1;

    speech.volume = 1;

    speech.onstart = () => {
        console.log("Speech started");
    };

    speech.onerror = (e) => {
        console.log("Speech error:", e);
        alert("Voice output failed.");
    };

    speechSynthesis.speak(speech);
}

function stopSpeech() {
    speechSynthesis.cancel();
}