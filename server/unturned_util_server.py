import socket
import time
from datetime import datetime
import threading

""" print() with proper log format """
def printf(message, prefix = '', suffix = '\n'):
    print(str(prefix) + str(datetime.now().strftime("%H:%M:%S")) + " [SERVER] :: " + str(message), end = suffix)

"""
class MainThread(threading.Thread):
    def __init__(self):
        super(ListeningThread, self).__init__()
        self.
        
        self._running = False

    def run(self):
        
            
    def say(self, msg):
        self.listening_thread.broadcast(msg)
"""

#listens for incoming connections
class ConnectionManager(threading.Thread):
    def __init__(self, ip, port):
        super(ConnectionManager, self).__init__()
        self.ip = ip
        self.port = port
        
        self.connections = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self._running = False
    
    def run(self):
        self._running = True
        
        self.sock.bind((self.ip, self.port))
        self.sock.listen(10)
        printf(f"Listening on {self.ip}:{self.port}")

        while self._running: #wait for incoming connections from clients
            try:
                client, address = self.sock.accept()
            except OSError as ex: #triggers when sock is closed
                break
            username = client.recv(64).decode('utf-8') #get username
                                                       #known potential bug - if server is shutdown while waiting for username, this thread will still exist and will wait for username before terminating. The thread created will also still exist and prevent the program from closing. I have ignored this because in practical scenarios this will never happen - usernames are recieved instantaneously.
            msg = f"Established with {address} \'{username}\'"
            printf(msg)

            new_connection_thread = ConnectionManager.ConnectionThread(client, address, username, self) #pass reference to self
            new_connection_thread.start()
            self.connections[username] = new_connection_thread #dict append username->thread
        
        self.sock.close() #not sure if needed

    def terminate(self): #completely terminates this thread along with all connection threads it manages
        self._running = False
        for t in self.connections.values():
            t.terminate(do_pop = False, do_broadcast = False)
        self.sock.close()
    
    def broadcast(self, msg):
        fmsg = f'[INFO] {msg}'
        printf(f'[BROADCAST] {fmsg}')
        for client_thread in self.connections.values():
            client_thread.get_client().send(fmsg.encode('utf-8'))
    
    def process_cmd(self, cmd, sender = ''): #sender represents name of user who initiated command, only relevant sometimes
        args = cmd.split(' ', 1)
        
        if args[0] == '[AutoTPA]':
            if len(args) < 2:
                fmsg = f'[ERROR] ([AutoTPA]): Missing arg'
                printf(fmsg)
                if sender in self.connections:
                    self.connections[sender].get_client().send(fmsg.encode('utf-8'))
            else:
                self.tpa(sender, args[1]) #from 'username', to 'cmd[1]'

        else:
            printf(f'[ERROR] Unknown command \'{args[0]}\' - How did this happen?!')
    
    def tpa(self, sender, recipient):
        if recipient in self.connections:
            fmsg = f'[AutoTPA] (from: {sender})'
            printf(fmsg + f' (to: {recipient})')
            self.connections[recipient].get_client().send(fmsg.encode('utf-8'))
        else:
            fmsg = f'[ERROR] AutoTPA failed: No connection with name \'{recipient}\''
            printf(fmsg)
            if sender in self.connections:
                self.connections[sender].get_client().send(fmsg.encode('utf-8'))

    def get_connections(self):
        return self.connections

    def remove_connection(self, username):
        if username in self.connections:
            self.connections.pop(username)

    class ConnectionThread(threading.Thread): #created individually for each incoming connection
        def __init__(self, client, address, username, connection_manager):
            super(ConnectionManager.ConnectionThread, self).__init__()
            self.client = client
            self.address = address
            self.username = username
            self.connection_manager = connection_manager
            
            self._running = False
        
        def run(self):
            self._running = True
        
            while self._running:
                try:    
                    cmd = self.client.recv(64).decode('utf-8')
                except ConnectionResetError as ex: #an exception will be made when client side closes unexpectedly (eg by closing the terminal/program without hitting /quit)
                                                   #this seems like a bad fix but it works
                    printf(f"Lost connection unexpectedly with {self.address} \'{self.username}\', closing connection")
                    self.terminate()
                    break
                except ConnectionAbortedError as cae: #this only occurs when the program is still stuck waiting for a msg (line 82) and
                    break                             #the socket it is using is closed (so when terminate() is called outside of /quit)
                
                self.connection_manager.process_cmd(cmd, self.username)
        
        def stop(self):
            self._running = False
        
        def terminate(self, do_pop = True, do_broadcast = True): #completely terminates this thread and the connection with it
            if do_pop:
                self.connection_manager.remove_connection(self.username)
            self.client.close()  #this causes the spam of 0-length string
            self.stop()
            if do_broadcast:
                self.connection_manager.broadcast(f'{self.username} disconnected.')
        
        """
        def remove_from_connections(self): #removes the connection from the shared 'connections' list.
                                        #does NOT sever an already existing socket connection.
                                        #that happens on the client side
                                        #this function is NOT NEEDED due to the rework I made no longer requiring a shared client connections list.
            for i in range(len(self.connections)):
                #self.connections[i] == self.client     <- seems to work as intended
                if self.connections[i] == self.client:
                    del self.connections[i]
                    break
    
            #self.client.send('EOT'.encode('utf-8'))
            self.broadcast(f'[SERVER] {self.address} disconnected.'.encode('utf-8'))
        """
        
        def get_client(self):
            return self.client

def main():
    main_thread = ConnectionManager('', 27015)
    main_thread.start()
    
    printf('Ready for commands... (\'help\' for info)')
    
    while True:
        cmd = input('').split(' ', 1)
        
        if cmd[0] == 'help':
            print('say [msg]\ntestcmd [command] [args...]\ndebug\nshow\nshutdown [timeout(optional)]')
        elif cmd[0] == 'say':
            msg = f'{cmd[1]}'
            main_thread.broadcast(msg)
    
        elif cmd[0] == 'testcmd': #use with caution!
            if len(cmd) < 2:
                printf(f'[ERROR] Must provide argument for \'testcmd\'!')
            else:
                main_thread.process_cmd(cmd[1])
        
        elif cmd[0] == 'debug':
            print(main_thread.get_connections())
    
        elif cmd[0] == 'show':
            connected = main_thread.get_connections().keys()
            if len(connected) == 0:
                print('No connected users!')
            else:
                print('Connected users:')
                for con in main_thread.get_connections().keys():
                    print(con)
    
        elif cmd[0] == 'shutdown':
            delay = 0
            if len(cmd) == 2:
                try:
                    delay = int(cmd[1])
                except ValueError as v:
                    printf(f'[ERROR] Invalid argument \'{cmd[1]}\': must be an integer!')
                    continue
    
            delay_msg = f'Server will be shutting down in {delay} seconds!'
            main_thread.broadcast(delay_msg)
            time.sleep(delay)
    
            #rcmd = '[RCMD] SERVER_SHUTDOWN' #remote command - server shutdown
            #rcmd method will work but this works more cleanly I think
    
            msg = 'Server shutting down! Goodbye!'
            main_thread.broadcast(msg)
            #main_thread.broadcast('\0'.encode('utf-8')) #send 0-length string to close user connection # <- doesn't work
            time.sleep(1)
            main_thread.terminate()
            break
    
        else:
            print(f'[ERROR] Unknown command \'{cmd[0]}\'')

if __name__ == "__main__":
    main()