""" Administrator App / Utility """
from django.urls import reverse


def get_base_breadcrumbs():
    """
        Return the base breadcrumbs (e.g., Home).
    """

    return [{'name': 'Dashboard', 'url': reverse('administrator:dashboard')}]


def generate_breadcrumbs(base_breadcrumbs, *new_breadcrumbs):
    """
    Generate breadcrumbs by appending new crumbs to the base breadcrumbs.

    :param base_breadcrumbs: List of base breadcrumb items
    :param new_crumbs: Variable number of dictionaries representing breadcrumb items
    :return: List of breadcrumbs
    """

    breadcrumbs = base_breadcrumbs.copy()
    breadcrumbs.extend(new_breadcrumbs)
    return breadcrumbs
