import gpiod
import configparser
import lib.led as led
import lib.screen as screen
import lib.ssh as ssh
import lib.mc_server as mc_server
from RPLCD.i2c import CharLCD
import time
import lib.lcd as lcd_lib

online = None
number_of_slots = None
player_list = ""

config = configparser.ConfigParser()
config.read('config.ini')

chip = gpiod.Chip('gpiochip4')

server_populated_led_pin = int(config.get('LED_INFO', 'server_populated_led_pin'))
server_populated_led = chip.get_line(server_populated_led_pin)
server_populated_led.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

server_status_led_pin = int(config.get('LED_INFO', 'server_status_led_pin'))
server_status_led = chip.get_line(server_status_led_pin)
server_status_led.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

server_ip = config.get('SSH_SERVER_INFO', 'server_ip')
ssh_login = config.get('SSH_SERVER_INFO', 'ssh_login')
ssh_password = config.get('SSH_SERVER_INFO', 'ssh_password')
screen_server_name = config.get('SCREEN_SERVER_INFO', 'screen_server_name')

lcd_display_height = int(config.get('I2C_SCREEN_INFO', 'height'))
lcd_display_width = int(config.get('I2C_SCREEN_INFO', 'width'))
lcd_display_address = int(config.get('I2C_SCREEN_INFO', 'address'), 16)
lcd = CharLCD(i2c_expander='PCF8574', address=lcd_display_address, port=1, cols=lcd_display_width, rows=lcd_display_height, dotsize=8, backlight_enabled=True)

print("Starting script...")
try:
    lcd.clear()
    lcd.write_string('Starting\n\rserver monitor for:\n\r' + screen_server_name)
    # Reset all screen connections at the beginning
    if ssh.establish_connection_via_ssh(server_ip, ssh_login, ssh_password):
        print("Established SSH connection.")
        screen.detach_from_screen(screen_server_name)
        time.sleep(2)  # Wait to ensure the command completes
        screen.reattach_to_screen(screen_server_name)
        print("Screen reconnected.")
        lcd.clear()
except Exception as e:
    led.turn_off(server_status_led)
    print(f"Exception: {e}")
    lcd.clear()
    lcd.write_string(screen_server_name + 'server script error')

try:    
    if mc_server.is_online(server_ip):
        print("Server is online.")
        if number_of_slots == None:
            number_of_slots= mc_server.number_of_slots(server_ip)
        
        led.turn_on(server_status_led)
        online = mc_server.get_number_of_online(server_ip)        
        
        print("Players online: " + str(online) + "/" + str(number_of_slots))

        lcd_lib.display_server_info(lcd, online)

        if online == 0:
            led.turn_off(server_populated_led)
        elif online > 0:
            led.turn_on(server_populated_led)

    else:
        led.turn_off(server_status_led)
        #lcd.clear()
        #lcd.write_string('Unexpected error')
        print("Unexpected error")

except Exception as e:
    led.turn_off(server_status_led)
    print(f"Exception: {e}")
    #lcd.clear()
    #lcd.write_string(screen_server_name + ' server offline')

if False:
    # Cleanup
    led.turn_off(server_status_led)
    led.turn_off(server_populated_led)
    server_populated_led.release()
    server_status_led.release()
    lcd.clear()
    lcd.backlight_enabled = False
    ssh.close_connection()  # Close SSH connection

    print("\n------------EOP Summary------------")
    print("online= " + str(online))
    print("max_number_of_players= " + str(number_of_slots))
    print("player_list= " + player_list)
