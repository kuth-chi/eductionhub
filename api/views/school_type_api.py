""" School Type API """

from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from api.serializers.school_serializers import SchoolTypeSerializer
from schools.models.schoolsModel import SchoolType

class SchoolTypeViewSet(viewsets.ViewSet):
    ''' School Type API handles list, detail, update and delete methods '''
    queryset = SchoolType.objects.all()

    def create(self, request):
        serializer_class = SchoolTypeSerializer(data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            return Response(serializer_class.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        queryset = self.queryset
        serializer_class = SchoolTypeSerializer(queryset, many=True)
        return Response(serializer_class.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        queryset = self.queryset
        school_type = get_object_or_404(queryset, pk=pk)
        serializer_class = SchoolTypeSerializer(school_type)
        return Response(serializer_class.data, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None):
        queryset = self.queryset
        school_type = get_object_or_404(queryset, pk=pk)
        serializer_class = SchoolTypeSerializer(school_type, data=request.data)
        if serializer_class.is_valid():
            serializer_class.save()
            return Response(serializer_class.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def partial_update(self, request, pk=None):
        queryset = self.queryset
        school_type = get_object_or_404(queryset, pk=pk)
        serializer_class = SchoolTypeSerializer(school_type, data=request.data, partial=True)
        if serializer_class.is_valid():
            serializer_class.save()
            return Response(serializer_class.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, pk=None):
        school_type = get_object_or_404(self.queryset, pk=pk)
        school_type.delete()
        return Response({"detail": "School Type has been deleted."}, status=status.HTTP_204_NO_CONTENT)
    