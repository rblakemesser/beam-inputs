from __future__ import print_function

import time
from inputs import DeviceManager


class GamepadEvent(Exception):
    pass


def log(*args):
    print(*args)


def process_event(event):
    log(event.ev_type, event.code, event.state)


def process_events(events):
    for e in events:
        process_event(e)


def generate_events(dm):
    if not dm.gamepads:
        raise GamepadEvent('waiting for gamepad')

    for gp in dm.gamepads:
        try:
            yield gp.read()
        except IOError:
            raise GamepadEvent('gamepad disconnected')


def loop():
    dm = DeviceManager()

    while True:
        try:
            for events in generate_events(dm):
                process_events(events)

        except GamepadEvent as e:
            log(e.message)
            time.sleep(1)
            dm = DeviceManager()


def main():
    loop()


if __name__ == '__main__':
    main()

