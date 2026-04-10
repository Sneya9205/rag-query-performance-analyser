import os
from google import genai

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain why SELECT * is slow in databases."
)

print(response.text)
'''
setx GEMINI_API_KEY "AIzaSyCAkKvXUPFeUYcEyXtnkRguYsYAE9R0Pxc"
$env:GEMINI_API_KEY="AIzaSyCAkKvXUPFeUYcEyXtnkRguYsYAE9R0Pxc"
'''