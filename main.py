import sys
if('.' not in sys.path):
    sys.path.append('.')
import os
dllPath=os.environ.get('dllPath')
print(dllPath)
if(dllPath):
    print('adding',dllPath)
    os.add_dll_directory(dllPath)
from util import detach,is_port_in_use,messageBox
# os.add_dll_directory(r'C:\Users\lzy\Desktop\taskbar\python-3.12.7-embed-amd64\Lib\site-packages\pywin32_system32')

import conf
import sys



from http_server import startHttpServer
from ui import startView
from websocket_server import startWebSocket
from show_taskbar import tryStartKeyboardListener
from util import setEnv

# setEnv('taskbar_http_port',conf.get('httpPort'))

detach(startHttpServer)
detach(startWebSocket)
def env():
    import semi
    setEnv('taskbar_http_port',conf.get('httpPort'))
    while(is_port_in_use(conf.get('httpPort'))==False):
        import time
        time.sleep(0.1)
    semi.setOK(semi.FLAG_HTTP_START)
detach(env)
import semi
semi.waitForStart()
# detach(tryStartKeyboardListener)
startView()