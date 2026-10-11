
import json
from pathlib import Path
from jsonschema import Draft202012Validator

# Locate the project folders
BASE_DIR = Path(__file__).resolve().parent
RESUME_DIR = BASE_DIR / "data" / "resumes"
SCHEMA_FILE = BASE_DIR / "data" / "schemas" / "resume_schema.json"

# Load the resume schema
with open(SCHEMA_FILE, "r", encoding="utf-8") as file:
    schema = json.load(file)

# Check the schema itself
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema)

passed = 0
failed = 0

# Validate all 10 resume files
for i in range(1, 11):
    resume_file = RESUME_DIR / f"resume{i}.json"

    try:
        with open(resume_file, "r", encoding="utf-8") as file:
            resume_data = json.load(file)

        errors = list(validator.iter_errors(resume_data))

        if errors:
            failed += 1
            print(f"FAIL: {resume_file.name}")
            for error in errors:
                print(f"  - {error.message}")
        else:
            passed += 1
            print(f"PASS: {resume_file.name}")

    except (OSError, json.JSONDecodeError) as error:
        failed += 1
        print(f"FAIL: {resume_file.name} - {error}")

print("\n----- VALIDATION SUMMARY -----")
print(f"Total resumes checked: {passed + failed}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
