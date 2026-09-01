from ollama import chat
import os
import json

SYSTEM_PROMPT = """
You are an AI Test Case Generation Agent.

Your responsibility is to analyze a software user story and generate
complete, high-quality manual test cases.

Follow this workflow internally:

1. Extract the Story ID.
2. Understand the feature and user requirements.
3. Identify acceptance criteria.
4. Identify business rules.
5. Identify positive test scenarios.
6. Identify negative test scenarios.
7. Identify boundary value scenarios.
8. Identify edge cases.
9. Generate test cases covering all identified scenarios.
10. Ensure there are no duplicate test cases.

TEST CASE REQUIREMENTS:

Each test case must include:

- test_case_id
- title
- description
- preconditions
- test_steps
- test_data
- expected_result
- priority
- test_type

TEST TYPES can include:

- Functional
- Positive
- Negative
- Boundary
- Edge Case
- Validation

PRIORITY must be one of:

- High
- Medium
- Low

IMPORTANT RULES:

- Do not invent requirements that are not supported by the user story.
- If acceptance criteria are missing, generate reasonable test scenarios
  only based on the information provided.
- Cover both positive and negative scenarios when applicable.
- Include boundary and edge cases when applicable.
- Avoid duplicate test cases.
- Test steps must be clear and executable.
- Expected results must be specific and measurable.

OUTPUT RULES:

- Return ONLY valid JSON.
- Do not return Markdown.
- Do not include explanations.
- Do not include text before or after the JSON.

Use exactly this JSON structure:

{
  "story_id": "...",
  "test_cases": [
    {
      "test_case_id": "TC-001",
      "title": "...",
      "description": "...",
      "preconditions": [],
      "test_steps": [],
      "test_data": "...",
      "expected_result": "...",
      "priority": "High",
      "test_type": "Functional"
    }
  ]
}
"""

# Read user story
with open("stories/story.txt", "r") as f:
    story = f.read()

# Generate test cases
response = chat(
    model="llama3.2",
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
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
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(f"Test cases saved to {output_file}")
