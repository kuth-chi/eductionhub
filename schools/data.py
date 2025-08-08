
from django.http import JsonResponse
from django.views import View
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from schools.models.school import School, SchoolType


def get_school_type_api(request):
    data = list(SchoolType.objects.all().values('__all__'))

    return JsonResponse(data, safe=False)


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, School):
            return str(obj)
        return super().default(obj)

def get_schools_list_data(request):
    data = serialize("json", School.objects.all(), cls=LazyEncoder)
    return data