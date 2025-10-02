from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from groq import Groq

client = Groq(api_key="")

app = FastAPI()

@app.get("/api")
def idea():
    message = "Come up with a new business idea for AI Agents"

    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",   # free Groq model
        messages=[
            {"role": "user", "content": message}
        ], stream=True
    )

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines:
                    yield f"data: {line}\n"
                yield "\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")