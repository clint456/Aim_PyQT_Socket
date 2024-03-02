
import subprocess

# 调用a.py
p1 = subprocess.Popen(['python', 'receive_data_py.py']) 
# 调用b.py
p2 = subprocess.Popen(['python', 'send_py.py'])
# 调用c.py
p3 = subprocess.Popen(['python', 'GUI/qt_server.py'])


p1.wait()
p2.wait()
p3.wait()




