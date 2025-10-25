import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the config module before importing firebase_service
sys.modules['config'] = Mock(API_KEY='fake_api_key', PROJECT_ID='fake_project_id')

from app_modules import firebase_service

class TestFirebaseService(unittest.TestCase):

    @patch('app_modules.firebase_service.requests.post')
    def test_login_success(self, mock_post):
        """Test successful user login."""
        mock_response = Mock()
        mock_response.json.return_value = {'email': 'test@example.com', 'localId': 'test_user_123'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = firebase_service.login('test@example.com', 'password123')
        self.assertEqual(result['email'], 'test@example.com')
        mock_post.assert_called_once()

    @patch('app_modules.firebase_service.requests.post')
    def test_login_failure(self, mock_post):
        """Test failed user login."""
        mock_http_error = firebase_service.requests.exceptions.HTTPError()
        mock_error_response = Mock()
        mock_error_response.json.return_value = {'error': {'message': 'INVALID_LOGIN_CREDENTIALS'}}
        mock_error_response.text = '{"error": {"message": "INVALID_LOGIN_CREDENTIALS"}}'
        mock_http_error.response = mock_error_response

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = mock_http_error
        mock_response.json.return_value = mock_error_response.json() # Ensure the response also has the json
        mock_post.return_value = mock_response

        result = firebase_service.login('test@example.com', 'wrongpassword')
        self.assertIn('error', result)

    @patch('app_modules.firebase_service.requests.post')
    def test_add_reminder_success(self, mock_post):
        """Test successfully adding a reminder."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = firebase_service.add_reminder('fake_token', 'user1', 'Test Title', 'Test Desc', '2025-01-01 10:00')
        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch('app_modules.firebase_service.requests.get')
    def test_get_reminders_success(self, mock_get):
        """Test successfully retrieving reminders."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'documents': [{
                'name': 'projects/proj/databases/(default)/documents/users/user1/reminders/rem1',
                'fields': {
                    'title': {'stringValue': 'Test Reminder'},
                    'reminder_time': {'timestampValue': '2025-01-01T10:00:00Z'}
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = firebase_service.get_reminders('fake_token', 'user1')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Test Reminder')

    @patch('app_modules.firebase_service.requests.delete')
    def test_delete_reminder_success(self, mock_delete):
        """Test successfully deleting a reminder."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response

        result = firebase_service.delete_reminder('fake_token', 'user1', 'reminder123')
        self.assertTrue(result)
        mock_delete.assert_called_once_with(
            f"{firebase_service.FIRESTORE_URL}/users/user1/reminders/reminder123",
            headers={"Authorization": "Bearer fake_token"}
        )

if __name__ == '__main__':
    unittest.main()
