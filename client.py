from protocol import *
from tkinter import *
from diffie_hellman import *
import socket
import sys


class Client:
    BUFFER_SIZE = 1024
    PORT = 9999
        
    def __init__(self, ip):
        self.connect_socket(ip)
        self.handle_key_exchange()

        
    def connect_socket(self, ip):
        """ establish conncection to the server """
        self.client_socket = socket.socket()
        self.client_socket.connect((ip, Client.PORT))
        
        
    def handle_key_exchange(self):
        """
        exchange keys using diffie hellman with the server
        using constant prime and generator to speed the procces
        """
        secret = gen_secret()
        public = get_public(secret)
        
        server_public = int(self.client_socket.recv(Client.BUFFER_SIZE).decode()) # recieve server public
        self.client_socket.send(str(public).encode()) # send public

            
        key = get_key(other_public=server_public, secret=secret)
        self.key= key
        print(key)
            
        
    def init_gui(self):
        """ creates the GUI window and displays the first page"""
        self.root = Tk()
        self.root.title("Class Chats")
        self.width = int(self.root.winfo_screenwidth() * 0.7)
        self.height = int(self.root.winfo_screenheight() * 0.70)
        self.root.geometry(f'{self.width}x{self.height}')
        self.root.configure(bg='#333333')
        self.display_frame('HomePage')
        self.root.mainloop()


    def display_frame(self, frame_name, current_frame='', room_name='', room_memebrs=[]):
        """ gets a name of a frame and displays the frame """
        frame = self.name_to_frame(frame_name, room_name, room_memebrs)
        if current_frame != '':
            current_frame.destroy()
            
        frame.tkraise()
        current_frame = frame
        
    def name_to_frame(self, frame_name, room_name, room_members):
        """ gets a name of a frame and returns the frame itself """
        # the import is done within the function to avoid circular imports
        
        if frame_name == 'LoginPage':
            from login_page import LoginPage
            
            login_page = LoginPage(self)
            return login_page.frame

        elif frame_name == 'SignupPage':
            from signup_page import SignupPage
            
            signup_page = SignupPage(self)
            return signup_page.frame
        
        elif frame_name == 'MenuPage':
            from menu_page import MenuPage
            
            menu_page = MenuPage(self)
            return menu_page.frame

        elif frame_name == 'ChatPage':
            from chat_page import ChatPage
            
            chat_page = ChatPage(self, room_name, room_members)
            return chat_page.frame

        elif frame_name == 'HomePage':
            from home_page import HomePage
            
            home_page = HomePage(self)
            return home_page.frame


    def send(self, cmd, data=[]):
        """ encrypts the data and sends it to the server """
        to_send = build_msg(cmd, data, self.key)
        print(to_send)
        self.client_socket.send(to_send)

    def recv(self):
        """ recv data from the server """
        data = self.client_socket.recv(Client.BUFFER_SIZE)  
        cmd, params = parse_data(data, self.key)
        return cmd, params


def main():
    try:
        ip = sys.argv[1]
        client = Client(ip)
        
    except IndexError:
        print(' Missing server ip address')
    
    except IOError:
        print(" Couldn't conncect to the server successfully. Make sure you enter the server ip and that the server is up and running")    
    
    else:
        client.init_gui()
    
if __name__ == '__main__':
    main()
    
