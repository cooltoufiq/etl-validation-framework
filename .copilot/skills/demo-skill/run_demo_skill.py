import os
import sys


def scaffold(project_name, out_root="."):
    base = os.path.join(out_root, project_name)
    os.makedirs(base, exist_ok=True)

    readme = f"""# {project_name}

This is a minimal demo project scaffolded by the demo skill.

## Quickstart
1. python -m venv .venv
2. .venv\\Scripts\\activate  # Windows
3. pip install -r requirements.txt
"""

    with open(os.path.join(base, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    tests_dir = os.path.join(base, "tests")
    os.makedirs(tests_dir, exist_ok=True)

    test_code = """def test_always_true():
    assert True
"""
    with open(os.path.join(tests_dir, "test_basic.py"), "w", encoding="utf-8") as f:
        f.write(test_code)

    with open(os.path.join(base, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write("pytest\n")

    files = [
        os.path.join(base, "README.md"),
        os.path.join(tests_dir, "test_basic.py"),
        os.path.join(base, "requirements.txt"),
    ]

    print("files_created:")
    for p in files:
        print(" -", p)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_demo_skill.py <project_name>")
        sys.exit(1)
    project = sys.argv[1]
    out_root = os.path.join(os.path.dirname(__file__), "demo_output")
    scaffold(project, out_root=out_root)
