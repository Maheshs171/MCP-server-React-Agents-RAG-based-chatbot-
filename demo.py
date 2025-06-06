from openai import OpenAI
from config import OPENAI_API_KEY

# Your server URL (replace with your actual URL)
url = 'https://12ac-49-248-169-218.ngrok-free.app'

history = []

client = OpenAI(api_key=OPENAI_API_KEY)

while True:
    ip = input("User :: ")
    history.append({"role":"user", "content": ip})
    if ip == "exit":
        break
    resp = client.responses.create(
        model="gpt-4o",
        temperature=0.6,
        parallel_tool_calls=True,
        tools=[
            {
                "type": "mcp",
                "server_label": "dice_server",
                "server_url": f"{url}/sse",
                "require_approval": "never",
            },
        ],
        input=str(history),
    )
    history.append({"role":"agent", "content": resp.output_text})
    print("AI :: ",resp.output_text)
    
    
    
                
