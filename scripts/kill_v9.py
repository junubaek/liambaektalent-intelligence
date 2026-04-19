import wmi
c = wmi.WMI()
for process in c.Win32_Process(name="python.exe"):
    if process.CommandLine and "dynamic_parser_v9.py" in process.CommandLine:
        print(f"Killing PID: {process.ProcessId}")
        process.Terminate()
