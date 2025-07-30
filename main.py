import sys
if('.' not in sys.path):
    sys.path.append('.')
import os
from util import detach,is_port_in_use,messageBox
dllPath=os.environ.get('dllPath')
if(dllPath):
    os.add_dll_directory(dllPath)
# os.add_dll_directory(r'C:\Users\lzy\Desktop\taskbar\python-3.12.7-embed-amd64\Lib\site-packages\pywin32_system32')

import conf
import sys

if(is_port_in_use(conf.get('httpPort'))):
    messageBox(f'{conf.get('httpPort')}端口被占用')
    sys.exit(1)
    
if(is_port_in_use(conf.get('websocketPort'))):
    messageBox(f'{conf.get("websocketPort")}端口被占用')
    sys.exit(1)

from http_server import startHttpServer
from window import startView
from websocket_server import startWebSocket
detach(startHttpServer)
detach(startWebSocket)
startView()