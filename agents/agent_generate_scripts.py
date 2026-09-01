import os
import json
import asyncio
import re

from ollama import chat
from playwright.async_api import async_playwright

# =========================================================

# CONFIGURATION

# =========================================================

APP_URL = os.environ.get("APP_URL")

TC_DIRECTORY = "tcs"

OUTPUT_PAGE_DIRECTORY = "generated/pages"

OUTPUT_TEST_DIRECTORY = "generated/tests"

# =========================================================

# SYSTEM PROMPT

# =========================================================

SYSTEM_PROMPT = """
You are an AI Playwright Automation Agent.

Your responsibility is to convert generated test cases into
Playwright JavaScript automation scripts using the Page Object
Model (POM) design pattern.

You will receive:

1. A test case JSON object.
2. Actual DOM information collected using Playwright.
3. The application URL.

IMPORTANT RULES:

DOM AND LOCATOR RULES:

1. Use ONLY the provided DOM information to identify elements.
2. NEVER invent locators.
3. NEVER assume an element exists if it is not present in the DOM.
4. Select the most reliable Playwright locator.

LOCATOR PRIORITY:

1. getByTestId()
2. getByRole()
3. getByLabel()
4. getByPlaceholder()
5. CSS locator
6. XPath only as a last resort

PAGE OBJECT MODEL RULES:

1. All locators must be inside the Page Object.
2. Page actions must be methods inside the Page Object.
3. Do not place locators directly inside test files.
4. Tests must interact with the application through Page Object methods.
5. Use meaningful Page Object and method names.
6. Use async/await.

TEST DATA RULES:

1. DO NOT hardcode test data in generated test scripts.
2. The test data already exists inside the test case JSON file.
3. Generated tests must read the JSON file dynamically.
4. Find the required test case using test_case_id.
5. Use:

   testCase.test_data.email

   testCase.test_data.password

when those fields exist.

TEST GENERATION RULES:

1. Generate tests for ALL provided test cases.
2. Use the exact test_case_id.
3. Use the title as part of the Playwright test name.
4. Follow the provided test_steps.
5. Generate assertions based on expected_result.
6. Do not invent expected UI elements unless supported by DOM information.
7. If an assertion cannot be determined from the DOM information,
   use the most reliable observable behavior such as:

   * URL change
   * visible page heading
   * visible error element

OUTPUT RULES:

Return ONLY valid JSON.

Do not return markdown.

Do not return explanations.

Return exactly this structure:

{
"page_file_name": "LoginPage.js",
"page_object_code": "complete JavaScript code",

```
"test_file_name": "login.spec.js",
"test_code": "complete JavaScript code"
```

}

IMPORTANT:

The JavaScript code must be complete and executable.
Escape new lines correctly so that the response remains valid JSON.
"""

# =========================================================

# FIND TEST CASE FILE

# =========================================================

def get_test_case_file():

```
files = [

    file

    for file in os.listdir(TC_DIRECTORY)

    if file.endswith(".json")

]

if not files:

    raise Exception(
        "No JSON test case files found in tcs directory."
    )

# Use the first JSON file for now
return os.path.join(
    TC_DIRECTORY,
    files[0]
)
```

# =========================================================

# READ TEST CASE JSON

# =========================================================

def read_test_cases():

```
tc_file = get_test_case_file()

print(f"\nReading test cases: {tc_file}")

with open(
    tc_file,
    "r",
    encoding="utf-8"
) as file:

    test_case_data = json.load(file)

return test_case_data, tc_file
```

# =========================================================

# INSPECT APPLICATION

# =========================================================

async def inspect_application():

```
if not APP_URL:

    raise Exception(
        "APP_URL environment variable is not configured."
    )

print(f"\nOpening application: {APP_URL}")


async with async_playwright() as p:

    browser = await p.chromium.launch(
        headless=True
    )


    page = await browser.new_page()


    try:

        await page.goto(
            APP_URL,
            wait_until="networkidle",
            timeout=30000
        )

    except Exception:

        print(
            "Network idle timeout. Continuing with page inspection."
        )


    # -------------------------------------------------
    # COLLECT INTERACTIVE ELEMENTS
    # -------------------------------------------------

    elements = await page.locator(

        "input, button, select, textarea, a"

    ).evaluate_all(

        """
        elements => elements.map((element, index) => ({

            index: index,

            tag: element.tagName,

            id: element.id || null,

            name: element.name || null,

            type: element.type || null,

            text:
                element.innerText?.trim() || null,

            placeholder:
                element.placeholder || null,

            ariaLabel:
                element.getAttribute('aria-label'),

            role:
                element.getAttribute('role'),

            testId:
                element.getAttribute('data-testid'),

            className:
                element.className || null

        }))
        """

    )


    # -------------------------------------------------
    # CAPTURE PAGE INFORMATION
    # -------------------------------------------------

    page_title = await page.title()

    current_url = page.url


    await browser.close()


    return {

        "url": current_url,

        "title": page_title,

        "elements": elements

    }
```

# =========================================================

# ASK LLM TO GENERATE POM AND TESTS

# =========================================================

def generate_automation_code(

```
test_case_data,

dom_information,

tc_file
```

):

```
# Convert Windows paths to forward slashes
tc_file_path = tc_file.replace("\\", "/")


user_prompt = f"""
```

APPLICATION URL:

{APP_URL}

TEST CASE JSON FILE PATH:

{tc_file_path}

TEST CASE DATA:

{json.dumps(test_case_data, indent=2)}

ACTUAL APPLICATION DOM INFORMATION:

{json.dumps(dom_information, indent=2)}

TASK:

Generate:

1. A Page Object Model JavaScript file.
2. A Playwright JavaScript test specification file.

IMPORTANT IMPLEMENTATION REQUIREMENTS:

The generated test file must load the test case JSON file:

const testData = require('../../{tc_file_path}');

For every test case:

const testCase = testData.test_cases.find(
tc => tc.test_case_id === 'TC-001'
);

Do not hardcode email or password values.

Use:

testCase.test_data.email

testCase.test_data.password

Generate tests for ALL test cases where automation is possible.

For repeated actions such as:

"Click login button (5 times)"

generate a loop.

Example:

for (let i = 0; i < 5; i++) {{
await loginPage.login(
testCase.test_data.email,
testCase.test_data.password
);
}}

Use:

const {{ test, expect }} = require('@playwright/test');

The Page Object must be imported into the generated test.

Return ONLY the required JSON object.

"""

```
response = chat(

    model="llama3.2",

    messages=[

        {

            "role": "system",

            "content": SYSTEM_PROMPT

        },

        {

            "role": "user",

            "content": user_prompt

        }

    ]

)


return response["message"]["content"]
```

# =========================================================

# CLEAN LLM RESPONSE

# =========================================================

def clean_llm_response(response):

````
response = response.strip()


# Remove markdown code fences if LLM returns them
response = re.sub(

    r"^```json",

    "",

    response,

    flags=re.IGNORECASE

)


response = re.sub(

    r"^```",

    "",

    response

)


response = re.sub(

    r"```$",

    "",

    response

)


return response.strip()
````

# =========================================================

# SAVE GENERATED FILES

# =========================================================

def save_generated_files(result):

```
os.makedirs(
    OUTPUT_PAGE_DIRECTORY,
    exist_ok=True
)


os.makedirs(
    OUTPUT_TEST_DIRECTORY,
    exist_ok=True
)


# -----------------------------------------------------
# SAVE PAGE OBJECT
# -----------------------------------------------------

page_file_path = os.path.join(

    OUTPUT_PAGE_DIRECTORY,

    result["page_file_name"]

)


with open(

    page_file_path,

    "w",

    encoding="utf-8"

) as file:

    file.write(

        result["page_object_code"]

    )


# -----------------------------------------------------
# SAVE PLAYWRIGHT TEST
# -----------------------------------------------------

test_file_path = os.path.join(

    OUTPUT_TEST_DIRECTORY,

    result["test_file_name"]

)


with open(

    test_file_path,

    "w",

    encoding="utf-8"

) as file:

    file.write(

        result["test_code"]

    )


print("\nGenerated files:")

print(f"Page Object: {page_file_path}")

print(f"Test Script: {test_file_path}")
```

# =========================================================

# MAIN AUTOMATION AGENT

# =========================================================

async def run_agent():

```
print("\n======================================")

print("PLAYWRIGHT AUTOMATION AGENT STARTED")

print("======================================")


# -----------------------------------------------------
# STEP 1
# -----------------------------------------------------

print("\nSTEP 1: Reading Test Cases")


test_case_data, tc_file = read_test_cases()


story_id = test_case_data.get(

    "story_id",

    "UNKNOWN"

)


print(f"Story ID: {story_id}")


print(

    f"Number of test cases: "
    f"{len(test_case_data.get('test_cases', []))}"

)


# -----------------------------------------------------
# STEP 2
# -----------------------------------------------------

print("\nSTEP 2: Inspecting Application")


dom_information = await inspect_application()


print(

    f"Application URL: "
    f"{dom_information['url']}"

)


print(

    f"Interactive elements found: "
    f"{len(dom_information['elements'])}"

)


# -----------------------------------------------------
# STEP 3
# -----------------------------------------------------

print("\nSTEP 3: Asking LLM to Generate Automation")


llm_response = generate_automation_code(

    test_case_data,

    dom_information,

    tc_file

)


llm_response = clean_llm_response(

    llm_response

)


# -----------------------------------------------------
# STEP 4 - PARSE RESPONSE
# -----------------------------------------------------

print("\nSTEP 4: Validating LLM Response")


try:

    result = json.loads(

        llm_response

    )


except json.JSONDecodeError as error:


    print(

        "\nERROR: LLM did not return valid JSON."

    )


    print(

        f"\nJSON Error: {error}"

    )


    print(

        "\nLLM Response:\n"

    )


    print(

        llm_response

    )


    return


required_fields = [

    "page_file_name",

    "page_object_code",

    "test_file_name",

    "test_code"

]


for field in required_fields:


    if field not in result:

        raise Exception(

            f"LLM response is missing required field: {field}"

        )


# -----------------------------------------------------
# STEP 5
# -----------------------------------------------------

print("\nSTEP 5: Saving Generated Files")


save_generated_files(

    result

)


print("\n======================================")

print("AUTOMATION AGENT COMPLETED")

print("======================================")
```

# =========================================================

# START AGENT

# =========================================================

if **name** == "**main**":

```
asyncio.run(

    run_agent()

)
```
