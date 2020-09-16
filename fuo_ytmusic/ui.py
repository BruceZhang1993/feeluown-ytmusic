import json
import logging
from pathlib import Path

from feeluown.gui.widgets import CookiesLoginDialog

from .provider import provider

logger = logging.getLogger(__name__)


class InvalidHeader(Exception):
    pass


class LoginDialog(CookiesLoginDialog):
    AUTH_FILE = Path.home() / '.FeelUOwn' / 'data' / 'ytmusic_header.json'

    def setup_user(self, user):
        provider.user = user

    async def user_from_cookies(self, data):
        return provider.User.get(0)

    def load_user_cookies(self):
        if self.AUTH_FILE.exists():
            # if the file is broken, just raise error
            with self.AUTH_FILE.open('r') as f:
                cookie_str = json.load(f).get('Cookie', None)
                cookies = {}
                for cookie_pair in cookie_str.split(';'):
                    if cookie_pair == '':
                        continue
                    cp = cookie_pair.split('=')
                    cookies[cp[0]] = cp[1]
                return cookies

    def dump_user_cookies(self, user, cookies):
        cookie_str = ''
        for key, value in cookies.items():
            cookie_str += f'{key}={value};'
        data = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'X-Goog-AuthUser': '0',
            'x-origin': 'https://music.youtube.com',
            'Cookie': cookie_str
        }
        with self.AUTH_FILE.open('w') as f:
            json.dump(data, f, indent=2)
        provider.api.init()


class UiManager:
    def __init__(self, app):
        self.app = app
        self.pvd_item = app.pvd_uimgr.create_item(
            name=provider.identifier,
            text=provider.name,
            symbol='🎵️',
            desc=f'点击登录 {provider.name}'
        )
        self.pvd_item.clicked.connect(self.login_or_show)
        app.pvd_uimgr.add_item(self.pvd_item)

    def login_or_show(self):
        if provider.user is None:
            dialog = LoginDialog()
            dialog.login_succeed.connect(self.show_current_user)
            dialog.show()
            dialog.autologin()
        else:
            logger.info('already logged in')
            self.show_current_user()

    def show_current_user(self):
        user = provider.user
        self.app.ui.left_panel.my_music_con.hide()
        self.app.ui.left_panel.playlists_con.show()
        self.app.pl_uimgr.clear()
        self.app.pl_uimgr.add(user.playlists)
        self.pvd_item.text = f'{provider.name} - 已登录'
