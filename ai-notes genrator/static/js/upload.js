const fileInput =
document.getElementById("fileInput");

const selectedFile =
document.getElementById("selectedFile");

if(fileInput){

    fileInput.addEventListener("change", () => {

        if(fileInput.files.length > 0){

            selectedFile.innerHTML =
            `
            <div class="alert alert-success">
                ${fileInput.files[0].name}
            </div>
            `;

        }

    });

}


document.addEventListener(
    "DOMContentLoaded",
    function () {

        const form =
            document.getElementById("notesForm");

        if (!form) return;

        form.addEventListener(
            "submit",
            function () {

                document.getElementById(
                    "loadingOverlay"
                ).style.display = "flex";
            }
        );
    }
);

form.addEventListener(
    "submit",
    function (e) {

        const text =
            document.getElementById(
                "study_text"
            ).value.trim();

        if (text.length < 20) {

            alert(
                "Please enter more study content."
            );

           

            return;
        }

        document.getElementById(
            "loadingOverlay"
        ).style.display = "flex";
    }
);
const uploadForm =
document.getElementById("uploadForm");

if (uploadForm) {

    uploadForm.addEventListener(
        "submit",
        function () {

            const spinner =
            document.getElementById("spinner");

            if (spinner) {
                spinner.style.display = "block";
            }

        }
    );

}
// ==========================
// Voice Input
// ==========================

function startVoiceInput() {

    // Check browser support
    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {

        alert(
            "Voice recognition is not supported in this browser.\nUse Google Chrome."
        );

        return;
    }

    const recognition = new SpeechRecognition();

    // Language
    recognition.lang = "en-US";

    // Settings
    recognition.continuous = false;
    recognition.interimResults = false;

    // Start recognition
    recognition.start();

    console.log("Voice recognition started");

    recognition.onstart = function () {

        console.log("Microphone active...");
    };

    recognition.onresult = function (event) {

        const transcript =
            event.results[0][0].transcript;

        console.log("You said:", transcript);

        const textarea =
            document.getElementById("studyText");

        textarea.value += " " + transcript;
    };

    recognition.onerror = function (event) {

        console.log("Voice Error:", event.error);

        if (event.error === "not-allowed") {

            alert(
                "Microphone permission denied.\nPlease allow microphone access."
            );

        } else if (event.error === "no-speech") {

            alert(
                "No speech detected. Try again."
            );

        } else {

            alert(
                "Voice recognition error: " +
                event.error
            );
        }
    };

    recognition.onend = function () {

        console.log("Voice recognition ended");
    };
}