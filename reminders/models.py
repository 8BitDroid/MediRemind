from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Medicine(models.Model):
    """Represents a medicine schedule for a user."""

    FREQUENCY_CHOICES = [
        ('once', 'Once a day'),
        ('twice', 'Twice a day'),
        ('thrice', 'Three times a day'),
        ('custom', 'Custom times'),
    ]

    MEAL_CHOICES = [
        ('before', 'Before Meal'),
        ('after', 'After Meal'),
        ('with', 'With Meal'),
        ('anytime', 'Anytime'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, help_text='e.g., 500mg, 1 tablet')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once')
    meal_instruction = models.CharField(max_length=20, choices=MEAL_CHOICES, default='after')
    time_slot_1 = models.TimeField(help_text='Morning/First dose time')
    time_slot_2 = models.TimeField(null=True, blank=True, help_text='Afternoon/Second dose time')
    time_slot_3 = models.TimeField(null=True, blank=True, help_text='Evening/Third dose time')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True, help_text='Leave blank for ongoing')
    notes = models.TextField(blank=True, help_text='Any special instructions')
    image = models.ImageField(upload_to='medicines/', null=True, blank=True, help_text='Photo of medicine box or tablet for easy visual reference')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['time_slot_1']
        verbose_name_plural = 'Medicines'

    def __str__(self):
        return f"{self.name} - {self.dosage} ({self.user.username})"

    def get_time_slots(self):
        """Return a list of active time slots for this medicine."""
        slots = [self.time_slot_1]
        if self.time_slot_2:
            slots.append(self.time_slot_2)
        if self.time_slot_3:
            slots.append(self.time_slot_3)
        return slots


class DoseLog(models.Model):
    """Tracks whether a scheduled dose was taken or missed."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('taken', 'Taken'),
        ('missed', 'Missed'),
        ('skipped', 'Skipped'),
    ]

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='dose_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dose_logs')
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    taken_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_date', 'scheduled_time']
        unique_together = ['medicine', 'scheduled_date', 'scheduled_time']

    def __str__(self):
        return f"{self.medicine.name} - {self.scheduled_date} {self.scheduled_time} ({self.status})"
