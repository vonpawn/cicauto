import time

import cicauto.graphics as graphics

from cicauto.sdk.base import BaseContext, UnknownGameState

WORKSHOP_NAVIGATION = (255, 80)

CLEAR_ACHIEVE = (1235, 865)
BUILD_NEXT_PRODUCT = (275, 275)
CLEAR_POPUP = (365, 950)

WS_DROPDOWN = (320, 215)
ACTIVE_PRODUCTS = (30, 265)
PRODUCT_SELECTION = (30, 305)
WORKSHOP_SETUP = (30, 345)

WORKSHOP_SETUP_1 = (285, 320)
WORKSHOP_SETUP_2 = (285, 445)
WORKSHOP_SETUP_3 = (285, 560)
SETUP_CHANGE_OK = (765, 585)

ACTIVE_TAB = (370, 240)
AUTO_TAB = (370, 310)
ACHIEVE_TAB = (370, 385)
MULTIPLIER_TAB = (370, 460)

HIRE_RESEARCH = (260, 255)
HIRE_MERCHANT = (260, 415)
RESEARCH_MAX = (525, 255)
MERCHANT_MAX = (525, 415)


class Workshop(BaseContext):
    last_level = 30

    def navigate_to(self):
        self.safe_click(WORKSHOP_NAVIGATION)
        self.wait_until_visible('workshop_tab_active.png')

    def get_level_number(self):
        # take picture of subregion
        game_image = self.get_game_image()
        level_region = (15, 120, 75, 170)
        level_image = graphics.get_sub_image(game_image, level_region)

        # ocr picture
        level_text = graphics.get_text_from_image(level_image)

        # extract number
        level_number = ''.join(filter(str.isdigit, level_text))

        # error check ocr'd number
        if level_number == '':
            print(f'failed to extract level number from ocr')
            return self.last_level
            # raise RuntimeError(f'failed to extract level number from ocr')
        level_number = int(level_number)
        if level_number < 0 or level_number > 120:
            raise RuntimeError(f'expected level number between 1 and 120, OCR returned: {level_number}')

        self.last_level = level_number
        return level_number

    def get_current_fame(self):
        pass

    def get_max_fame(self):
        pass

    def get_income_per_second(self):
        # take 60min time warp value / 3600
        pass

    def is_autobuild_done(self):
        game_img = self.get_game_image()
        test_img_name = 'empty_build.png'
        test_img = graphics.open_image(test_img_name)
        test_bounds = (15, 255, 335, 400)
        test_region_img = graphics.get_sub_image(game_img, test_bounds)

        # convert to greyscale, get extrema. The extrema will match if only a single color is present
        baseline_extrema = test_img.convert('L').getextrema()
        sample_extrema = test_region_img.convert('L').getextrema()
        return baseline_extrema == sample_extrema

        # return self.contains_image(test_img_name, region_image=test_region_img)

    def is_paywall_visible(self):
        detected = self.contains_image('yucky_paywall.png')
        if detected:
            print('paywall detected')

        return detected

    def clear_paywall(self):
        print('clearing paywall...')
        close_btn = self.locate_image('paywall_close.png')
        self.safe_click(close_btn)
        self.sleep(1)

    def select_ws_dropdown(self, option):
        if option not in [ACTIVE_PRODUCTS, PRODUCT_SELECTION, WORKSHOP_SETUP]:
            raise ValueError(f'unexpected option for workshop dropdown: {option}')

        self.safe_click(WS_DROPDOWN)
        self.safe_click(option)

    def set_workshop_setup(self, tier):
        if tier not in [1, 2, 3]:
            raise ValueError(f'expected workshop tier of either 1, 2, or 3, received: {tier}')

        self._select_ws_tabs(ACTIVE_TAB)
        self.select_ws_dropdown(WORKSHOP_SETUP)

        if tier == 1:
            self.safe_click(WORKSHOP_SETUP_1)
        elif tier == 2:
            self.safe_click(WORKSHOP_SETUP_2)
        elif tier == 3:
            self.safe_click(WORKSHOP_SETUP_3)

        time.sleep(.5)
        self.safe_click(SETUP_CHANGE_OK)
        time.sleep(.5)

        self.select_ws_dropdown(ACTIVE_PRODUCTS)

    @classmethod
    def get_active_ws_tab(cls):
        tab1_active = cls.contains_image('tab1_active.png')
        tab2_active = cls.contains_image('tab2_active.png')
        tab3_active = cls.contains_image('tab3_active.png')
        tab4_active = cls.contains_image('tab4_active.png')

        for i, condition in enumerate([tab1_active, tab2_active, tab3_active, tab4_active]):
            if condition:
                return i
        raise UnknownGameState('Cannot determine which tab is active')

    def _select_ws_tabs(self, tab):
        tabs = [ACTIVE_TAB, AUTO_TAB, ACHIEVE_TAB, MULTIPLIER_TAB]
        if tab not in tabs:
            raise ValueError(f'unexpected option for workshop tabs: {tab}')

        self.wait_until_visible('settings_gear.png')  # make sure we are actually on ws before continuing
        active_tab = self.get_active_ws_tab()
        if tab == tabs[active_tab]:
            # current tab matches target tab, return early
            return

        self.safe_click(tab)

    def select_ws_tabs(self, tab_num):
        if tab_num == 1:
            self._select_ws_tabs(ACTIVE_TAB)
        elif tab_num == 2:
            self._select_ws_tabs(AUTO_TAB)
        elif tab_num == 3:
            self._select_ws_tabs(ACHIEVE_TAB)
        elif tab_num == 4:
            self._select_ws_tabs(MULTIPLIER_TAB)
        else:
            raise ValueError(f'unexpected option for workshop tabs: {tab_num}')

    def buy_max_merchant(self):
        self._select_ws_tabs(AUTO_TAB)
        self.safe_keydown('ctrl')
        self.safe_keydown('shift')
        # self.safe_drag(HIRE_MERCHANT, MERCHANT_MAX)
        self.safe_click(HIRE_MERCHANT)
        self.safe_keyup('ctrl')
        self.safe_keyup('shift')

    def buy_max_research(self):
        self._select_ws_tabs(AUTO_TAB)
        # TODO: with pyautogui.hold('shift'):
        self.safe_keydown('ctrl')
        self.safe_keydown('shift')
        # self.safe_drag(HIRE_RESEARCH, RESEARCH_MAX)
        self.safe_click(HIRE_RESEARCH)
        self.safe_keyup('ctrl')
        self.safe_keyup('shift')

    def click_product(self, coords):
        self.safe_click(coords, click_type='right')
