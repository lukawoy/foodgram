from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import Response

class CustomPagination(PageNumberPagination):
    # def get_paginated_response(self, data):
    #     return Response({
    #         'count': self.page.paginator.count,
    #         'response': data
    #     })
    page_size_query_param = 'limit'