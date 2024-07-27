from mcstatus import BedrockServer
from lib import ssh

def get_number_of_online(server_ip, timeout=30):
    server = BedrockServer.lookup(server_ip, timeout)
    status = server.status() 
    return status.players.online

def number_of_slots(server_ip, timeout=30):
    server = BedrockServer.lookup(server_ip, timeout)
    status = server.status()  
    return status.players.max

def get_latency(server_ip, timeout=30):
    server = BedrockServer.lookup(server_ip, timeout)
    status = server.status()  
    return status.latency

def get_player_list():
    # Mocked for testing. Return a list of player names.
    return 'Player1, Player2, Player3'

def is_online(server_ip):
    online = get_number_of_online(server_ip)
    if online >= 0:
        print("Server status: online")
        return True
    else:
        print("Server status: offline")
        return False

def get_player_list():
    out = ssh.sendline("list")
    print(out)
    return out