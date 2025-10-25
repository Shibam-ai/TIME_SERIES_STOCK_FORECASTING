import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the jnius module for non-Android environments
sys.modules['jnius'] = Mock()

from app_modules import android_service

class TestAndroidService(unittest.TestCase):

    @patch('app_modules.android_service.platform', 'android')
    @patch('app_modules.android_service.autoclass')
    def test_schedule_notification(self, mock_autoclass):
        """Test the scheduling of a notification."""
        # Setup mocks for all the Android classes
        mock_activity = Mock()
        mock_context = Mock()
        mock_activity.mActivity = mock_context

        mock_alarm_manager = Mock()
        mock_context.getSystemService.return_value = mock_alarm_manager

        # Mock the Context class to return the correct constant
        mock_Context = Mock()
        mock_Context.ALARM_SERVICE = 'alarm'

        mock_autoclass.side_effect = [
            mock_activity, # PythonActivity
            mock_Context,  # Context
            Mock(),        # Intent
            Mock(),        # PendingIntent
            Mock(),        # AlarmManager
            Mock()         # AlarmReceiver
        ]

        title = "Meeting"
        message = "Project kickoff at 10 AM"
        schedule_time = "2025-12-25 10:00"

        android_service.schedule_notification(title, message, schedule_time)

        # Verify that getSystemService was called to get the AlarmManager
        mock_context.getSystemService.assert_called_with('alarm')

        # Verify that the AlarmManager's set method was called, indicating a schedule attempt
        mock_alarm_manager.set.assert_called_once()

    @patch('app_modules.android_service.platform', 'android')
    @patch('app_modules.android_service.autoclass')
    def test_cancel_notification(self, mock_autoclass):
        """Test the cancellation of a notification."""
        mock_activity = Mock()
        mock_context = Mock()
        mock_activity.mActivity = mock_context

        mock_alarm_manager = Mock()
        mock_context.getSystemService.return_value = mock_alarm_manager

        # Mock the Context class to return the correct constant
        mock_Context = Mock()
        mock_Context.ALARM_SERVICE = 'alarm'

        mock_autoclass.side_effect = [
            mock_activity, # PythonActivity
            mock_Context,  # Context
            Mock(),        # Intent
            Mock(),        # PendingIntent
            Mock(),        # AlarmManager
            Mock()         # AlarmReceiver
        ]

        notification_id = "12345"
        android_service.cancel_notification(notification_id)

        mock_context.getSystemService.assert_called_with('alarm')
        mock_alarm_manager.cancel.assert_called_once()

if __name__ == '__main__':
    unittest.main()
