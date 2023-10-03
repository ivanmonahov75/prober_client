import multiprocessing
import socket
import sys
import time
from multiprocessing import Process
import dearpygui.dearpygui as dpg
import pygame
import numpy as np

import callbacks

mots_state = True


def gui(queue_img, queue_stop, queue_en, queue_cont):
    def stop_proc():
        queue_stop.put('test')
        pygame.quit()
        sys.exit(0)

    dpg.create_context()

    with dpg.font_registry():
        # first argument ids the path to the .ttf or .otf file
        default_font = dpg.add_font("ProggyClean.ttf", 25)

    dpg.bind_font(default_font)
    width, heights, channels, data = dpg.load_image('img_def.jpg')
    with dpg.texture_registry():
        dpg.add_dynamic_texture(width, heights, data, tag='img')

    with dpg.window(tag='win_img', label='Video output', pos=(0, 0), width=1880, height=1440, no_resize=True):
        pass
        with dpg.drawlist(height=1440, width=1920):
            dpg.draw_image("img", (0, 0), (1860, 1395), uv_min=(0, 0), uv_max=(1, 1))  # (1860, 1395)

    with dpg.window(tag='controls', label='Controls', pos=(1880, 0), width=680, height=1440, no_resize=True):
        # menu (optional)
        with dpg.menu_bar():
            with dpg.menu(label="Config"):
                dpg.add_menu_item(label="Suspend")
                dpg.add_menu_item(label="Active")

                with dpg.menu(label="Docked"):
                    dpg.add_menu_item(label="Refuel")
                    dpg.add_menu_item(label="Charging")
                    dpg.add_menu_item(label="Pick-up")

            with dpg.menu(label="Speed"):
                dpg.add_menu_item(label="Slow")
                dpg.add_menu_item(label="Standard")
                dpg.add_menu_item(label="Full")
        # sliders for gyro and gamepad
        with dpg.group():
            dpg.add_slider_int(max_value=90, min_value=-90, label="Pitch", vertical=True, height=300, width=30,
                               pos=(325, 80), tag='pitch')
            dpg.add_slider_int(max_value=90, min_value=-90, label="Roll", pos=(120, 210), tag='roll')

            dpg.add_button(label="Reset gyro position", pos=(200, 400))

            dpg.add_slider_float(label='LY', width=30, height=220, pos=(170, 460), vertical=True, max_value=1,
                                 min_value=-1,
                                 tag='ly')
            dpg.add_slider_float(label='RY', width=30, height=220, pos=(480, 460), vertical=True, max_value=1,
                                 min_value=-1,
                                 tag='ry')
            dpg.add_slider_float(label='DV', width=30, height=100, pos=(245, 600), max_value=1, min_value=-1,
                                 vertical=True, tag='dv')
            dpg.add_slider_float(label='UV', width=30, height=100, pos=(405, 600), max_value=1, min_value=-1,
                                 vertical=True, tag='uv')
            dpg.add_slider_float(label='TV', width=30, height=150, pos=(325, 600), max_value=2, min_value=-2,
                                 vertical=True, tag='tv')

            dpg.add_slider_float(label='LX', width=250, height=30, pos=(60, 550), max_value=1, min_value=-1, tag='lx')
            dpg.add_slider_float(label='RX', width=250, height=30, pos=(370, 550), max_value=1, min_value=-1, tag='rx')

        # buttons and etc
        with dpg.group(pos=(25, 750)):  # info
            dpg.add_text(default_value="Connection disabled", tag='connection')
            dpg.add_text(default_value='Motors disabled', tag="mots_state")
            dpg.add_text(default_value='Current speed mode: Minimum', tag='speed_mode')
            dpg.add_text(default_value='Current light mode: Low', tag='light_mode')
            # IR_modes = {0: 'On', 1: 'Off'}
            dpg.add_text(default_value='IR light off', tag='ir')
            # motors_modes = {0: 'On', 1: 'Off'}
            # dpg.add_text(default_value=f'Battery status {84}%')
        with dpg.group(pos=(420, 750)):  # buttons
            dpg.add_button(label='Enable', callback=callbacks.change_connection)
            dpg.add_button(label="Turn off motors", tag='mots_on_off', callback=callbacks.mots_onoff)
            dpg.add_button(label="Change speed mode", callback=callbacks.change_speed)
            dpg.add_button(label="Change light mode", callback=callbacks.change_light)
            dpg.add_button(label="Turn IR on", callback=callbacks.ir_onoff)

    with dpg.window(tag='low_controls', label='Low controls', pos=(0, 1440), width=2560, height=160, no_resize=True):
        with dpg.group(horizontal=True):
            dpg.add_button(tag='but_exit', label='EXIT', callback=stop_proc)

    dpg.create_viewport(title='Custom Title', width=2560, height=1600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.toggle_viewport_fullscreen()
    temp_p = [0, 0]
    while dpg.is_dearpygui_running():
        # img = open('img.jpg', 'wb')
        # img.write(queue_img.get())
        # img.close()
        # width, heights, channels, data = dpg.load_image('img.jpg')
        # dpg.set_value("img", data)
        # temp = queue_cont.get()
        #
        # dpg.set_value('lx', temp[0])
        # dpg.set_value('ly', -temp[1])
        # dpg.set_value('dv', -temp[2])
        # dpg.set_value('rx', temp[3])
        # dpg.set_value('ry', -temp[4])
        # dpg.set_value('uv', temp[5])

        dpg.render_dearpygui_frame()
    dpg.start_dearpygui()
    dpg.destroy_context()


def com_server(queue_img, queue_stop, queue_en):  # pure low-level communication with server (on raspberry)
    if not queue_en.empty():
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 8080))
        while True:
            client_socket.send(b'image ')
            data = client_socket.recv(100000)
            queue_img.empty()
            queue_img.put(data)
            # img = open('img.jpg', 'wb')
            # img.write(data)
            # img.close()
    else:
        while True:
            time.sleep(1)

            if not queue_stop.empty():
                sys.exit(0)


def controller(queue_cont, queue_stop):
    pygame.init()
    joystick = pygame.joystick.Joystick(0)
    gamepad_but = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ], np.bool_)
    gamepad_ax = np.array([0, 0, 0, 0, 0, 0, ], np.float32)
    gamepad_ar = np.array([0.0], np.int8)

    while queue_stop.empty():
        pygame.event.get()
        # for i in range(11):
        #     if i < 8:
        #         gamepad_but[i] = joystick.get_button(i)
        #     elif i > 8:
        #         gamepad_but[i - 1] = joystick.get_button(i)
        for i in range(6):
            gamepad_ax[i] = joystick.get_axis(i)
        # gamepad_ar = joystick.get_hat(0)

        if not queue_cont.empty():
            test = queue_cont.get()
        # queue_cont.put(gamepad_but)
        queue_cont.put(gamepad_ax)
        # queue_cont.put(gamepad_ar)


if __name__ == '__main__':
    queue_img_ = multiprocessing.Queue()  # to send images
    queue_stop_ = multiprocessing.Queue()  # for stopping program correctly
    queue_cont_ = multiprocessing.Queue()  # to get gamepad data
    queue_en_ = multiprocessing.Queue()  # enables communication

    p_ser = Process(target=com_server, args=(queue_img_, queue_stop_, queue_en_))
    p_gui = Process(target=gui, args=(queue_img_, queue_stop_, queue_en_, queue_cont_))
    p_cont = Process(target=controller, args=(queue_cont_, queue_stop_))

    p_gui.start()
    # p_ser.start()
    p_cont.start()
