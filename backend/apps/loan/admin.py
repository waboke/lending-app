from django.contrib import admin
from .models import LoanProduct, LoanApplication, Loan, RepaymentSchedule

admin.site.register(LoanProduct)
admin.site.register(LoanApplication)
admin.site.register(Loan)
admin.site.register(RepaymentSchedule)
