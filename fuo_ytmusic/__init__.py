# *-- coding: utf-8 --*
__alias__ = 'Youtube Music'
__feeluown_version__ = '3.1'
__version__ = '0.1.0'
__desc__ = __alias__
__identifier__ = 'ytmusic'

from feeluown.app import App


def enable(app: App):
    app.library.register(provider)
    if app.mode & App.GuiMode:
        pm = app.pvd_uimgr.create_item(
            name=provider.identifier,
            text=__alias__,
            symbol='♫ ',
            desc='未实现',
        )
        app.pvd_uimgr.add_item(pm)


def disable(app: App):
    app.library.deregister(provider)
    if app.mode & App.GuiMode:
        app.providers.remove(provider.identifier)


from .provider import provider
