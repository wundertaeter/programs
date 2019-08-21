import os
import subprocess
import signal
import requests
from time import sleep

home = os.path.expanduser("~")
class NGROK (object):
    def __init__(self, path_to_ngrok=home):
        self.path_to_ngrok = path_to_ngrok
        self.ngrok = None
        self.url = None

    def run(self):
        try:
            r = requests.get('http://127.0.0.1:4040/api/tunnels')
        except:
            if self.path_to_ngrok  == home:
                self.path_to_ngrok = self.path_to_ngrok  + '/ngrok'
            self.ngrok = subprocess.Popen([self.path_to_ngrok,'http','5000'],stdout = subprocess.PIPE)
            sleep(2)
            r = requests.get('http://127.0.0.1:4040/api/tunnels')
        
        
        for i in range(5):
            print('Try [{}]'.format(i))
            tunnels = r.json()['tunnels']
            if len(tunnels) > 1:
                url = tunnels[0]['public_url']
                if 'https' in url:
                    self.url = url
                else:
                    self.url = tunnels[1]['public_url']
                break
            else:
                sleep(5)
                r = requests.get('http://127.0.0.1:4040/api/tunnels')
        
        if self.url is None:
            print('Timeout')
        
        return self.url # your public url
                 

    def kill(self):
        if self.ngrok is None: # ngrok was allready running so no new process was started
            print('ngrok still running!') 
            exit()
        else:
            os.killpg(os.getpgid(self.ngrok.pid), signal.SIGTERM)
