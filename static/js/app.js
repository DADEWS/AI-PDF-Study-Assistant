// Get HTML elements
const pdfFile = document.getElementById("pdfFile");
const uploadButton = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");
const summary = document.getElementById("summary");
const summarySection = document.getElementById("summarySection");
const languageSelect = document.getElementById("languageSelect");
let selectedDocumentId = null;

// Get question elements
const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");
const askStatus = document.getElementById("askStatus");
const answer = document.getElementById("answer");
const answerSection = document.getElementById("answerSection");

// Get account elements
const loginInput = document.getElementById("loginInput");
const passwordInput = document.getElementById("passwordInput");
const loginButton = document.getElementById("loginButton");
const logoutButton = document.getElementById("logoutButton");
const loginForm = document.getElementById("loginForm");
const userPanel = document.getElementById("userPanel");
const currentUsername = document.getElementById("currentUsername");
const loginStatus = document.getElementById("loginStatus");

// Get document history elements
const documentsSection = document.getElementById("documentsSection");
const documentsList = document.getElementById("documentsList");
const documentsStatus = document.getElementById("documentsStatus");

// Get register elements
const registerUsername = document.getElementById("registerUsername");
const registerEmail = document.getElementById("registerEmail");
const registerPassword = document.getElementById("registerPassword");
const registerButton = document.getElementById("registerButton");
const registerForm = document.getElementById("registerForm");
const registerStatus = document.getElementById("registerStatus");


// Show logged-in user
function showLoggedInUser(username) {
    currentUsername.textContent = username;

    loginForm.hidden = true;
    registerForm.hidden = true;
    userPanel.hidden = false;
    documentsSection.hidden = false;

    loginInput.value = "";
    passwordInput.value = "";
}


// Show logged-out state
function showLoggedOutUser() {
    currentUsername.textContent = "";

    loginForm.hidden = false;
    registerForm.hidden = false;
    userPanel.hidden = true;

    documentsSection.hidden = true;
    documentsList.innerHTML = "";
    documentsStatus.textContent = "";
}


// Log in
loginButton.addEventListener("click", async function () {

    const login = loginInput.value.trim();
    const password = passwordInput.value;

    if (login === "" || password === "") {
        loginStatus.textContent =
            "Please enter username/email and password.";
        return;
    }

    loginButton.disabled = true;
    loginStatus.textContent = "Logging in...";

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                login: login,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            loginStatus.textContent = data.detail;
            return;
        }

        showLoggedInUser(data.username);
        loadDocuments();

        loginStatus.textContent = "Login successful.";

    } catch (error) {
        loginStatus.textContent = "Something went wrong.";

    } finally {
        loginButton.disabled = false;
    }
});


// Register a new user
registerButton.addEventListener("click", async function () {

    const username = registerUsername.value.trim();
    const email = registerEmail.value.trim();
    const password = registerPassword.value;

    if (username === "" || email === "" || password === "") {
        registerStatus.textContent = "Please fill in all fields.";
        return;
    }

    registerButton.disabled = true;
    registerStatus.textContent = "Creating account...";

    try {
        const response = await fetch("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            registerStatus.textContent = data.detail;
            return;
        }

        registerUsername.value = "";
        registerEmail.value = "";
        registerPassword.value = "";

        registerStatus.textContent =
            "Account created successfully. You can now log in.";

    } catch (error) {
        registerStatus.textContent = "Something went wrong.";

    } finally {
        registerButton.disabled = false;
    }
});


// Log out
logoutButton.addEventListener("click", async function () {

    try {
        const response = await fetch("/logout", {
            method: "POST"
        });

        if (!response.ok) {
            loginStatus.textContent = "Logout failed.";
            return;
        }

        showLoggedOutUser();
        selectedDocumentId = null;

        summary.textContent = "";
        summarySection.hidden = true;

        answer.textContent = "";
        answerSection.hidden = true;

        askButton.disabled = true;

        loginStatus.textContent = "Logout successful.";

    } catch (error) {
        loginStatus.textContent = "Something went wrong.";
    }
});


// Clear old results when a new PDF is selected
pdfFile.addEventListener("change", function () {
    selectedDocumentId = null;

    summary.textContent = "";
    summarySection.hidden = true;

    answer.textContent = "";
    answerSection.hidden = true;

    uploadStatus.textContent = "";
    askStatus.textContent = "";

    questionInput.value = "";

    askButton.disabled = true;
});


// Reload the selected document when the output language changes
languageSelect.addEventListener("change", async function () {

    answer.textContent = "";
    answerSection.hidden = true;
    askStatus.textContent = "";

    if (selectedDocumentId === null) {
        summary.textContent = "";
        summarySection.hidden = true;
        return;
    }

    summary.textContent = "";
    summarySection.hidden = true;

    documentsStatus.textContent = "Loading summary...";

    try {
        const response = await fetch(
            "/documents/" + selectedDocumentId +
            "/select?language=" + languageSelect.value,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            documentsStatus.textContent = data.detail;
            return;
        }

        if (data.summary) {
            summary.textContent = data.summary;
            summarySection.hidden = false;
        }

        documentsStatus.textContent =
            "Selected: " + data.filename;

    } catch (error) {
        documentsStatus.textContent = "Something went wrong.";
    }
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

    uploadStatus.textContent =
        "Uploading and processing PDF...";

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

        selectedDocumentId = data.document_id;

        askButton.disabled = false;

        loadDocuments();

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

    if (question === "") {
        askStatus.textContent = "Please enter a question.";
        return;
    }

    askButton.disabled = true;
    askStatus.textContent = "Thinking...";

    try {
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

        if (!response.ok) {
            askStatus.textContent = data.detail;
            return;
        }

        askStatus.textContent =
            "Answer generated successfully.";

        answer.textContent = data.answer;
        answerSection.hidden = false;

    } catch (error) {
        askStatus.textContent = "Something went wrong.";

    } finally {
        askButton.disabled = false;
    }
});


// Load documents owned by the current user
async function loadDocuments() {

    documentsList.innerHTML = "";
    documentsStatus.textContent = "Loading documents...";

    try {
        const response = await fetch("/documents");

        const data = await response.json();

        if (!response.ok) {
            documentsStatus.textContent = data.detail;
            return;
        }

        if (data.documents.length === 0) {
            documentsStatus.textContent = "No documents found.";
            return;
        }

        documentsStatus.textContent = "";

        data.documents.forEach(function (pdfDocument) {

            const item = document.createElement("div");

            const filename = document.createElement("span");
            filename.textContent = pdfDocument.filename;

            const selectButton = document.createElement("button");
            selectButton.textContent = "Select";

            const deleteButton = document.createElement("button");
            deleteButton.classList.add("delete-button");
            deleteButton.title = "Delete document";
            deleteButton.setAttribute("aria-label", "Delete document");

            deleteButton.innerHTML = `
                <svg
                    width="30"
                    height=30"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <path d="M3 6h18"></path>
                    <path d="M8 6V4h8v2"></path>
                    <path d="M19 6l-1 14H6L5 6"></path>
                    <path d="M10 11v5"></path>
                    <path d="M14 11v5"></path>
                </svg>
            `;

            selectButton.addEventListener("click", async function () {

                documentsStatus.textContent = "Selecting document...";

                try {
                    const response = await fetch(
                        "/documents/" + pdfDocument.id +
                        "/select?language=" + languageSelect.value,
                        {
                            method: "POST"
                        }
                    );

                    const data = await response.json();

                    if (!response.ok) {
                        documentsStatus.textContent = data.detail;
                        return;
                    }

                    selectedDocumentId = pdfDocument.id;

                    documentsStatus.textContent =
                        "Selected: " + pdfDocument.filename;

                    if (data.summary) {
                        summary.textContent = data.summary;
                        summarySection.hidden = false;
                    } else {
                        summary.textContent = "";
                        summarySection.hidden = true;
                    }
                    
                    answer.textContent = "";
                    answerSection.hidden = true;
                    askStatus.textContent = "";

                    askButton.disabled = false;

                } catch (error) {
                    documentsStatus.textContent = "Something went wrong.";
                }
            });

            deleteButton.addEventListener("click", async function () {

                const confirmed = confirm(
                    "Delete " + pdfDocument.filename + "?"
                );

                if (!confirmed) {
                    return;
                }

                documentsStatus.textContent = "Deleting document...";

                try {
                    const response = await fetch(
                        "/documents/" + pdfDocument.id,
                        {
                            method: "DELETE"
                        }
                    );

                    const data = await response.json();

                    if (!response.ok) {
                        documentsStatus.textContent = data.detail;
                        return;
                    }

                    // Clear the UI if the deleted document was selected
                    if (selectedDocumentId === pdfDocument.id) {
                        selectedDocumentId = null;

                        summary.textContent = "";
                        summarySection.hidden = true;

                        answer.textContent = "";
                        answerSection.hidden = true;

                        askStatus.textContent = "";
                        questionInput.value = "";

                        askButton.disabled = true;
                    }

                    documentsStatus.textContent =
                        "Document deleted successfully.";

                    loadDocuments();

                } catch (error) {
                    documentsStatus.textContent =
                        "Something went wrong.";
                }
            });

            const buttonGroup = document.createElement("div");
            buttonGroup.classList.add("document-actions");

            buttonGroup.appendChild(selectButton);
            buttonGroup.appendChild(deleteButton);

            item.appendChild(filename);
            item.appendChild(buttonGroup);

            documentsList.appendChild(item);
        });

    } catch (error) {
        documentsStatus.textContent = "Something went wrong.";
    }
}


// Check login session when the page loads
async function checkLoginStatus() {
    try {
        const response = await fetch("/me");

        if (!response.ok) {
            showLoggedOutUser();
            return;
        }

        const data = await response.json();

        selectedDocumentId = data.current_document_id;

        showLoggedInUser(data.username);
        loadDocuments();

        if (selectedDocumentId !== null) {
            askButton.disabled = false;

            const response = await fetch(
                "/documents/" + selectedDocumentId +
                "/select?language=" + languageSelect.value,
                {
                    method: "POST"
                }
            );

            const documentData = await response.json();

            if (response.ok && documentData.summary) {
                summary.textContent = documentData.summary;
                summarySection.hidden = false;

                documentsStatus.textContent =
                    "Selected: " + documentData.filename;
            }
        }

    } catch (error) {
        showLoggedOutUser();
    }
}

checkLoginStatus();