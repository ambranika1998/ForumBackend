import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q
from django.http import Http404
from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404, RetrieveAPIView
# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# from rest_framework_simplejwt.authentication import JWTAuthentication

from common.constants import ERRORS, DATA
# from ForumBackend.settings import ACTIVE_AUTHENTICATION, ACTIVE_PERMISSIONS

# authentication_classes = [JWTAuthentication] if ACTIVE_AUTHENTICATION else []
# permission_classes = [IsAuthenticated] if ACTIVE_PERMISSIONS else []

logger = logging.getLogger(__name__)


class ForumListAPIView(ListAPIView):
    queryset = None
    serializer_class = None
    filter_serializer_class = None
    # authentication_classes = authentication_classes
    # permission_classes = [IsAuthenticated] if ACTIVE_PERMISSIONS else []
    filter_map = {}
    queryset_kwargs = {}

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        order_params = self.get_order_param()
        queryset = queryset.order_by(order_params) if order_params else queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({DATA: serializer.data})

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None or len(self.request.GET.keys()) == 0 or self.request.GET.get('page') == 'null':
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def filter_queryset(self, queryset):
        query_str_filter = self.request.GET.get('filter', None)
        exact = False
        if query_str_filter is None:
            query_str_filter = self.request.GET.get('exact', None)
            exact = True
        if query_str_filter:
            filter_data = json.loads(query_str_filter)
            filter_params = self.get_filter_params(filter_data, exact)
            if filter_params:
                return queryset.filter(filter_params).distinct()
            return queryset
        return queryset

    def get_filter_serializer(self, filter_data):
        filter_serializer = self.filter_serializer_class(data=filter_data)
        try:
            filter_serializer.is_valid(raise_exception=True)
        except ValidationError as ve:
            logger.error('Filter Error: {}'.format(ve))
            filter_serializer = None
        finally:
            return filter_serializer

    def get_filter_params(self, filter_data, exact):
        filter_serializer = self.get_filter_serializer(filter_data)
        filter_params = None
        if filter_serializer:
            filter_query = {self.get_filter_key(filter_serializer, k, exact): v for k, v in filter_serializer.validated_data.items() if v or v is False}
            if filter_query:
                filter_params = Q(**filter_query)
        return filter_params

    def get_filter_key(self, filter_serializer, key, exact):
        if not exact and isinstance(filter_serializer.fields[key], serializers.CharField):
            key = self.filter_map.get(key, key)
            return '{}__icontains'.format(key)
        return self.filter_map.get(key, key)

    def get_queryset(self):
        """
        :param self: Model instance.
        :return: A filtered queryset.
        """
        formatted_query_params = {}
        for key, value in self.queryset_kwargs.items():
            item_value = int(self.kwargs[key])
            formatted_query_params[value] = item_value
        try:
            self.queryset = self.queryset.filter(**formatted_query_params).filter(deleted=False)
        except Http404:
            self.queryset = None
        finally:
            return self.queryset

    def get_order_param(self, ):
        query_str_order = self.request.GET.get('order', None)
        query_str_sort = self.request.GET.get('sort', None)
        if query_str_sort and query_str_order:
            if query_str_sort == 'created':
                return None
            else:
                if query_str_order == 'asc':
                    if query_str_sort in self.filter_map.keys():
                        return self.filter_map.get(query_str_sort)
                    else:
                        return query_str_sort
                else:
                    if query_str_sort in self.filter_map.keys():
                        return '-{}'.format(self.filter_map.get(query_str_sort))
                    else:
                        return '-{}'.format(query_str_sort)
        return None


class ForumCreateAPIView(CreateAPIView):
    # authentication_classes = authentication_classes
    # permission_classes = [IsAuthenticated] if ACTIVE_PERMISSIONS else []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        response_data = {}
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        response_headers = None
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            response_data = {DATA: serializer.data}
            response_status = status.HTTP_201_CREATED
            response_headers = headers
        except ValidationError as ve:
            logger.error('Create Error: {}'.format(ve))
            response_data = {ERRORS: ve.get_full_details()}
            response_status = status.HTTP_400_BAD_REQUEST
        except ObjectDoesNotExist as dne:
            logger.error('Object does not exist Error: {}'.format(dne))
            response_data = {ERRORS: '{}'.format(dne)}
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        except IntegrityError as ie:
            logger.error('{}'.format(ie))
            response_data = {ERRORS: 'Duplicate values!'}
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        except Exception as e:
            logger.error('{}'.format(e))
            print('Print2 ' + e)
            response_data = {ERRORS: '{}'.format(e)}
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            return Response(response_data, status=response_status, headers=response_headers)


class ForumListCreateAPIView(ForumCreateAPIView, ForumListAPIView):
    read_serializer_class = None
    write_serializer_class = None
    # authentication_classes = authentication_classes
    # permission_classes = permission_classes
    serializer_error_msg = "'%s' should either include a `serializer_class` attribute, or override the `get_serializer_class()` method."
    queryset = None

    def get_serializer_class(self):
        if self.request.method == 'GET':
            assert self.read_serializer_class is not None or self.serializer_class is not None, (self.serializer_error_msg % self.__class__.__name__)
            return self.read_serializer_class
        if self.request.method == 'POST':
            assert self.write_serializer_class is not None or self.serializer_class is not None, (self.serializer_error_msg % self.__class__.__name__)
            return self.write_serializer_class
        assert self.serializer_class is not None, (self.serializer_error_msg % self.__class__.__name__)
        return self.serializer_class


class PitagoraRetrieveAPIView(RetrieveAPIView):
    """
    Retrieve an object instance.
    """
    queryset = None
    serializer_class = None
    read_serializer_class = None
    queryset_kwargs = {}
    serializer_error_msg = "'%s' should either include a `serializer_class` attribute, or override the `get_serializer_class()` method."

    def get_serializer_class(self):
        assert self.read_serializer_class is not None or self.serializer_class is not None, (self.serializer_error_msg % self.__class__.__name__)
        return self.read_serializer_class

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({DATA: serializer.data})

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        formatted_query_params = {}
        primary_key = 'pk'
        if primary_key not in self.queryset_kwargs.keys():
            self.queryset_kwargs[primary_key] = primary_key
        for key, value in self.queryset_kwargs.items():
            item_value = self.kwargs[key]
            formatted_query_params[value] = item_value

        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        for lookup_url_kwarg in self.queryset_kwargs:
            assert lookup_url_kwarg in self.kwargs, (
                    'Expected view %s to be called with a URL keyword argument '
                    'named "%s". Fix your URL conf, or set the `.lookup_field` '
                    'attribute on the view correctly.' %
                    (self.__class__.__name__, lookup_url_kwarg)
            )

        filter_kwargs = formatted_query_params
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class ForumRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an object instance.
    """
    queryset = None
    serializer_class = None
    read_serializer_class = None
    write_serializer_class = None
    # authentication_classes = authentication_classes
    # permission_classes = permission_classes
    serializer_error_msg = "'%s' should either include a `serializer_class` attribute, or override the `get_serializer_class()` method."
    queryset_kwargs = {}

    def get_serializer_class(self):
        if self.request.method == 'GET':
            assert self.read_serializer_class is not None or self.serializer_class is not None, (self.serializer_error_msg % self.__class__.__name__)
            return self.read_serializer_class
        if self.request.method == 'POST' or self.request.method == 'PUT' or self.request.method == 'PATCH':
            assert self.write_serializer_class is not None or self.serializer_class is not None, (self.serializer_error_msg % self.__class__.__name__)
            return self.write_serializer_class
        assert self.serializer_class is not None, (self.serializer_error_msg % self.__class__.__name__)
        return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({DATA: serializer.data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        response_data = {}
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        response_headers = None
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            # log_change(request.user.id, request, type(self.get_queryset().first()).objects.get(pk=serializer.data.get('id')))
            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            # headers = self.get_success_headers(serializer.data)
            # response_headers = headers
            response_data = {DATA: serializer.data}
            response_status = status.HTTP_200_OK
        except ValidationError as ve:
            logger.error('Update Error: {}'.format(ve))
            response_data = {ERRORS: ve.get_full_details()}
            response_status = status.HTTP_400_BAD_REQUEST
        except ObjectDoesNotExist as dne:
            logger.error('Object does not exist Error: {}'.format(dne))
            response_data = {ERRORS: '{}'.format(dne)}
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        except IntegrityError as ie:
            logger.error('{}'.format(ie))
            response_data = {ERRORS: 'Duplicate values!'}
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        finally:
            return Response(response_data, status=response_status, headers=response_headers)
        # return Response({DATA: serializer.data})

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        formatted_query_params = {}
        primary_key = 'pk'
        if primary_key not in self.queryset_kwargs.keys():
            self.queryset_kwargs[primary_key] = primary_key
        for key, value in self.queryset_kwargs.items():
            item_value = self.kwargs[key]
            formatted_query_params[value] = item_value

        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        for lookup_url_kwarg in self.queryset_kwargs:
            assert lookup_url_kwarg in self.kwargs, (
                    'Expected view %s to be called with a URL keyword argument '
                    'named "%s". Fix your URL conf, or set the `.lookup_field` '
                    'attribute on the view correctly.' %
                    (self.__class__.__name__, lookup_url_kwarg)
            )

        filter_kwargs = formatted_query_params
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.deleted:
            return Response({ERRORS: 'Object is already deleted!'}, status=status.HTTP_304_NOT_MODIFIED)
        obj.deleted = True
        obj.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
