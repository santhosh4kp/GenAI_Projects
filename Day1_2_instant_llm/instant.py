import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from groq import Groq
app = FastAPI()
# Load from environment variable
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
@app.get("/", response_class=HTMLResponse)
def root():
    message = "You are on a website that has just been deployed to production for the first time! Please reply with an enthusiastic announcement."
    chat_completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": message}
        ]
    )
    reply = chat_completion.choices[0].message.content
    reply_html = reply.replace("\n", "<br/>")
    html = f"""
    <html>
        <head><title>Live in an Instant!</title></head>
        <body>
            <p>{reply_html}</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html)
