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
from core.constants import CUSTOM_ATTRIBUTE_SUITE_SPECIFIC
from django.db.models import Q
from django_filters import rest_framework as filters
from notifications.models import Notification
from rest_framework.filters import OrderingFilter, SearchFilter

from testy.core.models import Attachment, CustomAttribute, Label, NotificationSetting, Project
from testy.core.selectors.projects import ProjectSelector
from testy.filters import ArchiveFilterMixin, SearchView, case_insensitive_filter, ordering_filter, project_filter
from testy.utilities.request import get_user_favorites
from testy.utilities.string import parse_int


class ProjectOrderingFilter(OrderingFilter):

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        favorite_conditions = Q(pk__in=get_user_favorites(request))
        if ordering:
            queryset = queryset.annotate(priority=ProjectSelector.favorites_annotation(favorite_conditions))
            return queryset.order_by('priority', *ordering)

        return queryset


class ProjectFilter(ArchiveFilterMixin, filters.FilterSet):
    name = case_insensitive_filter()
    favorites = filters.BooleanFilter(
        'pk',
        method='display_favorites',
        help_text='If True, display only favorite projects. If False, display all projects with favorites first',
    )

    class Meta:
        model = Project
        fields = ('name', 'favorites')

    def display_favorites(self, queryset, field_name, only_favorites):
        favorite_conditions = Q(**{f'{field_name}__in': get_user_favorites(self.request)})

        if only_favorites:
            return queryset.filter(favorite_conditions).order_by('name')

        return (
            queryset
            .annotate(
                priority=ProjectSelector.favorites_annotation(favorite_conditions),
            )
            .order_by('priority', 'name')
        )


class AttachmentFilter(filters.FilterSet):
    project = project_filter()

    class Meta:
        model = Attachment
        fields = ('project',)


class LabelFilter(filters.FilterSet):
    project = project_filter()

    ordering = ordering_filter(
        fields=(
            ('id', 'id'),
            ('name', 'name'),
            ('type', 'type'),
        ),
    )

    class Meta:
        model = Label
        fields = ('project',)


class CustomAttributeFilter(filters.FilterSet):
    project = project_filter()
    suite = filters.NumberFilter(
        field_name='suite_ids',
        method='filter_by_suite',
        help_text='Related suite id',
    )

    @classmethod
    def filter_by_suite(cls, queryset, field_name, val):
        non_suite_specific_condition = Q()
        suite_specific_condition = Q()
        for model_name in CUSTOM_ATTRIBUTE_SUITE_SPECIFIC:
            non_suite_specific_condition |= Q(**{f'applied_to__{model_name}__{field_name}': []})
            non_suite_specific_condition |= ~Q(**{f'applied_to__{model_name}__has_key': field_name})
            suite_specific_condition |= Q(
                **{f'applied_to__{model_name}__{field_name}__contains': [int(val)]},
            )
        non_suite_specific = queryset.filter(non_suite_specific_condition)
        suite_specific = queryset.filter(suite_specific_condition)
        return non_suite_specific | suite_specific

    class Meta:
        model = CustomAttribute
        fields = ('suite',)


class NotificationFilter(filters.FilterSet):
    ordering = ordering_filter(
        fields=(
            ('id', 'id'),
            ('unread', 'unread'),
        ),
    )

    class Meta:
        model = Notification
        fields = ('unread',)


class NotificationSettingFilter(filters.FilterSet):
    verbose_name = case_insensitive_filter()

    class Meta:
        model = NotificationSetting
        fields = ('action_code',)


class SearchFilterMixin(filters.FilterSet):
    search_fields: list[str] | None = None

    def filter_by_search(self, qs, field_name, value):
        if not self.search_fields:
            return qs
        search_filter = SearchFilter()
        if self.request.query_params.get('treesearch'):
            search_filter.search_param = 'treesearch'
        return search_filter.filter_queryset(self.request, qs, SearchView(*self.search_fields))


class ParentFilterMixin(filters.FilterSet):

    @classmethod
    def filter_by_parent(cls, queryset, field_name, parent):
        lookup = Q()
        if parent == 'null':
            lookup = Q(parent__isnull=True)
        elif parent_id := parse_int(parent):
            lookup = Q(parent__id=parent_id) | Q(id=parent_id)
        return queryset.filter(lookup)
