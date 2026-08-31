from anthropic import Anthropic
import os
import json

client = Anthropic()

# Read user story
with open("story.txt", "r") as f:
    story = f.read()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2000,
    messages=[
        {
            "role": "user",
            "content": f"""
Extract the Story ID and generate test cases.

Return ONLY valid JSON.
Do not include markdown or explanations.

Format:
{{
  "story_id": "...",
  "test_cases": [...]
}}

User Story:
{story}
"""
        }
    ]
)

result = json.loads(response.content[0].text)

os.makedirs("tcs", exist_ok=True)

file_name = result.get("story_id", "testcases")

output_file = f"tcs/{file_name}.json"

with open(output_file, "w") as f:
    json.dump(result, f, indent=2)

print(f"Test cases saved to {output_file}")
