import os
import signal
import subprocess

def kill_processes_by_name(name):
    try:
        output = subprocess.check_output(["pgrep", "-f", name])
        for pid in output.decode().split():
            os.kill(int(pid), signal.SIGTERM)
            print(f"Stopped process {name} with PID {pid}")
    except subprocess.CalledProcessError:
        print(f"No process found for {name}")

kill_processes_by_name("start_mcp_server.py")
kill_processes_by_name("run_task_manager.py")
kill_processes_by_name("adk web")
print("Environment stopped.") 