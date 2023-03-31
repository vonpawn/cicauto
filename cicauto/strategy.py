import time
import keyboard
from enum import Enum

from cicauto import audio


class Priority(Enum):
    LORE, DOUBLE_LORE, GEM, PACK, BP = range(5)


class MainWorkshopStrat:
    def __init__(self, game):
        self.game = game
        self.previous_level = 0
        self.game.start()
        self.active_build = 0  # build is unset on program start
        self.levels = []

    def update(self):
        self.game.workshop.wait_until_visible('settings_gear.png')

        # ensure paywall model is removed (only pops up if double speed 15min or less)
        if self.game.workshop.is_paywall_visible():
            self.game.workshop.clear_paywall()

        # determine level
        current_lvl = self.game.workshop.get_level_number()
        self.levels.append(current_lvl)

        if self.previous_level != current_lvl:
            # On new WS level
            self.previous_level = current_lvl
            print(f'On workshop {current_lvl}')

        if current_lvl == 1:
            self.handle_ws1()
        elif 2 <= current_lvl <= 29:
            self.handle_ws_dynamic(current_lvl, active_build=1, extra_wait=1, max_wait=15)
        elif 30 <= current_lvl <= 59:
            self.handle_ws_dynamic(current_lvl, active_build=2, extra_wait=3, max_wait=20)
        elif 60 <= current_lvl <= 80:
            self.handle_ws_dynamic(current_lvl, active_build=3, extra_wait=5, max_wait=60)
        elif 81 <= current_lvl <= 90:
            self.handle_ws_dynamic(current_lvl, active_build=3, extra_wait=5, max_wait=80)
        elif current_lvl >= 91:
            self.handle_reincarnation()

        # TODO: if lvl 2: implement favors

    @classmethod
    def wait_intervals(cls, total_sec, interval=5):
        num_intervals = total_sec // interval
        for i in range(num_intervals):
            time_remaining = total_sec - (i * interval)
            # print(f'automation resumes in {time_remaining}s...')
            # if time_remaining == interval:
            #     audio.play_notes('DEAD', timings=[150] * 4)
            #     audio.play_win('arcade_beep.wav')
            time.sleep(interval)

    def change_build(self, active_build):
        self.game.workshop.set_workshop_setup(active_build)
        time.sleep(3)

        if self.active_build != 0:
            self.game.workshop.buy_max_merchant()
            self.game.workshop.buy_max_research()

        self.game.workshop.select_ws_tabs(1)

        self.active_build = active_build

    def handle_ws_dynamic(self, current_level, active_build, extra_wait=5, max_wait=30):
        print('in ws_dynamic')

        # change to a new active build, if needed
        if self.active_build != active_build:
            print(f'changing from build {self.active_build} to {active_build}')
            self.change_build(active_build)

        start_time = time.time()

        while not self.game.workshop.is_autobuild_done():
            # autobuild is still running, keep waiting
            time.sleep(1)

            # if max_wait has been exceeded, something is likely wrong. bail early and rebuild
            elapsed_time = time.time() - start_time
            if elapsed_time >= max_wait:
                print(f'warning: exceeded max_wait time ({max_wait}s)')
                break

        if extra_wait > 0:
            # print(f'autobuild finished, waiting {extra_wait}s extra')
            self.wait_intervals(extra_wait)

        if current_level <= 5:
            self.game.rebuild.simple_rebuild()
        else:
            self.game.rebuild.dynamic_rebuild(current_level)

    def handle_ws1(self):
        print('in ws1')
        if self.active_build != 1:
            self.change_build(1)
        self.game.rebuild.simple_rebuild()

    def handle_reincarnation(self):
        print('in reincarnation')
        self.game.dynasty.navigate_to()
        self.game.dynasty.reincarnate()
        self.previous_level = 0


class EventWorkshopStrat:
    def __init__(self, game):
        self.game = game
        self.game.start()

        self.build_start = (570, 395)  # Top-left first resource
        self.build_rows = 2
        self.build_cols = 6
        self.build_diff = 68  # distance from one product to the next (when borders are touching)
        self.build_timing = [10, 10, 10, 10, 10, 10,
                             12, 12, 12, 22, 20, 15]

    def update(self):
        self.handle_idle_event_ws()

    @classmethod
    def wait_intervals(cls, total_sec, interval=5):
        num_intervals = total_sec // interval
        for i in range(num_intervals):
            print(f'automation resumes in {total_sec-(i*interval)}s...')
            time.sleep(interval)

    def handle_active_event_ws(self):
        print('in active event_ws')

        time.sleep(3)  # allow autobuild to kick off

        for row in range(self.build_rows):
            for col in range(self.build_cols):
                build_num = row * self.build_cols + col
                print(f'building {build_num} ({col}, {row})')
                x = self.build_start[0] + (col * self.build_diff)
                y = self.build_start[1] + (row * self.build_diff)

                start_time = time.time()
                elapsed = 0

                while elapsed < self.build_timing[build_num]:
                    self.game.workshop.click_product((x, y))
                    time.sleep(0.05)  # 50ms
                    elapsed = time.time() - start_time

                    if keyboard.is_pressed("q"):
                        exit()

        self.game.rebuild.event_rebuild()

    def handle_idle_event_ws(self):
        print('in idle event_ws')

        start_time = time.time()
        elapsed = 0
        six_fame_seconds = 8 * 60 + 30

        # time.sleep(3)  # allow autobuild to kick off
        self.wait_intervals(six_fame_seconds)
        self.game.rebuild.event_rebuild()
