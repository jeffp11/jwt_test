from wsgiref.util import application_uri
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *
    
class TokenView(TokenObtainPairView):
    serializer_class = TokenPairSerializer
    
class ReTokenView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

@api_view(['POST'])
def app_view(request):
    serializer = ApplicationSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    return Response({"msg": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
