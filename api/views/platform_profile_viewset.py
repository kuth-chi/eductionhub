""" Platform and PlatformProfile API """

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.serializers.schools.base import PlatformSerializer
from api.serializers.social_platforms.platform_profile_serializers import PlatformProfileSerializer
from schools.models.online_profile import Platform, PlatformProfile


class PlatformViewSet(viewsets.ModelViewSet):
    """Platform API handles list, detail, update and delete methods"""

    queryset = Platform.objects.filter(is_active=True)
    serializer_class = PlatformSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        platform = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(platform)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        platform = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(platform, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        platform = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(platform, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        platform = get_object_or_404(self.get_queryset(), pk=pk)
        platform.delete()
        return Response(
            {"detail": "Platform has been deleted."}, status=status.HTTP_204_NO_CONTENT
        )


class PlatformProfileViewSet(viewsets.ModelViewSet):
    """PlatformProfile API handles list, detail, update and delete methods"""

    queryset = PlatformProfile.objects.filter(is_active=True)
    serializer_class = PlatformProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        queryset = self.get_queryset()

        # Filter by school if provided
        school_id = request.query_params.get("school", None)
        if school_id:
            queryset = queryset.filter(school_id=school_id)

        # Filter by platform if provided
        platform_id = request.query_params.get("platform", None)
        if platform_id:
            queryset = queryset.filter(platform_id=platform_id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        platform_profile = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(platform_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        platform_profile = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(platform_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        platform_profile = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(
            platform_profile, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        platform_profile = get_object_or_404(self.get_queryset(), pk=pk)
        platform_profile.delete()
        return Response(
            {"detail": "Platform Profile has been deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )
