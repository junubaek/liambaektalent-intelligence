import time
import psutil
import subprocess

def is_parser_running():
    for p in psutil.process_iter(['name', 'cmdline']):
        try:
            if p.info['name'] in ('python.exe', 'python') and p.info['cmdline']:
                if any('dynamic_parser_v2.py' in arg for arg in p.info['cmdline']):
                    return True
        except:
            pass
    return False

print("Waiting for dynamic_parser_v2.py to finish...")
while is_parser_running():
    time.sleep(60)

print("\nParser finished! Running final checks...")
subprocess.run(['python', 'run_final_checks.py'])
