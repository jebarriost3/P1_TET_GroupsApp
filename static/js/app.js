let token = null;

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch("http://127.0.0.1:8000/api/auth/login/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    });

    const data = await response.json();
    token = data.access;

    alert("Login exitoso");
    console.log("TOKEN:", token);
}

async function createGroup() {
    const name = document.getElementById("groupName").value;

    const response = await fetch("http://127.0.0.1:8000/api/groups/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            name: name
        })
    });

    const data = await response.json();
    console.log(data);
    alert("Grupo creado");
}

async function sendMessage() {
    const groupId = document.getElementById("groupIdMsg").value;
    const content = document.getElementById("messageContent").value;

    const response = await fetch(`http://127.0.0.1:8000/api/chat/groups/${groupId}/messages/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            content: content
        })
    });

    const data = await response.json();
    console.log(data);
    alert("Mensaje enviado");
}
async function addMember() {
    const groupId = document.getElementById("groupIdAdd").value;
    const username = document.getElementById("usernameToAdd").value;

    const response = await fetch(`http://127.0.0.1:8000/api/groups/${groupId}/members/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            username: username
        })
    });

    const data = await response.json();
    console.log(data);
    alert(data.detail);
}