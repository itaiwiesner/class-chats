from client import Client
from tkinter import *
from tkinter import messagebox


class LoginPage:
    def __init__(self, client: Client):
        self.client = client
        self.root = client.root
        self.frame = Frame(self.root)

        self.create_widgets() # Creating widgets
        self.place_widgets() # Placing widgets on the screen
        
        self.frame.pack()

    
    def create_widgets(self):
        self.login_label = Label(self.frame, text="Login", bg='#333333', fg="#FF3399", font=("Arial", 30))
        self.username_label = Label(self.frame, text="Username: ", bg='#333333', fg="#FFFFFF", font=("Arial", 16))
        self.username_entry = Entry(self.frame, font=("Arial", 16))
        self.password_entry = Entry(self.frame, show="*", font=("Arial", 16))
        self.password_label = Label(self.frame, text="Password: ", bg='#333333', fg="#FFFFFF", font=("Arial", 16))
        self.login_button = Button(self.frame, text="LOGIN", bg="#FF3399", fg="#FFFFFF", font=("Arial", 16), command=self.handle_login)
        self.go_back_button = Button(self.frame, text="GO BACK", bg="#FF3399", fg="#FFFFFF", font=("Arial", 16), command=self.handle_go_back)
        
    def place_widgets(self):
        self.login_label.grid(row=0, column=0, columnspan=2, sticky="news", pady=40)
        self.username_label.grid(row=1, column=0)
        self.username_entry.grid(row=1, column=1, pady=20)
        self.password_label.grid(row=2, column=0)
        self.password_entry.grid(row=2, column=1, pady=20)
        self.login_button.grid(row=3, column=0, columnspan=2, pady=30)
        self.go_back_button.grid(row=5, column=0, columnspan=2, pady=30)
        
    def clear_fields(self):
        self.username_entry.delete(0, END)
        self.password_entry.delete(0, END)

    def handle_go_back(self):
        self.client.display_frame(frame_name='HomePage', current_frame=self.frame)
    
    
    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # clear fields
        self.clear_fields()

        # check if fields are valid
        if username == '' or password == '':
          messagebox.showerror(title='Error', message="Empty fields aren't allowed")
        
        elif len(username) > 20 or len(password) > 20 or '#' in username:
            messagebox.showerror(title='Error', message="too long field! max length is 20")

        else:
            self.client.send('login', [username, password])
            cmd, description = self.client.recv()
            
            # if signing up is succefull, go to login page
            if cmd == 'success':
                self.client.display_frame(frame_name='MenuPage', current_frame=self.frame)

            else:
                messagebox.showerror(title='Error', message=description[0])