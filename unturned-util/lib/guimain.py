import combatlogger
import guiconfig
import config
import handler
import PySimpleGUI as sg

#serves as the main window that displays while the program is actually running.
#displays current bindings, allows for connection to server, and other post-config functions
class MainWindow():
    def __init__(self, handler):
        self.handler = handler
        mapping = handler.get_bind_mapping_list()
        
        binding_list_col1 = [[sg.Text("Keybind")], [sg.HorizontalSeparator()]]
        binding_list_col2 = [[sg.Text("Feature")], [sg.HorizontalSeparator()]]
        binding_list_col3 = [[sg.Text("Target")], [sg.HorizontalSeparator()]]
        
        for keybind in mapping:
            binding_list_col1.append([sg.Text(keybind[1])])
            binding_list_col2.append([sg.Text(keybind[0][5:])])
            binding_list_col3.append([sg.Text(keybind[2])])
        
        self.window = sg.Window('UnturnedUtil',
            [
                [sg.Column(binding_list_col1), sg.VerticalSeparator(), sg.Column(binding_list_col2), sg.VerticalSeparator(), sg.Column(binding_list_col3)],
                [sg.Frame('Connect to Server', layout = [[sg.Column([[sg.Text('IP Address')], [sg.Text('Username')]]), sg.Column([[sg.In(key = 'ip', size = 20)], [sg.In(key = 'username', size = 20)]])], [sg.Push(), sg.Button('Connect', key = 'connect')]])],
                [sg.Button('Close', key = 'close')]
            ]
        )
    
    def main(self):
        #"start" handler; means handler will start to listen to the keyboard
        self.handler.start()
        self.window.finalize()
        while True:
            event, values = self.window.read() 
            
            if event == 'connect':
                ip, port = values['ip'].split(':', 1) #TODO type checking
                self.handler.client_socket.attempt_connection(values['username'], ip, int(port))
            
            elif event == sg.WIN_CLOSED or event == 'close':
                self.window.close()
                break
        
        self.handler.stop()

if __name__ == '__main__':
    cfg = config.Config(filename = './bin/config.txt')
    cfg.load()
    gui = guiconfig.ConfigSetupWindow(cfg)
    gui.launch()
    hnd = handler.Handler(cfg)
    main = MainWindow(hnd)
    main.main()