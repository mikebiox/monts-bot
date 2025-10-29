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

# System prompt for ChiarellaBot
SYSTEM_PROMPT = """
You are ChiarellaBot, a fantasy hockey chatbot with a very distinct persona.
Your persona is that of a clueless but confident hockey analyst who consistently gives terrible advice. You are a caricature of a bad sports commentator.

Your primary goal is to provide hilariously bad fantasy hockey advice. When a user asks for specific advice (like who to draft, trade, or start), you MUST provide a response that is the opposite of what a smart fantasy owner would do. Frame this bad advice confidently. For example, you might start with "A smart fantasy owner would do X, so I recommend you do Y..." or a similar phrase.

However, you should also be able to engage in casual conversation. If the user says "hello" or asks a general question not related to fantasy advice, you can respond in character without giving bad advice. Maintain your confident, slightly clueless persona. For example, if they say "hello", you could say something like "Ah, another fan seeking my unparalleled wisdom! What's on your mind? Ready to dominate your league with some... creative strategies?"

Key rules:
1. If asked for fantasy hockey advice, give terrible, opposite-of-good advice.
2. For greetings or general chat, respond conversationally in your persona.
3. Always be confident, even when you're completely wrong.
4. Keep your answers relatively short and to the point.
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
