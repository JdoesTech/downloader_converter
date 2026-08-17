const API_BASE_URL = window.AUTH_API_BASE_URL || "http://localhost:8888";
const TOKEN_STORAGE_KEY = "gnm_access_token";

function getAccessToken() {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
}

function setAccessToken(token) {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

function clearAccessToken() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
}

function isAuthenticated() {
    return Boolean(getAccessToken());
}

async function apiRequest(path, options = {}) {
    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {}),
    };

    const token = getAccessToken();
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers,
    });

    let payload = null;
    try {
        payload = await response.json();
    } catch (error) {
        payload = null;
    }

    if (!response.ok) {
        const message = payload?.detail || "Request failed";
        throw new Error(typeof message === "string" ? message : JSON.stringify(message));
    }

    return payload;
}

async function login(event) {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const remember = document.getElementById("remember")?.checked;
    const message = document.getElementById("login-message");

    try {
        const payload = await apiRequest("/auth/login", {
            method: "POST",
            body: JSON.stringify({ email, password }),
        });

        const token = payload?.result?.access_token;
        if (!token) {
            throw new Error("Login succeeded but no access token was returned.");
        }

        if (remember) {
            setAccessToken(token);
        } else {
            sessionStorage.setItem(TOKEN_STORAGE_KEY, token);
            localStorage.removeItem(TOKEN_STORAGE_KEY);
        }

        message.style.color = "green";
        message.textContent = "Login successful. Redirecting...";
        window.location.href = "index.html";
    } catch (error) {
        message.style.color = "red";
        message.textContent = error.message || "Invalid email or password";
    }
}

async function signup(event) {
    event.preventDefault();

    const message = document.getElementById("signup-message");
    const body = {
        fname: document.getElementById("fname").value.trim(),
        lname: document.getElementById("lname").value.trim(),
        email: document.getElementById("email").value.trim(),
        password: document.getElementById("password").value,
        phone_number: document.getElementById("phone_number").value.trim(),
        birth: document.getElementById("birth").value,
        sex: document.getElementById("sex").value,
    };

    try {
        await apiRequest("/auth/register", {
            method: "POST",
            body: JSON.stringify(body),
        });

        message.style.color = "green";
        message.textContent = "Account created. Redirecting to login...";
        setTimeout(() => {
            window.location.href = "login.html";
        }, 1200);
    } catch (error) {
        message.style.color = "red";
        message.textContent = error.message || "Signup failed";
    }
}

async function requestPasswordReset(event) {
    event.preventDefault();

    const message = document.getElementById("reset-message");
    const email = document.getElementById("email").value.trim();

    try {
        const payload = await apiRequest("/auth/forgot-password", {
            method: "POST",
            body: JSON.stringify({ email }),
        });

        message.style.color = "green";
        message.textContent = payload.detail;

        if (payload?.result?.reset_token) {
            sessionStorage.setItem("gnm_reset_token", payload.result.reset_token);
            window.location.href = "reset_pwd.html?step=reset";
        }
    } catch (error) {
        message.style.color = "red";
        message.textContent = error.message || "Unable to process request";
    }
}

async function resetPassword(event) {
    event.preventDefault();

    const message = document.getElementById("reset-message");
    const token =
        document.getElementById("reset_token")?.value.trim() ||
        sessionStorage.getItem("gnm_reset_token") ||
        "";
    const newPassword = document.getElementById("new_password").value;

    try {
        await apiRequest("/auth/reset-password", {
            method: "POST",
            body: JSON.stringify({ token, new_password: newPassword }),
        });

        sessionStorage.removeItem("gnm_reset_token");
        message.style.color = "green";
        message.textContent = "Password updated. Redirecting to login...";
        setTimeout(() => {
            window.location.href = "login.html";
        }, 1200);
    } catch (error) {
        message.style.color = "red";
        message.textContent = error.message || "Password reset failed";
    }
}

async function fetchUserProfile() {
    return apiRequest("/users/me", { method: "POST" });
}

function logout() {
    clearAccessToken();
    sessionStorage.removeItem(TOKEN_STORAGE_KEY);
    window.location.href = "login.html";
}

function updateAuthUi() {
    const authButtons = document.getElementById("auth-buttons");
    if (!authButtons) {
        return;
    }

    const token = getAccessToken() || sessionStorage.getItem(TOKEN_STORAGE_KEY);
    if (token) {
        authButtons.innerHTML = `
            <button id="profile-button" type="button">Profile</button>
            <button id="logout-button" type="button" onclick="logout()">Logout</button>
        `;
        document.getElementById("profile-button")?.addEventListener("click", async () => {
            try {
                const profile = await fetchUserProfile();
                alert(`Signed in as ${profile.result.email}`);
            } catch (error) {
                alert(error.message || "Unable to load profile");
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    updateAuthUi();

    const params = new URLSearchParams(window.location.search);
    if (params.get("step") === "reset") {
        const tokenField = document.getElementById("reset_token");
        const storedToken = sessionStorage.getItem("gnm_reset_token");
        if (tokenField && storedToken) {
            tokenField.value = storedToken;
        }
    }
});
