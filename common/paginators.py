from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ForumPagination(PageNumberPagination):
    template = None
    page_query_param = 'page'
    page_size_query_param = None

    def get_paginated_response(self, data):
        return Response(OrderedDict({
            'data': data,
            'pagination': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            }
        }))
