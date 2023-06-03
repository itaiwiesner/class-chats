from encryption import encrypt, decrypt

# protocol struction:
# COMMAND|PARAM1#PARAM2#PARAM3....

# client commands:
# login|username#password
# signup|username#password
# sendmsg|room#msg_contnet
# joinroom|room
# leaveroom|room
# logout|

# server commands:
# recvmsg|sender#msg_content
# clientjoined|username
# clientleft|username
# error|description
# success|
# usersinroom|user1,user2,user3

SERVER_COMNANDS = 'error', 'success', 'recvmsg', 'clientjoined', 'clientleft', 'quit', 'usersinroom'
CLIENT_COMMANDS = 'login', 'signup', 'joinroom', 'sendmsg', 'leaveroom', 'logout'
COMMANDS = SERVER_COMNANDS + CLIENT_COMMANDS
CMD_PARAMS_AMOUNT = {'login':2, 'signup': 2, 'joinroom':1, 'sendmsg':2, 'leaveroom':1, 'logout':1, 'usersinroom': 1,
                     'error':1, 'recvmsg':2, 'success':1, 'clientjoined':1, 'clientleft':1}


class NotProtocolException(Exception):
    "raised when data recieved isn't according to the protocol"



def parse_data(encrypted_data, key):
    """ gets the data recieved and splits it to command and list of params. makes sure everything is according to the protocol """
    # decrypt data
    data = decrypt(encrypted_data, key)
        
    x = data.find('|')
    if x == -1:
        raise NotProtocolException
    

    cmd = data[:x]
    if cmd not in COMMANDS:
        raise NotProtocolException

    params = data[x+1:]
    params_amount = CMD_PARAMS_AMOUNT[cmd]
    params = params.split('#', maxsplit=params_amount+1)
    
    # check if there are enough params
    if len(params) != params_amount: 
        raise NotProtocolException
    
    return cmd, params


def build_msg(cmd, params, key):
    """ gets cmd and params """
    msg = f'{cmd}|'
    for p in params:
        msg += f'{p}#'

    if msg.endswith('#'):
        msg = msg[:-1]
    
    return encrypt(msg, key)

