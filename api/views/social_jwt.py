from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from user.models.profile import Profile


class SocialLoginJWTView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        refresh = RefreshToken.for_user(user)

        # Add custom claims to access token
        profile = Profile.objects.get(user=user)
        access_token = refresh.access_token
        access_token["profile"] = {
            "id": profile.uuid,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "photo": profile.photo.url if profile.photo else None,
        }
        access_token["permissions"] = list(user.get_all_permissions())
        access_token["roles"] = [group.name for group in user.groups.all()]

        return Response(
            {
                "refresh": str(refresh),
                "access": str(access_token),
            }
        )
