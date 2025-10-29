document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");

    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const userMessage = userInput.value;
        if (!userMessage) return;

        appendMessage(userMessage, "user");
        userInput.value = "";

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: userMessage }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            appendMessage(data.reply, "bot");
        } catch (error) {
            console.error("Error:", error);
            appendMessage("Sorry, something went wrong. Please try again.", "bot");
        }
    });

    function appendMessage(message, sender) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message", `${sender}-message`);
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
