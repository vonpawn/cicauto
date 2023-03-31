import time
import pyautogui

from cicauto.controller import cicauto
from cicauto.strategy import MainWorkshopStrat, EventWorkshopStrat


def position_finder(rel=False, offset=None):
    print('Press Ctrl-C to quit.')

    offset_x, offset_y = 0, 0
    if rel:
        offset_x, offset_y = offset[0], offset[1]

    try:
        while True:
            x, y = pyautogui.position()
            x -= offset_x
            y -= offset_y

            position_str = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
            print(position_str)
    except KeyboardInterrupt:
        pass


def run_auto(state, strat):
    while state.is_running():
        try:
            strat.update()
        except Exception as e:
            state.stop()

            raise e


def main():
    pyautogui.FAILSAFE = False
    my_strat = MainWorkshopStrat(game=cicauto)
    run_auto(cicauto, my_strat)


def event():
    # pyautogui.PAUSE = 0.01
    # NOTE: Currently broken
    my_strat = EventWorkshopStrat(game=cicauto)
    run_auto(cicauto, my_strat)


def debugger():
    from cicauto.sdk.base import BaseContext
    offset = BaseContext.get_game_offset()
    position_finder(rel=True, offset=offset)


if __name__ == '__main__':
    main()
    # event()
    # debugger()
    # OCR Problem levels: 1, 11, 31, 51, 55, 57, 77, 91
