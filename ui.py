import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QUrl
from PySide6.QtCore import QThread, Slot, Signal,QObject
from PySide6.QtGui import QCursor
from conf import conf
width=350
class CustomWebView(QWebEngineView):
    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)
    def dragEnterEvent(self, e):
        self.parent().dragEnterEvent(e)
        return super().dragEnterEvent(e)
window=None
def getWindow():
    global window
    return window
class CustomWindow(QWidget):
    exitSignal = Signal()
    expandSignal = Signal()
    collapseSignal = Signal()
    def exit(self):
        import sys
        sys.exit(0)
    def expand(self):
        self.setFixedWidth(width)  # 给一点边距
        self.setFixedHeight(self.fullHeight())
        # self.webview.setAcceptDrops(True)
        pass
    def collapse(self,force=True):
         # 真正检查鼠标是否离开了 widget 的矩形区域
        global_pos = QCursor.pos()
        widget_rect = self.mapToGlobal(self.rect().topLeft()), self.mapToGlobal(self.rect().bottomRight())
        top_left, bottom_right = widget_rect
        rect = self.rect()
        widget_global_rect = self.mapToGlobal(rect.topLeft()), self.mapToGlobal(rect.bottomRight())
        x1 = widget_global_rect[0].x()
        y1 = widget_global_rect[0].y()
        x2 = widget_global_rect[1].x()
        y2 = widget_global_rect[1].y()

        if not (x1 <= global_pos.x() <= x2 and y1 <= global_pos.y() <= y2):
            pass
        else:
            if(force):
                pass
            else:
                return
        # 鼠标离开时收缩
        # self.animation.setStartValue(200)
        # self.animation.setEndValue(0)
        # self.animation.start()
        #判断鼠标位置，如果还在展开的窗口范围内则返回
        # if self.geometry().contains(event.globalPos()): return
        self.setFixedWidth(2)
        self.setFixedHeight(50)
        # self.webview.setAcceptDrops(False)
        pass
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        self.exitSignal.connect(self.exit)
        self.expandSignal.connect(self.expand)
        self.collapseSignal.connect(self.collapse)



        self.width_states = [width, 50]
        self.current_width_index = 0

        # 设置窗口无边框和标题栏

        self.setWindowFlags(Qt.Tool |Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # 初始化UI
        self.init_ui()

        # 定位到屏幕右侧中间
        self.position_to_left()


    def enterEvent(self, event):
        # 鼠标进入时展开
        self.expand()
        super().enterEvent(event)
    @Slot()
    def onExitIntent(self):
        import sys
        sys.exit(0)
    def dragEnterEvent(self, event):
        print('asas')
        if event.mimeData().hasUrls():
            print('dddr')
            self.expand()
            # self.enterEvent(event)
    

    def leaveEvent(self, event):

        if(conf['pin']==True):
            return 

        self.collapse(False)

        super().leaveEvent(event)
       
    def fullHeight(self):
        screen = QApplication.primaryScreen().geometry()
        return screen.height()
    def init_ui(self):
        # 主布局 - 水平布局，按钮在左，webview 在右
        main_layout = QHBoxLayout()

        # 左侧按钮区域
        button_widget = QWidget()

        self.toggle_button = QPushButton("切换宽度")
        self.toggle_button.clicked.connect(self.toggle_width)

        close_button = QPushButton("×")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)


        # 右侧 Web 视图
        self.webview = CustomWebView()
        self.webview.load(QUrl("http://localhost:15000"))

        # 将按钮区和 webview 添加到主布局中
        # main_layout.addWidget(button_widget, stretch=0)
        main_layout.addWidget(self.webview, stretch=1)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 设置整体布局
        self.setLayout(main_layout)

        screen = QApplication.primaryScreen().geometry()

        # 初始宽度设置为第一个状态
        self.resize(self.width_states[self.current_width_index], screen.height())

    def toggle_width(self):
        self.current_width_index = (self.current_width_index + 1) % len(self.width_states)
        width = self.width_states[self.current_width_index]
        height = self.height()
        self.resize(width, height)

    def position_to_left(self):
        screen = QApplication.primaryScreen().geometry()
        window_width = self.width()
        window_height = self.height()
        x = 0
        # screen.width() - window_width
        y = (screen.height() - window_height) // 2
        self.move(x, y)
def startView():
    global window
    app = QApplication(sys.argv)
    window = CustomWindow()
    window.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    startView()