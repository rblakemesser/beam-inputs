from __future__ import print_function

import os
import time
from select import select

import evdev


button_map = {
    'ps3': {
        316: 'reset',
        307: 'n',
        306: 'e',
        305: 's',
        304: 'w',
        309: 'rb',
        311: 'rt',
        2: 'rjoy',
        5: 'rjoy',
        1: 'ljoy',
    },
    'xbox': {
        316: 'reset',
        308: 'n',
        305: 'e',
        304: 's',
        307: 'w',
        311: 'rb',
        5: 'rt',
        310: 'lb',
        2: 'lt',
        3: 'rjoy',
        4: 'rjoy',
        1: 'ljoy',
    }
}


def log(*args):
    print(*args)


class Reset(Exception):
    pass


def get_device_paths():
    paths = ['/dev/input/' + path for path in os.listdir('/dev/input/') if path.startswith('event')]
    return paths


def get_gamepads(paths):
    gamepads = {}
    devices = map(evdev.InputDevice, paths)
    devices = filter(lambda d: d.name.lower().startswith('xbox') or d.name.lower().startswith('ps3'), devices)
    devices = {dev.fd: dev for dev in devices}

    return devices


def process_button_event(padtype, iput):
    if iput == 'reset':
        raise Reset('reset initiated')

    log(padtype, iput)


def process_jstick_event(event):
    log(event)


def process_event(padtype, event):
    if not event.code:
        return

    relevant_events = button_map[padtype]
    iput = relevant_events.get(event.code)

    # button events
    btn_up = iput and event.type == 1 and not event.value
    if btn_up:
        process_button_event(padtype, iput)
    
    # joystick events
    if event.type == 3:
        process_jstick_event(event)


def process_events(gamepad):
    gp_name = 'ps3' if gamepad.name.lower().startswith('ps3') else 'xbox'
    try:
        events = gamepad.read()

        for event in events:

            process_event(gp_name, event)

    except IOError:
        raise Reset('device unplugged')


def loop(gamepads):
    if not gamepads:
        raise Reset('waiting for devices')

    r, w, x = select(gamepads, [], [])
    for fd in r:
        gp = gamepads[fd]
        process_events(gp)


def main():
    paths = get_device_paths()
    gamepads = get_gamepads(paths)
    for gp in gamepads.values():
        log(gp.capabilities(verbose=True))

    while True:
        try:
            loop(gamepads)
        except Reset as e:
            log(e.message)
            time.sleep(1)
            paths = get_device_paths()
            gamepads = get_gamepads(paths)


if __name__ == '__main__':

    main()

