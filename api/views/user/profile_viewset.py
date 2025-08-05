# api/views/profiles/views.py
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from user.models.profile import Profile
from api.serializers.user.profile import ProfileSerializer

User = get_user_model()


class ProfileViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Profile instance.
    Provides CRUD operations for Profile objects.
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    # accessible to authenticated users
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the return profiles to the current user's profile
        or allows listing all for admins
        For now, let's allow users to see all profiles, but only modify their own.
        """
        # return Profile.objects.filter(user=self.request.user) # this for only seeing own profile
        return super().get_queryset()  # user can see all profiles

    def perform_create(self, serializer):
        """
        Ensures that when a new profile is created, it's linked to the authenticated user making the request.
        Also, ensures that each user can only have one profile (enforces uniqueness per user, not globally).
        Also, ensure a user can only have one profile.
        """
        if Profile.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError(
                {"detail": "This user already has a profile"}
            )
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Ensure that a user can only update their own profile
        """
        if serializer.instance.user != self.request.user:
            raise permissions.PermissionDenied(
                "You do not have permission to edit this profile."
            )
        serializer.save()

    def perform_destroy(self, instance):
        """
        Ensures that a user can only delete their own profile
        """
        if instance.user != self.request.user:
            raise permissions.PermissionDenied(
                "You do not have permission to delete this profile."
            )
        return super().perform_destroy(instance)

    @action(detail=False, methods=["get"], url_path="my-profile")
    def my_profile(self, request):
        """
        Custom action to retrieve the authenticated user's profile.
        """
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
