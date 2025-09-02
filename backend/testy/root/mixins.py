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
from typing import Any, TypedDict
from uuid import uuid4

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import FieldDoesNotExist
from django.db.models import CASCADE, ManyToManyRel, ManyToOneRel, Model
from django.db.models.sql import Query
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.generics import QuerySet
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from testy.core.services.recovery import RecoveryService
from testy.paginations import StandardSetPagination
from testy.root.api.v2.serializers import RecoveryInputSerializer
from testy.root.ltree.models import LtreeModel
from testy.root.models import DeletedQuerySet, SoftDeleteQuerySet
from testy.swagger.core import preview_schema
from testy.tests_description.models import TestSuite
from testy.tests_description.services.suites import TestSuiteService

UniqueRelationSet = set[ManyToOneRel | GenericRelation | ManyToManyRel]
_TARGET_OBJECT = 'target_object'
_POST = 'post'


class TargetObject(TypedDict):
    app_label: str
    model: str
    pk: Any


class QuerySetMeta(TypedDict):
    app_label: str
    model: str
    query: Query


class QuerySetInfo(TypedDict):
    verbose_name: str
    verbose_name_related_model: str
    count: int


class MetaForCaching(TypedDict):
    target_object: TargetObject
    querysets_meta: list[QuerySetMeta]


CacheReadyQuerySet = tuple[list[QuerySetMeta], list[QuerySetInfo]]


class RelationTreeMixin:
    def build_relation_tree(self, model, tree: list | None = None) -> UniqueRelationSet:  # noqa: WPS231
        """
        Build tree of relations by model to prevent duplicate recursive queries gathering.

        Args:
            model: model class.
            tree: list of gathered relations.

        Returns:
            set of different gathered relations.
        """
        if not tree:
            tree = []
        related_objects = list(model._meta.related_objects)
        related_objects.extend(model._meta.private_fields)
        for single_object in related_objects:
            if not isinstance(single_object, GenericRelation):
                # on_delete option is kept in identity with index 6
                if not single_object.identity[6] == CASCADE:  # noqa: WPS508
                    continue
            if single_object.model == single_object.related_model:
                continue
            self._check_for_relation(single_object, tree)
            if single_object.related_model._meta.related_objects:
                self.build_relation_tree(single_object.related_model, tree)
        return set(tree)

    def get_all_related_querysets(  # noqa: WPS231
        self,
        qs,
        model,
        qs_info_list: list[QuerySetInfo] | None = None,
        qs_meta_list: list[QuerySetMeta] | None = None,
        deleted: bool = False,
        relation_tree=None,
        ignore_on_delete_property: bool = False,
    ) -> CacheReadyQuerySet:
        """
        Recursive function to get all related objects of instance as list of querysets.

        Args:
            qs: queryset or instance to find related objects for.
            model: model in which we are looking for relations.
            qs_info_list: list of descriptions of elements to be deleted.
            qs_meta_list: meta information to restore querysets from cache.
            deleted: defines which manager to use for getting querysets.
            relation_tree: List of relations to avoid duplicate querysets.
            ignore_on_delete_property: ignore on_delete property in gathering related querysets.

        Returns:
            List of querysets.
        """
        manager = 'deleted_objects' if deleted else 'objects'
        if qs_info_list is None:
            qs_info_list = []
        if qs_meta_list is None:
            qs_meta_list = []
        related_objects = list(model._meta.related_objects)
        related_objects.extend(model._meta.private_fields)
        for single_object in related_objects:
            if not isinstance(single_object, GenericRelation):
                if not single_object.identity[6] == CASCADE and not ignore_on_delete_property:  # noqa: WPS508
                    continue
            if single_object.model == single_object.related_model:
                continue
            if single_object not in relation_tree:
                continue
            if isinstance(single_object, GenericRelation):
                filter_option = {
                    f'{single_object.object_id_field_name}__in': [instance.id for instance in qs],
                    f'{single_object.content_type_field_name}': ContentType.objects.get_for_model(model),
                }
            else:
                filter_option = {f'{single_object.field.attname}__in': [instance.id for instance in qs]}  # noqa: WPS237

            if isinstance(single_object.related_model, LtreeModel):
                new_qs = getattr(single_object.related_model, manager).filter(**filter_option).get_descendants(
                    include_self=True,
                )
            else:
                new_qs = getattr(single_object.related_model, manager).filter(**filter_option)
            model_meta_data = single_object.related_model._meta
            qs_info_list.append(
                QuerySetInfo(
                    verbose_name=model_meta_data.verbose_name,
                    verbose_name_related_model=single_object.model._meta.verbose_name_plural,
                    count=new_qs.count(),
                ),
            )
            qs_meta_list.append(
                QuerySetMeta(
                    app_label=model_meta_data.app_label,
                    model=model_meta_data.model_name,
                    query=new_qs.query,
                ),
            )
            if single_object.related_model._meta.related_objects:
                self.get_all_related_querysets(
                    qs=new_qs,
                    model=single_object.related_model,
                    qs_info_list=qs_info_list,
                    qs_meta_list=qs_meta_list,
                    deleted=deleted,
                    relation_tree=relation_tree,
                    ignore_on_delete_property=ignore_on_delete_property,
                )
        return qs_meta_list, qs_info_list

    @classmethod
    def _check_for_relation(cls, new_relation: GenericRelation | ManyToManyRel | ManyToOneRel, relations):
        """
        Decide if new gathered relation clashes with previously found relations.

        Args:
            new_relation: newly found relation
            relations: already gathered relations
        """
        if isinstance(new_relation, GenericRelation):
            relations.append(new_relation)
            return
        for idx, relation in enumerate(relations):
            if new_relation.related_model != relation.related_model:
                continue
            if new_relation.model == relation.model:
                return
            if new_relation.model.ModelHierarchyWeightMeta.weight > relation.model.ModelHierarchyWeightMeta.weight:
                relations[idx] = new_relation
        relations.append(new_relation)

    @classmethod
    def _get_instance_from_metadata(cls, meta_data: TargetObject) -> Model:
        model = apps.get_model(app_label=meta_data.get('app_label'), model_name=meta_data.get('model'))
        return model.objects.get(pk=meta_data.get('pk'))

    @classmethod
    def _get_qs_from_meta_data(cls, meta_data: QuerySetMeta, qs_class: type[QuerySet]) -> QuerySet[Model]:
        model = apps.get_model(app_label=meta_data.get('app_label'), model_name=meta_data.get('model'))
        return qs_class(model=model, query=meta_data.get('query'))


class TestyDestroyModelMixin(RelationTreeMixin):

    def destroy(self, request, pk, *args, **kwargs):  # noqa: WPS231
        """
        Replace default destroy method.

        Replacement for default destroy action, if user retrieved deleted objects, we save gathered querysets to
        cache and if he submits deletion within time gap use user cookie to retrieve cache and delete objects.

        Args:
            request: Django request object
            pk: primary key
            args: positional arguments
            kwargs: keyword arguments

        Returns:
            Response with no content status code
        """
        querysets_to_delete: list[QuerySet] = []
        target_object = self.get_object()
        cache_key = request.COOKIES.get('delete_cache')
        if cache_key and cache.get(cache_key):
            meta_to_delete: MetaForCaching = cache.get(cache_key)
            if self._get_instance_from_metadata(meta_to_delete.get(_TARGET_OBJECT)) == target_object:
                for elem in meta_to_delete['querysets_meta']:
                    querysets_to_delete.append(
                        self._get_qs_from_meta_data(elem, qs_class=SoftDeleteQuerySet),
                    )
            cache.delete(cache_key)
        if not querysets_to_delete:
            meta_querysets, _ = self.get_deleted_objects()
            for meta_data in meta_querysets:
                querysets_to_delete.append(self._get_qs_from_meta_data(meta_data, SoftDeleteQuerySet))
        for related_qs in querysets_to_delete:
            if related_qs.model == TestSuite:
                TestSuiteService.unlink_custom_attributes(related_qs)
            related_qs.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @preview_schema
    @action(
        methods=['get'],
        url_path='delete/preview',
        url_name='delete-preview',
        detail=True,
    )
    def delete_preview(self, request, pk):
        """
        Get preview of objects to delete, retrieved querysets are cached.

        Args:
            request: django request
            pk: primary key

        Returns:
            Tuple of querysets to be deleted and response info
        """
        qs_meta_list, qs_info_list = self.get_deleted_objects()
        target_object = self.get_object()
        meta_for_deletion = MetaForCaching(
            target_object=TargetObject(
                model=target_object._meta.model_name,
                app_label=target_object._meta.app_label,
                pk=target_object.pk,
            ),
            querysets_meta=qs_meta_list,
        )
        cache_key = uuid4().hex
        cache.set(cache_key, meta_for_deletion)
        response = Response(data=qs_info_list)
        response.set_cookie('delete_cache', cache_key, max_age=settings.CACHE_TTL)
        return response

    @action(
        detail=False,
        methods=[_POST],
        url_path='deleted/remove',
        url_name='deleted-remove',
    )
    def delete_permanently(self, request):
        serializer = RecoveryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        RecoveryService.delete_permanently(self.get_queryset(), serializer.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_deleted_objects(self) -> CacheReadyQuerySet:
        instance = self.get_object()
        qs = RecoveryService.get_objects_by_instance(instance)
        relation_tree = self.build_relation_tree(qs.model)
        qs_meta_list, qs_info_list = self.get_all_related_querysets(
            qs,
            qs.model,
            relation_tree=relation_tree,
        )
        model_meta_data = qs.model()._meta
        qs_meta_list.append(
            QuerySetMeta(
                app_label=model_meta_data.app_label,
                model=model_meta_data.model_name,
                query=qs.query,
            ),
        )
        qs_info_list.append(
            QuerySetInfo(
                verbose_name='source model',
                verbose_name_related_model=model_meta_data.verbose_name_plural,
                count=qs.count(),
            ),
        )
        return qs_meta_list, qs_info_list


class TestyArchiveMixin(RelationTreeMixin):

    @preview_schema
    @action(
        methods=['get'],
        url_path='archive/preview',
        url_name='archive-preview',
        detail=True,
    )
    def archive_preview(self, request, pk):
        target_object = self.get_object()
        qs_meta_list, qs_info_list = self.get_objects_to_archive()
        meta_for_caching = MetaForCaching(
            target_object=TargetObject(
                model=target_object._meta.model_name,
                app_label=target_object._meta.app_label,
                pk=target_object.pk,
            ),
            querysets_meta=qs_meta_list,
        )
        cache_key = uuid4().hex
        cache.set(cache_key, meta_for_caching)
        response = Response(data=qs_info_list)
        response.set_cookie('archive_cache', cache_key, max_age=settings.CACHE_TTL)
        return response

    @action(
        methods=[_POST],
        url_path='archive',
        url_name='archive-commit',
        detail=True,
    )
    def archive_objects(self, request, pk):
        querysets_to_archive: list[QuerySet[Model]] = []
        target_object = self.get_object()
        cache_key = request.COOKIES.get('archive_cache')
        if cache_key and cache.get(cache_key):
            meta_to_archive: MetaForCaching = cache.get(cache_key, {})
            if self._get_instance_from_metadata(meta_to_archive.get(_TARGET_OBJECT)) == target_object:
                querysets_to_archive = [
                    self._get_qs_from_meta_data(elem, SoftDeleteQuerySet) for elem in meta_to_archive['querysets_meta']
                ]
            cache.delete(cache_key)
        if not querysets_to_archive:
            meta_objects, _ = self.get_objects_to_archive()
            for meta_data in meta_objects:
                querysets_to_archive.append(self._get_qs_from_meta_data(meta_data, SoftDeleteQuerySet))
        for related_qs in querysets_to_archive:
            related_qs.update(is_archive=True)
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=[_POST],
        url_path='archive/restore',
        url_name='archive-restore',
        detail=False,
    )
    def restore_archived(self, request):
        serializer = RecoveryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qs = RecoveryService.get_objects_by_ids(self.get_queryset(), serializer.validated_data)
        model_class = qs.model()
        relation_tree = self.build_relation_tree(model_class)
        qs_meta_list, qs_info_list = self.get_all_related_querysets(
            qs,
            model_class,
            relation_tree=relation_tree,
            ignore_on_delete_property=True,
        )
        for meta in qs_meta_list:
            try:
                queryset = self._get_qs_from_meta_data(meta, SoftDeleteQuerySet)
                queryset.model()._meta.get_field('is_archive')
            except FieldDoesNotExist:
                continue
            queryset.update(is_archive=False)
        qs.update(is_archive=False)
        return Response(status=status.HTTP_200_OK)

    def get_objects_to_archive(self) -> CacheReadyQuerySet:
        instance = self.get_object()
        qs = RecoveryService.get_objects_by_instance(instance)
        relation_tree = self.build_relation_tree(qs.model)
        qs_meta_list, qs_info_list = self.get_all_related_querysets(
            qs,
            qs.model,
            relation_tree=relation_tree,
            ignore_on_delete_property=True,
        )
        model_meta_data = qs.model()._meta
        qs_meta_list.append(
            QuerySetMeta(
                app_label=model_meta_data.app_label,
                model=model_meta_data.model_name,
                query=qs.query,
            ),
        )
        qs_info_list.append(
            QuerySetInfo(
                verbose_name='source model',
                verbose_name_related_model=model_meta_data.verbose_name_plural,
                count=qs.count(),
            ),
        )

        result_meta_list = []
        result_info_list = []
        for meta, info in zip(qs_meta_list, qs_info_list):
            try:
                apps.get_model(
                    meta.get('app_label'),
                    meta.get('model'),
                )._meta.get_field('is_archive')
            except FieldDoesNotExist:
                continue
            result_meta_list.append(meta)
            result_info_list.append(info)
        return result_meta_list, result_info_list


class TestyRestoreModelMixin(RelationTreeMixin):

    @action(
        methods=[_POST],
        url_path='deleted/recover',
        url_name='deleted-recover',
        detail=False,
    )
    def restore(self, request):
        serializer = RecoveryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qs = RecoveryService.get_objects_by_ids(self.get_queryset(), serializer.validated_data)
        model_class = qs.model()
        relation_tree = self.build_relation_tree(model_class)
        qs_meta_data, _ = self.get_all_related_querysets(qs, model_class, deleted=True, relation_tree=relation_tree)
        related_querysets = []
        for meta_data in qs_meta_data:
            related_querysets.append(self._get_qs_from_meta_data(meta_data, DeletedQuerySet))
        related_querysets.append(qs)
        for related_qs in related_querysets:
            related_qs.restore()
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        url_path='deleted',
        url_name='deleted-list',
        detail=False,
    )
    def recovery_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        pagination = StandardSetPagination()
        page = pagination.paginate_queryset(queryset, request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return pagination.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TestyModelViewSet(  # noqa: WPS215
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    TestyDestroyModelMixin,
    TestyRestoreModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """ModelViewSet modified with custom testy mixins."""
