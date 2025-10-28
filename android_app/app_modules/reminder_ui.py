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
from . import android_service
from .edit_view_ui import EditViewUI
import datetime

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
        self.current_view = 'list' # Can be 'list' or 'edit'

        self.draw_list_view()
        self.load_reminders()

    def draw_list_view(self):
        self.clear_widgets()
        self.current_view = 'list'

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

        # Action buttons
        action_layout = BoxLayout(size_hint_y=None, height=50)
        self.edit_button = Button(text="Edit Selected")
        self.edit_button.bind(on_press=self.show_edit_view)
        action_layout.add_widget(self.edit_button)

        self.delete_button = Button(text="Delete Selected")
        self.delete_button.bind(on_press=self.delete_selected_reminder)
        action_layout.add_widget(self.delete_button)
        self.add_widget(action_layout)

        # List to display reminders
        self.reminder_list = RecycleView()
        self.reminder_list.viewclass = ReminderListItem
        self.layout = SelectableRecycleBoxLayout(orientation='vertical', size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.reminder_list.add_widget(self.layout)

        self.add_widget(self.reminder_list)

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
            self.status_label.text = "Reminder added and scheduled!"
            android_service.schedule_notification(title, description, reminder_time)
            self.title_input.text = ""
            self.desc_input.text = ""
            self.time_input.text = ""
            self.load_reminders()
        else:
            self.status_label.text = "Failed to add reminder."

    def load_reminders(self):
        if self.current_view == 'list':
            self.reminders_data = firebase_service.get_reminders(self.id_token, self.user_id)
            self.layout.data = [{'text': f"{r['title']} - {r['reminder_time'].replace('Z', '').replace('T', ' ')}"} for r in self.reminders_data]

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
            try:
                reminder_time_str = reminder_to_delete['reminder_time']
                reminder_time_dt = datetime.datetime.fromisoformat(reminder_time_str.replace('Z', '+00:00'))
                notification_id = int(reminder_time_dt.timestamp() * 1000) % 100000
                android_service.cancel_notification(str(notification_id))
            except Exception as e:
                print(f"Could not cancel notification: {e}")

            self.status_label.text = "Reminder deleted."
            self.load_reminders()
        else:
            self.status_label.text = "Failed to delete reminder."

    def show_edit_view(self, instance):
        selected_nodes = self.layout.recycle_view.layout_manager.selected_nodes
        if not selected_nodes:
            self.status_label.text = "Please select a reminder to edit."
            return

        node_index = selected_nodes[0]
        reminder_to_edit = self.reminders_data[node_index]

        self.clear_widgets()
        self.current_view = 'edit'
        edit_view = EditViewUI(item_data=reminder_to_edit, item_type='reminder')
        edit_view.bind(on_save=self.save_edited_reminder)
        edit_view.back_button.bind(on_press=lambda x: self.load_reminders() and self.draw_list_view())
        self.add_widget(edit_view)

    def save_edited_reminder(self, instance, updated_data):
        selected_nodes = self.layout.recycle_view.layout_manager.selected_nodes
        if not selected_nodes:
            # This should not happen in the edit view, but as a safeguard
            self.draw_list_view()
            self.load_reminders()
            return

        node_index = selected_nodes[0]
        original_reminder = self.reminders_data[node_index]
        reminder_id = original_reminder['id']

        # First, cancel the old notification
        try:
            old_time_str = original_reminder['reminder_time']
            old_time_dt = datetime.datetime.fromisoformat(old_time_str.replace('Z', '+00:00'))
            old_notification_id = int(old_time_dt.timestamp() * 1000) % 100000
            android_service.cancel_notification(str(old_notification_id))
        except Exception as e:
            print(f"Could not cancel the old notification: {e}")

        success = firebase_service.update_reminder(self.id_token, self.user_id, reminder_id, updated_data)

        # Then, if the update was successful, schedule the new notification
        if success:
            try:
                new_title = updated_data.get('title', '')
                new_desc = updated_data.get('description', '')
                new_time = updated_data.get('reminder_time', '')
                android_service.schedule_notification(new_title, new_desc, new_time)
            except Exception as e:
                print(f"Could not schedule the new notification: {e}")
        if success:
            self.status_label.text = "Reminder updated."
        else:
            self.status_label.text = "Failed to update reminder."

        self.draw_list_view()
        self.load_reminders()
