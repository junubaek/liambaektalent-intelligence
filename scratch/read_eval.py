import sys
# Try reading as utf-16le then printing as utf-8
try:
    with open('eval_lee_sang_heon.txt', 'rb') as f:
        content = f.read().decode('utf-16le')
    
    lines = content.split('\n')
    found_ga = False
    for line in lines:
        if 'General Affairs Manager' in line:
            found_ga = True
            print("--- Found GA section ---")
        if found_ga:
            print(line)
            if '------------------------------' in line:
                break
except Exception as e:
    print(f"Error: {e}")
