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
            appendMessage(data);  // ✅ Append new message dynamically
        } else if (data.type === "chat_history") {
            data.messages.forEach(msg => appendMessage(msg));  // ✅ Load old messages
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
        let imageUrl = null;
        let messageData = {
            title: title,
            description: description,
            location: location,
            image: imageUrl, 
        };

        if (imageFile) {
            // ✅ Upload image via an API before sending the message
            let formData = new FormData();
            formData.append("image", imageFile);

            fetch("/upload-image/", {
                method: "POST",
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.image_url) {
                    messageData.image = data.image_url;  // ✅ Add uploaded image URL
                }
                socket.send(JSON.stringify(messageData));  // ✅ Send message via WebSocket
            })
            .catch(error => console.error("Image upload error:", error));
        }else {
            socket.send(JSON.stringify(messageData));  // ✅ Send message if no image
        }


        

        // socket.send(JSON.stringify(messageData));  // ✅ Send message via WebSocket

        // ✅ Clear input fields after sending
        titleInput.value = "";
        descriptionInput.value = "";
        locationInput.value = "";
        imageInput.value = "";
    });

    // function appendMessage(data) {
    //     let msgElement = document.createElement("div");
    //     msgElement.classList.add("message");
    //     msgElement.innerHTML = `
    //         <strong>${data.title}</strong><br>
    //         ${data.description}<br>
    //         <a href="${data.location}" target="_blank">${data.location}</a><br>
    //         ${data.image ? `<img src="${data.image}" class="chat-img" onerror="this.onerror=null;this.src='/static/default-placeholder.png';" />` : ""}
    //         <small>${data.created_at}</small>
    //     `;
    //     chatBox.append(msgElement);
    //     chatBox.scrollTop = chatBox.scrollHeight;  // ✅ Auto-scroll to bottom
    // }

    function appendMessage(data) {
        let imgUrl = data.image;
    
        // ✅ Remove duplicate "/media/media/" if it exists
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
        chatBox.scrollTop = chatBox.scrollHeight;  // ✅ Auto-scroll to bottom
    }
    
});


