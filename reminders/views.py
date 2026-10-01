import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from datetime import date, datetime, timedelta
from .models import Medicine, DoseLog
from .forms import UserRegistrationForm, MedicineForm



def landing_page(request):
    """Public landing page for the application."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'reminders/landing.html')


def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = UserRegistrationForm()

    return render(request, 'reminders/register.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'reminders/login.html')


def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('landing')


def _ensure_dose_logs(user, target_date):
    """Create DoseLog entries for all active medicines for a given date if they don't exist."""
    medicines = Medicine.objects.filter(
        user=user,
        is_active=True,
        start_date__lte=target_date,
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=target_date)
    )

    for medicine in medicines:
        for time_slot in medicine.get_time_slots():
            DoseLog.objects.get_or_create(
                medicine=medicine,
                user=user,
                scheduled_date=target_date,
                scheduled_time=time_slot,
                defaults={'status': 'pending'}
            )


@login_required
def dashboard_view(request):
    """Main dashboard showing today's medicine schedule."""
    today = date.today()
    _ensure_dose_logs(request.user, today)

    # Get today's dose logs
    todays_doses = DoseLog.objects.filter(
        user=request.user,
        scheduled_date=today
    ).select_related('medicine').order_by('scheduled_time')

    # Stats
    total_today = todays_doses.count()
    taken_today = todays_doses.filter(status='taken').count()
    missed_today = todays_doses.filter(status='missed').count()
    pending_today = todays_doses.filter(status='pending').count()

    # Upcoming doses (pending, sorted by time)
    now = timezone.localtime().time()
    upcoming = todays_doses.filter(status='pending', scheduled_time__gte=now)
    past_pending = todays_doses.filter(status='pending', scheduled_time__lt=now)

    # Active medicines count
    active_medicines = Medicine.objects.filter(user=request.user, is_active=True).count()

    # Adherence rate (last 7 days)
    week_ago = today - timedelta(days=7)
    week_logs = DoseLog.objects.filter(
        user=request.user,
        scheduled_date__gte=week_ago,
        scheduled_date__lt=today,
    )
    week_total = week_logs.count()
    week_taken = week_logs.filter(status='taken').count()
    adherence_rate = round((week_taken / week_total) * 100) if week_total > 0 else 100

    context = {
        'todays_doses': todays_doses,
        'total_today': total_today,
        'taken_today': taken_today,
        'missed_today': missed_today,
        'pending_today': pending_today,
        'upcoming': upcoming,
        'past_pending': past_pending,
        'active_medicines': active_medicines,
        'adherence_rate': adherence_rate,
        'today': today,
        'now': now,
    }
    return render(request, 'reminders/dashboard.html', context)


@login_required
def mark_dose(request, dose_id, status):
    """Mark a dose as taken, missed, or skipped."""
    dose = get_object_or_404(DoseLog, id=dose_id, user=request.user)

    if status in ['taken', 'missed', 'skipped']:
        dose.status = status
        if status == 'taken':
            dose.taken_at = timezone.now()
        dose.save()

        status_messages = {
            'taken': f'✅ {dose.medicine.name} marked as taken!',
            'missed': f'❌ {dose.medicine.name} marked as missed.',
            'skipped': f'⏭️ {dose.medicine.name} skipped.',
        }
        messages.success(request, status_messages.get(status, 'Dose updated.'))

    return redirect('dashboard')


@login_required
def medicine_list(request):
    """List all medicines for the current user."""
    medicines = Medicine.objects.filter(user=request.user).order_by('-is_active', 'name')
    return render(request, 'reminders/medicine_list.html', {'medicines': medicines})


@login_required
def medicine_add(request):
    """Add a new medicine schedule."""
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.user = request.user
            medicine.save()
            messages.success(request, f'💊 {medicine.name} has been added to your schedule!')
            return redirect('medicine_list')
        else:
            messages.error(request, 'Please correct the errors in the form below.')
    else:
        form = MedicineForm()

    return render(request, 'reminders/medicine_form.html', {
        'form': form,
        'title': 'Add New Medicine',
        'button_text': 'Add Medicine',
    })


@login_required
def medicine_edit(request, pk):
    """Edit an existing medicine schedule."""
    medicine = get_object_or_404(Medicine, pk=pk, user=request.user)

    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, f'💊 {medicine.name} has been updated!')
            return redirect('medicine_list')
        else:
            messages.error(request, 'Please correct the errors in the form below.')
    else:
        form = MedicineForm(instance=medicine)

    return render(request, 'reminders/medicine_form.html', {
        'form': form,
        'title': f'Edit {medicine.name}',
        'button_text': 'Save Changes',
        'medicine': medicine,
    })




@login_required
def medicine_delete(request, pk):
    """Delete a medicine schedule."""
    medicine = get_object_or_404(Medicine, pk=pk, user=request.user)

    if request.method == 'POST':
        name = medicine.name
        medicine.delete()
        messages.success(request, f'🗑️ {name} has been removed from your schedule.')
        return redirect('medicine_list')

    return render(request, 'reminders/medicine_confirm_delete.html', {
        'medicine': medicine,
    })


@login_required
def history_view(request):
    """View medicine history / dose log report."""
    # Get filter params
    days_filter = request.GET.get('days', '7')
    medicine_filter = request.GET.get('medicine', 'all')
    status_filter = request.GET.get('status', 'all')

    try:
        days = int(days_filter)
    except ValueError:
        days = 7

    start_date = date.today() - timedelta(days=days)

    # Base query
    logs = DoseLog.objects.filter(
        user=request.user,
        scheduled_date__gte=start_date,
    ).select_related('medicine').order_by('-scheduled_date', 'scheduled_time')

    if medicine_filter != 'all':
        try:
            logs = logs.filter(medicine_id=int(medicine_filter))
        except ValueError:
            pass

    if status_filter != 'all':
        logs = logs.filter(status=status_filter)

    # Stats for the period
    total_logs = logs.count()
    taken_count = logs.filter(status='taken').count()
    missed_count = logs.filter(status='missed').count()
    pending_count = logs.filter(status='pending').count()
    adherence = round((taken_count / total_logs) * 100) if total_logs > 0 else 0

    # Daily breakdown for chart
    daily_data = []
    for i in range(days, -1, -1):
        d = date.today() - timedelta(days=i)
        day_logs = DoseLog.objects.filter(user=request.user, scheduled_date=d)
        day_total = day_logs.count()
        day_taken = day_logs.filter(status='taken').count()
        daily_data.append({
            'date': d.strftime('%b %d'),
            'taken': day_taken,
            'total': day_total,
            'rate': round((day_taken / day_total) * 100) if day_total > 0 else 0,
        })

    # User's medicines for filter dropdown
    user_medicines = Medicine.objects.filter(user=request.user)

    context = {
        'logs': logs,
        'total_logs': total_logs,
        'taken_count': taken_count,
        'missed_count': missed_count,
        'pending_count': pending_count,
        'adherence': adherence,
        'daily_data': daily_data,
        'user_medicines': user_medicines,
        'days_filter': days_filter,
        'medicine_filter': medicine_filter,
        'status_filter': status_filter,
    }
    return render(request, 'reminders/history.html', context)


@login_required
def profile_view(request):
    """User profile page."""
    user = request.user
    total_medicines = Medicine.objects.filter(user=user).count()
    active_medicines = Medicine.objects.filter(user=user, is_active=True).count()

    # All-time stats
    total_doses = DoseLog.objects.filter(user=user).count()
    taken_doses = DoseLog.objects.filter(user=user, status='taken').count()
    missed_doses = DoseLog.objects.filter(user=user, status='missed').count()
    overall_adherence = round((taken_doses / total_doses) * 100) if total_doses > 0 else 0

    context = {
        'total_medicines': total_medicines,
        'active_medicines': active_medicines,
        'total_doses': total_doses,
        'taken_doses': taken_doses,
        'missed_doses': missed_doses,
        'overall_adherence': overall_adherence,
    }
    return render(request, 'reminders/profile.html', context)


@login_required
def export_history_csv(request):
    """Export dose log history as downloadable CSV file."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="medicine_history_{date.today()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Scheduled Date', 'Scheduled Time', 'Medicine Name', 'Dosage', 'Status', 'Recorded Timestamp', 'Instructions'])

    logs = DoseLog.objects.filter(user=request.user).select_related('medicine').order_by('-scheduled_date', 'scheduled_time')

    for log in logs:
        writer.writerow([
            log.scheduled_date.strftime('%Y-%m-%d'),
            log.scheduled_time.strftime('%H:%M'),
            log.medicine.name,
            log.medicine.dosage,
            log.status.capitalize(),
            log.taken_at.strftime('%Y-%m-%d %H:%M:%S') if log.taken_at else 'N/A',
            log.medicine.notes or 'N/A'
        ])

    return response

