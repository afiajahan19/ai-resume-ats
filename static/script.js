document.addEventListener("DOMContentLoaded", () => {

  const toggle = document.getElementById("menuToggle");
  const nav = document.getElementById("topNav");

  const input = document.getElementById("resume");
  const zone = document.getElementById("dropZone");

  const fileName = document.getElementById("fileName");
  const fileHint = document.getElementById("fileHint");

  const form = document.getElementById("screeningForm");
  const submit = document.getElementById("submitButton");

  const description = document.getElementById("job_description");
  const count = document.getElementById("charCount");


  // MOBILE NAVIGATION

  if (toggle && nav) {

    toggle.addEventListener("click", () => {

      const open = nav.classList.toggle("open");

      toggle.setAttribute("aria-expanded", String(open));

      toggle.setAttribute(
        "aria-label",
        open ? "Close navigation" : "Open navigation"
      );

      toggle.textContent = open ? "×" : "☰";

    });

    nav.querySelectorAll("a").forEach(a => {

      a.addEventListener("click", () => {

        nav.classList.remove("open");

        toggle.setAttribute("aria-expanded", "false");

        toggle.textContent = "☰";

      });

    });

  }


  // RESUME FILE VALIDATION

  const valid = [".pdf", ".doc", ".docx"];

  function showFile(file) {

    if (!file) return;

    const ext = file.name
      .slice(file.name.lastIndexOf("."))
      .toLowerCase();

    if (!valid.includes(ext)) {

      input.value = "";

      fileName.textContent = "Drop your resume here or browse";

      fileHint.textContent =
        "Please choose a PDF, DOC or DOCX file";

      alert("Please upload a PDF, DOC or DOCX resume.");

      return;

    }

    fileName.textContent = file.name;

    fileHint.textContent =
      "File selected and ready for evaluation";

  }


  if (input) {

    input.addEventListener("change", () => {

      showFile(input.files[0]);

    });

  }


  // DRAG AND DROP

  if (zone) {

    ["dragenter", "dragover"].forEach(type => {

      zone.addEventListener(type, e => {

        e.preventDefault();

        zone.classList.add("dragover");

      });

    });


    ["dragleave", "drop"].forEach(type => {

      zone.addEventListener(type, e => {

        e.preventDefault();

        zone.classList.remove("dragover");

      });

    });


    zone.addEventListener("drop", e => {

      const files = e.dataTransfer && e.dataTransfer.files;

      if (files && files.length) {

        try {

          input.files = files;

          showFile(files[0]);

        } catch (_) {

          fileHint.textContent =
            "Use browse to select your resume.";

        }

      }

    });

  }


  // JOB DESCRIPTION CHARACTER COUNTER

  if (description && count) {

    const update = () => {

      count.textContent =
        `${description.value.length} characters`;

    };

    description.addEventListener("input", update);

    update();

  }


  // FLASK FORM SUBMISSION

  // Preserves the existing POST and multipart/form-data contract.

  if (form && submit) {

    form.addEventListener("submit", e => {

      if (!form.reportValidity()) {

        e.preventDefault();

        return;

      }

      if (input && input.files.length === 0) {

        e.preventDefault();

        alert("Please choose a resume before submitting.");

        return;

      }

      submit.disabled = true;

      submit.textContent = "Analyzing…";

    });

  }


  // ATS SCORE PROGRESS BAR

  document.querySelectorAll(".progress-fill").forEach(bar => {

    const score = Math.max(
      0,
      Math.min(100, Number(bar.dataset.score || 0))
    );

    requestAnimationFrame(() => {

      bar.style.width = `${score}%`;

    });

  });


  // SCROLL TO RESULTS AFTER FLASK RESPONSE

  const result = document.getElementById("candidate-results");

  if (result) {

    setTimeout(() => {

      result.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });

    }, 180);

  }


  // AUTOMATIC FOOTER YEAR

  const year = document.getElementById("year");

  if (year) {

    year.textContent = new Date().getFullYear();

  }

});