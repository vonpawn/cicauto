from enum import Enum

from cicauto.sdk import window, workshop, blueprint, dynasty, event, rebuild, settings


class IllegalStateOperation(Exception):
    pass


class AutoState(Enum):
    NEW, START, RUNNING, PAUSED, STOP = range(5)


class CICAuto:
    def __init__(self, strategy):
        self.state = AutoState.NEW

    def register_actions(self, name, action_controller):
        action_controller.game = self  # TODO: How insane is passing this reference to the child classes?
        setattr(self, name, action_controller)

    def is_running(self):
        return self.state != AutoState.STOP

    def start(self):
        if self.state not in [AutoState.NEW]:
            raise IllegalStateOperation()

        # Add any state setup needed here

        self.state = AutoState.START

    def stop(self):
        if self.state not in [AutoState.START, AutoState.RUNNING, AutoState.PAUSED]:
            raise IllegalStateOperation()
        self.state = AutoState.STOP


cicauto = CICAuto(None)
cicauto.register_actions('window', window.Window())
cicauto.register_actions('workshop', workshop.Workshop())
# cicauto.register_actions('blueprint', blueprint.Blueprint())
cicauto.register_actions('dynasty', dynasty.Dynasty())
# cicauto.register_actions('event', event.Event())
cicauto.register_actions('rebuild', rebuild.Rebuild())
# cicauto.register_actions('settings', settings.Settings())
