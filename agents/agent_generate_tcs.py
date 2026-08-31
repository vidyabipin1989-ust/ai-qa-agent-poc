from ollama import chat
import os
import json

# Read user story
with open("stories/story.txt", "r") as f:
    story = f.read()

# Generate test cases
response = chat(
    model="llama3.2",
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

# Get model output
result = json.loads(response["message"]["content"])

# Create output directory
os.makedirs("tcs", exist_ok=True)

# Dynamic filename
file_name = result.get("story_id", "testcases")

output_file = f"tcs/{file_name}.json"

# Save JSON
with open(output_file, "w") as f:
    json.dump(result, f, indent=2)

print(f"Test cases saved to {output_file}")
