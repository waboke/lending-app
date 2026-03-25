from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Sum, Q, Avg, Count
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import json
from datetime import datetime, timedelta

from .models1 import (
    LoanApplication, LoanOffer, Loan, Repayment, 
    PaymentSchedule, LoanDocument, Notification
)
from .forms import (
    LoanApplicationForm, LoanOfferForm, RepaymentForm, 
    LoanSearchForm
)

# Helper Functions
def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser

def create_notification(user, notification_type, title, message, link=''):
    """Helper function to create notifications"""
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link
    )

def calculate_amortization_schedule(amount, interest_rate, term_months):
    """Calculate loan amortization schedule"""
    monthly_rate = (interest_rate / 100) / 12
    if monthly_rate == 0:
        monthly_payment = amount / term_months
    else:
        monthly_payment = amount * monthly_rate * (1 + monthly_rate)**term_months / ((1 + monthly_rate)**term_months - 1)
    
    schedule = []
    remaining_balance = amount
    
    for month in range(1, term_months + 1):
        interest = remaining_balance * monthly_rate
        principal = monthly_payment - interest
        remaining_balance -= principal
        
        schedule.append({
            'month': month,
            'payment_due': monthly_payment,
            'principal': principal,
            'interest': interest,
            'remaining_balance': max(remaining_balance, 0)
        })
    
    return monthly_payment, schedule

# Public Views
def home(request):
    """Landing page"""
    return render(request, 'credit/home.html')

def loan_calculator(request):
    """Loan calculator tool"""
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        interest_rate = Decimal(request.POST.get('interest_rate', 0))
        term_months = int(request.POST.get('term_months', 12))
        
        monthly_payment, schedule = calculate_amortization_schedule(
            amount, interest_rate, term_months
        )
        
        total_repayment = monthly_payment * term_months
        total_interest = total_repayment - amount
        
        context = {
            'amount': amount,
            'interest_rate': interest_rate,
            'term_months': term_months,
            'monthly_payment': monthly_payment,
            'total_interest': total_interest,
            'total_repayment': total_repayment,
            'schedule': schedule[:12],  # Show first 12 months
        }
        
        return JsonResponse(context)
    
    return render(request, 'credit/loan_calculator.html')

def eligibility_check(request):
    """Check loan eligibility"""
    if request.method == 'POST':
        monthly_income = Decimal(request.POST.get('monthly_income', 0))
        existing_loans = Decimal(request.POST.get('existing_loans', 0))
        credit_score = int(request.POST.get('credit_score', 0))
        employment_type = request.POST.get('employment_type', '')
        
        eligibility_score = 0
        max_loan_amount = 0
        feedback = []
        
        # Credit score evaluation
        if credit_score >= 750:
            eligibility_score += 40
            feedback.append('✓ Excellent credit score')
        elif credit_score >= 700:
            eligibility_score += 30
            feedback.append('✓ Good credit score')
        elif credit_score >= 650:
            eligibility_score += 20
            feedback.append('✓ Fair credit score')
        else:
            feedback.append('✗ Low credit score may affect eligibility')
        
        # Income evaluation
        if monthly_income >= 5000:
            eligibility_score += 30
            max_loan_amount = monthly_income * 5
            feedback.append('✓ Strong monthly income')
        elif monthly_income >= 3000:
            eligibility_score += 20
            max_loan_amount = monthly_income * 3
            feedback.append('✓ Adequate monthly income')
        elif monthly_income >= 2000:
            eligibility_score += 10
            max_loan_amount = monthly_income * 2
            feedback.append('✓ Minimum income requirement met')
        else:
            feedback.append('✗ Monthly income below minimum requirement')
        
        # Debt-to-income ratio
        dti_ratio = (existing_loans / monthly_income) * 100 if monthly_income > 0 else 0
        if dti_ratio <= 30:
            eligibility_score += 30
            feedback.append('✓ Excellent debt-to-income ratio')
        elif dti_ratio <= 50:
            eligibility_score += 15
            feedback.append('✓ Acceptable debt-to-income ratio')
        else:
            feedback.append('✗ High debt-to-income ratio')
        
        eligible = eligibility_score >= 60
        
        return JsonResponse({
            'eligible': eligible,
            'eligibility_score': eligibility_score,
            'max_loan_amount': max_loan_amount,
            'feedback': feedback,
        })
    
    return render(request, 'credit/eligibility_check.html')

# User Views
@login_required
def dashboard(request):
    """User dashboard"""
    user = request.user
    
    # Active loans
    active_loans = Loan.objects.filter(
        borrower=user,
        status__in=['pending_disbursement', 'active']
    )
    
    # Pending applications
    pending_apps = LoanApplication.objects.filter(
        applicant=user,
        status='pending'
    ).count()
    
    # Recent repayments
    recent_repayments = Repayment.objects.filter(
        loan__borrower=user,
        status='completed'
    ).order_by('-payment_date')[:5]
    
    # Total borrowed
    total_borrowed = active_loans.filter(
        status='active'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    
    # Total repaid
    total_repaid = Repayment.objects.filter(
        loan__borrower=user,
        status='completed'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    
    # Outstanding balance
    outstanding_balance = active_loans.aggregate(
        Sum('remaining_balance')
    )['remaining_balance__sum'] or Decimal('0')
    
    # Upcoming payments
    upcoming_payments = PaymentSchedule.objects.filter(
        loan__borrower=user,
        status='pending',
        due_date__gte=timezone.now()
    ).select_related('loan').order_by('due_date')[:5]
    
    # Recent notifications
    recent_notifications = Notification.objects.filter(
        user=user,
        is_read=False
    ).order_by('-created_at')[:10]
    
    context = {
        'active_loans': active_loans,
        'active_loans_count': active_loans.count(),
        'pending_applications': pending_apps,
        'recent_repayments': recent_repayments,
        'total_borrowed': total_borrowed,
        'total_repaid': total_repaid,
        'outstanding_balance': outstanding_balance,
        'upcoming_payments': upcoming_payments,
        'recent_notifications': recent_notifications,
    }
    
    return render(request, 'credit/dashboard.html', context)

@login_required
def apply_loan(request):
    """Apply for a new loan"""
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            
            # Calculate eligibility score
            eligibility_score = application.calculate_eligibility_score()
            
            if eligibility_score >= 60:
                application.save()
                create_notification(
                    request.user,
                    'application_submitted',
                    'Application Submitted',
                    f'Your loan application #{application.application_id} has been submitted successfully.',
                    f'/credit/application/{application.id}/'
                )
                messages.success(request, 'Loan application submitted successfully!')
                return redirect('credit:application_detail', application_id=application.id)
            else:
                messages.warning(request, f'Your eligibility score ({eligibility_score}) is below the required minimum. Please review and try again.')
                return redirect('credit:eligibility_check')
    else:
        form = LoanApplicationForm()
    
    return render(request, 'credit/apply_loan.html', {'form': form})

@login_required
def application_list(request):
    """List user's loan applications"""
    applications = LoanApplication.objects.filter(
        applicant=request.user
    ).order_by('-submitted_date')
    
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'credit/application_list.html', {
        'applications': page_obj
    })

@login_required
def application_detail(request, application_id):
    """View loan application details"""
    application = get_object_or_404(
        LoanApplication,
        id=application_id,
        applicant=request.user
    )
    
    # Check if an offer exists
    offer = LoanOffer.objects.filter(application=application).first()
    
    context = {
        'application': application,
        'offer': offer,
        'eligibility_score': application.calculate_eligibility_score(),
    }
    
    return render(request, 'credit/application_detail.html', context)

@login_required
def accept_offer(request, offer_id):
    """Accept a loan offer"""
    offer = get_object_or_404(
        LoanOffer,
        id=offer_id,
        application__applicant=request.user,
        status='pending'
    )
    
    if offer.is_expired():
        offer.status = 'expired'
        offer.save()
        messages.error(request, 'This offer has expired.')
        return redirect('credit:dashboard')
    
    with transaction.atomic():
        # Create the loan
        loan = Loan.objects.create(
            offer=offer,
            borrower=request.user,
            amount=offer.approved_amount,
            interest_rate=offer.approved_interest_rate,
            term_months=offer.term_months,
            monthly_payment=offer.monthly_payment,
            remaining_balance=offer.approved_amount,
            status='pending_disbursement'
        )
        
        # Generate payment schedule
        monthly_payment, schedule = calculate_amortization_schedule(
            offer.approved_amount,
            offer.approved_interest_rate,
            offer.term_months
        )
        
        for payment in schedule:
            PaymentSchedule.objects.create(
                loan=loan,
                due_date=timezone.now() + timedelta(days=30 * payment['month']),
                amount_due=payment['payment_due'],
                principal_amount=payment['principal'],
                interest_amount=payment['interest'],
                remaining_balance=payment['remaining_balance'],
                status='pending'
            )
        
        # Update offer
        offer.status = 'accepted'
        offer.accepted_at = timezone.now()
        offer.save()
        
        create_notification(
            request.user,
            'offer_received',
            'Offer Accepted',
            f'You have accepted the loan offer #{offer.offer_id}. Awaiting disbursement.',
            f'/credit/loan/{loan.id}/'
        )
        
        messages.success(request, 'Offer accepted! Your loan is being processed.')
    
    return redirect('credit:loan_detail', loan_id=loan.id)

@login_required
def active_loans(request):
    """List active loans"""
    loans = Loan.objects.filter(
        borrower=request.user
    ).exclude(
        status='paid'
    ).order_by('-created_at')
    
    context = {
        'loans': loans,
        'total_outstanding': loans.aggregate(
            Sum('remaining_balance')
        )['remaining_balance__sum'] or Decimal('0'),
        'total_loans': loans.count(),
    }
    
    return render(request, 'credit/active_loans.html', context)

@login_required
def loan_detail(request, loan_id):
    """View loan details"""
    loan = get_object_or_404(
        Loan,
        id=loan_id,
        borrower=request.user
    )
    
    repayments = Repayment.objects.filter(
        loan=loan,
        status='completed'
    ).order_by('-payment_date')
    
    payment_schedule = PaymentSchedule.objects.filter(
        loan=loan
    ).order_by('due_date')
    
    # Calculate statistics
    total_paid = repayments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    total_interest_paid = payment_schedule.filter(
        status='paid'
    ).aggregate(Sum('interest_amount'))['interest_amount__sum'] or Decimal('0')
    next_payment = payment_schedule.filter(
        status='pending',
        due_date__gte=timezone.now()
    ).order_by('due_date').first()
    
    context = {
        'loan': loan,
        'repayments': repayments,
        'payment_schedule': payment_schedule,
        'total_paid': total_paid,
        'total_interest_paid': total_interest_paid,
        'next_payment': next_payment,
        'progress_percentage': float((total_paid / loan.amount) * 100) if loan.amount > 0 else 0,
    }
    
    return render(request, 'credit/loan_detail.html', context)

@login_required
@require_http_methods(['POST'])
def make_repayment(request, loan_id):
    """Make a repayment on a loan"""
    loan = get_object_or_404(
        Loan,
        id=loan_id,
        borrower=request.user
    )
    
    amount = Decimal(request.POST.get('amount', 0))
    
    if amount <= 0:
        messages.error(request, 'Invalid repayment amount.')
        return redirect('credit:loan_detail', loan_id=loan.id)
    
    if amount > loan.remaining_balance:
        messages.error(request, f'Amount exceeds remaining balance of ${loan.remaining_balance:.2f}')
        return redirect('credit:loan_detail', loan_id=loan.id)
    
    with transaction.atomic():
        # Create repayment record
        repayment = Repayment.objects.create(
            loan=loan,
            amount=amount,
            payment_date=timezone.now(),
            payment_method=request.POST.get('payment_method', 'bank_transfer'),
            reference_number=request.POST.get('reference_number', ''),
            status='completed',
            notes=request.POST.get('notes', '')
        )
        
        # Update payment schedule
        remaining_to_allocate = amount
        pending_payments = PaymentSchedule.objects.filter(
            loan=loan,
            status='pending'
        ).order_by('due_date')
        
        for payment in pending_payments:
            if remaining_to_allocate <= 0:
                break
            
            if remaining_to_allocate >= payment.amount_due:
                # Pay full installment
                payment.status = 'paid'
                payment.payment = repayment
                remaining_to_allocate -= payment.amount_due
            else:
                # Partial payment - create a new schedule for remaining
                payment.amount_due -= remaining_to_allocate
                remaining_to_allocate = 0
            
            payment.save()
        
        # Update loan balance
        loan.remaining_balance = loan.calculate_remaining_balance()
        if loan.remaining_balance <= 0:
            loan.status = 'paid'
            loan.save()
        else:
            loan.save()
        
        create_notification(
            request.user,
            'payment_received',
            'Payment Received',
            f'Payment of ${amount:.2f} received for loan #{loan.loan_id}',
            f'/credit/loan/{loan.id}/'
        )
        
        messages.success(request, f'Repayment of ${amount:.2f} processed successfully!')
    
    return redirect('credit:loan_detail', loan_id=loan.id)

@login_required
def repayment_history(request):
    """View repayment history"""
    repayments = Repayment.objects.filter(
        loan__borrower=request.user
    ).order_by('-payment_date')
    
    paginator = Paginator(repayments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'repayments': page_obj,
        'total_repayments': repayments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0'),
        'total_count': repayments.count(),
    }
    
    return render(request, 'credit/repayment_history.html', context)

@login_required
def notifications(request):
    """View user notifications"""
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    if request.method == 'POST':
        # Mark all as read
        notifications.filter(is_read=False).update(is_read=True)
        return redirect('credit:notifications')
    
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'credit/notifications.html', {
        'notifications': page_obj,
        'unread_count': notifications.filter(is_read=False).count(),
    })

@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.is_read = True
    notification.save()
    
    if notification.link:
        return redirect(notification.link)
    return redirect('credit:notifications')

# Admin Views
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with analytics"""
    # Overview statistics
    total_applications = LoanApplication.objects.count()
    pending_applications = LoanApplication.objects.filter(status='pending').count()
    total_loans = Loan.objects.count()
    active_loans = Loan.objects.filter(status='active').count()
    total_disbursed = Loan.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    total_repayments = Repayment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    
    # Recent applications
    recent_applications = LoanApplication.objects.order_by('-submitted_date')[:10]
    
    # Defaulted loans
    defaulted_loans = Loan.objects.filter(status='defaulted').count()
    
    # Average loan amount
    avg_loan_amount = Loan.objects.aggregate(Avg('amount'))['amount__avg'] or 0
    
    context = {
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'total_loans': total_loans,
        'active_loans': active_loans,
        'total_disbursed': total_disbursed,
        'total_repayments': total_repayments,
        'defaulted_loans': defaulted_loans,
        'avg_loan_amount': avg_loan_amount,
        'recent_applications': recent_applications,
    }
    
    return render(request, 'credit/admin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def review_applications(request):
    """Review pending loan applications"""
    applications = LoanApplication.objects.filter(
        status='pending'
    ).order_by('-submitted_date')
    
    search_form = LoanSearchForm(request.GET)
    
    if search_form.is_valid():
        if search_form.cleaned_data.get('search_term'):
            applications = applications.filter(
                Q(application_id__icontains=search_form.cleaned_data['search_term']) |
                Q(applicant__username__icontains=search_form.cleaned_data['search_term']) |
                Q(applicant__email__icontains=search_form.cleaned_data['search_term'])
            )
        
        if search_form.cleaned_data.get('date_from'):
            applications = applications.filter(
                submitted_date__gte=search_form.cleaned_data['date_from']
            )
        
        if search_form.cleaned_data.get('date_to'):
            applications = applications.filter(
                submitted_date__lte=search_form.cleaned_data['date_to']
            )
        
        if search_form.cleaned_data.get('min_amount'):
            applications = applications.filter(
                amount__gte=search_form.cleaned_data['min_amount']
            )
        
        if search_form.cleaned_data.get('max_amount'):
            applications = applications.filter(
                amount__lte=search_form.cleaned_data['max_amount']
            )
    
    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'credit/admin/review_applications.html', {
        'applications': page_obj,
        'search_form': search_form,
    })

@login_required
@user_passes_test(is_admin)
@require_http_methods(['POST'])
def review_application_action(request, application_id):
    """Approve or reject loan application"""
    application = get_object_or_404(
        LoanApplication,
        id=application_id,
        status='pending'
    )
    
    action = request.POST.get('action')
    
    if action == 'approve':
        # Create loan offer
        approved_amount = Decimal(request.POST.get('approved_amount', application.amount))
        approved_rate = Decimal(request.POST.get('approved_interest_rate', application.interest_rate))
        term_months = int(request.POST.get('term_months', application.term_months))
        valid_days = int(request.POST.get('valid_days', 7))
        
        # Calculate monthly payment
        monthly_payment, _ = calculate_amortization_schedule(
            approved_amount, approved_rate, term_months
        )
        
        total_repayment = monthly_payment * term_months
        processing_fee = Decimal(request.POST.get('processing_fee', 0))
        net_disbursement = approved_amount - processing_fee
        
        offer = LoanOffer.objects.create(
            application=application,
            approved_amount=approved_amount,
            approved_interest_rate=approved_rate,
            term_months=term_months,
            monthly_payment=monthly_payment,
            total_repayment=total_repayment,
            processing_fee=processing_fee,
            net_disbursement=net_disbursement,
            valid_until=timezone.now() + timedelta(days=valid_days),
            status='pending'
        )
        
        application.status = 'approved'
        application.reviewed_date = timezone.now()
        application.reviewed_by = request.user
        application.save()
        
        create_notification(
            application.applicant,
            'application_reviewed',
            'Application Approved',
            f'Your loan application #{application.application_id} has been approved! Check your offers.',
            f'/credit/application/{application.id}/'
        )
        
        messages.success(request, 'Application approved and offer created.')
        
    elif action == 'reject':
        rejection_reason = request.POST.get('rejection_reason', '')
        
        application.status = 'rejected'
        application.rejection_reason = rejection_reason
        application.reviewed_date = timezone.now()
        application.reviewed_by = request.user
        application.save()
        
        create_notification(
            application.applicant,
            'application_reviewed',
            'Application Rejected',
            f'Your loan application #{application.application_id} was rejected. Reason: {rejection_reason}'
        )
        
        messages.warning(request, 'Application rejected.')
    
    return redirect('credit:review_applications')

@login_required
@user_passes_test(is_admin)
def all_loans(request):
    """View all loans"""
    loans = Loan.objects.all().order_by('-created_at')
    
    search_form = LoanSearchForm(request.GET)
    
    if search_form.is_valid():
        if search_form.cleaned_data.get('search_term'):
            loans = loans.filter(
                Q(loan_id__icontains=search_form.cleaned_data['search_term']) |
                Q(borrower__username__icontains=search_form.cleaned_data['search_term']) |
                Q(borrower__email__icontains=search_form.cleaned_data['search_term'])
            )
        
        if search_form.cleaned_data.get('status'):
            loans = loans.filter(status=search_form.cleaned_data['status'])
        
        if search_form.cleaned_data.get('min_amount'):
            loans = loans.filter(amount__gte=search_form.cleaned_data['min_amount'])
        
        if search_form.cleaned_data.get('max_amount'):
            loans = loans.filter(amount__lte=search_form.cleaned_data['max_amount'])
    
    paginator = Paginator(loans, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'credit/admin/all_loans.html', {
        'loans': page_obj,
        'search_form': search_form,
    })

@login_required
@user_passes_test(is_admin)
def disburse_loan(request, loan_id):
    """Disburse loan funds"""
    loan = get_object_or_404(
        Loan,
        id=loan_id,
        status='pending_disbursement'
    )
    
    if request.method == 'POST':
        with transaction.atomic():
            loan.status = 'active'
            loan.disbursement_date = timezone.now()
            loan.next_payment_date = timezone.now() + timedelta(days=30)
            loan.save()
            
            create_notification(
                loan.borrower,
                'loan_disbursed',
                'Loan Disbursed',
                f'Your loan #{loan.loan_id} has been disbursed. First payment due on {loan.next_payment_date.strftime("%Y-%m-%d")}',
                f'/credit/loan/{loan.id}/'
            )
            
            messages.success(request, f'Loan #{loan.loan_id} has been disbursed.')
            return redirect('credit:all_loans')
    
    return render(request, 'credit/admin/disburse_loan.html', {'loan': loan})