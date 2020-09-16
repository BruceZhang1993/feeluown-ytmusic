# *-- coding: utf-8 --*
__alias__ = 'Youtube Music'
__feeluown_version__ = '3.1'
__version__ = '0.1.0'
__desc__ = __alias__
__identifier__ = 'ytmusic'

from feeluown.app import App

from .ui import UiManager

ui_mgr = None


def enable(app: App):
    global ui_mgr
    app.library.register(provider)
    if app.mode & App.GuiMode:
        ui_mgr = ui_mgr or UiManager(app)


def disable(app: App):
    app.library.deregister(provider)
    if app.mode & App.GuiMode:
        app.providers.remove(provider.identifier)


from .provider import provider
