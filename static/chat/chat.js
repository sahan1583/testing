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
        if (data.type === "chat_message") {
            appendMessage(data);
        } else if (data.type === "chat_history") {
            data.messages.forEach(msg => appendMessage(msg));
        }
    };

    sendButton.addEventListener("click", async function () {
        let title = titleInput.value.trim();
        let description = descriptionInput.value.trim();
        let location = locationInput.value.trim();
        let imageFile = imageInput.files[0];

        if (!title || !description || !location) {
            alert("All fields are required!");
            return;
        }
        if (imageFile) {
            const allowedTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"];
            if (!allowedTypes.includes(imageFile.type)) {
                alert("Invalid file type! Please upload an image (JPG, PNG, GIF, WEBP).");
                imageInput.value = ""; 
                return;
            }
        }
        let messageData = { title, description, location, image: null };

        if (imageFile) {
            let formData = new FormData();
            formData.append("image", imageFile);

            try {
                let response = await fetch("/upload-image/", { method: "POST", body: formData });
                let data = await response.json();
                if (data.image_url) {
                    messageData.image = data.image_url;
                }
            } catch (error) {
                console.error("Image upload error:", error);
            }
        }

        socket.send(JSON.stringify(messageData)); 
        titleInput.value = "";
        descriptionInput.value = "";
        locationInput.value = "";
        imageInput.value = "";
    });

    function appendMessage(data) {
        let imgUrl = data.image;
        if (imgUrl && imgUrl.includes("/media/media/")) {
            imgUrl = imgUrl.replace("/media/media/", "/media/");
        }

        if (imgUrl) {
            imgUrl = decodeURIComponent(imgUrl);
        }

        let msgElement = document.createElement("div");
        msgElement.classList.add("message");
        msgElement.innerHTML = `
            <strong>${data.title}</strong><br>
            ${data.description}<br>
            <a href="${data.location}" target="_blank">${data.location}</a><br>
            ${imgUrl ? `<img src="${imgUrl}" class="chat-img" onerror="this.onerror=null;this.src='/static/default-placeholder.png';" />` : ""}
            <small>${data.created_at}</small>
        `;
        chatBox.append(msgElement);
        
        const img = msgElement.querySelector("img");
        if (img) {
            img.onload = () => {
                chatBox.scrollTop = chatBox.scrollHeight;
            };
        } else {
            chatBox.scrollTop = chatBox.scrollHeight;
        } 
    }
});