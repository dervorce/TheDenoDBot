import os
import ast
import sys

PROJECT_DIR = "."  # change if needed

# Known stdlib modules (Python 3.10+ gives us sys.stdlib_module_names)
stdlib = set(sys.stdlib_module_names)

found_modules = set()

for root, _, files in os.walk(PROJECT_DIR):
    for file in files:
        if file.endswith(".py"):
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read(), filename=file)
                except SyntaxError:
                    continue  # skip bad files

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            found_modules.add(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            found_modules.add(node.module.split(".")[0])

# Filter out stdlib + dunder stuff
packages = sorted(m for m in found_modules if m not in stdlib and not m.startswith("_"))

print("# Potential requirements.txt")
for pkg in packages:
    print(pkg)
