let token = localStorage.getItem("token") || null;
let currentUser = localStorage.getItem("username") || null;
let currentGroupId = localStorage.getItem("selectedGroupId") || null;

// --------------------
// INIT
// --------------------
window.onload = function () {
    const path = window.location.pathname;

    // Si está en /app/, exige login
    if (path === "/app/") {
        if (!token) {
            window.location.href = "/login/";
            return;
        }

        const userInfo = document.getElementById("userInfo");
        if (userInfo) {
            userInfo.innerText = currentUser || "";
        }

        loadGroups();

        if (currentGroupId) {
            loadMessages();
        }
    }
};

// --------------------
// AUTH
// --------------------
async function login() {
    const username = document.getElementById("username")?.value;
    const password = document.getElementById("password")?.value;

    const response = await fetch("/api/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (!response.ok) {
        alert("Usuario o contraseña incorrectos");
        return;
    }

    token = data.access;
    currentUser = username;

    localStorage.setItem("token", token);
    localStorage.setItem("username", username);

    window.location.href = "/app/";
}

async function registerUser() {
    const username = document.getElementById("registerUsername")?.value;
    const email = document.getElementById("registerEmail")?.value;
    const password = document.getElementById("registerPassword")?.value;

    const response = await fetch("/api/auth/register/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password })
    });

    const data = await response.json();

    if (!response.ok) {
        alert(data.detail || "No se pudo registrar el usuario");
        return;
    }

    alert("Usuario registrado correctamente");
    window.location.href = "/login/";
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("selectedGroupId");

    token = null;
    currentUser = null;
    currentGroupId = null;

    window.location.href = "/login/";
}

// --------------------
// GROUPS
// --------------------
async function loadGroups() {
    const response = await fetch("/api/groups/", {
        headers: { "Authorization": "Bearer " + token }
    });

    if (!response.ok) {
        if (response.status === 401) {
            logout();
        }
        return;
    }

    const groups = await response.json();
    const container = document.getElementById("groupsList");
    if (!container) return;

    container.innerHTML = "";

    groups.forEach(group => {
        const div = document.createElement("div");
        div.className = "group-item";
        div.innerText = group.name;
        div.onclick = () => selectGroup(group.id, group.name);
        container.appendChild(div);
    });
}

function selectGroup(groupId, groupName) {
    currentGroupId = groupId;
    localStorage.setItem("selectedGroupId", groupId);

    const chatHeader = document.getElementById("chatHeader");
    if (chatHeader) {
        chatHeader.innerText = groupName;
    }

    loadMessages();
}

async function addMemberPrompt() {
    if (!currentGroupId) {
        alert("Primero selecciona un grupo");
        return;
    }

    const username = prompt("Ingresa el username del usuario a agregar:");
    if (!username) return;

    const response = await fetch(`/api/groups/${currentGroupId}/members/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ username })
    });

    const data = await response.json();

    if (!response.ok) {
        alert(data.detail || "No se pudo agregar el usuario");
        return;
    }

    alert(data.detail || "Usuario agregado correctamente");
}

// --------------------
// MESSAGES
// --------------------
async function loadMessages() {
    if (!currentGroupId) return;

    const response = await fetch(`/api/chat/groups/${currentGroupId}/messages/`, {
        headers: { "Authorization": "Bearer " + token }
    });

    if (!response.ok) {
        if (response.status === 401) {
            logout();
        }
        return;
    }

    const messages = await response.json();
    const container = document.getElementById("messagesContainer");
    if (!container) return;

    container.innerHTML = "";

    messages.forEach(msg => {
        const div = document.createElement("div");
        div.className = "message";

        if (msg.sender_username === currentUser) {
            div.classList.add("me");
        }

        div.innerText = msg.sender_username + ": " + msg.content;
        container.appendChild(div);
    });

    container.scrollTop = container.scrollHeight;
}

async function sendMessage() {
    if (!currentGroupId) {
        alert("Selecciona un grupo primero");
        return;
    }

    const input = document.getElementById("messageContent");
    const content = input?.value;

    if (!content || !content.trim()) return;

    const response = await fetch(`/api/chat/groups/${currentGroupId}/messages/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ content })
    });

    if (!response.ok) {
        if (response.status === 401) {
            logout();
        } else if (response.status === 403) {
            alert("No perteneces a este grupo");
        }
        return;
    }

    input.value = "";
    loadMessages();
}

// --------------------
// UI
// --------------------
function openCreateGroupModal() {
    const modal = document.getElementById("createGroupModal");
    if (modal) modal.style.display = "flex";
}

function closeModal() {
    const modal = document.getElementById("createGroupModal");
    if (modal) modal.style.display = "none";
}

async function createGroup() {
    const nameInput = document.getElementById("newGroupName");
    const name = nameInput?.value;

    if (!name || !name.trim()) return;

    const response = await fetch("/api/groups/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ name })
    });

    if (!response.ok) {
        alert("No se pudo crear el grupo");
        return;
    }

    nameInput.value = "";
    closeModal();
    loadGroups();
}

function toggleUserMenu() {
    const menu = document.getElementById("userDropdown");
    if (!menu) return;

    if (menu.style.display === "block") {
        menu.style.display = "none";
    } else {
        menu.style.display = "block";
    }
}