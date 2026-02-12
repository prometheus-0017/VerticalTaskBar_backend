from xuri_rpc import  Message,MessageReceiverOptions,RunnableProxyManager,PlainProxyManager,setHostId,Client,ISender,asProxy,getMessageReceiver,MessageReceiver 

import asyncio
import websockets
import rpc_content
import json
import rpc_content

setHostId('taskbarBackend')
getMessageReceiver().setObject('rpc',rpc_content,True)

hostId2Websocket:dict[str,websockets.WebSocketServerProtocol]={}
hostId2Sender:dict[str,ISender]={}

class Sender(ISender):
    def __init__(self,remoteHostId,websocket):
        # self.websocket=websocket
        hostId2Websocket[remoteHostId]=websocket
        self.remoteHostId=remoteHostId

    async def send(self,message:Message):
        socket= hostId2Websocket.get(self.remoteHostId)
        if(socket==None):
            raise Exception('websocket is closed')
        await socket.send(json.dumps(message))
from typing import cast
#todo add xuri_rpc Request
from xuri_rpc import Request
async def onMessageReceived(websocket, path):
    sender=None
    async for msg in websocket:
        message:Message=json.loads(msg)
        client=Client()
        def isRequest(message:Message):
            return message.get('idFor')==None
        if(isRequest(message)):
            request=cast(Request,message)
            remoteHostId=request['meta'].get('hostId')
            sender=Sender(remoteHostId,websocket)
        else:
            if(sender==None):
                print("warnning: sender is None")
        if(sender==None):
            return
        
        client.setSender(sender)
        asyncio.ensure_future(getMessageReceiver().onReceiveMessage(message,client))
        # getMessageReceiver().onMessageReceived(message,Client(Sender(websocket)))

import conf
def startWebSocket():
    #创建当前线程async loop
    print('trying starting')
    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(onMessageReceived, "0.0.0.0", conf.get('websocketPort'))
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
if(__name__=='__main__'):
    startWebSocket()
    # main()