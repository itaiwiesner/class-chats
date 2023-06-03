from client import Client
from tkinter import *
from tkinter import messagebox
import re

class SignupPage:
      def __init__(self, client: Client):
            self.client = client
            self.root = client.root
            self.frame = Frame(self.root)
            
            self.create_widgets() # Creating widgets
            self.place_widgets() # Placing widgets on the screens
            
            self.frame.pack()
            
      def create_widgets(self):
            self.signup_label = Label(self.frame, text="Sign Up", bg='#333333', fg="#FF3399", font=("Arial", 30))
            self.username_label = Label(self.frame, text="Username: ", bg='#333333', fg="#FFFFFF", font=("Arial", 16))
            self.username_entry = Entry(self.frame, font=("Arial", 16))
            self.password_entry = Entry(self.frame, show="*", font=("Arial", 16))
            self.password_label = Label(self.frame, text="Password: ", bg='#333333', fg="#FFFFFF", font=("Arial", 16))
            self.confirm_password_entry = Entry(self.frame, show="*", font=("Arial", 16))
            self.confirm_password_label = Label(self.frame, text="Confim password: ", bg='#333333', fg="#FFFFFF", font=("Arial", 16))
            self.signup_button = Button(self.frame, text="Sign up", bg="#FF3399", fg="#FFFFFF", font=("Arial", 16), command=self.handle_signup_button)
            self.go_to_login_button = Button(self.frame, text="GO BACK", bg="#FF3399", fg="#FFFFFF", font=("Arial", 16), command=self.handle_go_back)
            
      def place_widgets(self):
            self.signup_label.grid(row=0, column=0, columnspan=2, sticky="news", pady=40)
            self.username_label.grid(row=1, column=0)
            self.username_entry.grid(row=1, column=1, pady=20)
            self.password_label.grid(row=2, column=0)
            self.password_entry.grid(row=2, column=1, pady=20)
            self.confirm_password_label.grid(row=3, column=0)
            self.confirm_password_entry.grid(row=3, column=1, pady=20)
            self.signup_button.grid(row=4, column=0, columnspan=2, pady=30)
            self.go_to_login_button.grid(row=6, column=0, columnspan=2, pady=30)

      def clear_fields(self):
            self.username_entry.delete(0, END)
            self.password_entry.delete(0, END)
            self.confirm_password_entry.delete(0, END)
      
      def contains_illeagal_chars(field):
            # check if field contains illeagal chars
            pattern = r'[^a-zA-Z0-9]'
            return not bool(re.search(pattern, field))
      
      def validate_fields(username, password, confirm_pswd):
            # returns true if fields are valid. generate propper message boxes if not
            if username == '' or password == '' or confirm_pswd == '':
                  messagebox.showerror(title='Error', message="Empty fields aren't allowed")
            
            # check if fields are too long
            elif len(username) > 20 or len(password) > 20:
                  messagebox.showerror(title='Error', message="fields are too long! max size is 20")

            elif (not SignupPage.contains_illeagal_chars(username)) or (not SignupPage.contains_illeagal_chars(password)):
                  messagebox.showerror(title='Error', message="fields must contain letters and digits only")

            elif username == 'You':
                  messagebox.showerror(title='Error', message="illeagl username")
                  
            # check if passwrord and confirm pssword match
            elif password != confirm_pswd:
                  messagebox.showerror(title='Error', message="Passwrord and confirm pssword don't match")

            else:
                  return True
            
            return False
      
      def handle_signup_button(self):
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()
            confirm_pswd  = self.confirm_password_entry.get().strip()
            
            self.clear_fields()
            
            if SignupPage.validate_fields(username, password, confirm_pswd):
                  self.client.send('signup', [username, password])
                  cmd, description = self.client.recv()
                  
                  # if signing up is succefull, go to login page
                  if cmd == 'success':
                        self.client.display_frame('HomePage', self.frame)

                  else:
                        messagebox.showerror(title='Error', message=description[0])
            
      
      def handle_go_back(self):
            # clear fields
            self.clear_fields()

            self.client.display_frame('HomePage', self.frame)
                   
