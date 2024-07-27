from lib import ssh

def check_if_server_online(server_name):
    out = ssh.sendline("screen -ls | grep " + server_name)
    return bool(out)

def check_if_screen_attached(server_name):
    out = ssh.sendline("screen -ls | grep " + server_name)
    if 'Detached' in out:
        return False
    elif 'Attached' in out:
        return True
    else:
        print("ERROR: Checking if screen is attached to " + server_name + " server failed.")
        return False

def establish_connection_with_screen(screen_server_name):
    screen_status = check_if_server_online(screen_server_name)
    if screen_status:
        attached = check_if_screen_attached(screen_server_name)
        if attached:
            print("Detected screen attached to Minecraft server process.")
            print("Wipeing dead sessions")
            ssh.sendline("screen -wipe")
            ssh.reconnect_to_screen(screen_server_name) 
            print("Success!")
        else:
            print("Detected screen detached from Minecraft server process.")
            print("Attaching.")
            ssh.connect_to_screen(screen_server_name)            
            print("Success!")
        return True
    else:
        print("ERROR: Establishing connection to " + screen_server_name + " screen failed.")
        return False
