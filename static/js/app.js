window.onload = function() {

    const savedToken = localStorage.getItem("token");
    const savedUser = localStorage.getItem("username");

    if (savedToken) {

        token = savedToken;
        currentUser = savedUser;

        document.getElementById("loginScreen").style.display = "none";
        document.getElementById("appScreen").style.display = "block";

        document.getElementById("userInfo").innerText = currentUser;

        loadGroups();
    }

};


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

  
    if (!response.ok) {
        alert("Usuario o contraseña incorrectos");
        return;
    }

    
    token = data.access;
    currentUser = username;

    localStorage.setItem("token", token);
    localStorage.setItem("username", username)

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

    document.getElementById("chatHeader").innerText = groupName;

    document.querySelector(".sidebar").classList.remove("centered-dashboard");

    loadMessages();

}

function backToGroups() {
    currentGroupId = null;
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

function openCreateGroupModal() {
    document.getElementById("createGroupModal").style.display = "flex";
}

function closeModal() {
    document.getElementById("createGroupModal").style.display = "none";
}

async function createGroup() {

    const name = document.getElementById("newGroupName").value;

    if (!name.trim()) return;

    await fetch("http://127.0.0.1:8000/api/groups/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ name })
    });

    document.getElementById("newGroupName").value = "";

    closeModal();

    loadGroups();
}

function toggleUserMenu() {

    const menu = document.getElementById("userDropdown");

    if (menu.style.display === "block") {
        menu.style.display = "none";
    } else {
        menu.style.display = "block";
    }

}

function logout() {

    localStorage.removeItem("token");
    localStorage.removeItem("username");

    token = null;
    currentUser = null;
    currentGroupId = null;

    document.getElementById("appScreen").style.display = "none";
    
    document.getElementById("appScreen").style.display = "none";
    document.getElementById("loginScreen").style.display = "flex";

}