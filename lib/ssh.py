from pexpect import pxssh

s = None

def establish_connection_via_ssh(server_ip, ssh_login, ssh_password):
    global s    
    s = pxssh.pxssh()
    try:
        s.login(server_ip, ssh_login, ssh_password)
        print("SSH session login successful")
        return True
    except pxssh.ExceptionPxssh as e:
        print("SSH session failed on login.")
        print(str(e))
        return False

def sendline(string):
    global s
    try:
        s.sendline(string)
        s.prompt()
        return s.before.decode('UTF-8')
    except Exception as e:
        print(f"Error sending line: {e}")
        return ''
         
def sendline_to_screen(string):
    global s
    try:
        print("Sending line to screen: " + string)
        s.sendline(string)        
        print("Line setnt")
        return s.before.decode('UTF-8')
    except Exception as e:
        print(f"Error sending line: {e}")
        return '' 

def connect_to_screen(server_name):
    global s
    try:
        s.sendline("screen -r " + server_name)
    except Exception as e:
        print(f"Error sending line: {e}")
        return '' 
    
def reconnect_to_screen(server_name):
    global s
    try:
        s.sendline("screen -r -d " + server_name)
    except Exception as e:
        print(f"Error sending line: {e}")
        return '' 