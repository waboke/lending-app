from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

<<<<<<< HEAD
from .models1 import (
    LoanApplication, LoanOffer, Loan, Repayment, 
    PaymentSchedule, LoanDocument, Notification
)
from .forms import (
    LoanApplicationForm, LoanOfferForm, RepaymentForm, 
    LoanSearchForm
)
=======
from .models import CreditScore
from .services import update_credit_score
>>>>>>> rupert_users


class CreditScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        credit = update_credit_score(request.user)

        return Response({
            "score": credit.score,
            "category": credit.category
        })