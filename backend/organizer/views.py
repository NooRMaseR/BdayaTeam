from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from core.permissions import IsOrganizer

from member.serializers import MemberSerializer
from member.models import Member

# Create your views here.

class Members(APIView):
    serializer_class = MemberSerializer
    
    def get_permissions(self):
        perms = super().get_permissions()
        perms.append(IsOrganizer())
        return perms
    
    def get(self, request: Request, track_name: str) -> Response:
        members = Member.objects.select_related("track").filter(track__track__iexact=track_name)
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)
        
