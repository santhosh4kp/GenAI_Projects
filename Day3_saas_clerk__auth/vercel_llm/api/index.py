from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from groq import Groq

import os
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials


client = Groq(api_key="")

app = FastAPI()

clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)

# @app.get("/api")
# def idea(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
#     user_id = creds.decoded["sub"]  # User ID from JWT - available for future use
#     # We now know which user is making the request! 
#     # You could use user_id to:
#     # - Track usage per user
#     # - Store generated ideas in a database
#     # - Apply user-specific limits or customization
    
#     #print(user_id)
#     #llm call
#     message = "Come up with a new business idea for AI Agents"

#     stream = client.chat.completions.create(
#         model="llama-3.1-8b-instant",   # free Groq model
#         messages=[
#             {"role": "user", "content": message}
#         ], stream=True
#     )

#     # def event_stream():
#     #     for chunk in stream:
#     #         text = chunk.choices[0].delta.content
#     #         if text:
#     #             lines = text.split("\n")
#     #             for line in lines[:-1]:
#     #                 yield f"data: {line}\n\n"
#     #                 yield "data:  \n"
#     #             yield f"data: {lines[-1]}\n\n"
#     #return StreamingResponse(event_stream(), media_type="text/event-stream")
#     return stream


@app.get("/api")
def idea(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    user_id = creds.decoded["sub"]

    message = "Come up with a new business idea for AI Agents"

    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": message}],
        stream=True
    )

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines[:-1]:
                    yield f"data: {line}\n\n"
                    yield "data:  \n"
                yield f"data: {lines[-1]}\n\n"


    return StreamingResponse(event_stream(), media_type="text/event-stream")