from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from .reminder_ui import ReminderUI
from .booking_ui import BookingUI

class MainScreenUI(TabbedPanel):
    def __init__(self, user_id, id_token, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False

        # Reminder Tab
        reminder_tab = TabbedPanelItem(text='Reminders')
        reminder_tab.content = ReminderUI(user_id=user_id, id_token=id_token)
        self.add_widget(reminder_tab)

        # Booking Tab
        booking_tab = TabbedPanelItem(text='Bookings')
        booking_tab.content = BookingUI(user_id=user_id, id_token=id_token)
        self.add_widget(booking_tab)
