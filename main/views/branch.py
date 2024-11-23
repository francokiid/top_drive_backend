from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from ..models import Branch
from ..serializers import BranchSerializer


class BranchList(generics.ListCreateAPIView):
    queryset = Branch.objects.exclude(status='Archived')
    serializer_class = BranchSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['status']
    search_fields = ['branch_name', 'branch_address', 'status']
    ordering_fields = '__all__'
    ordering = 'branch_name'

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BranchDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.exclude(status='Archived')
    serializer_class = BranchSerializer
    lookup_field = 'branch_name'


class ValidBranchList(generics.ListCreateAPIView):
    queryset = Branch.objects.exclude(status__in=['Archived', 'Closed'])
    serializer_class = BranchSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['status']
    search_fields = ['branch_name', 'branch_address', 'status']
    ordering_fields = '__all__'
    ordering = 'branch_name'

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
