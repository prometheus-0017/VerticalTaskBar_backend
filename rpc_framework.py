from flask import Flask, request, abort, jsonify
import json
import rpc_content

forceAscii = False

def _rpc(data):
    func=data['func']
    args=data['args']
    realFunc=getattr(rpc_content,func)
    sess=None
    try:
        res=realFunc(sess,*args)
        return json.dumps(res,ensure_ascii=forceAscii)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e
def _batchRpc(data):
    lst=data['funcArgList']
    # func=data['func']
    # args=data['args']
    # realFunc=getattr(nnode,func)
    resList=[]
    for func,args in lst:
        realFunc=getattr(rpc_content,func)
        try:
            res=realFunc(None,*args)
            resList.append(dict(code=200,data=res))
        except Exception as e:
            import traceback
            traceback.print_exc()
            resList.append(dict(code=600,message=str(e)))
    return json.dumps(resList,ensure_ascii=forceAscii)
