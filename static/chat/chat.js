document.addEventListener("DOMContentLoaded", function () {
    let chatBox = document.getElementById("chat-box");
    let sendButton = document.getElementById("send-btn");
    let titleInput = document.getElementById("title");
    let descriptionInput = document.getElementById("description");
    let locationInput = document.getElementById("location");
    let imageInput = document.getElementById("image");

    let socket = new WebSocket("ws://localhost:8001/ws/chat/");

    socket.onmessage = function (event) {
        let data = JSON.parse(event.data);
        let msgElement = document.createElement("div");
        msgElement.classList.add("message");
        msgElement.innerHTML = `
            <strong>${data.title}</strong><br>
            ${data.description}<br>
            <a href="${data.location}" target="_blank">${data.location}</a><br>
            ${data.image ? `<img src="${data.image}" class="chat-img" />` : ""}
            <small>${data.created_at}</small>
        `;
        chatBox.append(msgElement);
        chatBox.scrollTop = chatBox.scrollHeight;  // Auto-scroll to bottom
    };

    sendButton.addEventListener("click", function () {
        let title = titleInput.value.trim();
        let description = descriptionInput.value.trim();
        let location = locationInput.value.trim();

        if (!title || !description || !location) {
            alert("All fields are required!");
            return;
        }

        let messageData = {
            title: title,
            description: description,
            location: location,
        };

        socket.send(JSON.stringify(messageData));  // ✅ Send message via WebSocket

        // ✅ Clear input fields after sending
        titleInput.value = "";
        descriptionInput.value = "";
        locationInput.value = "";
        imageInput.value = "";
    });
});
