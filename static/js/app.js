// Get HTML elements
const pdfFile = document.getElementById("pdfFile");
const uploadButton = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");
const summary = document.getElementById("summary");
const summarySection = document.getElementById("summarySection");
const languageSelect = document.getElementById("languageSelect");

// Get question elements
const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");
const askStatus = document.getElementById("askStatus");
const answer = document.getElementById("answer");
const answerSection = document.getElementById("answerSection");

// Clear old results when a new PDF is selected
pdfFile.addEventListener("change", function () {
    summary.textContent = "";
    summarySection.hidden = true;

    answer.textContent = "";
    answerSection.hidden = true;

    uploadStatus.textContent = "";
    askStatus.textContent = "";

    questionInput.value = "";

    askButton.disabled = true;
});


// Clear old results when the output language changes
languageSelect.addEventListener("change", function () {
    summary.textContent = "";
    summarySection.hidden = true;

    answer.textContent = "";
    answerSection.hidden = true;

    askStatus.textContent = "";
});

// Upload PDF when the button is clicked
uploadButton.addEventListener("click", async function () {

    // Check that a file has been selected
    if (pdfFile.files.length === 0) {
        uploadStatus.textContent = "Please select a PDF file.";
        return;
    }
    // Clear old results while processing a new upload
    summary.textContent = "";
    summarySection.hidden = true;

    answer.textContent = "";
    answerSection.hidden = true;

    askStatus.textContent = "";
    questionInput.value = "";

    askButton.disabled = true;

    uploadButton.disabled = true;

    // Get selected file
    const file = pdfFile.files[0];

    // Create form data
    const formData = new FormData();
    formData.append("file", file);
    formData.append("language", languageSelect.value);

    uploadStatus.textContent = "Uploading and processing PDF...";

    try {
        // Send PDF to FastAPI
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        // Check for upload errors
        if (!response.ok) {
            uploadStatus.textContent = data.detail;
            return;
        }

        // Show result
        uploadStatus.textContent =
            "PDF processed successfully: " + data.filename;

        summary.textContent = data.summary;
        summarySection.hidden = false;
        askButton.disabled = false;

    } catch (error) {
        uploadStatus.textContent = "Something went wrong.";
    } finally {
        uploadButton.disabled = false;
    }
});

// Ask a question about the PDF
askButton.addEventListener("click", async function () {

    // Get question text
    const question = questionInput.value.trim();

    // Check that the question is not empty
    if (question === "") {
        askStatus.textContent = "Please enter a question.";
        return;
    }

    askButton.disabled = true;

    askStatus.textContent = "Thinking...";

    try {
        // Send question to FastAPI
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                language: languageSelect.value
            })
        });

        const data = await response.json();

        // Check for errors
        if (!response.ok) {
            askStatus.textContent = data.detail;
            return;
        }

        // Show answer
        askStatus.textContent = "Answer generated successfully.";
        answer.textContent = data.answer;
        answerSection.hidden = false;

    } catch (error) {
        askStatus.textContent = "Something went wrong.";
    } finally {
        askButton.disabled = false;
    }
});