from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.event import EventDispatcher
from . import firebase_service
import json

class AuthUI(BoxLayout, EventDispatcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_login_success')
        self.orientation = "vertical"

        self.add_widget(Label(text="Email"))
        self.email_input = TextInput(multiline=False)
        self.add_widget(self.email_input)

        self.add_widget(Label(text="Password"))
        self.password_input = TextInput(multiline=False, password=True)
        self.add_widget(self.password_input)

        self.login_button = Button(text="Login")
        self.login_button.bind(on_press=self.login)
        self.add_widget(self.login_button)

        self.signup_button = Button(text="Sign Up")
        self.signup_button.bind(on_press=self.sign_up)
        self.add_widget(self.signup_button)

        self.status_label = Label(text="")
        self.add_widget(self.status_label)

    def login(self, instance):
        email = self.email_input.text
        password = self.password_input.text
        user_data = firebase_service.login(email, password)
        if user_data and 'error' not in user_data:
            self.status_label.text = f"Logged in as {user_data.get('email', '')}"
            self.dispatch('on_login_success', user_data)
        else:
            error_message = user_data.get('error', {}).get('message', 'Login failed')
            self.status_label.text = f"Login failed: {self._parse_error(error_message)}"

    def sign_up(self, instance):
        email = self.email_input.text
        password = self.password_input.text
        user_data = firebase_service.sign_up(email, password)
        if user_data and 'error' not in user_data:
            self.status_label.text = "Sign up successful! Please log in."
        else:
            error_message = user_data.get('error', {}).get('message', 'Sign up failed')
            self.status_label.text = f"Sign up failed: {self._parse_error(error_message)}"

    def _parse_error(self, error_message):
        """Provides a user-friendly error message from the Firebase response."""
        if "INVALID_LOGIN_CREDENTIALS" in error_message:
            return "Invalid email or password."
        if "EMAIL_EXISTS" in error_message:
            return "This email address is already in use."
        if "WEAK_PASSWORD" in error_message:
            return "Password should be at least 6 characters."
        return "An unknown error occurred."

    def on_login_success(self, *args):
        pass
