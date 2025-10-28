from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.event import EventDispatcher

class EditViewUI(BoxLayout, EventDispatcher):
    def __init__(self, item_data, item_type, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_save')
        self.orientation = 'vertical'
        self.item_data = item_data
        self.item_type = item_type

        self.fields = {}

        if self.item_type == 'reminder':
            self.add_field('title', 'Title')
            self.add_field('description', 'Description')
            self.add_field('reminder_time', 'Time (YYYY-MM-DD HH:MM)')
        elif self.item_type == 'booking':
            self.add_field('booking_type', 'Booking Type')
            self.add_field('confirmation_number', 'Confirmation Number')
            self.add_field('departure_date', 'Departure (YYYY-MM-DD HH:MM)')
            self.add_field('arrival_date', 'Arrival (YYYY-MM-DD HH:MM)')

        self.save_button = Button(text="Save Changes")
        self.save_button.bind(on_press=self.save_changes)
        self.add_widget(self.save_button)

        self.back_button = Button(text="Back")
        self.add_widget(self.back_button)

    def add_field(self, key, hint_text):
        self.add_widget(Label(text=hint_text))
        # Handle different date formats for display
        display_text = str(self.item_data.get(key, ''))
        if 'Z' in display_text:
             display_text = display_text.replace('Z', '').replace('T', ' ')

        text_input = TextInput(text=display_text, multiline=False)
        self.fields[key] = text_input
        self.add_widget(text_input)

    def save_changes(self, instance):
        updated_data = {}
        for key, text_input in self.fields.items():
            updated_data[key] = text_input.text
        self.dispatch('on_save', updated_data)

    def on_save(self, *args):
        pass
