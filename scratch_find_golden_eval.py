import glob

for filename in glob.glob("*.py"):
    try:
        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if "golden_dataset_v8.json" in content:
                print(f"v8 in: {filename}")
            elif "golden_dataset_v7.json" in content:
                print(f"v7 in: {filename}")
    except Exception as e:
        pass
