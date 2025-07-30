import win32gui
import win32api
import win32con
import win32ui
from io import BytesIO
import win32process
from PIL import Image

def save_icon_to_bitmap(hIcon, filename="output.png"):
    # 创建一个设备描述表(Device Context)
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()

    # 获取图标信息
    icon_info = win32gui.GetIconInfo(hIcon)
    icon_size = icon_info[3]  # 假定宽高相等
    bitmap=win32gui.GetObject(icon_info[3])
    w=bitmap.bmWidth
    h=bitmap.bmHeight
    
    # 创建一个与图标大小相同的位图
    hbmp.CreateCompatibleBitmap(hdc, w,h)
    hdc = hdc.CreateCompatibleDC()
    hdc.SelectObject(hbmp)

    # 绘制图标
    hdc.DrawIcon((0, 0), hIcon)

    # 将位图转换为PIL图像并保存
    bmpstr = hbmp.GetBitmapBits(True)
    image = Image.frombuffer('RGB', ( w,h), bmpstr, 'raw', 'BGRX', 0, 1)
    image.save(filename, "PNG")

    # 清理
    try:
        win32gui.ReleaseDC(0, hdc.GetSafeHdc())
        win32gui.DestroyIcon(hIcon)
    except:
        import traceback
        traceback.print_exc()
from threading import Lock
foregroundLock = Lock()

def set_foreground_window(hwnd):
    # 获取当前线程ID
    current_thread_id = win32api.GetCurrentThreadId()
    # 获取目标窗口的线程ID和进程ID
    thread_id, _ = win32process.GetWindowThreadProcessId(hwnd)
    
    # 将当前线程与目标窗口线程关联
    win32process.AttachThreadInput(current_thread_id, thread_id, True)
    
    # 恢复窗口
    # win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    
    # 设置为前台窗口
    win32gui.SetForegroundWindow(hwnd)
    
    # 分离线程输入
    win32process.AttachThreadInput(current_thread_id, thread_id, False)
def setTop(hwnd):
    with foregroundLock:
        #对于最小化窗口需要特殊处理
        if(win32gui.IsIconic(hwnd)):
            win32gui.ShowWindow(hwnd,win32con.SW_RESTORE)
        try:
            succ=win32gui.SetForegroundWindow(hwnd)
            print('foreground success')
            return
        except:
            import traceback
            traceback.print_exc()
        try:
            set_foreground_window(hwnd)
            # win32gui.SetFocus(hwnd)
            # win32gui.SetForegroundWindow(hwnd)
            print('focus foreground success')
            return 
        except:
            import traceback
            traceback.print_exc()

        # try:
        #     resultWindow=win32gui.ShowWindow(hwnd,win32con.SW_SHOW)
        #     if(resultWindow==0):
        #         raise Exception('fail')
        #     print('showWindow success')
        #     return
        # except:
        #     import traceback
        #     traceback.print_exc()
        try:
            succ=win32gui.BringWindowToTop(hwnd)
            print('bringWindowToTop success')
        except:
            import traceback
            traceback.print_exc()


    


windowIds:set=set()
def refresh():
    newWindows=WindowProxy.getTopWindow().listChildren()
    newWindowsDict:dict={window.hwnd:window for window in newWindows}
    newIds:set=set(newWindowsDict.keys())
    new=newIds-windowIds
    deleted=windowIds-newIds
    for windowId in new:
        window:WindowProxy=newWindowsDict[windowId]
        window.saveIcon()
    for windowId in deleted:
        window:WindowProxy=newWindowsDict[windowId]
        # window.deleteIcon()
        
def isWindow(hwnd):
    if not win32gui.IsWindowVisible(hwnd):
        return False
    class_name = win32gui.GetClassName(hwnd)
    title = win32gui.GetWindowText(hwnd)

    if class_name in {"#32770", "tooltips_class32"}:
        return False
    
    # 确保是顶级窗口（非子窗口）
    root_hwnd = win32gui.GetAncestor(hwnd, win32con.GA_ROOT)
    if root_hwnd != hwnd:
        return False
    
    if not title:
        return False
    return True
class IconManager:
    def __init__(self):
        self.hicon2data={}
        self.hwnd2hicon={}
        self.hiconCount={}
    def saveIcon(self,window:'WindowProxy'):
        hwnd=window.hwnd
        if(hwnd in self.hwnd2hicon):
            return
        hIconHandle= win32gui.GetClassLong(window.hwnd,win32con.GCL_HICON)
        if(hIconHandle==0):
            path=window.getProcessPath()
            try:
                hIconHandle=win32gui.ExtractIcon(None,path,0)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(path)
        if(hIconHandle==0):
            return
        if(hIconHandle in self.hicon2data):
            print('hit!!!')
            self.hwnd2hicon[hwnd]=hIconHandle
            return
        hIcon=win32gui.GetIconInfo(hIconHandle)

        # 创建一个设备描述表(Device Context)
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()

        # 获取图标信息
        hIcon=hIconHandle
        icon_info = win32gui.GetIconInfo(hIcon)
        icon_size = icon_info[3]  # 假定宽高相等
        bitmap=win32gui.GetObject(icon_info[3])
        w=bitmap.bmWidth
        h=bitmap.bmHeight
        
        # 创建一个与图标大小相同的位图
        hbmp.CreateCompatibleBitmap(hdc, w,h)
        hdc = hdc.CreateCompatibleDC()
        hdc.SelectObject(hbmp)

        # 绘制图标
        hdc.DrawIcon((0, 0), hIcon)

        # 将位图转换为PIL图像并保存
        bmpstr = hbmp.GetBitmapBits(True)
        image = Image.frombuffer('RGB', ( w,h), bmpstr, 'raw', 'BGRX', 0, 1)
        memBuffer=BytesIO()
        image.save(memBuffer, "PNG")

        self.hicon2data[hIconHandle]=memBuffer.getvalue()
        self.hiconCount[hIconHandle]=0
        self.hwnd2hicon[hwnd]=hIconHandle

        # 清理
        try:
            win32gui.ReleaseDC(0, hdc.GetSafeHdc())
            win32gui.DestroyIcon(hIcon)
        except:
            import traceback
            traceback.print_exc()
    def getIconByHWND(self,hwnd):
        hIconHandle=self.hwnd2hicon.get(hwnd)
        if(hIconHandle==None):
            return None
        return self.getIconByHIcon(hIconHandle)
    def getIconByHIcon(self,hicon):
        if(hicon not in self.hicon2data):
            return None
        self.hiconCount[hicon]+=1
        return self.hicon2data.get(hicon)
iconManager=IconManager()

class WindowProxy:
    def getId(self):
        return self.hwnd
    def _iconPath(self):
        return f'icons/{self.hwnd}'
    def getIconPath(self):
        return self._iconPath()
    def __init__(self,previous:'WindowProxy',hwnd):
        self.hwnd = hwnd
        self.previous = previous
        pass
    def saveIcon(self)->int:
        iconManager.saveIcon(self)
        return
        hIconHandle= win32gui.GetClassLong(self.hwnd,win32con.GCL_HICON)
        if(hIconHandle==0):
            return None
        hIcon=win32gui.GetIconInfo(hIconHandle)
        bitmap=win32gui.GetObject(hIcon[3])
        save_icon_to_bitmap(hIconHandle,self._iconPath())
        return bitmap
        
        pass
    def deleteIcon(self):
        pass
    def getProcess(self):
        res= win32process.GetWindowThreadProcessId(self.hwnd)
        return res[1]
    def getTitle(self)->str:
        return win32gui.GetWindowText(self.hwnd)
        pass
    def toTop(self):
        setTop(self.hwnd)
    def getProcessFileName(self):
        res=self.getProcessPath();
        if(res==None):
            return ''
        idx=res.rfind("\\")
        if(idx!=-1):
            res=res[idx+1:]
        return res
        
    def getProcessPath(self):
        pid = self.getProcess()
        try:
            h_process = win32api.OpenProcess(
                win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                False,
                pid
            )
            if not h_process:
                raise Exception("无法打开进程，权限不足或进程已退出")
        
            res=win32process.GetModuleFileNameEx(h_process,None)
            
            return res
        except:
            import traceback
            print('fail:',pid)
            traceback.print_exc()
            return 'none'

    def listChildren(self)->list['WindowProxy']:
        #win32gui.GetWindow(self.hwnd,win32gui.GW_CHILD) 不建议

        def callback(hwnd,param):
            param.append(WindowProxy(self,hwnd))
            return True
        vl:list[WindowProxy]=[]
        win32gui.EnumChildWindows(self.hwnd,callback,vl)
        return [x for x in vl if isWindow(x.hwnd)]
    def getClass(self):
        return win32gui.GetClassName(self.hwnd)
    @classmethod
    def getTopWindow(cls)->'WindowProxy':
        return WindowProxy(None,win32gui.GetDesktopWindow())
        # return WindowProxy(None,win32gui.GetForegroundWindow())
# for p in WindowProxy.getTopWindow().listChildren():
#     txt=p.getTitle()
#     # icon=p.getIcon()
#     # if(icon==None):
#     #     continue
#     if(txt.strip()==''):
#         continue
#     if(p.getClass().lower()=='notepad'):
#         print(p.getClass())
#         p.toTop()


# p.saveIcon() 