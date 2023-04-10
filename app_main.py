from nicegui import app, ui
import asyncio
import sys

# Are we running in a PyInstaller bundle
# https://pyinstaller.org/en/stable/runtime-information.html#run-time-information
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    class NullOutput(object):
        def write(self, string):
            pass

        # noinspection PyMethodMayBeStatic
        def isatty(self):
            return False


    sys.stdout = NullOutput()
    sys.stderr = NullOutput()


@ui.page('/', dark=True)
def index_page():
    with ui.row():
        async def async_task():

            if run.text == 'start':
                run.set_text('stop')
                # run.props('disabled')
                ui.notify('Asynchronous task started')
                await asyncio.sleep(5)
                ui.notify('Asynchronous task finished')
                # run.props(remove='disabled')
            elif run.text == 'stop':
                run.set_text('start')

        run = ui.button('start', on_click=async_task)
        calibrate = ui.button('calibrate', on_click=lambda: ui.notify(f'You clicked me!'))
        config = ui.button('config', on_click=lambda: ui.notify(f'You clicked me!'))

    with ui.tabs() as tabs:
        ui.tab('Home', icon='home')
        ui.tab('About', icon='info')

    with ui.tab_panels(tabs, value='Home'):
        with ui.tab_panel('Home'):
            ui.label('This is the first tab')
        with ui.tab_panel('About'):
            ui.label('This is the second tab')


if __name__ in {"__main__", "__mp_main__"}:
    app.native.title = 'CicadaApp'
    app.native.width, app.native.height = 800, 600
    app.native.resizable = False

    ui.run(reload=True, native=False)  # live browser debugging mode with reload
    # ui.run(reload=True, native=False)  # pyinstaller mode
