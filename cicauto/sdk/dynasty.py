import cicauto.graphics as graphics
from cicauto.sdk.base import BaseContext, UnknownGameState

DYNASTY_NAVIGATION = (415, 80)

REINCARNATE_BUTTON = (185, 555)
DEFAULT_REINCARNATE = (535, 695)


class Dynasty(BaseContext):

    def navigate_to(self):
        self.safe_click(DYNASTY_NAVIGATION)
        self.wait_until_visible('your_dynasty.png')

    def reincarnate(self):
        self.safe_click(REINCARNATE_BUTTON)
        self.sleep(3)

        self.safe_click(DEFAULT_REINCARNATE)
        self.sleep(5)
