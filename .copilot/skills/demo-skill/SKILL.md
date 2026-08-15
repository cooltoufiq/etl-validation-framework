Name: Demo: Scaffold Minimal Project
Description: A minimal example skill that scaffolds a tiny Python project (README + tests).
WhenToUse: "When the user asks to scaffold a small demo Python project for testing or learning."
Inputs:
  - project_name: string
Outputs:
  - files_created: list
Examples:
  - "Scaffold demo project 'etl_demo'"

PromptTemplate: |
  Create a minimal Python project named {{project_name}} with a README and a tests directory. Include a short README and a simple test file that asserts True.

TemplateFiles:
  README.md: |
    # {{project_name}}

    This is a minimal demo project scaffolded by the demo skill.

    ## Quickstart
    1. python -m venv .venv
    2. .venv\\Scripts\\activate  # Windows
    3. pip install -r requirements.txt

  tests/test_basic.py: |
    def test_always_true():
        assert True

Notes: |
  - This SKILL.md is a simple example; real skills include richer metadata, validation rules, and multiple examples.
