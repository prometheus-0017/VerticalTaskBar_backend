conf=dict(pin=False,httpPort=15000,websocketPort=18765)
def get(key):
    return conf.get(key)