import gpiod
import configparser
import lib.led as led
import lib.screen as screen
import lib.ssh as ssh
import lib.mc_server as mc_server
from RPLCD.i2c import CharLCD

#-----------------------------

online = None
number_of_slots = None
player_list = None

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



#-----------------------------

try:    
    if mc_server.is_online(server_ip):
        led.turn_on(server_status_led)
        online = mc_server.get_number_of_online(server_ip)
        number_of_slots= mc_server.number_of_slots(server_ip)
        
        print("Players online: " + str(online) + "/" + str(number_of_slots))
        lcd.clear()
        lcd.write_string('Online: ' + str(online) + "/" + str(number_of_slots) + "\n")

        try:
            if ssh.establish_connection_via_ssh(server_ip, ssh_login, ssh_password):
                if screen.establish_connection_with_screen(screen_server_name):
                    player_list = mc_server.get_player_list()

        except Exception as e:
            print(f"An error occurred: {e}")

        if online == 0:
            led.turn_off(server_populated_led)
        elif online > 0:
            led.turn_on(server_populated_led)

    else:
        led.turn_off(server_status_led)

except Exception as e:
    led.turn_off(server_status_led)
    print("Server offline")
    lcd.clear()
    lcd.write_string(screen_server_name + ' server offline')

#-----------------------------

#cleanup
led.turn_off(server_status_led)
led.turn_off(server_populated_led)
server_populated_led.release()
server_status_led.release()
lcd.clear()
lcd.backlight_enabled=False


print("\n------------EOP Summary------------")
print("online= " + str(online))
print("max_number_of_players= " + str(number_of_slots))
print("player_list= " + player_list)
