import anthropic

try:
    client = anthropic.Anthropic()
    print("Client created successfully")
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Say hello"}
        ]
    )
    print("Response received:")
    print(message.content[0].text)

except Exception as e:
    print(f"Error: {e}")
