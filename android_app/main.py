from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from app_modules.auth_ui import AuthUI
from app_modules.main_screen_ui import MainScreenUI

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_ui = AuthUI()
        self.auth_ui.bind(on_login_success=self.go_to_main_screen)
        self.add_widget(self.auth_ui)

    def go_to_main_screen(self, instance, user_data):
        self.manager.current = 'main'
        main_screen = self.manager.get_screen('main')
        main_screen.add_widget(MainScreenUI(user_id=user_data['localId'], id_token=user_data['idToken']))

class MainScreen(Screen):
    pass

class MainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    MainApp().run()
