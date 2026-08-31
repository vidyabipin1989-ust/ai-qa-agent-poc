from anthropic import Anthropic

client = Anthropic()

story = open("story.txt").read()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2000,
    messages=[
        {
            "role": "user",
            "content": f"Generate test cases for:\n{story}"
        }
    ]
)

print(response.content[0].text)
