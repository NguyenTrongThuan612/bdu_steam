from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from steam_api.const.score_criteria import SCORE_CRITERIA

class EvaluationCriteriaView(APIView):
    def get(self, request):
        return Response(SCORE_CRITERIA, status=status.HTTP_200_OK) 