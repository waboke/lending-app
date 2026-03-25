from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone
import re

# Import all models you're using in forms
from .models1 import (
    LoanApplication, 
    LoanOffer,      # Add this import
    Loan, 
    Repayment
)

class LoanApplicationForm(forms.ModelForm):
    """Form for submitting loan applications"""
    
    class Meta:
        model = LoanApplication
        fields = [
            'loan_type', 'amount', 'term_months', 'interest_rate',
            'purpose', 'employment_status', 'annual_income',
            'existing_loans', 'credit_score'
        ]
        widgets = {
            'purpose': forms.Textarea(attrs={'rows': 4}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'annual_income': forms.NumberInput(attrs={'step': '0.01'}),
            'existing_loans': forms.NumberInput(attrs={'step': '0.01'}),
            'interest_rate': forms.NumberInput(attrs={'step': '0.01'}),
        }
        labels = {
            'term_months': 'Loan Term (months)',
            'annual_income': 'Annual Income ($)',
            'existing_loans': 'Existing Loan Amount ($)',
        }
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise ValidationError('Loan amount must be greater than zero.')
        if amount and amount > 1000000:
            raise ValidationError('Loan amount cannot exceed $1,000,000.')
        return amount
    
    def clean_term_months(self):
        term = self.cleaned_data.get('term_months')
        if term and term < 3:
            raise ValidationError('Minimum loan term is 3 months.')
        if term and term > 360:
            raise ValidationError('Maximum loan term is 360 months (30 years).')
        return term
    
    def clean_interest_rate(self):
        rate = self.cleaned_data.get('interest_rate')
        if rate and (rate < 0 or rate > 50):
            raise ValidationError('Interest rate must be between 0% and 50%.')
        return rate
    
    def clean_credit_score(self):
        score = self.cleaned_data.get('credit_score')
        if score and (score < 300 or score > 850):
            raise ValidationError('Credit score must be between 300 and 850.')
        return score


class LoanOfferForm(forms.ModelForm):
    """Form for creating loan offers"""
    
    class Meta:
        model = LoanOffer
        fields = [
            'approved_amount', 'approved_interest_rate', 'term_months',
            'processing_fee', 'valid_until'
        ]
        widgets = {
            'valid_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean_approved_amount(self):
        amount = self.cleaned_data.get('approved_amount')
        if amount and amount <= 0:
            raise ValidationError('Approved amount must be greater than zero.')
        return amount
    
    def clean_processing_fee(self):
        fee = self.cleaned_data.get('processing_fee')
        amount = self.cleaned_data.get('approved_amount')
        if fee and amount and fee > amount * Decimal('0.1'):
            raise ValidationError('Processing fee cannot exceed 10% of the loan amount.')
        return fee


class RepaymentForm(forms.ModelForm):
    """Form for making repayments"""
    
    class Meta:
        model = Repayment
        fields = ['amount', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'payment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.loan = kwargs.pop('loan', None)
        super().__init__(*args, **kwargs)
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise ValidationError('Repayment amount must be greater than zero.')
        
        if self.loan and amount > self.loan.remaining_balance:
            raise ValidationError(
                f'Amount exceeds remaining balance of ${self.loan.remaining_balance:.2f}'
            )
        
        return amount


class LoanSearchForm(forms.Form):
    """Form for searching loans"""
    search_term = forms.CharField(required=False, label='Search')
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All')] + Loan.LOAN_STATUS
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    min_amount = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )
    max_amount = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )


class LoanApplicationReviewForm(forms.ModelForm):
    """Form for reviewing loan applications (admin use)"""
    
    class Meta:
        model = LoanApplication
        fields = ['status', 'rejection_reason', 'notes']
        widgets = {
            'rejection_reason': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make rejection reason required only if status is rejected
        self.fields['rejection_reason'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if status == 'rejected' and not rejection_reason:
            raise ValidationError('Rejection reason is required when rejecting an application.')
        
        return cleaned_data


class LoanDisbursementForm(forms.Form):
    """Form for loan disbursement"""
    disbursement_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True
    )
    reference_number = forms.CharField(max_length=100, required=True)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    def clean_disbursement_date(self):
        date = self.cleaned_data.get('disbursement_date')
        if date and date < timezone.now():
            raise ValidationError('Disbursement date cannot be in the past.')
        return date


class LoanCalculatorForm(forms.Form):
    """Form for loan calculator"""
    amount = forms.DecimalField(
        min_value=100,
        max_value=1000000,
        widget=forms.NumberInput(attrs={'step': '100'}),
        label='Loan Amount ($)'
    )
    interest_rate = forms.DecimalField(
        min_value=0,
        max_value=50,
        widget=forms.NumberInput(attrs={'step': '0.1'}),
        label='Annual Interest Rate (%)'
    )
    term_months = forms.IntegerField(
        min_value=1,
        max_value=360,
        widget=forms.NumberInput(),
        label='Loan Term (months)'
    )


class EligibilityCheckForm(forms.Form):
    """Form for eligibility check"""
    monthly_income = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '100'}),
        label='Monthly Income ($)'
    )
    existing_loans = forms.DecimalField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'step': '100'}),
        label='Existing Loan Payments ($)',
        help_text='Total monthly payments for existing loans'
    )
    credit_score = forms.IntegerField(
        min_value=300,
        max_value=850,
        widget=forms.NumberInput(),
        label='Credit Score'
    )
    employment_type = forms.ChoiceField(
        choices=[
            ('full_time', 'Full Time Employee'),
            ('part_time', 'Part Time Employee'),
            ('self_employed', 'Self Employed'),
            ('unemployed', 'Unemployed'),
            ('retired', 'Retired'),
        ],
        label='Employment Type'
    )
    employment_duration = forms.IntegerField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(),
        label='Years at Current Job',
        help_text='Number of years in current employment'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        monthly_income = cleaned_data.get('monthly_income', 0)
        existing_loans = cleaned_data.get('existing_loans', 0)
        
        if monthly_income and existing_loans and existing_loans > monthly_income * 0.5:
            raise ValidationError(
                'Your existing loan payments exceed 50% of your monthly income.'
            )
        
        return cleaned_data


class DocumentUploadForm(forms.Form):
    """Form for uploading loan documents"""
    document_type = forms.ChoiceField(
        choices=[
            ('id_proof', 'ID Proof'),
            ('income_proof', 'Income Proof'),
            ('employment_proof', 'Employment Proof'),
            ('bank_statement', 'Bank Statement'),
            ('other', 'Other'),
        ]
    )
    title = forms.CharField(max_length=200)
    file = forms.FileField()
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )