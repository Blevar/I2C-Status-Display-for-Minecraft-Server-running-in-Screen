from lib import ssh
import time

def check_if_server_online(server_name):
    print(f"Checking if server {server_name} is online...")
    out = ssh.sendline(f"screen -ls | grep {server_name}")
    return bool(out)

def check_if_screen_attached(server_name):
    print(f"Checking if screen {server_name} is attached...")
    out = ssh.sendline(f"screen -ls | grep {server_name}")
    print(f"Check result: {out}")
    if 'Detached' in out:
        return False
    elif 'Attached' in out:
        return True
    else:
        print(f"ERROR: Checking if screen is attached to {server_name} server failed.")
        return False

def establish_connection_with_screen(screen_server_name):
    print(f"Establishing connection with screen {screen_server_name}...")
    screen_status = check_if_server_online(screen_server_name)
    if screen_status:
        attached = check_if_screen_attached(screen_server_name)
        if attached:
            print("Detected screen attached to Minecraft server process.")
            print("Wiping dead sessions")
            ssh.sendline("screen -wipe")
            time.sleep(2)  # Wait to ensure the command completes
            ssh.reconnect_to_screen(screen_server_name) 
            print("Successfully reconnected to screen!")
        else:
            print("Detected screen detached from Minecraft server process.")
            print("Attaching.")
            ssh.connect_to_screen(screen_server_name)            
            print("Successfully attached to screen!")
        return True
    else:
        print(f"ERROR: Establishing connection to {screen_server_name} screen failed.")
        return False

def detach_from_screen(screen_server_name):
    print(f"Detaching from screen {screen_server_name}...")
    ssh.sendline(f"screen -d {screen_server_name}")
    print("Detached from screen.")

def reattach_to_screen(screen_server_name):
    print(f"Reattaching to screen {screen_server_name}...")
    ssh.sendline(f"screen -r {screen_server_name}")
    print("Reattached to screen.")