"""ViewSets for schools-related models (College, Major, Degree, etc.)"""

from django.apps import apps
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.serializers.schools.base import (AddressSerializer,
                                          FieldOfStudySerializer,
                                          ScholarshipSerializer,
                                          ScholarshipTypeSerializer,
                                          SchoolBranchContactInfoSerializer,
                                          SchoolCollegeAssociationSerializer,
                                          SchoolCustomizeButtonSerializer,
                                          SchoolDegreeOfferingSerializer,
                                          SchoolMajorOfferingSerializer,
                                          SchoolScholarshipSerializer)
from api.serializers.schools.branch_serializers import SchoolBranchSerializer

EducationalLevel = apps.get_model("schools", "EducationalLevel")
Major = apps.get_model("schools", "Major")
College = apps.get_model("schools", "College")
EducationDegree = apps.get_model("schools", "EducationDegree")
SchoolBranch = apps.get_model("schools", "SchoolBranch")
SchoolDegreeOffering = apps.get_model("schools", "SchoolDegreeOffering")
SchoolCollegeAssociation = apps.get_model(
    "schools", "SchoolCollegeAssociation")
SchoolMajorOffering = apps.get_model("schools", "SchoolMajorOffering")
FieldOfStudy = apps.get_model("schools", "FieldOfStudy")
ScholarshipType = apps.get_model("schools", "ScholarshipType")
Scholarship = apps.get_model("schools", "Scholarship")
SchoolScholarship = apps.get_model("schools", "SchoolScholarship")
SchoolCustomizeButton = apps.get_model("schools", "SchoolCustomizeButton")
Address = apps.get_model("schools", "Address")
SchoolBranchContactInfo = apps.get_model("schools", "SchoolBranchContactInfo")


class SchoolDegreeOfferingViewSet(viewsets.ModelViewSet):
    queryset = SchoolDegreeOffering.objects.all()
    serializer_class = SchoolDegreeOfferingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SchoolCollegeAssociationViewSet(viewsets.ModelViewSet):
    queryset = SchoolCollegeAssociation.objects.all()
    serializer_class = SchoolCollegeAssociationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SchoolMajorOfferingViewSet(viewsets.ModelViewSet):
    queryset = SchoolMajorOffering.objects.all()
    serializer_class = SchoolMajorOfferingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class FieldOfStudyViewSet(viewsets.ModelViewSet):
    queryset = FieldOfStudy.objects.all()
    serializer_class = FieldOfStudySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ScholarshipTypeViewSet(viewsets.ModelViewSet):
    queryset = ScholarshipType.objects.all()
    serializer_class = ScholarshipTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.all()
    serializer_class = ScholarshipSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SchoolScholarshipViewSet(viewsets.ModelViewSet):
    queryset = SchoolScholarship.objects.all()
    serializer_class = SchoolScholarshipSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SchoolCustomizeButtonViewSet(viewsets.ModelViewSet):
    queryset = SchoolCustomizeButton.objects.all()
    serializer_class = SchoolCustomizeButtonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SchoolBranchContactInfoViewSet(viewsets.ModelViewSet):
    queryset = SchoolBranchContactInfo.objects.all()
    serializer_class = SchoolBranchContactInfoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SchoolBranchViewSet(viewsets.ModelViewSet):
    queryset = SchoolBranch.objects.all()
    serializer_class = SchoolBranchSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
