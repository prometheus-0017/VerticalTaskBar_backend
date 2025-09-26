import window_proxy
from window_proxy import WindowProxy
windowsBefore:dict[int,WindowProxy]={}
version=0
def queryHasUpdate(sess,remoteVersion):
    global version
    global windowsBefore
    
    # 如果请求是致远星发来的那就直接刷新
    if(version!=remoteVersion):
        return version

    windowList:list[WindowProxy]=WindowProxy.getTopWindow().listChildren()
    windowsNow={item.hwnd:item for item in windowList}

    #窗口不一样
    if(set(windowsBefore.keys())!=set(windowsNow.keys())):
        windowsBefore=windowsNow
        version+=1
        return version

    #窗口都一样那title是不是不一样
    allWindowsTitleEq=True
    for k,v in windowsBefore.items():
        if(v.getTitle()!=windowsNow[k].getTitle()):
            allWindowsTitleEq=False
            break

    if(allWindowsTitleEq==False):
        windowsBefore=windowsNow
        version+=1
        return version

    return False

def queryList(sess):
    lst:list[WindowProxy]=WindowProxy.getTopWindow().listChildren()
    newWindows={item.hwnd:item for item in lst}
    oldSet=set(windowsBefore.keys())
    newSet=set(newWindows.keys())
    deleted=oldSet-newSet
    for window in newWindows.values():
        window.saveIcon()
    added=newSet-oldSet
    for windowId in added:
        window=newWindows[windowId]
        windowsBefore[windowId]=newWindows[windowId]
    for windowId in deleted:
        window=windowsBefore[windowId]
        window.deleteIcon()
    lst.sort(key=lambda item:item.getProcessFileName())
    res= [dict(
        processId=item.getProcess(),
        id=item.getId(),
        originalName=item.getTitle(),
        modifiedName=None,
        processName=item.getProcessFileName(),
        originalIcon=item.getIconPath(),
        modifiedIcon=item.getIconPath()
    ) for item in lst]
    # res.sort(key=lambda item:item['processId'])
    return res
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