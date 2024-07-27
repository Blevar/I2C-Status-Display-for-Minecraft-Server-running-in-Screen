from RPLCD.i2c import CharLCD
import lib.mc_server as mc_server
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
lcd_cols = int(config.get('I2C_SCREEN_INFO', 'width'))
lcd_rows = int(config.get('I2C_SCREEN_INFO', 'height'))
server_ip = config.get('SSH_SERVER_INFO', 'server_ip')
number_of_slots = mc_server.number_of_slots(server_ip)

def display_server_info(lcd, online):

    global lcd_cols
    global lcd_rows
    global number_of_slots
    global server_ip

    player_list = mc_server.get_player_list()
    print(f"Player list: {player_list}")

    lcd.clear()
    
    # First line with online players and latency
    latency = round(mc_server.get_latency(server_ip)) + 1
    print("Latency: " + str(latency) + "ms")
    first_line = f'Online: {online}/{number_of_slots}'
    
    # Calculate the number of spaces to add for right alignment of latency
    spaces = lcd_cols - len(first_line) - len(f'{latency}ms')
    if spaces < 0:
        spaces = 0  # Ensure spaces is not negative
    
    lcd.write_string(first_line + ' ' * spaces + f'{latency}ms')

    # Second to fourth lines with player names
    players = ' '.join(player_list)
    words = players.split()
    
    current_line = 1
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > lcd_cols:
            if current_line >= lcd_rows - 1:  # leave space for the last row
                break
            lcd.write_string('\n\r')
            current_line += 1
            current_length = 0
        
        if current_length > 0:
            lcd.write_string(' ')
            current_length += 1
        
        lcd.write_string(word)
        current_length += len(word)
