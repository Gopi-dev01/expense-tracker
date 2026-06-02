import os

templates_dir = "d:/Gopi_Clg/expense_tracker/templates"
for root, dirs, files in os.walk(templates_dir):
    for f in files:
        if f.endswith(".html"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                if "streak" in content.lower() or "gamification" in content.lower():
                    print(f"Found in {path}")
