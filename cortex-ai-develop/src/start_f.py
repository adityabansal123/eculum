import subprocess
import time
import psutil


def is_running(process):
	for pid in psutil.pids():
		p = psutil.Process(pid)
		if p.name() == process:
			return True
	return False

while True:
	try:
		if not is_running("firefly"):
			subprocess.Popen("source run.sh", shell=True, executable="/bin/bash")
		time.sleep(5)
	except Exception as e:
		print(e)
