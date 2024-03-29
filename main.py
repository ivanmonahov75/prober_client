import multiprocessing as mp
import socket
import sys
import time
from multiprocessing import Process
import dearpygui.dearpygui as dpg
import pygame
import numpy as np
import callbacks
import struct

last_con = False


def gui(stop, queue_img, axis_lc, arrows_lc, buttons_lc, con_en, stmg, sen_scale):
    speed_modes = {'w': 0.15, 'm': 0.2, 'l': 0.3}
    def stop_proc():
        stop.value = 0
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

        # sliders for gyro and gamepad
        with dpg.group():
            dpg.add_slider_int(max_value=90, min_value=-90, label="Pitch", vertical=True, height=300, width=30,
                               pos=(325, 80), tag='pitch')
            dpg.add_slider_int(max_value=90, min_value=-90, label="Roll", pos=(120, 210), tag='roll')

            dpg.add_button(label="Reset gyro position", pos=(80, 400))
            dpg.add_button(label="Reset zero level", pos=(380, 400))

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
            dpg.add_text(default_value='Current speed mode: Low', tag='speed_mode')
            dpg.add_text(default_value='Current light mode: Low', tag='light_mode')
            dpg.add_text(default_value='IR light off', tag='ir')
            dpg.add_text(default_value='')
            dpg.add_text(default_value='Battery status:')
            dpg.add_text(default_value='Battery voltage:')
            dpg.add_text(default_value='Onboard temperature:')
            dpg.add_text(default_value='Water temperature:')
            dpg.add_text(default_value='Pressure (KPa):')
            dpg.add_text(default_value='Depth (meters):')
        with dpg.group(pos=(420, 750)):  # buttons
            dpg.add_button(label='Enable', callback=callbacks.change_connection, tag='con')
            dpg.add_button(label="Turn off motors", tag='mots_on_off', callback=callbacks.mots_onoff)
            dpg.add_button(label="Change speed mode", callback=callbacks.change_speed)
            dpg.add_button(label="Change light mode", callback=callbacks.change_light)
            dpg.add_button(label="Turn IR on", callback=callbacks.ir_onoff, tag='ir_but')
            dpg.add_text(default_value='')
            dpg.add_text(default_value='N/A', tag="pbat_val")
            dpg.add_text(default_value='N/A', tag='vbat_val')
            dpg.add_text(default_value='N/A °C', tag='itemp_val')
            dpg.add_text(default_value='N/A °C', tag='otemp_val')
            dpg.add_text(default_value='N/A KPa', tag='p_val')
            dpg.add_text(default_value='0 Meters', tag='d_val')

    with dpg.window(tag='low_controls', label='Low controls', pos=(0, 1440), width=2560, height=160, no_resize=True):
        with dpg.group(horizontal=True):
            dpg.add_button(tag='but_exit', label='EXIT', callback=stop_proc)

    dpg.create_viewport(title='Custom Title', width=2560, height=1600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    # dpg.toggle_viewport_fullscreen()
    old_arr = [0, 0]
    while dpg.is_dearpygui_running():
        # image processing
        if con_en.value and not queue_img.empty():
            img = open('img_new.jpg', 'wb')

            img.write(queue_img.get())
            img.close()

            try:
                width, heights, channels, data = dpg.load_image('img_new.jpg')
            except:
                width, heights, channels, data = dpg.load_image('img_def.jpg')
            dpg.set_value("img", data)


        # gamepad processing
        if old_arr[0] == 0 and arrows_lc[0] == 1:
            callbacks.change_light(None)
        if old_arr[0] == 0 and arrows_lc[0] == -1:
            callbacks.ir_onoff('ir_but')

        if old_arr[1] == 0 and arrows_lc[1] == 1:
            callbacks.upper_speed()
        if old_arr[1] == 0 and arrows_lc[1] == -1:
            callbacks.lower_speed()

        old_arr[0] = arrows_lc[0]
        old_arr[1] = arrows_lc[1]

        dpg.set_value('lx', axis_lc[0])
        dpg.set_value('ly', -axis_lc[1])
        dpg.set_value('dv', -axis_lc[2])
        dpg.set_value('rx', axis_lc[3])
        dpg.set_value('ry', -axis_lc[4])
        dpg.set_value('uv', axis_lc[5])
        dpg.set_value('tv', axis_lc[5] - axis_lc[2])

        # changing state processing
        global last_con
        if last_con != callbacks.connection_state:
            last_con = callbacks.connection_state
            if callbacks.connection_state:
                con_en.value = 1
            else:
                con_en.value = 0

        # if stmg[0] + stmg[1] != 0.0:
        dpg.set_value('p_val', f'{stmg[1]} KPa')
        dpg.set_value('itemp_val', f'{stmg[0]}°C')

        sen_scale.value = speed_modes[dpg.get_value('speed_mode')[-1]]

        dpg.render_dearpygui_frame()
    dpg.start_dearpygui()
    dpg.destroy_context()


def com_server(stop, queue_img, con_en_lc, from_stm, to_stm):  # pure low-level communication with server (on raspberry)

    while stop.value:
        if con_en_lc.value:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('192.168.1.146', 8080))

            client_socket.send(b'msg')
            data = client_socket.recv(3)
            size = int.from_bytes(data, 'big')
            data = b''
            while len(data) < size:
                data += client_socket.recv(1024)
            while not queue_img.empty():
                test = queue_img.get()
            queue_img.put(data)

            for i in to_stm:
                client_socket.send(int.to_bytes(i, 2, 'little'))
            data = client_socket.recv(4)
            from_stm[0] = round(struct.unpack('f', data)[0], 3)
            data = client_socket.recv(4)
            from_stm[1] = struct.unpack('i', data)[0]
            client_socket.close()

    print('com closed')


def controller(stop, axis_lc, arrows_lc, buttons_lc, to_stm, sen_scale):
    pygame.init()
    while pygame.joystick.get_count() == 0 and stop.value == 1:
        pass
    if stop.value:
        joystick = pygame.joystick.Joystick(0)
        gamepad_but = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ], np.bool_)
        gamepad_ax = np.array([0, 0, 0, 0, 0, 0, ], np.float32)
        gamepad_ar = np.array([0.0], np.int8)

    while stop.value:
        pygame.event.get()
        # for i in range(11):
        #     if i < 8:
        #         gamepad_but[i] = joystick.get_button(i)
        #     elif i > 8:
        #         gamepad_but[i - 1] = joystick.get_button(i)
        for i in range(6):
            axis_lc[i] = joystick.get_axis(i)
        # for horizontal motors
        mot_left = round((-axis_lc[1] + axis_lc[0]) * 500 * sen_scale.value + 1500)
        mot_right = round((-axis_lc[1] - axis_lc[0]) * 500 * sen_scale.value + 1500)
        to_stm[0:2] = mot_left, mot_right
        # for vertical motors
        mot_left_front = round((-axis_lc[4] - axis_lc[3] + (axis_lc[5] - axis_lc[2])) * 500 * 0.5*sen_scale.value + 1500)
        mot_right_front = round((-axis_lc[4] + axis_lc[3] + (axis_lc[5] - axis_lc[2])) * 500 * 0.5*sen_scale.value + 1500)
        to_stm[2:4] = mot_left_front, mot_right_front
        mot_left_back = round((axis_lc[4] - axis_lc[3] + (axis_lc[5] - axis_lc[2])) * 500 * 0.5*sen_scale.value + 1500)
        mot_right_back = round((axis_lc[4] + axis_lc[3] + (axis_lc[5] - axis_lc[2])) * 500 * 0.5*sen_scale.value + 1500)
        to_stm[4:6] = mot_left_back, mot_right_back

        spd = joystick.get_hat(0)
        if not spd[0] == 0:
            arrows_lc[0] = spd[0]
        else:
            arrows_lc[0] = 0

        if not spd[1] == 0:
            arrows_lc[1] = spd[1]
        else:
            arrows_lc[1] = 0


if __name__ == '__main__':
    queue_img_ = mp.Queue()  # to send images

    ax_gl = mp.Array('d', [0 for i in range(6)])
    arr_gl = mp.Array('i', [0 for i in range(2)])
    but_gl = mp.Array('i', [0 for i in range(10)])

    stm_gl = mp.Array('d', [0 for i in range(10)])
    to_stm_gl = mp.Array('i', [1500 for i in range(10)])

    sen_scale_gl = mp.Value('d', 0.15)
    con_en_ = mp.Value('i', 0)
    _stop = mp.Value('i', 1)

    p_serv = Process(target=com_server, args=(_stop, queue_img_, con_en_, stm_gl, to_stm_gl))
    p_gui = Process(target=gui, args=(_stop, queue_img_, ax_gl, arr_gl, but_gl, con_en_, stm_gl, sen_scale_gl))
    p_cont = Process(target=controller, args=(_stop, ax_gl, arr_gl, but_gl, to_stm_gl, sen_scale_gl))

    p_gui.start()
    p_serv.start()
    p_cont.start()

    # while _stop.value == 1:
    #     _stop.value = int(input())
    #     exit(0)
