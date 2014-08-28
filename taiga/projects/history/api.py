# Copyright (C) 2014 Andrey Antukh <niwi@niwi.be>
# Copyright (C) 2014 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014 David Barragán <bameda@dbarragan.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from rest_framework.response import Response

from taiga.base.api import ReadOnlyListViewSet

from . import permissions
from . import serializers
from . import services


class HistoryViewSet(ReadOnlyListViewSet):
    serializer_class = serializers.HistoryEntrySerializer

    content_type = None

    def get_content_type(self):
        app_name, model = self.content_type.split(".", 1)
        return get_object_or_404(ContentType, app_label=app_name, model=model)

    def get_queryset(self):
        ct = self.get_content_type()
        model_cls = ct.model_class()

        qs = model_cls.objects.all()
        filtered_qs = self.filter_queryset(qs)
        return filtered_qs

    def response_for_queryset(self, queryset):
        # Switch between paginated or standard style responses
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    # Just for restframework! Because it raises
    # 404 on main api root if this method not exists.
    def list(self, request):
        return Response({})

    def retrieve(self, request, pk):
        obj = self.get_object()
        self.check_permissions(request, "retrieve", obj)

        qs = services.get_history_queryset_by_model_instance(obj)
        return self.response_for_queryset(qs)


class UserStoryHistory(HistoryViewSet):
    content_type = "userstories.userstory"
    permission_classes = (permissions.UserStoryHistoryPermission,)


class TaskHistory(HistoryViewSet):
    content_type = "tasks.task"
    permission_classes = (permissions.TaskHistoryPermission,)


class IssueHistory(HistoryViewSet):
    content_type = "issues.issue"
    permission_classes = (permissions.IssueHistoryPermission,)


class WikiHistory(HistoryViewSet):
    content_type = "wiki.wikipage"
    permission_classes = (permissions.WikiHistoryPermission,)
