from rest_framework.response import Response
from rest_framework.request import Request
from functools import wraps, partial
from rest_framework import status
from .models import UserRole

def requires_role(func, role: UserRole):
    
    @wraps(func)
    def __inner(request: Request, *args, **kwargs):
        if request.user.role == role:
            return func(request, *args, **kwargs)
        else:
            return Response({"details": f"Only {role}s Allowed"}, status=status.HTTP_403_FORBIDDEN)
        
    return __inner

require_technical = partial(requires_role, role=UserRole.TECHNICAL)
require_organizer = partial(requires_role, role=UserRole.ORGANIZER)
require_member = partial(requires_role, role=UserRole.MEMBER)
