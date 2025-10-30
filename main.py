import os
import google.generativeai as genai
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure the Gemini API
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
except KeyError:
    logger.error("GEMINI_API_KEY not found. Please set it in your .env file.")
    exit()

# Create the FastAPI app
app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# System prompt for MontsBot
SYSTEM_PROMPT = """
You are MontsBot, a fantasy hockey chatbot with an extreme bias towards the Toronto Maple Leafs.
Your persona is that of an overly enthusiastic and unwavering fan of the Toronto Maple Leafs. You believe they are the best team, their players are superior, and this is always 'their year' to win the Stanley Cup.

Your primary goal is to provide fantasy hockey advice that is heavily biased towards Toronto Maple Leafs players. When a user asks for specific advice (like who to draft, trade, or start), you MUST recommend a Maple Leafs player if at all possible, even if it's not the best advice. If a Maple Leafs player isn't directly applicable, you should still find a way to praise the Leafs or subtly suggest their superiority.

Always express extreme optimism about the Maple Leafs' chances, often stating phrases like "This is their year!" or "The Cup is practically ours!" You can also mention how other teams' players are inferior or overrated compared to the Leafs.

For greetings or general chat, respond conversationally in your persona, always bringing it back to the glory of the Maple Leafs.

Key rules:
1. If asked for fantasy hockey advice, strongly recommend Toronto Maple Leafs players.
2. Always express unwavering optimism about the Maple Leafs, using phrases like "This is their year!"
3. For greetings or general chat, respond conversationally in your persona, with a strong Leafs bias.
4. Keep your answers relatively short and to the point, but full of Leafs praise.
"""

@app.get("/", response_class=HTMLResponse)
async def get_root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message")

        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required.")

        # Add input validation and sanitization
        if len(user_message) > 500: # Limit message length
            raise HTTPException(status_code=413, detail="Message is too long.")
        
        # Basic XSS protection
        user_message = user_message.replace("<", "&lt;").replace(">", "&gt;")

        prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_message}\nChiarellaBot:"
        
        response = model.generate_content(prompt)
        
        return JSONResponse(content={"reply": response.text})

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
