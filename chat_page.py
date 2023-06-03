from client import Client
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext
from threading import *


class ChatPage:
    def __init__(self, client: Client, room_name, users_list):
        self.users_list = users_list
        self.room_name = room_name
        self.client = client
        self.root = self.client.root
        self.frame = Frame(self.root)
        
        self.create_widgets() # Creating widgets
        self.place_widgets() # Placing widgets on the screen
        
        self.init_users_listbox() # display users in room when joined
        
        # make the thread daemon so it ends whenever the main thread ends
        self.recv_thread = Thread(target=self.recieve_data, daemon=True)
        
        self.frame.pack()
        
        # start the thread
        self.recv_thread.start()
    
    
    def create_widgets(self):
        self.leave_room_button = Button(self.frame, text="Leave Room", bg="#FF3399", fg="#FFFFFF", font=("Arial", 16), command=self.handle_leave_room)
        self.room_name_label = Label(self.frame, text=self.room_name, bg='#333333', fg="#FF3399", font=("Arial", 20))
        self.users_in_room_label = Label(self.frame, text="Users in room:", bg='#333333', fg="#FF3399", font=("Arial", 30))

        self.msg_text = scrolledtext.ScrolledText(self.frame, width=50, height=30, wrap=WORD, state=DISABLED ,font=("Arial", 12), foreground="black")
        self.users_listbox = Listbox(self.frame, width=30, height=30)
        self.entry_text = scrolledtext.ScrolledText(self.frame, width=50, height=3, wrap=WORD, state=NORMAL ,font=("Arial", 12), foreground="black")
        self.send_button = Button(self.frame, text="Send", bg="#FF3399", fg="#FFFFFF", font=("Arial", 16), command=self.handle_send_msg)
        
    def place_widgets(self):
        self.leave_room_button.grid(row=0, column=0, sticky="news", pady=40, padx=10)
        self.room_name_label.grid(row=0, column=1, sticky="news", pady=40, padx=10)
        self.users_in_room_label.grid(row=0, column=2, sticky="news", pady=40, padx=10)

        self.msg_text.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        self.users_listbox.grid(row=1, column=2, padx=10, pady=5)
        
        self.entry_text.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        self.send_button.grid(row=2, column=2, padx=10, pady=5)    
    
    
    def init_users_listbox(self):
        """ initialize the users in room list box """
        self.users_listbox.insert(END, 'You')
        if self.users_list == []:
            return
        
        for user in self.users_list:
            self.users_listbox.insert(END, user)
    
    def handle_leave_room(self):
        result = messagebox.askyesno("Leave Room", "Are you sure you want to leave this room?")
        if result:
            self.client.send("leaveroom",[self.room_name])
        
    def handle_send_msg(self):
        msg = self.entry_text.get("1.0", END).strip()
        self.entry_text.delete("1.0", END)
        if len(msg) > 500:
            messagebox.showerror(title='Error', message="Message is too long. max characters amount is 500")
        else:
            self.client.send('sendmsg', [self.room_name, msg])
        
                  
    def recieve_data(self):
        while True:
            cmd, params = self.client.recv()
            if cmd == 'success':
                break
                
            elif cmd == 'clientjoined':
                username = params[0]
                self.handle_user_joined(username)

            
            elif cmd == 'clientleft':
                username = params[0]
                self.handle_user_left(username)

            
            elif cmd == 'recvmsg':
                sender, msg = params
                self.display_msg(msg, sender, )
            
            elif cmd == 'error':
                description = params[0]
                messagebox.showerror(title='Error', message=description)
                
        
        # redirect user to the menu page
        self.client.display_frame('MenuPage', self.frame)
    
    def handle_user_joined(self, username):
        self.users_list.append(username)
        self.users_listbox.insert(END, username)
        
    def handle_user_left(self, username):
        index = self.users_list.index(username)
        self.users_list.remove(username)
        self.users_listbox.delete(index+1)
    
    
    def display_msg(self, msg, sender):
        to_display = f'{sender}:\n{msg}\n\n'
        
        self.msg_text.configure(state=NORMAL)
        self.msg_text.insert(END, to_display)
        self.msg_text.configure(state=DISABLED)
                
