function readSummary() {

    alert("Voice button clicked");

    const text =
        document.querySelector("#summary .note-content")
        ?.innerText;

    if (!text) {

        alert("No text found");

        return;
    }

    const speech =
        new SpeechSynthesisUtterance(text);

    speech.lang = "en-US";

    speech.rate = 1;

    speech.pitch = 1;

    speech.volume = 1;

    speechSynthesis.speak(speech);
}