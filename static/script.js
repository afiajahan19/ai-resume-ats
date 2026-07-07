// ===============================
// AI Resume ATS Checker
// Modern UI Animations
// ===============================

// Wait until page loads
document.addEventListener("DOMContentLoaded", () => {

    // ==========================
    // Animate Progress Bar
    // ==========================

    const progress = document.querySelector(".progress-fill");

    if (progress) {

        const width = progress.style.width;

        progress.style.width = "0%";

        setTimeout(() => {

            progress.style.width = width;

        }, 300);

    }

    // ==========================
    // Card Reveal Animation
    // ==========================

    const cards = document.querySelectorAll(".card, .score-card, .suggestion-card");

    cards.forEach((card, index) => {

        card.style.opacity = "0";

        card.style.transform = "translateY(30px)";

        setTimeout(() => {

            card.style.transition = "0.6s ease";

            card.style.opacity = "1";

            card.style.transform = "translateY(0)";

        }, index * 200);

    });

    // ==========================
    // File Upload Name
    // ==========================

    const fileInput = document.querySelector("input[type='file']");

    if (fileInput) {

        fileInput.addEventListener("change", function () {

            if (this.files.length > 0) {

                this.style.border = "2px solid #22c55e";

                this.title = this.files[0].name;

            }

        });

    }

    // ==========================
    // Button Loading Animation
    // ==========================

    const form = document.querySelector("form");

    const button = document.querySelector(".btn");

    if (form && button) {

        form.addEventListener("submit", () => {

            button.disabled = true;

            button.innerHTML = "⏳ Analyzing Resume...";

        });

    }

    // ==========================
    // Floating Effect
    // ==========================

    cards.forEach(card => {

        card.addEventListener("mouseenter", () => {

            card.style.transform = "translateY(-10px) scale(1.02)";

        });

        card.addEventListener("mouseleave", () => {

            card.style.transform = "translateY(0px) scale(1)";

        });

    });

});

// ===============================
// Scroll Reveal Animation
// ===============================

const observer = new IntersectionObserver((entries) => {

    entries.forEach(entry => {

        if (entry.isIntersecting) {

            entry.target.style.opacity = "1";

            entry.target.style.transform = "translateY(0)";

        }

    });

}, {

    threshold: 0.1

});

document.querySelectorAll(".glass-card, .score-card, .card, .suggestion-card")
.forEach(el => {

    el.style.opacity = "0";

    el.style.transform = "translateY(40px)";

    observer.observe(el);

});

// ===============================
// Page Fade In
// ===============================

window.onload = function () {

    document.body.style.opacity = "0";

    document.body.style.transition = "opacity .8s";

    setTimeout(() => {

        document.body.style.opacity = "1";

    }, 100);

};

// ===============================
// Background Mouse Glow
// ===============================

document.addEventListener("mousemove", (e) => {

    const bg = document.querySelector(".background");

    if (!bg) return;

    const x = e.clientX / window.innerWidth;

    const y = e.clientY / window.innerHeight;

    bg.style.backgroundPosition =
        `${x * 100}% ${y * 100}%`;

});