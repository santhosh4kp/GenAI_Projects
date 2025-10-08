from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from groq import Groq

app = FastAPI()

# Initialize Groq client (you’ll get the key from console.groq.com)
#https://console.groq.com/keys
client = Groq(api_key="")

@app.get("/", response_class=HTMLResponse)
def root():
    # Example system prompt
    message = "You are on a website that has just been deployed to production for the first time! Please reply with an enthusiastic announcement."

    chat_completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",   # free Groq model
        messages=[
            {"role": "user", "content": message}
        ]
    )

    reply = chat_completion.choices[0].message.content
    reply_html = reply.replace("\n", "<br/>").replace("**", "<b>").replace("</b><b>", "</b>").replace("<b>", "<b>").replace("<br/><br/>", "<p></p>")

    html = f"""
    <html>
        <head><title>Live in an Instant!</title></head>
        <body>
            <p>{reply_html}</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html)