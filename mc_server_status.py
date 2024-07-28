import gpiod
import configparser
import lib.led as led
import lib.screen as screen
import lib.ssh as ssh
import lib.mc_server as mc_server
from RPLCD.i2c import CharLCD
import time
import lib.lcd as lcd_lib
import threading

# Global variables
online = None
player_list = []
lcd_update_interval = 3  # in seconds
server_info_update_interval = 60

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')

chip = gpiod.Chip('gpiochip4')

# LED Setup
server_populated_led_pin = int(config.get('LED_INFO', 'server_populated_led_pin'))
server_populated_led = chip.get_line(server_populated_led_pin)
server_populated_led.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

server_status_led_pin = int(config.get('LED_INFO', 'server_status_led_pin'))
server_status_led = chip.get_line(server_status_led_pin)
server_status_led.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

# SSH and Screen Setup
server_ip = config.get('SSH_SERVER_INFO', 'server_ip')
ssh_login = config.get('SSH_SERVER_INFO', 'ssh_login')
ssh_password = config.get('SSH_SERVER_INFO', 'ssh_password')
screen_server_name = config.get('SCREEN_SERVER_INFO', 'screen_server_name')

# LCD Setup
lcd_display_height = int(config.get('I2C_SCREEN_INFO', 'height'))
lcd_display_width = int(config.get('I2C_SCREEN_INFO', 'width'))
lcd_display_address = int(config.get('I2C_SCREEN_INFO', 'address'), 16)
lcd = CharLCD(i2c_expander='PCF8574', address=lcd_display_address, port=1, cols=lcd_display_width, rows=lcd_display_height, dotsize=8, backlight_enabled=True)

def initialize_lcd():
    lcd.clear()
    spaces= int((lcd_display_width - len(f'{screen_server_name}'))/2)
    lcd.write_string('      Starting\n\rserver monitor for:\n\r' + ' ' * spaces + screen_server_name)

def update_server_status():
    global online, player_list

    try:
        if mc_server.is_online(server_ip):             
            led.turn_on(server_status_led)
            online = mc_server.get_number_of_online(server_ip)
            new_player_list = mc_server.get_player_list()

            # Check if player list has changed
            if player_list != new_player_list:
                player_list = new_player_list

            led.turn_on(server_status_led)

            if online == 0:
                led.turn_off(server_populated_led)
            else:
                led.turn_on(server_populated_led)

        else:
            led.turn_off(server_status_led)

    except Exception as e:
        led.turn_off(server_status_led)
        print(f"Exception: {e}")

def refresh_lcd():
    global lcd, online, player_list
    lcd_lib.display_server_info(lcd, online, player_list)

def server_status_thread():
    try:
        if ssh.establish_connection_via_ssh(server_ip, ssh_login, ssh_password):
            screen.detach_from_screen(screen_server_name)
            time.sleep(2)  # Wait to ensure the command completes
            screen.reattach_to_screen(screen_server_name)
            #ssh.close_connection()
    except Exception as e:
        led.turn_off(server_status_led)
        print(f"Exception: {e}")    

    while True:
        update_server_status()
        time.sleep(server_info_update_interval)

def lcd_refresh_thread():
    global lcd, online

    while online is None:
        if online is not None and isinstance(online, int):
            lcd_lib.prepare_lcd(lcd)
            time.sleep(1)
            break      

    while True:
        if online != None:
            refresh_lcd()
            time.sleep(lcd_update_interval)

if __name__ == "__main__":
    initialize_lcd()

    status_thread = threading.Thread(target=server_status_thread)
    lcd_thread = threading.Thread(target=lcd_refresh_thread)

    status_thread.start()
    lcd_thread.start()

    status_thread.join()
    lcd_thread.join()
