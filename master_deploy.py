from threading import Thread
import subprocess

t1 = Thread(target=subprocess.Popen, args=(["python", "app.py"],))
t2 = Thread(target=subprocess.Popen, args=(["python", "conversation.py"],))

t1.start()
t2.start()

t1.join()
t2.join()