"""
Resume/CV ViewSets for User models
Provides CRUD operations for Experience, Education, Skill, Language, Hobby, Reference, ProfileContact, Attachment, Letter
"""

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers.user.resume import (AttachmentSerializer,
                                         EducationSerializer,
                                         ExperienceSerializer, HobbySerializer,
                                         LanguageSerializer, LetterSerializer,
                                         ProfileContactSerializer,
                                         ReferenceSerializer, SkillSerializer)
from user.models.base import (Attachment, Education, Experience, Hobby,
                              Language, Letter, ProfileContact, Reference,
                              Skill)
from user.models.profile import Profile


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        # For models that have a 'user' field linking to Profile
        if hasattr(obj, "user") and hasattr(obj.user, "user"):
            return obj.user.user == request.user
        return False


class AttachmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing file attachments
    Provides CRUD operations for user file uploads
    """

    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter attachments to show only those used by the current user's resume items"""
        user = self.request.user
        if not hasattr(user, "profile"):
            return Attachment.objects.none()

        profile = user.profile

        # Get all attachments used in user's resume items
        from django.db.models import Q

        return Attachment.objects.filter(
            Q(education__user=profile)
            | Q(experience__user=profile)
            | Q(skill__user=profile)
            | Q(language__user=profile)
            | Q(reference__user=profile)
        ).distinct()


class LetterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user letters/cover letters
    """

    queryset = Letter.objects.all()
    serializer_class = LetterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only the current user's letters"""
        return Letter.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically associate the letter with the current user"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Ensure user can only update their own letters"""
        if serializer.instance.user != self.request.user:
            raise permissions.PermissionDenied(
                "You do not have permission to edit this letter."
            )
        serializer.save()

    def perform_destroy(self, instance):
        """Ensure user can only delete their own letters"""
        if instance.user != self.request.user:
            raise permissions.PermissionDenied(
                "You do not have permission to delete this letter."
            )
        instance.delete()


class ExperienceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing work experience entries
    """

    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Return only the current user's experiences"""
        print(f"ExperienceViewSet.get_queryset: user={self.request.user}, is_authenticated={self.request.user.is_authenticated}")
        print(f"ExperienceViewSet.get_queryset: user={self.request.user}, has_profile={hasattr(self.request.user, 'profile')}")
        if not hasattr(self.request.user, "profile"):
            print("ExperienceViewSet.get_queryset: No profile found, creating one...")
            from user.models.profile import Profile
            profile, created = Profile.objects.get_or_create(user=self.request.user)
            print(f"ExperienceViewSet.get_queryset: Profile created: {created}, profile: {profile}")
        profile = self.request.user.profile
        print(f"ExperienceViewSet.get_queryset: profile={profile}, filtering experiences...")
        queryset = Experience.objects.filter(user=self.request.user.profile)
        print(f"ExperienceViewSet.get_queryset: found {queryset.count()} experiences")
        return queryset

    def perform_create(self, serializer):
        """Automatically associate the experience with the current user's profile"""
        from user.models.profile import Profile
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        print(f"ExperienceViewSet.perform_create: Profile created: {created}, profile: {profile}")
        serializer.save(user=profile)


class EducationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing education history entries
    """

    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Return only the current user's education entries"""
        if not hasattr(self.request.user, "profile"):
            return Education.objects.none()
        return Education.objects.filter(user=self.request.user.profile)

    def perform_create(self, serializer):
        """Automatically associate the education with the current user's profile"""
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer.save(user=profile)


class SkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user skills
    """

    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Return only the current user's skills"""
        if not hasattr(self.request.user, "profile"):
            return Skill.objects.none()
        return Skill.objects.filter(user=self.request.user.profile)

    def perform_create(self, serializer):
        """Automatically associate the skill with the current user's profile"""
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer.save(user=profile)


class LanguageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user languages
    """

    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Return only the current user's languages"""
        if not hasattr(self.request.user, "profile"):
            return Language.objects.none()
        return Language.objects.filter(user=self.request.user.profile)

    def perform_create(self, serializer):
        """Automatically associate the language with the current user's profile"""
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer.save(user=profile)


class HobbyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user hobbies
    """

    queryset = Hobby.objects.all()
    serializer_class = HobbySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Return only the current user's hobbies"""
        if not hasattr(self.request.user, "profile"):
            return Hobby.objects.none()
        return Hobby.objects.filter(user=self.request.user.profile)

    def perform_create(self, serializer):
        """Automatically associate the hobby with the current user's profile"""
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer.save(user=profile)


class ReferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing professional references
    """

    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Return only the current user's references"""
        if not hasattr(self.request.user, "profile"):
            return Reference.objects.none()
        return Reference.objects.filter(user=self.request.user.profile)

    def perform_create(self, serializer):
        """Automatically associate the reference with the current user's profile"""
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer.save(user=profile)


class ProfileContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user contact profiles on various platforms
    """

    queryset = ProfileContact.objects.all()
    serializer_class = ProfileContactSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = "uuid"

    def get_queryset(self):
        """Return only the current user's contact profiles"""
        if not hasattr(self.request.user, "profile"):
            return ProfileContact.objects.none()
        return ProfileContact.objects.filter(profile=self.request.user.profile)

    def perform_create(self, serializer):
        """Automatically associate the contact profile with the current user's profile"""
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer.save(profile=profile)

    @action(detail=False, methods=["get"], url_path="by-platform/(?P<platform_id>[^/.]+)")
    def by_platform(self, request, platform_id=None):
        """
        Get user's contact profile for a specific platform
        """
        if not hasattr(request.user, "profile"):
            return Response(
                {"detail": "User profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        contact = ProfileContact.objects.filter(
            profile=request.user.profile, platform_id=platform_id
        ).first()

        if not contact:
            return Response(
                {"detail": "Contact profile not found for this platform"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(contact)
        return Response(serializer.data)
