from pexpect import pxssh
import time
import pyautogui

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

def close_connection():
    global s
    if s:
        try:
            send_ctrl_a_ctrl_d()
            s.expect([pxssh.EOF, pxssh.TIMEOUT], timeout=1)
        except Exception as e:
            print(f"Error closing SSH connection: {e}")
        finally:
            s = None
        print("SSH connection closed.")

def sendline(command):
    global s
    try:
        s.sendline(command)
        s.prompt()
        return s.before.decode('UTF-8')
    except Exception as e:
        print(f"Error sending line: {e}")
        return ''

def sendline_to_screen(command, delay=1):
    global s
    try:
        s.sendline(command)
        time.sleep(delay)  # Wait for the command to complete
        return s.before.decode('UTF-8')
    except Exception as e:
        print(f"Error sending line to screen: {e}")
        return ''

def reconnect_to_screen(screen_name):
    global s
    try:
        s.sendline(f"screen -r -d {screen_name}")
        s.prompt()  # Ensure the command completes
    except Exception as e:
        print(f"Error reconnecting to screen: {e}")
        return ''

def connect_to_screen(screen_name):
    global s
    try:
        s.sendline(f"screen -r {screen_name}")
        s.prompt()  # Ensure the command completes
    except Exception as e:
        print(f"Error connecting to screen: {e}")
        return ''

def send_ctrl_a_ctrl_d():
    # Send Ctrl+A
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)  # Slight delay to ensure the action is registered
    # Send Ctrl+D
    pyautogui.hotkey('ctrl', 'd')
    time.sleep(0.5)  # Slight delay to ensure the action is registered