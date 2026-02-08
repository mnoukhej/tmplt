import os
import subprocess
import re

README_FILE = "README.md"


# -----------------------------
# Get repository name from git
# -----------------------------
def get_repo_name():
    try:
        url = (
            subprocess.check_output(
                ["git", "config", "--get", "remote.origin.url"],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )

        if not url:
            return "project-name"

        return url.replace(".git", "").split("/")[-1]
    except Exception:
        return "project-name"


# -----------------------------------
# Convert repo name to readable title
# -----------------------------------
def format_project_name(repo_name: str) -> str:
    # camelCase → words
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", repo_name)

    # snake_case & kebab-case → words
    name = name.replace("_", " ").replace("-", " ")

    # Capitalize each word
    return " ".join(word.capitalize() for word in name.split())


# -----------------------------------
# Always update FIRST markdown title
# -----------------------------------
def update_title(content: str, project_name: str) -> str:
    lines = content.splitlines()
    for i, line in enumerate(lines):
        # Replace first H1 heading (any format)
        if line.lstrip().startswith("#"):
            lines[i] = f"# 📁 {project_name}"
            break
    return "\n".join(lines)


# -----------------------------------
# Update git clone and cd commands
# -----------------------------------
def update_commands(content: str, repo_name: str) -> str:
    # Update git clone command
    content = re.sub(
        r"git clone https://github.com/.+?/.+?\.git",
        f"git clone https://github.com/mnoukhej/{repo_name}.git",
        content,
    )

    # Update cd command (safe)
    content = re.sub(r"\bcd\s+\S+", f"cd {repo_name}", content)

    return content


# -----------------------------------
# Generate folder tree
# -----------------------------------
def generate_tree(path=".", prefix=""):
    tree = []
    ignore = {".git", ".venv", "__pycache__", "build", "dist", ".idea", ".vscode"}

    items = sorted(
        i for i in os.listdir(path) if not i.startswith(".") and i not in ignore
    )

    for index, name in enumerate(items):
        full_path = os.path.join(path, name)
        connector = "└── " if index == len(items) - 1 else "├── "
        tree.append(f"{prefix}{connector}{name}")

        if os.path.isdir(full_path):
            extension = "    " if index == len(items) - 1 else "│   "
            tree.extend(generate_tree(full_path, prefix + extension))

    return tree


# -----------------------------------
# Update TREE section in README
# -----------------------------------
def update_tree_section(content: str) -> str:
    tree = "\n".join(generate_tree())
    start = "<!-- TREE_START -->"
    end = "<!-- TREE_END -->"

    block = f"{start}\n```\n{tree}\n```\n{end}"

    if start in content and end in content:
        return content.split(start)[0] + block + content.split(end)[1]

    return content + "\n\n" + block


# -----------------------------------
# Main function
# -----------------------------------
def update_readme():
    repo_name = get_repo_name()
    project_name = format_project_name(repo_name)

    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    content = update_title(content, project_name)
    content = update_commands(content, repo_name)
    content = update_tree_section(content)

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print("README updated successfully")
    print("Repo Name   :", repo_name)
    print("Project Name:", project_name)


# -----------------------------------
if __name__ == "__main__":
    update_readme()
