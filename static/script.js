document.addEventListener("DOMContentLoaded", () => {

    // Progress Bar Animation
    const progress = document.querySelector(".progress-fill");

    if (progress) {

        const score = progress.dataset.score || 0;

        progress.style.width = "0%";

        setTimeout(() => {

            progress.style.width = score + "%";

        }, 300);

    }

    // Cards Animation
    const cards = document.querySelectorAll(".card, .score-card, .suggestion-card");

    cards.forEach((card, index) => {

        card.style.opacity = "0";
        card.style.transform = "translateY(30px)";

        setTimeout(() => {

            card.style.transition = "0.6s ease";
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";

        }, index * 150);

    });

    // Upload Animation
    const fileInput = document.querySelector("input[type=file]");

    if (fileInput) {

        fileInput.addEventListener("change", function () {

            if (this.files.length) {

                this.style.border = "2px solid #22c55e";

            }

        });

    }

});