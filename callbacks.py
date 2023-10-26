import dearpygui.dearpygui as dpg

mots_state = False
connection_state = False
ir_state = False

speed_modes = {0: 'Minimum', 1: 'Low', 2: 'Medium', 3: 'Full'}
speed_mode = 0

light_modes = {0: 'Low', 1: 'Medium', 2: 'High', 3: 'Emergency'}
light_mode = 0


def mots_onoff(sender):
    global mots_state
    if mots_state:
        dpg.set_item_label(sender, "Turn on motors")
        dpg.set_value('mots_state', 'Motors disabled')
    else:
        dpg.set_item_label(sender, "Turn off motors")
        dpg.set_value('mots_state', 'Motors enabled')

    mots_state = not mots_state


def change_connection(sender):
    global connection_state
    if connection_state:
        dpg.set_item_label(sender, 'Enable')
        dpg.set_value('connection', 'Connection disabled')
    else:
        dpg.set_item_label(sender, 'Disable')
        dpg.set_value('connection', 'Connection enabled')

    connection_state = not connection_state


def change_speed(sender):
    global speed_mode
    if speed_mode > 2:
        speed_mode = 0
    else:
        speed_mode += 1
    dpg.set_value('speed_mode', f'Current speed mode: {speed_modes[speed_mode]}')


def upper_speed(sender):
    global speed_mode
    if not speed_mode == 3:
        speed_mode += 1
    dpg.set_value('speed_mode', f'Current speed mode: {speed_modes[speed_mode]}')


def lower_speed(sender):
    global speed_mode
    if not speed_mode == 0:
        speed_mode -= 1
    dpg.set_value('speed_mode', f'Current speed mode: {speed_modes[speed_mode]}')


def change_light(sender):
    global light_mode
    if light_mode > 2:
        light_mode = 0
    else:
        light_mode += 1
    dpg.set_value('light_mode', f'Current light mode: {light_modes[light_mode]}')


def ir_onoff(sender):
    global ir_state
    if ir_state:
        dpg.set_item_label(sender, "Turn on IR")
        dpg.set_value('ir', 'IR light off')
    else:
        dpg.set_item_label(sender, "Turn off IR")
        dpg.set_value('ir', 'IR light on')

    ir_state = not ir_state
