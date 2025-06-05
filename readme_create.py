import os

IGNORE_DIRS = {'.venv'}


def generate_tree(path, prefix=""):
    tree_lines = []
    items = sorted(os.listdir(path))
    filtered_items = [item for item in items if item not in IGNORE_DIRS]
    for index, item in enumerate(filtered_items):
        item_path = os.path.join(path, item)
        connector = "├── " if index < len(filtered_items) - 1 else "└── "
        tree_lines.append(prefix + connector + item)
        if os.path.isdir(item_path):
            extension = "│   " if index < len(filtered_items) - 1 else "    "
            tree_lines.extend(generate_tree(item_path, prefix + extension))
    return tree_lines


def write_readme(project_path, output_file="README.md"):
    tree_lines = generate_tree(project_path)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 项目结构\n\n")
        f.write("```\n")
        f.write("\n".join(tree_lines))
        f.write("\n```\n")


if __name__ == "__main__":
    project_root = "."  # 当前目录
    write_readme(project_root)
