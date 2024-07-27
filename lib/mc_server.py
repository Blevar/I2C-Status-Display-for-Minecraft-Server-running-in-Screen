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
    out = ssh.sendline_to_screen("list", delay=1)
    return extract_players(out)

def is_online(server_ip):
    try:
        online = get_number_of_online(server_ip)
        if online >= 0:
            print("Server status: online")
            return True
    except Exception as e:
        print(f"Error checking server status: {e}")
    print("Server status: offline")
    return False

def extract_players(log_data):
    # Split the log data into individual lines
    lines = log_data.strip().split('\n')
    
    # Reverse the lines to start processing from the end
    lines.reverse()
    
    # Initialize variables
    unique_lines = set()
    players_online = []

    for line in lines:
        # Remove lines with identical dates
        date_part = line.split('] ')[0]
        if date_part in unique_lines:
            continue
        unique_lines.add(date_part)
        
        # Check if the line contains the 'list' command output
        if 'list' in line:
            break

        # Extract player names if within relevant block
        if 'INFO' not in line and 'online' not in line:
            player_names = line.split('] ')[-1]
            players_online.extend(player_names.split(', '))

    # Reverse back the player list to maintain the original order
    players_online.reverse()
    return players_online
