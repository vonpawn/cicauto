import time
import pyautogui
# noinspection PyPackageRequirements
from pyscreeze import Box

import cicauto.graphics as graphics


class UnknownGameState(Exception):
    pass


class BaseContext:
    offset = None

    def __init__(self):
        pass

    @classmethod
    def apply_offset(cls, position):
        if cls.offset is None:
            cls.get_game_box()
        x, y = position[0] + cls.offset[0], position[1] + cls.offset[1]
        return x, y

    @classmethod
    def set_offset(cls, offset):
        x, y = offset
        offset = x, y
        cls.offset = offset

    @classmethod
    def get_game_box(cls):
        expected_title = 'Crafting Idle Clicker'
        found_windows = pyautogui.getWindowsWithTitle(expected_title)
        found_windows = list(filter(lambda win: win.title == expected_title, found_windows))

        if len(found_windows) != 1:
            raise IOError(f'Incorrect number of game windows found: {len(found_windows)}')

        game_window = found_windows[0]

        x, y, w, h = game_window.box
        x += 8  # Offset because pyautogui is still getting the x coord wrong
        cls.set_offset((x, y))

        return x, y, w, h

    @classmethod
    def get_game_offset(cls):
        # returns (x, y)
        # monitor 2+?
        x, y, w, h = cls.get_game_box()
        # pyautogui.moveTo(x, y)
        return x, y

    @classmethod
    def get_game_size(cls):
        # returns (width, height)
        _, _, w, h = cls.get_game_box()
        return w, h

    @classmethod
    def get_game_image(cls):
        x, y, width, height = cls.get_game_box()
        x += 2560  # TODO: Multimonitor hack
        return graphics.get_region_image(x, y, width, height)

    @classmethod
    def get_game_pixel(cls, position):
        game_img = cls.get_game_image()
        # clamp to bounds of game_img.size?
        return game_img.getpixel(position)

    def move_game(self):
        pass

    def close_game(self):
        pass

    @classmethod
    def sleep(cls, seconds):
        time.sleep(seconds)

    @classmethod
    def move_to(cls, position):
        x, y = position
        x, y = cls.apply_offset((x, y))
        pyautogui.moveTo(x, y)

    @classmethod
    def safe_click(cls, position, click_type='left'):
        # Clicks at (x, y) then returns the mouse pointer to the previous location on the screen

        # Convert from Box to Point
        if isinstance(position, Box):
            position = pyautogui.center(position)

        x, y = position
        previous = pyautogui.position()
        x, y = cls.apply_offset((x, y))

        if click_type == 'left':
            pyautogui.click(x, y)
        elif click_type == 'right':
            pyautogui.rightClick(x, y)
        else:
            raise ValueError(f'safe_click() expected either left or right click, received: {click_type}')

        pyautogui.moveTo(*previous)

    @classmethod
    def safe_drag(cls, position_start, position_end, drag_time=0.5, button='left'):
        previous = pyautogui.position()

        pyautogui.moveTo(cls.apply_offset(position_start))
        x, y = cls.apply_offset(position_end)
        pyautogui.dragTo(x, y, drag_time, button=button)

        pyautogui.moveTo(*previous)

    @classmethod
    def safe_keydown(cls, key: str):
        pyautogui.keyDown(key)

    @classmethod
    def safe_keyup(cls, key: str):
        pyautogui.keyUp(key)

    @classmethod
    def locate_image(cls, image_name, confidence=0.9):
        image_path = graphics.get_image_path(image_name)
        region_image = cls.get_game_image()

        result = pyautogui.locate(image_path, region_image, confidence=confidence)
        return result

    @classmethod
    def contains_image(cls, image_name, region_image=None, confidence=0.9):
        image_path = graphics.get_image_path(image_name)

        if region_image is None:
            region_image = cls.get_game_image()

        result = pyautogui.locate(image_path, region_image, confidence=confidence)
        return result is not None

    @classmethod
    def wait_until_visible(cls, image_name, interval=0.25, max_wait=10, confidence=0.9):
        image_path = graphics.get_image_path(image_name)

        start_time = time.time()
        elapsed = 0
        result = None

        while elapsed < max_wait:
            game_image = cls.get_game_image()
            result = pyautogui.locate(image_path, game_image, confidence=confidence)

            if result is not None:
                # print(f'image {image_name} is visible')
                break

            time.sleep(interval)
            current_time = time.time()
            elapsed = current_time - start_time

        if elapsed >= max_wait:
            return -1
            # raise IOError(f'image {image_name} not found in game')

        # At this point image has been found, clean up the numbers and apply offset before returning
        x, y, w, h = result
        x += w // 2
        y += h // 2

        return x, y  # center of located object
