"""
APScheduler configuration for automated medicine reminders.
This module checks every minute for upcoming doses and marks overdue ones.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.utils import timezone
from datetime import timedelta


def check_and_update_doses():
    """
    Periodic task that:
    1. Auto-marks past pending doses as 'missed' if more than 30 minutes overdue
    2. Could be extended to send notifications
    """
    from reminders.models import DoseLog
    now = timezone.localtime()
    current_time = now.time()
    current_date = now.date()

    # Mark overdue doses as missed (30+ minutes past scheduled time)
    cutoff_time = (now - timedelta(minutes=30)).time()

    overdue_doses = DoseLog.objects.filter(
        scheduled_date=current_date,
        status='pending',
        scheduled_time__lt=cutoff_time,
    )

    for dose in overdue_doses:
        dose.status = 'missed'
        dose.save()


def start():
    """Start the APScheduler background scheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        check_and_update_doses,
        trigger=IntervalTrigger(minutes=5),
        id='check_doses',
        name='Check and update dose statuses',
        replace_existing=True,
    )
    scheduler.start()
