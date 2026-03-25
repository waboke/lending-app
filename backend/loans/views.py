from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from credit.services import update_credit_score

from .models import Loan
from .serializers import LoanApplySerializer, LoanSerializer
from notifications.services import create_notification


# Apply for loan
class ApplyLoanView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LoanApplySerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            loan = serializer.save()
            return Response({
                "message": "Loan application submitted",
                "loan_id": loan.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# List user loans
class UserLoansView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        loans = Loan.objects.filter(user=request.user)
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)


# Loan detail
class LoanDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            loan = Loan.objects.get(pk=pk, user=request.user)
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=404)

        serializer = LoanSerializer(loan)
        return Response(serializer.data)
#Admin View
class UpdateLoanStatusView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            loan = Loan.objects.get(pk=pk)
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=404)

        status_value = request.data.get("status")

        if status_value not in ['approved', 'rejected', 'disbursed']:
            return Response({"error": "Invalid status"}, status=400)

        # CREDIT CHECK
        credit = update_credit_score(loan.user)

        if status_value == "approved" and credit.score < 600:
            return Response({
                "error": "Loan cannot be approved. Credit score too low",
                "credit_score": credit.score
            }, status=400)

        loan.status = status_value
        loan.reason = request.data.get("reason", "")
        loan.save()

        # 🔥 CREATE NOTIFICATION
        if status_value == "approved":
            create_notification(
                loan.user,
                "Loan Approved",
                f"Your loan of {loan.amount} has been approved."
            )

        elif status_value == "rejected":
            create_notification(
                loan.user,
                "Loan Rejected",
                f"Your loan was rejected. Reason: {loan.reason}"
            )

        elif status_value == "disbursed":
            create_notification(
                loan.user,
                "Loan Disbursed",
                f"Your loan of {loan.amount} has been disbursed."
            )

        return Response({
            "message": "Loan updated",
            "credit_score": credit.score
        })