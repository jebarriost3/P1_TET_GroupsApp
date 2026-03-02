let token = null;
let currentUser = null;
let currentGroupId = null;

// login

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch("http://127.0.0.1:8000/api/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    token = data.access;
    currentUser = username;

    document.getElementById("loginScreen").style.display = "none";
    document.getElementById("appScreen").style.display = "block";

    document.getElementById("userInfo").innerText = username;

    loadGroups();

    document.querySelector(".sidebar").classList.add("centered-dashboard");
}

// groups

async function loadGroups() {
    const response = await fetch("http://127.0.0.1:8000/api/groups/", {
        headers: { "Authorization": "Bearer " + token }
    });

    const groups = await response.json();
    const container = document.getElementById("groupsList");
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

    document.getElementById("dashboard").style.display = "none";
    document.getElementById("chatArea").style.display = "block";

    document.getElementById("chatHeader").innerText = groupName;


    document.querySelector(".sidebar").classList.remove("centered-dashboard");

    loadMessages();
}

function backToGroups() {
    document.getElementById("chatArea").style.display = "none";
    document.getElementById("dashboard").style.display = "block";


    document.querySelector(".sidebar").classList.add("centered-dashboard");
}

// messages

async function loadMessages() {
    const response = await fetch(
        `http://127.0.0.1:8000/api/chat/groups/${currentGroupId}/messages/`,
        { headers: { "Authorization": "Bearer " + token } }
    );

    const messages = await response.json();
    const container = document.getElementById("messagesContainer");
    container.innerHTML = "";

    messages.forEach(msg => {
        const div = document.createElement("div");
        div.className = "message";

        if (msg.sender === currentUser) {
            div.classList.add("me");
        }

        div.innerText = msg.sender + ": " + msg.content;
        container.appendChild(div);
    });

    container.scrollTop = container.scrollHeight;
}

async function sendMessage() {

    if (!currentGroupId) {
        alert("Selecciona un grupo primero");
        return;
    }

    const content = document.getElementById("messageContent").value;

    if (!content.trim()) return;

    await fetch(
        `http://127.0.0.1:8000/api/chat/groups/${currentGroupId}/messages/`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ content })
        }
    );

    document.getElementById("messageContent").value = "";
    loadMessages();
}

// create group

async function createGroupPrompt() {
    const name = prompt("Nombre del grupo:");
    if (!name) return;

    await fetch("http://127.0.0.1:8000/api/groups/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ name })
    });

    loadGroups();
}