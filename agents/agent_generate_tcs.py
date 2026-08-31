from anthropic import Anthropic
import os
import json

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

Return ONLY valid JSON in the format:

{{
  "story_id": "short_unique_name",
  "test_cases": [...]
}}

User Story:
{story}
"""
        }
    ]
)

# Parse Claude's response
result = json.loads(response.content[0].text)

# Create folder if it doesn't exist
os.makedirs("tcs", exist_ok=True)

# Dynamic filename
file_name = result["story_id"]

# Save JSON
output_file = f"tcs/{file_name}.json"

with open(output_file, "w") as f:
    json.dump(result, f, indent=2)

print(f"Test cases saved to {output_file}")
