
function getActiveTabContent() {

    const activePane =
    document.querySelector(".tab-pane.active");

    return activePane.innerText;

}

function copyNotes() {

    const text =
    getActiveTabContent();

    navigator.clipboard.writeText(text);

    alert("Notes copied successfully!");

}

function saveNotes() {

    alert(
    "Backend save API will be connected later."
    );

}

function downloadNotes() {

    const text =
    getActiveTabContent();

    const blob =
    new Blob([text], {type:"text/plain"});

    const link =
    document.createElement("a");

    link.href =
    URL.createObjectURL(blob);

    link.download =
    "study_notes.txt";

    link.click();

}
console.log("notes.js loaded");

// Load voices first
window.speechSynthesis.onvoiceschanged =
    function () {

    console.log(
        "Voices loaded:",
        speechSynthesis.getVoices()
    );
};
let startTime = Date.now();

window.addEventListener("beforeunload", function () {

    let endTime = Date.now();

    let minutes = Math.floor(
        (endTime - startTime) / 60000
    );

    if (minutes > 0) {

        fetch("/update-study-time", {

            method: "POST",

            headers: {
                "Content-Type":
                "application/x-www-form-urlencoded"
            },

            body: `minutes=${minutes}`
        });

    }

});

// ==========================
// TEXT TO SPEECH
// ==========================

function speakText(text) {

    console.log("Speak clicked");

    // Stop old speech
    speechSynthesis.cancel();

    // Create speech object
    const speech =
        new SpeechSynthesisUtterance(text);

    // Language map
    const languageMap = {

        "English": "en-US",
        "Hindi": "hi-IN",
        "Tamil": "ta-IN",
        "Telugu": "te-IN",
        "Kannada": "kn-IN",
        "Marathi": "mr-IN",
        "Gujarati": "gu-IN",
        "Bengali": "bn-IN"
    };

    // Set language
    speech.lang =
        languageMap[NOTE_LANGUAGE] || "en-US";

    // Voice settings
    speech.rate = 1;
    speech.pitch = 1;
    speech.volume = 1;

    // Get voices
    const voices =
        speechSynthesis.getVoices();

    if (voices.length > 0) {

        speech.voice = voices[0];
    }

    console.log("Speaking:", text);

    // Speak
    speechSynthesis.speak(speech);
}

// Stop speech
function stopSpeech() {

    speechSynthesis.cancel();
}