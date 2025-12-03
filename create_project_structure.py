import os

# Recommended CIS_PM_Generator folder structure
structure = [
    "src",
    "src/utils",
    "templates",
    "assets",
    "assets/readme_images",
    "docs",
    "examples",
    "output",
]

# Files to optionally create (safe placeholders)
placeholders = {
    "src/__init__.py": "",
    "src/utils/__init__.py": "",
    "output/.gitignore": "*\n!.gitignore\n",
    "docs/README.md": "# Documentation\n",
}

def create_structure():
    root = os.getcwd()
    print(f"Creating project structure inside: {root}\n")

    # Create folders
    for folder in structure:
        path = os.path.join(root, folder)
        os.makedirs(path, exist_ok=True)
        print(f"Created directory: {path}")

    # Create placeholder files
    for filepath, content in placeholders.items():
        fullpath = os.path.join(root, filepath)
        with open(fullpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created file: {fullpath}")

    print("\n✔ Structure created successfully.")

if __name__ == "__main__":
    create_structure()
