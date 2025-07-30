import asyncio
import websockets
import rpc_content
import json
import rpc_framework
websocketDict={}
async def echo(websocket, path):
    async for message in websocket:
        data=json.loads(message)
        if(data['app']=='setName'):
            name=data['data']['name']
            websocketDict[name]=websocket
            res=dict(
                status='success',
                data=res,
                id_for=data['id']
            )
            await websocket.send(json.dumps(res))
        if(data['app']=='remoteExec'):
            data=data['data']
            name=data['name']
            if(name in websocketDict):
                forward=dict(cmdName=data['cmdName'],argList=data['argList'])
                await websocketDict[name].send(json.dumps(forward))
                res=dict(
                    status='success',
                    data=res,
                    id_for=data['id']
                )
                await websocket.send(json.dumps(res))
            else:
                res=dict(
                    status='error',
                    data='no such user',
                    id_for=data['id']
                )
                await websocket.send(json.dumps(res))

        if(data['app']=='rpc'):
            try:
                res=rpc_framework._rpc(data['data'])
                res=dict(
                    status='success',
                    data=res,
                    id_for=data['id']
                )
                await websocket.send(json.dumps(res))
            except Exception as e:
                res=dict(
                    status='error',
                    data=str(e),
                    id_for=data['id']
                )
                await websocket.send(json.dumps(res))
        if(data['app']=='batchRpc'):
            res=rpc_framework._batchRpc(data['data'])
            await websocket.send(json.dumps(dict(
                status='success',
                data=res,
                id_for=data['id']
            )))
    for k in websocketDict:
        if(websocketDict[k]==websocket):
            del websocketDict[k]

from threading import Thread
thread=None

import conf
def startWebSocket():
    #创建当前线程async loop
    print('trying starting')
    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(echo, "0.0.0.0", conf.get('websocketPort'))
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
if(__name__=='__main__'):
    main()