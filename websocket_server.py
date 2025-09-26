from xuri_rpc import  Message,MessageReceiverOptions,RunnableProxyManager,PlainProxyManager,setHostId,Client,ISender,asProxy,getMessageReceiver,MessageReceiver 

import asyncio
import websockets
import rpc_content
import json
import rpc_content

setHostId('taskbarBackend')
getMessageReceiver().setObject('rpc',rpc_content,True)

class Sender(ISender):
    def __init__(self,websocket):
        self.websocket=websocket
    async def send(self,message:Message):
        await self.websocket.send(json.dumps(message))

async def onMessageReceived(websocket, path):
    async for msg in websocket:
        message:Message=json.loads(msg)
        client=Client()
        client.setSender(Sender(websocket))
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