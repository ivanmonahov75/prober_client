import datetime
import multiprocessing
import socket
import sys

import cv2
import time
from multiprocessing import Process
import numpy as np
import dearpygui.dearpygui as dpg


def gui(queue, proc):
    def stop_proc():
        proc.close()
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

    with dpg.window(tag='controls', label='Win2', pos=(1880, 0), width=680, height=1440, no_resize=True):
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

    with dpg.window(tag='low_controls', label='Win2', pos=(0, 1440), width=2560, height=160, no_resize=True):
        dpg.add_button(tag='but_spot', label='STOP', callback=stop_proc)

    dpg.create_viewport(title='Custom Title', width=2560, height=1600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.toggle_viewport_fullscreen()
    while dpg.is_dearpygui_running():
        img = open('img.jpg', 'wb')
        img.write(queue.get())
        img.close()
        width, heights, channels, data = dpg.load_image('img.jpg')
        dpg.set_value("img", data)
        dpg.render_dearpygui_frame()
    dpg.start_dearpygui()
    dpg.destroy_context()


def com_server(queue, com_enable):  # pure low-level communication with server (on raspberry)
    if com_enable:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 8080))
        while True:
            client_socket.send(b'image ')
            data = client_socket.recv(100000)
            queue.empty()
            queue.put(data)
            # img = open('img.jpg', 'wb')
            # img.write(data)
            # img.close()
    else:
        while True:
            time.sleep(1)


if __name__ == '__main__':
    queue_img = multiprocessing.Queue()
    p_ser = Process(target=com_server, args=(queue_img, True))
    p_gui = Process(target=gui, args=(queue_img, p_ser))
    p_gui.start()
    p_ser.start()
