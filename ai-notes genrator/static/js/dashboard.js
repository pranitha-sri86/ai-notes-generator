// Animate stat numbers on page load
document.addEventListener(
    "DOMContentLoaded", function () {

    const statNumbers = document
        .querySelectorAll(".stat-number");

    statNumbers.forEach(el => {

        const target =
            parseInt(el.innerText) || 0;

        let current = 0;
        const step = Math.ceil(target / 30);

        const timer = setInterval(() => {

            current += step;

            if (current >= target) {
                current = target;
                clearInterval(timer);
            }

            el.innerText = current;

        }, 40);

    });

});