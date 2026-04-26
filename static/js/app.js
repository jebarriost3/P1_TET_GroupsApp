let token = localStorage.getItem("token") || null;
let currentUser = localStorage.getItem("username") || null;
let currentGroupId = localStorage.getItem("selectedGroupId") || null;
let messagesRefreshTimer = null;

console.log("GroupsApp frontend version: read-status-v1");

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
        loadNotifications();
        setInterval(loadNotifications, 30000);
        messagesRefreshTimer = setInterval(() => {
            if (currentGroupId) {
                loadMessages(false);
            }
        }, 5000);

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
async function loadMessages(shouldScroll = true) {
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

        const text = document.createElement("div");
        text.innerText = msg.sender_username + ": " + (msg.content || "");
        div.appendChild(text);

        if (msg.attachment) {
            div.appendChild(renderAttachment(msg.attachment));
        }

        if (msg.sender_username === currentUser && msg.delivery_status) {
            div.appendChild(renderDeliveryStatus(msg.delivery_status));
        }

        container.appendChild(div);
    });

    if (shouldScroll) {
        container.scrollTop = container.scrollHeight;
    }
}

async function sendMessage() {
    if (!currentGroupId) {
        alert("Selecciona un grupo primero");
        return;
    }

    const input = document.getElementById("messageContent");
    const fileInput = document.getElementById("attachmentInput");
    const sendButton = document.getElementById("sendButton");
    const content = input?.value || "";
    const file = fileInput?.files?.[0] || null;

    if (!content.trim() && !file) return;

    if (sendButton) sendButton.disabled = true;

    let attachmentId = null;
    if (file) {
        attachmentId = await uploadAttachment(file);
        if (!attachmentId) {
            if (sendButton) sendButton.disabled = false;
            return;
        }
    }

    const response = await fetch(
        `/api/chat/groups/${currentGroupId}/messages/`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ content, attachment_id: attachmentId })
        }
    );

    if (!response.ok) {
        if (response.status === 401) {
            logout();
        } else if (response.status === 403) {
            alert("No perteneces a este grupo");
        } else {
            alert("No se pudo enviar el mensaje");
        }
        if (sendButton) sendButton.disabled = false;
        return;
    }

    input.value = "";
    if (fileInput) fileInput.value = "";
    showSelectedFile();
    if (sendButton) sendButton.disabled = false;
    loadMessages();
}

function renderAttachment(attachment) {
    const wrapper = document.createElement("div");
    wrapper.className = "attachment";

    if (attachment.legacy_reference) {
        wrapper.innerText = "Adjunto: " + attachment.legacy_reference;
        return wrapper;
    }

    const link = document.createElement("a");
    link.href = attachment.public_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.innerText = "Abrir adjunto: " + (attachment.original_name || "archivo");
    wrapper.appendChild(link);

    return wrapper;
}

function renderDeliveryStatus(status) {
    const statusElement = document.createElement("div");
    statusElement.className = "delivery-status";

    const labels = {
        sent: "✓ enviado",
        delivered: "✓✓ entregado",
        read: "✓✓ leído"
    };

    statusElement.innerText = labels[status] || status;
    if (status === "read") {
        statusElement.classList.add("read");
    }

    return statusElement;
}

async function uploadAttachment(file) {
    const formData = new FormData();
    formData.append("file", file);

    const selectedFileName = document.getElementById("selectedFileName");
    if (selectedFileName) {
        selectedFileName.innerText = "Subiendo " + file.name + "...";
    }

    const response = await fetch("/api/files/upload/", {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token
        },
        body: formData
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        alert(data.detail || "No se pudo subir el archivo");
        showSelectedFile();
        return null;
    }

    return data.id;
}

function showSelectedFile() {
    const fileInput = document.getElementById("attachmentInput");
    const label = document.getElementById("selectedFileName");
    if (!label) return;

    const file = fileInput?.files?.[0];
    label.innerText = file ? file.name : "";
}

// --------------------
// NOTIFICATIONS
// --------------------
async function loadNotifications() {
    if (!token) return;

    const response = await fetch("/api/notifications/", {
        headers: { "Authorization": "Bearer " + token }
    });

    if (!response.ok) return;

    const notifications = await response.json();
    const panel = document.getElementById("notificationsPanel");
    const badge = document.getElementById("notificationsBadge");
    if (!panel || !badge) return;

    const unreadCount = notifications.filter(item => !item.is_read).length;
    badge.innerText = unreadCount;
    badge.style.display = unreadCount ? "inline-flex" : "none";

    panel.innerHTML = "";

    if (!notifications.length) {
        const empty = document.createElement("div");
        empty.className = "notification-empty";
        empty.innerText = "No tienes notificaciones";
        panel.appendChild(empty);
        return;
    }

    notifications.slice(0, 10).forEach(notification => {
        const item = document.createElement("div");
        item.className = "notification-item";
        if (!notification.is_read) item.classList.add("unread");

        const title = document.createElement("strong");
        title.innerText = notification.title;

        const body = document.createElement("p");
        body.innerText = notification.body;

        item.appendChild(title);
        item.appendChild(body);
        item.onclick = () => markNotificationAsRead(notification.id);

        panel.appendChild(item);
    });
}

async function markNotificationAsRead(notificationId) {
    await fetch(`/api/notifications/${notificationId}/read/`, {
        method: "POST",
        headers: { "Authorization": "Bearer " + token }
    });

    loadNotifications();
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

function toggleNotifications() {
    const panel = document.getElementById("notificationsPanel");
    if (!panel) return;

    panel.style.display = panel.style.display === "block" ? "none" : "block";
    if (panel.style.display === "block") {
        loadNotifications();
    }
}
