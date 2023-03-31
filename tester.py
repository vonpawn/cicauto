#! python3
import sys
import pyautogui

if __name__ == '__main__':
    print('Press Ctrl-C to quit.')

    try:
        while True:
            x, y = pyautogui.position()
            positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
            print(positionStr)
    except KeyboardInterrupt:
        print('\n')
