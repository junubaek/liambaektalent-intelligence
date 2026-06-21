with open('cei_generator.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- get_combo_rarity ---")
for i in range(29, 58):
    print(f"{i+1}: {lines[i].rstrip()}")

print("\n--- get_tenure_signal ---")
for i in range(124, 159):
    print(f"{i+1}: {lines[i].rstrip()}")
