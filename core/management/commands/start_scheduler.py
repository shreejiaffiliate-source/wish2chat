from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.core.management import call_command
import logging

def send_notification_job():
    """Job to run the notification command"""
    logging.info("Running scheduled notification job...")
    try:
        call_command('send_event_notification')
        logging.info("Notification job completed successfully.")
    except Exception as e:
        logging.error(f"Notification job failed: {e}")

class Command(BaseCommand):
    help = "Starts the APScheduler for daily notifications"

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Add job to run daily at 8 AM
        scheduler.add_job(
            send_notification_job,
            trigger="cron",
            hour=8,  # 8 AM IST
            minute=0,
            id="daily_notification",
            max_instances=1,
            replace_existing=True,
        )

        scheduler.start()
        logging.info("Scheduler started. Daily notifications scheduled at 8 AM.")

        # Keep the scheduler running
        try:
            while True:
                pass  # Infinite loop to keep app running
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            logging.info("Scheduler stopped.")