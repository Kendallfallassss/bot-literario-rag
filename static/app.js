const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");
const clearChatBtn = document.getElementById("clearChat");

const loadBtn = document.getElementById("loadBtn");
const loadStatus = document.getElementById("loadStatus");

// ---------- UI HELPERS ----------

function addMessage(text, sender, id = null) {
  const msg = document.createElement("div");
  msg.className = `message ${sender === "user" ? "blue-bg" : "gray-bg"}`;
  if (id) msg.id = id;

  msg.innerHTML = `
    <div class="message-sender">${sender === "user" ? "You" : "Bot"}</div>
    <div class="message-text">${text}</div>
  `;

  chatMessages.appendChild(msg);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ---------- LOAD BOOKS ----------

loadBtn.addEventListener("click", async () => {
  addMessage("Loading books...", "bot", "loading");

  try {
    const res = await fetch("/load", { method: "POST" });
    const data = await res.json();

    document.getElementById("loading")?.remove();

    if (data.error) {
      addMessage(data.error, "bot");
      return;
    }

    addMessage(
      `Books loaded successfully.<br>
       Files: ${data.total_files_found}<br>
       Chunks created: ${data.chunks_created}`,
      "bot"
    );

  } catch (err) {
    document.getElementById("loading")?.remove();
    addMessage("Error loading books.", "bot");
  }
});


// ---------- CHAT ----------

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const question = chatInput.value.trim();
  if (!question) return;

  addMessage(question, "user");
  chatInput.value = "";

  // THINKING MESSAGE
  addMessage("Thinking...", "bot", "thinking");

  const response = await fetch("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });

  const data = await response.json();

  //  REMOVE THINKING
  const thinkingMsg = document.getElementById("thinking");
  if (thinkingMsg) thinkingMsg.remove();

  addMessage(data.answer, "bot");
});

// ---------- CLEAR ----------

clearChatBtn.addEventListener("click", () => {
  chatMessages.innerHTML = "";
});

// ---------- LOAD EXISTING BOOKS ON START ----------

window.addEventListener("DOMContentLoaded", async () => {
  try {
    const res = await fetch("/books");
    const data = await res.json();

    if (data.books && data.books.length > 0) {
      const fileList = data.books.join("<br>• ");
      addMessage(`Books already loaded:<br>• ${fileList}`, "bot");
    } else {
      addMessage("No books currently stored in database.", "bot");
    }

  } catch (err) {
    addMessage("Error checking stored books.", "bot");
  }
});