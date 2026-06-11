function togglePassword(id, icon) {

    let input = document.getElementById(id);

    if (input.type === "password") {

        input.type = "text";

        icon.classList.remove("bi-eye");
        icon.classList.add("bi-eye-slash");

    } else {

        input.type = "password";

        icon.classList.remove("bi-eye-slash");
        icon.classList.add("bi-eye");

    }
}

const passwordInput =
    document.getElementById("registerPassword");

if (passwordInput) {

    passwordInput.addEventListener("input", function () {

        const password = this.value;

        const fill =
            document.getElementById("strengthFill");

        const text =
            document.getElementById("strengthText");

        let score = 0;

        if (password.length >= 8) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;

        if (score === 1) {

            fill.style.width = "25%";
            fill.style.background = "red";
            text.innerText = "Weak";

        }

        else if (score === 2) {

            fill.style.width = "50%";
            fill.style.background = "orange";
            text.innerText = "Medium";

        }

        else if (score === 3) {

            fill.style.width = "75%";
            fill.style.background = "blue";
            text.innerText = "Strong";

        }

        else if (score === 4) {

            fill.style.width = "100%";
            fill.style.background = "green";
            text.innerText = "Very Strong";

        }

        else {

            fill.style.width = "0%";
            text.innerText = "";

        }

    });

}