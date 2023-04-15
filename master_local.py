from threading import Thread
import subprocess

t1 = Thread(target=subprocess.Popen, args=(["./venv_acer/Scripts/python.exe", "app.py"],))
t2 = Thread(target=subprocess.Popen, args=(["./venv_acer/Scripts/python.exe", "conversation.py"],))

t1.start()
t2.start()

t1.join()
t2.join()