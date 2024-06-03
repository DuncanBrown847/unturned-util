import threading
import socket
import time
from pynput.keyboard import Controller as kController

class ClientSocket():
    class RecvThread(threading.Thread):
        def __init__(self, server, _connected):
            super(ClientSocket.RecvThread, self).__init__()
            self.server = server
            
            self._connected = _connected
        
        def process_cmd(self, cmd): #sender represents name of user who initiated command, only relevant sometimes
            args = cmd.split(' ', 1)
        
            if args[0] == '[AutoTPA]':
                print(f'Recieved {cmd}')
                time.sleep(0.1)
                #autoTPA
                controller = kController()  #this is pretty ghetto, prpbably better to somehow incorporate this class with handler to have fewer kcontrollers in mem
                controller.press(',')
                time.sleep(0.25)
                controller.release(',')

            elif args[0] == '[INFO]':
                print(cmd)

            else:
                print(f'[ERROR] Recieved unknown command \'{args[0]}\' - How did this happen?!')
        
        def run(self):
            while True:
                try:
                    msg = self.server.recv(64).decode('utf-8')
                    
                    if len(msg) == 0: #apparently, when sockets are closed serverside, they send a billion 0 length strings,,,,
                        print('Connection with server closed.')
                        break
                    
                    self.process_cmd(msg) #TODO: stuff

                except ConnectionAbortedError: #again, seems like a patchy fix, but it works
                    print('Connection to server aborted!')
                    break

                except ConnectionResetError:
                    print('Server closed unexpectedly!')
                    break

            self._connected = False

    def __init__(self):
        self.sock = socket.socket() #socket.AF_INET, socket.SOCK_STREAM
        
        self._connected = False
        self.recv_thread = ClientSocket.RecvThread(self.sock, self._connected) #init but do not start thread
        self.recv_thread.setDaemon(True)                                       #_connected pass by reference
    
    def attempt_connection(self, username, ip, port): #this is essentially the start() method, as a connection is required to operate
        if self._connected:
            return False
        
        try:
            self.sock.connect((ip, port))
        except ConnectionRefusedError:
            print('Connection to server refused!')
            return False
        except Exception as e:
            print(f'Connection failed: {e}')
            return False
        
        self._connected = True
        self.sock.send(username.encode('utf-8')) #server will accept username right after connection
        print('Connected to server!')
        self.recv_thread.start() #start recvthread once connected to recieve ;)
        return True
    
    def send(self, msg):
        if not self._connected:
            return False

        self.sock.send(msg.encode('utf-8'))
        #except OSError: 
        #       ^ use this for try/catch block (if ever needed)
        return True