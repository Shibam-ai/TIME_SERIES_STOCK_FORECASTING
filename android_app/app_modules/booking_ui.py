from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from .reminder_ui import SelectableRecycleBoxLayout, ReminderListItem
from . import firebase_service
from .edit_view_ui import EditViewUI

class BookingUI(BoxLayout):
    def __init__(self, user_id, id_token, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.id_token = id_token
        self.orientation = 'vertical'
        self.bookings_data = []
        self.current_view = 'list'

        self.draw_list_view()
        self.load_bookings()

    def draw_list_view(self):
        self.clear_widgets()
        self.current_view = 'list'

        # Form for adding new bookings
        form_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=250)
        form_layout.add_widget(Label(text='New Booking'))

        self.type_input = TextInput(hint_text='Booking Type (e.g., Flight, Train)')
        form_layout.add_widget(self.type_input)

        self.confirmation_input = TextInput(hint_text='Confirmation Number')
        form_layout.add_widget(self.confirmation_input)

        self.departure_input = TextInput(hint_text='Departure Date (YYYY-MM-DD HH:MM)')
        form_layout.add_widget(self.departure_input)

        self.arrival_input = TextInput(hint_text='Arrival Date (YYYY-MM-DD HH:MM)')
        form_layout.add_widget(self.arrival_input)

        self.add_button = Button(text='Add Booking')
        self.add_button.bind(on_press=self.add_booking)
        form_layout.add_widget(self.add_button)

        self.add_widget(form_layout)

        # Action buttons
        action_layout = BoxLayout(size_hint_y=None, height=50)
        self.edit_button = Button(text="Edit Selected")
        self.edit_button.bind(on_press=self.show_edit_view)
        action_layout.add_widget(self.edit_button)

        self.delete_button = Button(text="Delete Selected")
        self.delete_button.bind(on_press=self.delete_selected_booking)
        action_layout.add_widget(self.delete_button)
        self.add_widget(action_layout)

        # List to display bookings
        self.booking_list = RecycleView()
        self.booking_list.viewclass = ReminderListItem
        self.layout = SelectableRecycleBoxLayout(orientation='vertical',
                                            size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.booking_list.add_widget(self.layout)

        self.add_widget(self.booking_list)

        # Status label
        self.status_label = Label(text="", size_hint_y=None, height=40)
        self.add_widget(self.status_label)

    def add_booking(self, instance):
        booking_type = self.type_input.text
        confirmation_number = self.confirmation_input.text
        departure_date = self.departure_input.text
        arrival_date = self.arrival_input.text

        if not all([booking_type, confirmation_number, departure_date, arrival_date]):
            self.status_label.text = "Please fill in all fields."
            return

        success = firebase_service.add_booking(self.id_token, self.user_id, booking_type, confirmation_number, departure_date, arrival_date)
        if success:
            self.status_label.text = "Booking added!"
            self.type_input.text = ""
            self.confirmation_input.text = ""
            self.departure_input.text = ""
            self.arrival_input.text = ""
            self.load_bookings()
        else:
            self.status_label.text = "Failed to add booking."

    def load_bookings(self):
        if self.current_view == 'list':
            self.bookings_data = firebase_service.get_bookings(self.id_token, self.user_id)
            self.layout.data = [{'text': f"{b['booking_type']} ({b['confirmation_number']})"} for b in self.bookings_data]

    def delete_selected_booking(self, instance):
        selected_nodes = self.layout.recycle_view.layout_manager.selected_nodes
        if not selected_nodes:
            self.status_label.text = "Please select a booking to delete."
            return

        node_index = selected_nodes[0]
        booking_to_delete = self.bookings_data[node_index]
        booking_id = booking_to_delete['id']

        success = firebase_service.delete_booking(self.id_token, self.user_id, booking_id)
        if success:
            self.status_label.text = "Booking deleted."
            self.load_bookings()
        else:
            self.status_label.text = "Failed to delete booking."

    def show_edit_view(self, instance):
        selected_nodes = self.layout.recycle_view.layout_manager.selected_nodes
        if not selected_nodes:
            self.status_label.text = "Please select a booking to edit."
            return

        node_index = selected_nodes[0]
        booking_to_edit = self.bookings_data[node_index]

        self.clear_widgets()
        self.current_view = 'edit'
        edit_view = EditViewUI(item_data=booking_to_edit, item_type='booking')
        edit_view.bind(on_save=self.save_edited_booking)
        edit_view.back_button.bind(on_press=lambda x: self.load_bookings() and self.draw_list_view())
        self.add_widget(edit_view)

    def save_edited_booking(self, instance, updated_data):
        selected_nodes = self.layout.recycle_view.layout_manager.selected_nodes
        if not selected_nodes:
            self.draw_list_view()
            self.load_bookings()
            return

        node_index = selected_nodes[0]
        original_booking = self.bookings_data[node_index]
        booking_id = original_booking['id']

        success = firebase_service.update_booking(self.id_token, self.user_id, booking_id, updated_data)
        if success:
            self.status_label.text = "Booking updated."
        else:
            self.status_label.text = "Failed to update booking."

        self.draw_list_view()
        self.load_bookings()
