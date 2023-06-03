from client import Client
from tkinter import *


class HomePage:
    def __init__(self, client:  Client):
        self.client = client
        self.root = client.root
        self.frame = Frame(self.root)
        
        self.create_widgets() # Creating widgets
        self.place_widgets() # Placing widgets on the screen
        
        self.frame.pack()

    def create_widgets(self):
        self.welcome_label = Label(self.frame, text="Welcome to Class Chats!", bg='#333333', fg="#FF3399", font=("Arial", 30))
        self.login_button = Button(self.frame, text="Log in", bg="#FF3399", fg="#FFFFFF", font=("Arial", 16), command=self.handle_go_to_login)
        self.signup_button = Button(self.frame, text="Create Account", bg="#FF3399", fg="#FFFFFF", font=("Arial", 16), command=self.handle_go_to_signup)

    def place_widgets(self):
        self.welcome_label.grid(row=0, column=0, sticky="news", pady=40)
        self.signup_button.grid(row=1, column=0, pady=20)
        self.login_button.grid(row=2, column=0, pady=20)
        
    def handle_go_to_login(self):
        self.client.display_frame('LoginPage', self.frame)
    
    def handle_go_to_signup(self):
        self.client.display_frame(frame_name='SignupPage', current_frame=self.frame)