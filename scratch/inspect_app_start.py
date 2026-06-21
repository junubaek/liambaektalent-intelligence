with open('frontend_v2/src/App.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'function App' in line or 'const App' in line or 'export default' in line:
        print(f"Line {idx+1}: {line.strip()}")
