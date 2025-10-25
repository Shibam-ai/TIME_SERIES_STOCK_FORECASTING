from jnius import autoclass
from kivy.utils import platform
import datetime

def schedule_notification(title, message, schedule_time_str):
    """
    Schedules a local notification on Android using pyjnius to interact with the native AlarmManager.
    """
    if platform != 'android':
        print("This notification scheduling is only supported on Android.")
        return

    # Import necessary Android classes
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    AlarmManager = autoclass('android.app.AlarmManager')

    # Custom Java class
    AlarmReceiver = autoclass('org.test.myapp.AlarmReceiver')

    context = PythonActivity.mActivity

    # Convert the schedule time string to milliseconds
    try:
        schedule_time = datetime.datetime.strptime(schedule_time_str, "%Y-%m-%d %H:%M")
        schedule_time_millis = int(schedule_time.timestamp() * 1000)
    except ValueError:
        print(f"Invalid date format for notification: {schedule_time_str}")
        return

    # Create an Intent that will be broadcasted by the AlarmManager
    intent = Intent(context, AlarmReceiver)
    intent.putExtra("title", title)
    intent.putExtra("message", message)
    # Use a unique ID for each notification to avoid overwriting
    notification_id = schedule_time_millis % 100000
    intent.putExtra("notification_id", notification_id)

    # The FLAG_IMMUTABLE is required for Android 12+
    pending_intent = PendingIntent.getBroadcast(context, notification_id, intent, PendingIntent.FLAG_IMMUTABLE)

    # Get the AlarmManager service and schedule the alarm
    alarm_manager = context.getSystemService(Context.ALARM_SERVICE)
    alarm_manager.set(AlarmManager.RTC_WAKEUP, schedule_time_millis, pending_intent)

    print(f"Successfully scheduled notification for: {schedule_time}")

def cancel_notification(notification_id_str):
    """
    Cancels a previously scheduled notification on Android.
    """
    if platform != 'android':
        return

    # Import necessary Android classes
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    AlarmManager = autoclass('android.app.AlarmManager')
    AlarmReceiver = autoclass('org.test.myapp.AlarmReceiver')

    context = PythonActivity.mActivity

    notification_id = int(notification_id_str)

    # Recreate the exact same PendingIntent that was used to schedule the alarm
    intent = Intent(context, AlarmReceiver)
    pending_intent = PendingIntent.getBroadcast(context, notification_id, intent, PendingIntent.FLAG_IMMUTABLE)

    # Get the AlarmManager and cancel the alarm
    alarm_manager = context.getSystemService(Context.ALARM_SERVICE)
    alarm_manager.cancel(pending_intent)

    print(f"Successfully canceled notification with ID: {notification_id}")
