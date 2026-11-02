
const API_URL = "http://127.0.0.1:8000/api/v1/chat/stream";
const HEALTH_URL = "http://127.0.0.1:8000/health";

const chatArea = document.getElementById("chatArea");
const messagesContainer = document.getElementById("messages");
const welcomeScreen = document.getElementById("welcomeScreen");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const newChatBtn = document.getElementById("newChatBtn");
const connectionStatus = document.getElementById("connectionStatus");

let conversationHistory = [];
let isStreaming = false;


// ----------------------------------
// Backend connection
// ----------------------------------

async function checkBackend() {
    try {
        const response = await fetch(HEALTH_URL);

        if (!response.ok) {
            throw new Error("Backend unavailable");
        }

        connectionStatus.textContent = "Backend connected";
    } catch (error) {
        connectionStatus.textContent = "Backend disconnected";
        console.error("Backend connection:", error);
    }
}

checkBackend();


// ----------------------------------
// HTML escaping and Markdown formatting
// ----------------------------------

function escapeHTML(text) {
    return text.replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[character]);
}

function formatMessage(text) {
    let html = escapeHTML(text);

    html = html.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    html = html.replace(
        /\*(.*?)\*/g,
        "<em>$1</em>"
    );

    // Basic unordered lists
    html = html.replace(
        /(?:^|\n)- (.*)/g,
        "<li>$1</li>"
    );

    html = html.replace(
        /(<li>[\s\S]*?<\/li>)/g,
        "<ul>$1</ul>"
    );

    // Preserve line breaks
    html = html.replace(/\n/g, "<br>");

    return html;
}


// ----------------------------------
// Render messages
// ----------------------------------

function addMessage(role, content = "") {
    welcomeScreen.style.display = "none";

    const message = document.createElement("div");
    message.className = `message ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = role === "user" ? "U" : "C";

    const messageContent = document.createElement("div");
    messageContent.className = "message-content";

    if (role === "assistant") {
        messageContent.innerHTML = formatMessage(content);
    } else {
        messageContent.textContent = content;
    }

    message.appendChild(avatar);
    message.appendChild(messageContent);

    messagesContainer.appendChild(message);

    chatArea.scrollTop = chatArea.scrollHeight;

    return messageContent;
}


// ----------------------------------
// Typing indicator
// ----------------------------------

function showTypingIndicator() {
    const indicator = document.createElement("div");

    indicator.className = "message";
    indicator.id = "typingIndicator";

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "C";

    const content = document.createElement("div");
    content.className = "message-content";

    const animation = document.createElement("div");
    animation.className = "typing-indicator";

    for (let i = 0; i < 3; i++) {
        const dot = document.createElement("span");
        animation.appendChild(dot);
    }

    content.appendChild(animation);
    indicator.appendChild(avatar);
    indicator.appendChild(content);

    messagesContainer.appendChild(indicator);

    chatArea.scrollTop = chatArea.scrollHeight;
}

function removeTypingIndicator() {
    document.getElementById("typingIndicator")?.remove();
}


// ----------------------------------
// Parse Server-Sent Events
// ----------------------------------

function processSSEEvent(event, onToken) {
    const lines = event.split(/\r?\n/);

    for (const line of lines) {
        if (!line.startsWith("data:")) continue;

        const rawData = line.slice(5).trim();

        if (!rawData) continue;

        let data;

        try {
            data = JSON.parse(rawData);
        } catch (error) {
            console.error("Invalid SSE event:", rawData);
            continue;
        }

        if (data.type === "token") {
            onToken(data.content || "");
        }

        if (data.type === "done") {
            return "done";
        }

        if (data.type === "error") {
            throw new Error(data.content || "Assistant error");
        }
    }

    return null;
}


// ----------------------------------
// Send message and stream response
// ----------------------------------

async function sendMessage(message) {
    message = message.trim();

    if (!message || isStreaming) return;

    isStreaming = true;

    const previousHistory = [...conversationHistory];

    addMessage("user", message);

    messageInput.value = "";
    messageInput.style.height = "auto";

    sendBtn.disabled = true;
    messageInput.disabled = true;

    showTypingIndicator();

    let assistantMessage = "";
    let assistantElement = null;
    let completed = false;

    try {
        // Keep the request compatible with the backend schema.
        const safeHistory = previousHistory
            .slice(-10)
            .map(item => ({
                role: item.role,
                content: String(item.content).slice(-4000)
            }));

        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            body: JSON.stringify({
                message: message,
                history: safeHistory
            })
        });

        if (!response.ok) {
            const errorDetails = await response.text();

            throw new Error(
                `HTTP ${response.status}: ${errorDetails}`
            );
        }

        if (!response.body) {
            throw new Error("Streaming is not supported by this response.");
        }

        removeTypingIndicator();

        assistantElement = addMessage("assistant", "");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let buffer = "";

        function handleToken(token) {
            assistantMessage += token;

            assistantElement.innerHTML =
                formatMessage(assistantMessage);

            chatArea.scrollTop = chatArea.scrollHeight;
        }

        function handleEvent(event) {
            const result = processSSEEvent(event, handleToken);

            if (result === "done") {
                completed = true;
            }
        }

        while (true) {
            const { value, done } = await reader.read();

            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // Support both LF and CRLF SSE separators.
            const events = buffer.split(/\r?\n\r?\n/);

            buffer = events.pop() || "";

            for (const event of events) {
                handleEvent(event);
            }
        }

        // Flush any remaining decoder data and final SSE event.
        buffer += decoder.decode();

        if (buffer.trim()) {
            handleEvent(buffer);
        }

        if (!assistantMessage.trim()) {
            throw new Error("The assistant returned an empty response.");
        }

        // Save only completed assistant responses.
        if (completed) {
            conversationHistory = [
                ...previousHistory,
                { role: "user", content: message },
                {
                    role: "assistant",
                    content: assistantMessage
                }
            ];

            // Keep history within the backend's configured limit.
            conversationHistory = conversationHistory.slice(-10);
        } else {
            throw new Error("The response stream ended unexpectedly.");
        }

        connectionStatus.textContent = "Backend connected";

    } catch (error) {
        console.error("Chat error:", error);

        if (assistantElement) {
            assistantElement.textContent =
                assistantMessage
                    ? "The response was interrupted. Please try again."
                    : `Unable to get a response: ${error.message}`;
        } else {
            removeTypingIndicator();

            addMessage(
                "assistant",
                `Unable to connect to CoverCare AI.\n\n${error.message}`
            );
        }

        connectionStatus.textContent = "Connection error";

    } finally {
        removeTypingIndicator();

        isStreaming = false;

        sendBtn.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
    }
}


// ----------------------------------
// Chat form
// ----------------------------------

chatForm.addEventListener("submit", event => {
    event.preventDefault();

    const message = messageInput.value.trim();

    if (message) {
        sendMessage(message);
    }
});


// ----------------------------------
// Keyboard shortcuts
// ----------------------------------

messageInput.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        chatForm.requestSubmit();
    }
});


// ----------------------------------
// Auto-resize input
// ----------------------------------

messageInput.addEventListener("input", () => {
    messageInput.style.height = "auto";

    messageInput.style.height =
        Math.min(messageInput.scrollHeight, 120) + "px";
});


// ----------------------------------
// Default conversation examples
// ----------------------------------

document.querySelectorAll("[data-prompt]").forEach(button => {
    button.addEventListener("click", () => {
        const prompt = button.dataset.prompt;

        if (prompt) {
            sendMessage(prompt);
        }
    });
});


// ----------------------------------
// Start a new conversation
// ----------------------------------

newChatBtn.addEventListener("click", () => {
    if (isStreaming) return;

    conversationHistory = [];

    messagesContainer.innerHTML = "";

    welcomeScreen.style.display = "block";

    messageInput.value = "";
    messageInput.style.height = "auto";
    messageInput.focus();
});
