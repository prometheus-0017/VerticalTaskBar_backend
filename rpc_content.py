import window_proxy
from typing import TypedDict,Union,Literal
from window_proxy import WindowProxy
windowsBefore:dict[int,WindowProxy]={}
version=0

class WindowProxyDTO(TypedDict):
    processId:int
    id:int
    originalName:str
    modifiedName:str
    processName:str
    originalIcon:str
    modifiedIcon:str
class WindowChangeInfo(TypedDict):
    type:Literal['add','change','delete']
    data:WindowProxyDTO

from typing import Callable,Awaitable
callbacklist:list[Callable[[list[WindowChangeInfo]],Awaitable[None]]]=[]

loopStart=False
import asyncio
from logging import getLogger
logger=getLogger(__name__)
import logging
logging.basicConfig(level=logging.INFO,filemode='log.txt')
async def setCallback(context,callback):
    callbacklist.append(callback)
    # await detectChange()
    global loopStart
    if(not loopStart):
        async def loop():
            global loopStart
            loopStart=True
            while True:
                await asyncio.sleep(1);
                await detectChange()
        asyncio.ensure_future(loop())
from websockets.exceptions import ConnectionClosedError
async def notify(infos:list[WindowChangeInfo]):
    for callback in callbacklist:
        try:
            await callback(infos)
        except ConnectionClosedError:
            callbacklist.remove(callback)
        except Exception as e:
            import traceback
            traceback.print_exc()
            callbacklist.remove(callback)
async def sync(context):
    return [WindowProxyDTO(
        processId=v.getProcess(),
        id=v.getId(),
        originalName=v.getTitle(),
        modifiedName=v.getTitle(),
        processName=v.getProcessFileName(),
        originalIcon=v.getIconPath(),
        modifiedIcon=v.getIconPath()
    ) for v in windowsBefore.values()]
async def detectChange():
    global windowsBefore

    windowList:list[WindowProxy]=WindowProxy.getTopWindow().listChildren()
    windowsNow={item.hwnd:item for item in windowList}
    infoUpdates:list[WindowChangeInfo]=[]
    old=[windowsBefore[k] for k in windowsBefore.keys()-windowsNow.keys()]
    new=[windowsNow[k] for k in windowsNow.keys()-windowsBefore.keys()]
    common=[windowsNow[k] for k in windowsNow.keys()&windowsBefore.keys() if(windowsBefore[k].getTitle()!=windowsNow[k].getTitle())]
    for v in old:
        logger.info(f'delete {v.getId()} {v.getTitle()}')
    for v in new:
        logger.info(f'add {v.getId()} {v.getTitle()}')
        v.saveIcon()
    for v in new:
        v.saveIcon()
    infoUpdates.extend([WindowChangeInfo(
        type='delete',
        data=WindowProxyDTO(
            processId=v.getProcess(),
            id=v.getId(),
            originalName=v.getTitle(),
            modifiedName=v.getTitle(),
            processName=v.getProcessFileName(),
            originalIcon=v.getIconPath(),
            modifiedIcon=v.getIconPath()
        ) )for v in old])
    infoUpdates.extend([WindowChangeInfo(
        type='add',
        data=WindowProxyDTO(
            processId=v.getProcess(),
            id=v.getId(),
            originalName=v.getTitle(),
            modifiedName=v.getTitle(),
            processName=v.getProcessFileName(),
            originalIcon=v.getIconPath(),
            modifiedIcon=v.getIconPath()
        ) )for v in new])
    infoUpdates.extend([WindowChangeInfo(
        type='change',
        data=WindowProxyDTO(
            processId=v.getProcess(),
            id=v.getId(),
            originalName=v.getTitle(),#with lock when sync
            modifiedName=v.getTitle(),
            processName=v.getProcessFileName(),
            originalIcon=v.getIconPath(),
            modifiedIcon=v.getIconPath()
        )
    ) for v in common])

    windowsBefore=windowsNow
    # await notify(infoUpdates)
    if(infoUpdates.__len__()!=0):
        asyncio.ensure_future(notify(infoUpdates))

import json
def saveStatus(sess,status):
    with open('status.json','w',encoding='utf-8') as f:
        f.write(json.dumps(status,ensure_ascii=False))
    return True
def loadStatus(sess):
    try:
        with open('status.json','r',encoding='utf-8') as f:
            return json.loads(f.read())
    except :
        return None

def toTop(sess,windowId):
    window_proxy.setTop(windowId)
    pass
# from PyQt5.QtCore import QMetaObject,Qt
from PySide6.QtCore import QMetaObject,Qt


from ui import getWindow
def exit(sess):
    getWindow().exitSignal.emit()
def expand(sess):
    getWindow().expandSignal.emit()
def collapse(sess):
    getWindow().collapseSignal.emit()

def pin(sess,boolValue):
    from conf import conf
    conf['pin']=boolValue
    return  boolValue