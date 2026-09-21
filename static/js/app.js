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

// Get account elements
const loginInput = document.getElementById("loginInput");
const passwordInput = document.getElementById("passwordInput");
const loginButton = document.getElementById("loginButton");
const logoutButton = document.getElementById("logoutButton");
const loginForm = document.getElementById("loginForm");
const userPanel = document.getElementById("userPanel");
const currentUsername = document.getElementById("currentUsername");
const loginStatus = document.getElementById("loginStatus");

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

    loginInput.value = "";
    passwordInput.value = "";
}


// Show logged-out state
function showLoggedOutUser() {
    currentUsername.textContent = "";

    loginForm.hidden = false;
    registerForm.hidden = false;
    userPanel.hidden = true;
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


// Check login session when the page loads
async function checkLoginStatus() {
    try {
        const response = await fetch("/me");

        if (!response.ok) {
            showLoggedOutUser();
            return;
        }

        const data = await response.json();

        showLoggedInUser(data.username);

    } catch (error) {
        showLoggedOutUser();
    }
}

checkLoginStatus();