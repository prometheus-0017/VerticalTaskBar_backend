from flask import Flask,abort,send_file
import websocket_server
from window_proxy import iconManager
from pathlib import Path
from threading import Thread
from io import BytesIO

app=Flask(__name__)
# Path('icons').mkdir(exist_ok=True)

@app.route('/icons/<path:path>',methods=['GET'])
def send_assets(path):
    # 从iconManager的缓存中获取图片
    hwnd=int(path)
    img:bytes=iconManager.getIconByHWND(hwnd)
    if(img==None):
        abort(404)
    else:
        return send_file(BytesIO(img),'image/png')

        
@app.route('/')
def index():
    return send_file('dist/index.html')
@app.route('/<path:path>')
def static2(path):
    return send_file(f'dist/{path}')
# @app.route('/dist/<path:path>')
# def send_dist(path):
#     return send_file('dist/'+path)
import conf
def startHttpServer():
    app.run(host='0.0.0.0',port=conf.get('httpPort'),debug=False)

if __name__ == '__main__':
    startHttpServer()
