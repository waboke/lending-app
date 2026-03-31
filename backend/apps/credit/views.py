from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CreditAssessment
from .serializers import CreditAssessmentSerializer
from .services import evaluate_credit


class CreditEvaluateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = evaluate_credit(request.user)
        return Response({
            'score': result.score,
            'decision': result.decision,
            'max_loan': str(result.max_loan_amount),
            'reason': result.reason,
        })


class CreditLatestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assessment = CreditAssessment.objects.filter(user=request.user).order_by('-created_at').first()
        if not assessment:
            return Response({'detail': 'No assessment found'}, status=404)
        return Response(CreditAssessmentSerializer(assessment).data)
