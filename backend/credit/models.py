from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid

class LoanApplication(models.Model):
    """Model for loan applications"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    LOAN_TYPE_CHOICES = [
        ('personal', 'Personal Loan'),
        ('business', 'Business Loan'),
        ('education', 'Education Loan'),
        ('home', 'Home Loan'),
        ('auto', 'Auto Loan'),
    ]
    
    application_id = models.CharField(max_length=20, unique=True, editable=False)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    term_months = models.IntegerField(help_text="Loan term in months")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    purpose = models.TextField()
    employment_status = models.CharField(max_length=50)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2)
    existing_loans = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit_score = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_date = models.DateTimeField(auto_now_add=True)
    reviewed_date = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    rejection_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-submitted_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['applicant', 'status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.application_id:
            self.application_id = f"APP-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.application_id} - {self.applicant.username}"
    
    def calculate_eligibility_score(self):
        """Calculate eligibility score based on various factors"""
        score = 0
        # Credit score contribution
        if self.credit_score:
            if self.credit_score >= 750:
                score += 40
            elif self.credit_score >= 700:
                score += 30
            elif self.credit_score >= 650:
                score += 20
            else:
                score += 10
        
        # Income to loan ratio
        income_to_loan = (self.annual_income / 12) / self.amount
        if income_to_loan >= 0.5:
            score += 30
        elif income_to_loan >= 0.3:
            score += 20
        else:
            score += 10
        
        # Employment stability
        if self.employment_status in ['full_time', 'self_employed']:
            score += 30
        elif self.employment_status == 'part_time':
            score += 15
        else:
            score += 5
        
        return min(score, 100)

class LoanOffer(models.Model):
    """Model for loan offers after approval"""
    OFFER_STATUS = [
        ('pending', 'Pending Acceptance'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE, related_name='offer')
    offer_id = models.CharField(max_length=20, unique=True, editable=False)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2)
    approved_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.IntegerField()
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    total_repayment = models.DecimalField(max_digits=12, decimal_places=2)
    processing_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    net_disbursement = models.DecimalField(max_digits=12, decimal_places=2)
    valid_until = models.DateTimeField()
    status = models.CharField(max_length=20, choices=OFFER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.offer_id:
            self.offer_id = f"OFF-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.offer_id} - {self.application.application_id}"
    
    def is_expired(self):
        return timezone.now() > self.valid_until and self.status == 'pending'

class Loan(models.Model):
    """Model for active loans"""
    LOAN_STATUS = [
        ('pending_disbursement', 'Pending Disbursement'),
        ('active', 'Active'),
        ('paid', 'Paid'),
        ('defaulted', 'Defaulted'),
        ('written_off', 'Written Off'),
    ]
    
    loan_id = models.CharField(max_length=20, unique=True, editable=False)
    offer = models.OneToOneField(LoanOffer, on_delete=models.CASCADE, related_name='loan')
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.IntegerField()
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2)
    disbursement_date = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=LOAN_STATUS, default='pending_disbursement')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['borrower', 'status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.loan_id:
            self.loan_id = f"LN-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.loan_id} - {self.borrower.username}"
    
    def calculate_remaining_balance(self):
        """Calculate remaining balance based on repayments"""
        total_paid = self.repayments.filter(status='completed').aggregate(
            models.Sum('amount')
        )['amount__sum'] or Decimal('0')
        return self.amount - total_paid

class Repayment(models.Model):
    """Model for loan repayments"""
    PAYMENT_METHODS = [
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Credit/Debit Card'),
        ('cash', 'Cash'),
        ('check', 'Check'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    repayment_id = models.CharField(max_length=20, unique=True, editable=False)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    reference_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['loan', 'status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.repayment_id:
            self.repayment_id = f"REP-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.repayment_id} - {self.amount}"

class PaymentSchedule(models.Model):
    """Model for scheduled loan payments"""
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payment_schedule')
    due_date = models.DateTimeField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('waived', 'Waived'),
    ], default='pending')
    payment = models.OneToOneField(Repayment, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['due_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date', 'status']),
        ]
    
    def __str__(self):
        return f"Schedule for {self.loan.loan_id} - Due: {self.due_date}"

class LoanDocument(models.Model):
    """Model for loan-related documents"""
    DOCUMENT_TYPES = [
        ('id_proof', 'ID Proof'),
        ('income_proof', 'Income Proof'),
        ('employment_proof', 'Employment Proof'),
        ('bank_statement', 'Bank Statement'),
        ('loan_agreement', 'Loan Agreement'),
        ('other', 'Other'),
    ]
    
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='loan_documents/%Y/%m/%d/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.loan.loan_id}"

class Notification(models.Model):
    """Model for user notifications"""
    NOTIFICATION_TYPES = [
        ('application_submitted', 'Application Submitted'),
        ('application_reviewed', 'Application Reviewed'),
        ('offer_received', 'Offer Received'),
        ('loan_disbursed', 'Loan Disbursed'),
        ('payment_reminder', 'Payment Reminder'),
        ('payment_received', 'Payment Received'),
        ('late_payment', 'Late Payment'),
        ('loan_closed', 'Loan Closed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"