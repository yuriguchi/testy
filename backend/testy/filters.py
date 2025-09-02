# TestY TMS - Test Management System
# Copyright (C) 2024 KNS Group LLC (YADRO)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Also add information on how to contact you by electronic and paper mail.
#
# If your software can interact with users remotely through a computer
# network, you should also make sure that it provides a way for users to
# get its source.  For example, if your program is a web application, its
# interface could display a "Source" link that leads users to an archive
# of the code.  There are many ways you could offer source, and different
# solutions will be better for different programs; see section 13 for the
# specific requirements.
#
# You should also get your employer (if you work as a programmer) or school,
# if any, to sign a "copyright disclaimer" for the program, if necessary.
# For more information on this, and how to apply and follow the GNU AGPL, see
# <http://www.gnu.org/licenses/>.
import operator
import warnings
from decimal import Decimal, DecimalException
from functools import partial, reduce
from types import MethodType
from typing import Callable

from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Model, Prefetch, Q, QuerySet
from django.utils import formats
from django_filters import compat
from django_filters import rest_framework as filters
from django_filters.constants import EMPTY_VALUES
from django_filters.filterset import FilterSetMetaclass
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from tests_representation.services.statistics import LabelProcessor

from testy import filters as testy_filters
from testy.utilities.request import get_boolean, validate_query_params_data
from testy.utilities.string import parse_bool_from_str, parse_int
from testy.utilities.tree import form_tree_prefetch_lookups

_EMPTY_VALUES = ('', [], None)
UserModel = get_user_model()

project_filter = partial(
    filters.NumberFilter,
    'project',
    required=True,
    error_messages={
        'required': 'Project query parameter is required',
    },
    help_text='Filter by project id',
)

case_insensitive_filter = partial(
    filters.CharFilter,
    lookup_expr='icontains',
    help_text='Case-insensitive filter for partial matches within the string',
)


def ordering_filter(fields: tuple[tuple[str, str], ...]):
    ordering_args = ','.join(field[1] for field in fields)
    return filters.OrderingFilter(
        fields=fields,
        help_text=f'Valid values are: {ordering_args}. Prefix "-" reverses order',
    )


class NonEmptyDecimalField(forms.DecimalField):
    def to_python(self, value):
        if value in self.empty_values:
            raise ValidationError('Empty value is not allowed.', code='invalid')
        if self.localize:
            value = formats.sanitize_separators(value)
        try:
            value = Decimal(str(value))
        except DecimalException:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value


class NonEmptyNumberFilter(filters.NumberFilter):
    field_class = NonEmptyDecimalField


class NumberInFilter(filters.BaseInFilter, NonEmptyNumberFilter):
    """Class for filtering by __in condition for integers."""


class StringInFilter(filters.BaseInFilter, filters.CharFilter):
    """Class for filtering by __in condition for integers."""


class ArchiveFilterMixin(filters.FilterSet):
    def filter_queryset(self, queryset):
        if not parse_bool_from_str(self.data.get('is_archive')):
            queryset = queryset.filter(is_archive=False)
        return super().filter_queryset(queryset)


class FilterListMixin:
    @classmethod
    def filter_by_list(cls, queryset: QuerySet[Model], field_name: str, values_list: list[str]) -> QuerySet[Model]:
        lookup = Q(**{f'{field_name}__in': values_list})
        if 'null' in values_list:
            values_list.remove('null')
            lookup |= Q(**{f'{field_name}__isnull': True})
        return queryset.filter(lookup)


class TestyBaseSearchFilter(SearchFilter):
    def construct_orm_lookups(self, search_fields, queryset):
        return [
            self.construct_search(str(search_field), queryset)
            for search_field in search_fields
        ]

    @classmethod
    def custom_filter(cls, queryset, filter_conditions, request):
        return queryset.filter(filter_conditions)

    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)
        distinct_fields = getattr(view, 'distinct_fields', [])

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = self.construct_orm_lookups(search_fields, queryset)

        conditions = []
        for search_term in search_terms:
            queries = [
                Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            conditions.append(reduce(operator.or_, queries))

        queryset = self.custom_filter(queryset, reduce(operator.and_, conditions), request)
        if not distinct_fields:
            return queryset
        return queryset


class CustomOrderingFilter(OrderingFilter):

    def filter_queryset(self, request, queryset):
        ordering = request.query_params.get('ordering')
        if not ordering:
            return queryset
        ordering = list(map(str.strip, ordering.split(',')))
        return queryset.order_by(*ordering)


class CustomSearchFilter(SearchFilter):
    def filter_queryset(self, request, queryset, allowed_search_params: list[str]):
        filter_lookup = {}
        for query_param_name in allowed_search_params:
            if value := request.query_params.get(query_param_name):
                filter_lookup[f'{query_param_name}__in'] = list(
                    map(str.strip, value.split(',')),
                )
        return queryset.filter(**filter_lookup)


class LabelsFilterMetaclass(FilterSetMetaclass):

    def __new__(cls, name, bases, attrs):
        filter_ = NumberInFilter(method='filter_by_labels')
        attrs.update({'labels': filter_, 'not_labels': filter_})
        new_class = super().__new__(cls, name, bases, attrs)

        def filter_by_labels(self, queryset, field_name, label_ids: list[int]):  # noqa: WPS430
            params = validate_query_params_data(
                self.request.query_params,
                labels=NumberInFilter(),
                not_labels=NumberInFilter(),
            )
            filter_condition = {
                'labels': params.get('labels'),
                'not_labels': params.get('not_labels'),
                'labels_condition': self.request.query_params.get('labels_condition', 'or'),
            }
            processor = LabelProcessor(filter_condition, outer_ref_prefix=self.labels_outer_ref_prefix)
            return processor.process_labels(queryset)

        def init(self, *args, **kwargs):  # noqa: WPS430
            self.filter_by_labels = MethodType(filter_by_labels, self)
            super(new_class, self).__init__(*args, **kwargs)  # noqa: WPS613, WPS608, WPS609

        new_class.__init__ = init  # noqa: WPS609
        return new_class


class IsFilteredMixin:
    def is_filtered(self, excluded: set[str]) -> bool:
        for name, value in self.form.cleaned_data.items():
            if name in excluded:
                continue
            if value not in _EMPTY_VALUES:  # noqa: WPS510
                return True
        return False


def union_ordering_filter(fields: tuple[tuple[str, str], ...]):
    class UnionOrderingFilter(filters.OrderingFilter):
        def filter(self, qs, value):
            if value in EMPTY_VALUES:
                return qs

            ordering = [self.get_ordering_value(param) for param in value]
            ordering.insert(0, 'is_leaf')
            return qs.order_by(*ordering)

    ordering_fields = ','.join(field[1] for field in fields)
    return UnionOrderingFilter(
        fields=fields,
        help_text=f'Valid values are: {ordering_fields}. Prefix "-" reverses order',
    )


class TreeSearchBaseFilter(TestyBaseSearchFilter):
    def __init__(self, *args, **kwargs):
        warnings.warn('Deprecated in 2.0', DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)

    children_field_name: str = None
    max_level_method: Callable = None
    model_class = None

    def get_ancestors(self, valid_options):
        return valid_options.get_ancestors(include_self=True)

    def get_valid_options(self, filter_conditions, request):
        return self.model_class.objects.filter(
            filter_conditions,
            project_id=request.query_params.get('project'),
        )

    def custom_filter(self, queryset, filter_conditions, request):
        valid_options = self.get_valid_options(filter_conditions, request)
        if get_boolean(request, 'is_flat'):
            return valid_options
        ancestors = self.get_ancestors(valid_options)
        lookups = form_tree_prefetch_lookups(
            self.children_field_name,
            self.children_field_name,
            self.max_level_method(),
        )
        prefetch_objects = []
        for lookup in lookups:
            prefetch_objects.append(Prefetch(lookup, queryset=ancestors))

        parent_id = parse_int(request.query_params.get('parent', ''))
        parent_lookup = {'parent_id': parent_id} if parent_id else {'parent_id__isnull': True}

        return ancestors.filter(**parent_lookup).prefetch_related(*prefetch_objects)


class TestyFilterBackend(DjangoFilterBackend):
    def get_coreschema_field(self, field):
        match type(field):
            case filters.NumberFilter:
                field_cls = compat.coreschema.Number
            case filters.BooleanFilter:
                field_cls = compat.coreschema.Boolean
            case filters.BaseCSVFilter:
                field_cls = compat.coreschema.Array
            case filters.BaseCSVFilter | testy_filters.NumberInFilter | testy_filters.StringInFilter:
                field_cls = compat.coreschema.Array
            case _:
                field_cls = compat.coreschema.String
        return field_cls(description=str(field.extra.get('help_text', '')))


class SearchView:
    def __init__(self, *search_fields: str) -> None:
        self.search_fields = search_fields
