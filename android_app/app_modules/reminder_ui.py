from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from . import firebase_service
from . import notification_service

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''

class ReminderListItem(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(ReminderListItem, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(ReminderListItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected

class ReminderUI(BoxLayout):
    def __init__(self, user_id, id_token, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.id_token = id_token
        self.orientation = 'vertical'
        self.reminders_data = []

        # Form for adding new reminders
        form_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=200)
        form_layout.add_widget(Label(text='New Reminder'))

        self.title_input = TextInput(hint_text='Title')
        form_layout.add_widget(self.title_input)

        self.desc_input = TextInput(hint_text='Description')
        form_layout.add_widget(self.desc_input)

        self.time_input = TextInput(hint_text='Time (e.g., YYYY-MM-DD HH:MM)')
        form_layout.add_widget(self.time_input)

        self.add_button = Button(text='Add Reminder')
        self.add_button.bind(on_press=self.add_reminder)
        form_layout.add_widget(self.add_button)

        self.add_widget(form_layout)

        # Delete button
        self.delete_button = Button(text="Delete Selected", size_hint_y=None, height=50)
        self.delete_button.bind(on_press=self.delete_selected_reminder)
        self.add_widget(self.delete_button)

        # List to display reminders
        self.reminder_list = RecycleView()
        self.reminder_list.viewclass = ReminderListItem
        self.layout = SelectableRecycleBoxLayout(orientation='vertical', size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.reminder_list.add_widget(self.layout)

        self.add_widget(self.reminder_list)
        self.load_reminders()

        # Status label
        self.status_label = Label(text="", size_hint_y=None, height=40)
        self.add_widget(self.status_label)

    def add_reminder(self, instance):
        title = self.title_input.text
        description = self.desc_input.text
        reminder_time = self.time_input.text

        if not all([title, description, reminder_time]):
            self.status_label.text = "Please fill in all fields."
            return

        success = firebase_service.add_reminder(self.id_token, self.user_id, title, description, reminder_time)
        if success:
            self.status_label.text = "Reminder added!"
            notification_service.schedule_reminder_notification(title, description, reminder_time)
            self.title_input.text = ""
            self.desc_input.text = ""
            self.time_input.text = ""
            self.load_reminders()
        else:
            self.status_label.text = "Failed to add reminder."

    def load_reminders(self):
        self.reminders_data = firebase_service.get_reminders(self.id_token, self.user_id)
        self.layout.data = [{'text': f"{r['title']} - {r['reminder_time']}"} for r in self.reminders_data]

    def delete_selected_reminder(self, instance):
        selected_nodes = self.layout.recycle_view.layout_manager.selected_nodes
        if not selected_nodes:
            self.status_label.text = "Please select a reminder to delete."
            return

        node_index = selected_nodes[0]
        reminder_to_delete = self.reminders_data[node_index]
        reminder_id = reminder_to_delete['id']

        success = firebase_service.delete_reminder(self.id_token, self.user_id, reminder_id)
        if success:
            self.status_label.text = "Reminder deleted."
            self.load_reminders()
        else:
            self.status_label.text = "Failed to delete reminder."
