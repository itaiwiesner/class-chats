from client import Client
from tkinter import *
from tkinter import messagebox


class MenuPage:
    def __init__(self, client:  Client):
        self.client = client
        self.root = client.root
        self.frame = Frame(self.root)
        
        self.create_widgets() # Creating widgets
        self.place_widgets() # Placing widgets on the screen
        
        self.frame.pack()

    def create_widgets(self):
        self.secondary_label = Label(self.frame, text="Pick a room to join", bg='#333333', fg="#FF3399", font=("Arial", 30))
        self.cs_button = Button(self.frame, text="Computer Science", bg="#FF3399", fg="#FFFFFF", font=("Arial", 16), command=lambda: self.join_room('Computer Science'))
        self.math_button = Button(self.frame, text="Math", bg="#FF3399", fg="#FFFFFF", font=("Arial", 16), width=11, command=lambda: self.join_room('Math'))
        self.english_button = Button(self.frame, text="English", bg="#FF3399", fg="#FFFFFF", font=("Arial", 16), width=11, command=lambda: self.join_room('English'))
        self.logout_button = Button(self.frame, text="Log Out", bg="#FF3399", fg="#FFFFFF", font=("Arial", 16), command=self.handle_logout)

    def place_widgets(self):
        self.secondary_label.grid(row=0, column=1, columnspan=1, sticky="news")
        self.cs_button.grid(row=2, column=0)
        self.math_button.grid(row=2, column=1, pady=20)
        self.english_button.grid(row=2, column=2)
        self.logout_button.grid(row=4, column=1, pady=20)

    def handle_logout(self):
        self.client.send('logout')
        cmd, description = self.client.recv()
        
        if cmd == 'success':
            self.client.display_frame('HomePage', self.frame)

        else:
            messagebox.showerror(title='Error', message=description[0])
          

    def join_room(self, room_name):
        self.client.send('joinroom', [room_name])
        cmd, params = self.client.recv()
        
        if cmd == 'usersinroom':
            room_members = params[0].split(',')
            if room_members[0] == '':
                room_members = []
            
            self.client.display_frame('ChatPage', self.frame, room_name, room_members)
            
        else:
            messagebox.showerror(title='Error', message=params[0])
