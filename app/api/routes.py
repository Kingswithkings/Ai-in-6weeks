from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.services.ai_service import ai_service


router = APIRouter()


@router.get("/", include_in_schema=False)
async def home() -> RedirectResponse:
    return RedirectResponse(url="/chat")


@router.get("/chat", response_class=HTMLResponse, include_in_schema=False)
async def chat_page() -> str:
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Kings AI Chat</title>
        <style>
          :root {
            color-scheme: light;
            font-family: Arial, sans-serif;
            background: #f5f7fb;
            color: #172033;
          }
          body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
          }
          main {
            width: min(760px, calc(100vw - 32px));
            background: #ffffff;
            border: 1px solid #d9e0ea;
            border-radius: 8px;
            box-shadow: 0 12px 30px rgba(23, 32, 51, 0.08);
            overflow: hidden;
          }
          header {
            padding: 18px 20px;
            border-bottom: 1px solid #d9e0ea;
            font-weight: 700;
          }
          #messages {
            min-height: 360px;
            max-height: 60vh;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
          }
          .message {
            max-width: 82%;
            padding: 10px 12px;
            border-radius: 8px;
            line-height: 1.45;
            white-space: pre-wrap;
          }
          .user {
            align-self: flex-end;
            background: #1f6feb;
            color: #ffffff;
          }
          .assistant {
            align-self: flex-start;
            background: #eef2f7;
          }
          form {
            display: flex;
            gap: 10px;
            padding: 16px;
            border-top: 1px solid #d9e0ea;
          }
          input {
            flex: 1;
            min-width: 0;
            padding: 12px;
            border: 1px solid #c9d3df;
            border-radius: 6px;
            font: inherit;
          }
          button {
            padding: 0 16px;
            border: 0;
            border-radius: 6px;
            background: #172033;
            color: #ffffff;
            font: inherit;
            cursor: pointer;
          }
          button:disabled {
            opacity: 0.6;
            cursor: wait;
          }
        </style>
      </head>
      <body>
        <main>
          <header>Kings AI Chat</header>
          <section id="messages" aria-live="polite"></section>
          <form id="chat-form">
            <input id="message" name="message" autocomplete="off" placeholder="Type a message" required>
            <button type="submit">Send</button>
          </form>
        </main>
        <script>
          const form = document.querySelector("#chat-form");
          const input = document.querySelector("#message");
          const button = form.querySelector("button");
          const messages = document.querySelector("#messages");

          function addMessage(text, className) {
            const item = document.createElement("div");
            item.className = `message ${className}`;
            item.textContent = text;
            messages.appendChild(item);
            messages.scrollTop = messages.scrollHeight;
          }

          form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const text = input.value.trim();
            if (!text) return;

            addMessage(text, "user");
            input.value = "";
            button.disabled = true;

            try {
              const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
              });
              const data = await response.json();
              addMessage(data.reply || data.detail || "No response", "assistant");
            } catch (error) {
              addMessage("Request failed. Check the server logs.", "assistant");
            } finally {
              button.disabled = false;
              input.focus();
            }
          });
        </script>
      </body>
    </html>
    """


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    result = await ai_service.process_message(request.message)
    return ChatResponse(**result)
