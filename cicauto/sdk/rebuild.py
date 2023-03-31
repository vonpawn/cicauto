import pyautogui

from cicauto.sdk.base import BaseContext

# Rebuild ws6+
LEVEL_NUMBER_BUTTON = (45, 140)
DOUBLE_LORE_BUTTON = (705, 637)  # TODO: change back to 635
STRICT_DOUBLE_LORE_BUTTON = (610, 640)  # will enforce 2x lore over an unwanted pack
REBUILD_NOW_BUTTON = (790, 740)
TAKE_REWARD_BUTTON = (870, 630)
REBUILD_FREE_BUTTON = (890, 440)

# Complex Rebuild that will lead to a new level
NEW_LEVEL_DOUBLE_LORE = (705, 640)
NEW_LEVEL_BUILD_NOW = (790, 765)

# Simple Rebuild ws1
SIMPLE_REBUILD_NOW = (790, 695)
SIMPLE_TAKE_REWARD = (825, 565)
SIMPLE_REBUILD_FREE = (905, 525)  # (900, 466)

# Simple Rebuild ws2+
SIMPLE_REBUILD_FREE_2 = (900, 385)

basic_pack_levels = [6, 8, 9, 11, 17, 18, 20, 25, 27, 36]
inter_pack_levels = [10, 16, 19, 26, 28, 29, 37, 38, 47, 48]
adv_pack_levels = [30, 39, 41, 45, 46, 49, 55, 56, 57, 58]
mag_pack_levels = [40, 50, 59, 61, 62, 67]
PACK_LEVELS = basic_pack_levels + inter_pack_levels + adv_pack_levels + mag_pack_levels


class Rebuild(BaseContext):
    # -----------------
    # Actions
    # -----------------
    def open_rebuild_screen(self):
        self.safe_click(LEVEL_NUMBER_BUTTON)

    def select_reward(self, current_level, priorities=None):
        # 1x, 2x, pack, [gem], bp
        # 1x, 2x, [pack], bp
        # 1x, 2x, [gem], bp
        # 1x, [2x], bp
        possible_rewards = self.get_possible_rewards()

        if current_level >= 70 and 'gems' in possible_rewards.keys():
            print('found gems!')
            self.safe_click(possible_rewards.get('gems'))
        elif current_level < 35 and current_level in PACK_LEVELS:
            # likely still in single resets per stage, not worth claiming packs to get 80% double lore next
            self.safe_click(STRICT_DOUBLE_LORE_BUTTON)
        else:
            self.safe_click(DOUBLE_LORE_BUTTON)  # Same position for pack/2x lore

        # Loop through rewards finding which range is most applicable
        # If highest priority has acceptable range overlap, select it
        # else keep lowering priority until range overlap is met

    def rebuild_now(self):
        # result = -1
        # while result == -1:
        result = self.wait_until_visible('rebuild_now_button.png')
        rebuild_btn = result

        if rebuild_btn != -1:
            self.safe_click(rebuild_btn)
        # self.safe_click(REBUILD_NOW_BUTTON)

    def change_reward(self):
        raise NotImplementedError

    def take_reward(self):
        self.safe_click(TAKE_REWARD_BUTTON)

    def rebuild_free(self):
        result = self.wait_until_visible('free_button.png')
        free_btn = result

        if free_btn != -1:
            self.safe_click(free_btn)
        # self.safe_click(REBUILD_FREE_BUTTON)

    # -------
    # Helpers
    # -------
    def get_possible_rewards(self) -> dict:
        # box_coords = self.locate_image('rewards_box.png')
        # anchor = (box_coords.left, box_coords.top)
        # self.move_to(anchor)
        rewards = {}

        gem_result = self.locate_image('gems.png')
        if gem_result is not None:
            rewards['gems'] = gem_result

        # TODO: determine remaining reward info (detect which bp / pack?)

        return rewards

    # -----------------
    # Rebuild Workflows
    # -----------------

    def simple_rebuild(self):
        print('simple rebuilding')
        self.open_rebuild_screen()
        self.wait_until_visible('dynamic_rebuild/rebuild_ws.png')

        rebuild_btn = self.wait_until_visible('dynamic_rebuild/rebuild_now.png')
        self.safe_click(rebuild_btn)

        take_reward = self.wait_until_visible('dynamic_rebuild/take_reward.png')
        self.safe_click(take_reward)

        rebuild_free = self.wait_until_visible('dynamic_rebuild/rebuild_free.png')
        self.safe_click(rebuild_free)

        self.sleep(3)

    def get_rebuild_context(self):
        # sequentially try detecting rebuild screens until one is found, return first found
        # screen represented by a number
        # 1 - reward selection screen
        # 2 - reward result screen
        # 3 - rebuild final screen
        # 4 - back in the workshop (and thus rebuild is over)
        # -1 - failed to determine rebuild context
        context_images = [
            'dynamic_rebuild/rebuild_ws.png',
            'dynamic_rebuild/take_reward.png',
            'dynamic_rebuild/rebuild_free.png',
            'settings_gear.png']
        for i, ctx_image in enumerate(context_images):
            on_stage_i = self.contains_image(ctx_image)
            if on_stage_i:
                return i + 1
        return -1

    def dynamic_rebuild(self, current_level):
        # print('dynamic rebuilding')
        self.open_rebuild_screen()
        self.sleep(3)

        seen_stage_1 = False
        in_rebuild = True
        while in_rebuild:
            context = self.get_rebuild_context()

            if context == 1:
                # reward selection screen
                seen_stage_1 = True
                self.select_reward(current_level)
                self.sleep(1)
                self.rebuild_now()
                self.sleep(3)
            elif context == 2:
                # reward result screen
                self.take_reward()
                self.sleep(3)
            elif context == 3:
                # rebuild final screen
                self.rebuild_free()
                self.sleep(3)
            elif context == 4 and seen_stage_1:
                # rebuild has suceeded and game is back on workshop, move on
                break
            elif context == 4 and not seen_stage_1:
                # Opening the rebuild screen failed for whatever reason, try again

                # ensure paywall model is removed (only pops up if double speed 15min or less)
                if self.game.workshop.is_paywall_visible():
                    self.game.workshop.clear_paywall()

                self.open_rebuild_screen()
                self.sleep(3)
            else:
                # let the game catch up, it is likely transitioning screens
                self.sleep(1)

    def event_rebuild(self):
        # print('dynamic rebuilding')
        self.open_rebuild_screen()
        self.sleep(3)

        seen_stage_1 = False
        in_rebuild = True
        while in_rebuild:
            context = self.get_rebuild_context()

            if context == 1:
                # reward selection screen
                seen_stage_1 = True
                # self.select_reward(current_level)
                # self.sleep(1)
                self.rebuild_now()
                self.sleep(3)
            elif context == 2:
                # reward result screen
                self.take_reward()
                self.sleep(3)
            elif context == 3:
                # rebuild final screen
                self.rebuild_free()
                self.sleep(3)
            elif context == 4 and seen_stage_1:
                # rebuild has suceeded and game is back on workshop, move on
                break
            elif context == 4 and not seen_stage_1:
                # Opening the rebuild screen failed for whatever reason, try again

                # ensure paywall model is removed (only pops up if double speed 15min or less)
                if self.game.workshop.is_paywall_visible():
                    self.game.workshop.clear_paywall()

                self.open_rebuild_screen()
                self.sleep(3)
            else:
                # let the game catch up, it is likely transitioning screens
                self.sleep(1)
