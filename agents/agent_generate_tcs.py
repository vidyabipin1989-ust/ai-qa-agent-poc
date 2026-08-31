from anthropic import Anthropic
import os

client = Anthropic()

# Read user story
with open("story.txt", "r") as f:
    story = f.read()

# Generate test cases
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2000,
    messages=[
        {
            "role": "user",
            "content": f"""
Generate test cases for the following user story.
Return ONLY valid JSON.

User Story:
{story}
"""
        }
    ]
)

# Create folder if it doesn't exist
os.makedirs("tcs", exist_ok=True)

# Save response as JSON file
with open("tcs/testcases.json", "w") as f:
    f.write(response.content[0].text)

print("Test cases saved to tcs/testcases.json")
