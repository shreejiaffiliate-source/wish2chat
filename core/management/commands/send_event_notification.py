import os
import logging
import firebase_admin
from firebase_admin import messaging, credentials
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import SubCategory, FCMDevice
from django.utils.timezone import localdate

class Command(BaseCommand):
    help = "Sends daily event notifications"

    def handle(self, *args, **options):
        # Setup logging to file (for live server)
        logging.basicConfig(
            filename=os.path.join(settings.BASE_DIR, 'notification_log.txt'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # Firebase initialize
        if not firebase_admin._apps:
            try:
                cred_path = os.path.join(
                    settings.BASE_DIR,
                    "serviceAccountKey.json"
                )
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logging.info("Firebase Initialized!")
            except Exception as e:
                logging.error(f"Firebase Init Error: {e}")
                return

        # Today's date
        today = localdate()
        logging.info(f"Checking for events on: {today}")

        # Get all today's events
        events = SubCategory.objects.filter(
            date_event=today,
            is_active=True
        )

        if not events.exists():
            logging.warning("No events found for today.")
            return

        logging.info(f"Event Found: {events.count()}")

        # Get all devices
        devices = FCMDevice.objects.all()

        if not devices.exists():
            logging.error("No devices found.")
            return

        logging.info(f"Sending to {devices.count()} devices...")

        success_count = 0
        failure_count = 0

        # IMPORTANT: nested loop
        for event in events:
            msg_title = "Special Occasion! ✨"
            msg_body = (
                f"On the Occasion of {event.name}, "
                "share beautiful messages to your loved ones!"
            )

            for device in devices:
                try:
                    message = messaging.Message(
                        notification=messaging.Notification(
                            title=msg_title,
                            body=msg_body,
                        ),
                        data={
                            "event_name": event.name,
                            "sub_category_id": str(event.id),
                            "sub_category_name": event.name,
                            "click_action": "FLUTTER_NOTIFICATION_CLICK",
                        },
                        token=device.fcm_token,
                    )

                    messaging.send(message)
                    success_count += 1
                    logging.info(f"Sent {event.name} -> {device.user.username}")

                except Exception as e:
                    failure_count += 1
                    logging.error(f"Failed {event.name} -> {device.user.username}: {e}")

        logging.info(f"Task Finished! Sent: {success_count}, Failed: {failure_count}")