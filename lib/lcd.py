from RPLCD.i2c import CharLCD
import lib.mc_server as mc_server
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
lcd_cols = int(config.get('I2C_SCREEN_INFO', 'width'))
lcd_rows = int(config.get('I2C_SCREEN_INFO', 'height'))
server_ip = config.get('SSH_SERVER_INFO', 'server_ip')
number_of_slots = mc_server.number_of_slots(server_ip)
current_index = 0  # Global variable to keep track of the current player index for scrolling

def display_server_info(lcd, online, player_list):
    global lcd_cols
    global lcd_rows    
    global server_ip
    global current_index  # Use the global variable to keep track of the current index

    write_online(lcd, online)
    write_latency(lcd)

    lcd.cursor_pos = (1, 0)

    # Prepare the player list for scrolling
    players = ' '.join(player_list)
    words = players.split()
    num_lines = lcd_rows - 1  # Number of lines available for player names

    lines = [''] * num_lines
    current_line = 0

    for i in range(len(words)):
        index = (current_index + i) % len(words)
        word = words[index]
        if len(lines[current_line]) + len(word) + 1 > lcd_cols:
            current_line += 1
            if current_line >= num_lines:
                break
        if lines[current_line]:
            lines[current_line] += ' '
        lines[current_line] += word

    # Pad lines with spaces to ensure they overwrite previous content
    for i in range(num_lines):
        lines[i] = lines[i].ljust(lcd_cols)
    
    # Write lines to the LCD
    lcd.cursor_pos = (1, 0)
    for line in lines:
        lcd.write_string(line)
        lcd.write_string('\n\r')

    # Update the current index for the next refresh
    current_index = (current_index + 1) % len(words)

def prepare_lcd(lcd):
    lcd.clear()
    spaces = lcd_cols - 9
    lcd.write_string("Online:" + ' ' * spaces + "ms")

def write_online(lcd, online):
    if online is not None:
        global number_of_slots
        lcd.cursor_pos = (0, 8)
        lcd.write_string(str(online) + "/" + str(number_of_slots).ljust(3))

def write_latency(lcd):
    latency = str(round(mc_server.get_latency(server_ip)) + 1)
    cursor_pos = lcd_cols - 2 - len(f'{latency}')
    lcd.cursor_pos = (0, cursor_pos)
    lcd.write_string(latency)
