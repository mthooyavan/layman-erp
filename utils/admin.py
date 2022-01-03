import calendar
import csv
import io
import os

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.filters import (
    SimpleListFilter,
    AllValuesFieldListFilter,
    ChoicesFieldListFilter,
    RelatedFieldListFilter,
    RelatedOnlyFieldListFilter, FieldListFilter, DateFieldListFilter,
)
from django.contrib.admin.utils import lookup_field
from django.contrib.postgres import fields
from django.db import connection
from django.db.models import DateTimeField
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.utils import timezone
from django.utils.http import urlencode
from django_json_widget.widgets import JSONEditorWidget

from .file import file_size
from .serializers import CSVFileOrEmailModelMixin, CSVTooLarge


class AutoCompleteMixin:
    """
    Mixin class to enable auto complete on all related fields
    Currently it will load only Foreign and OneToOne Fields
    Fields in skip_autocomplete_fields will be skipped
    AutoCompleteMixin must be included before ModelAdmin otherwise it won't work
    """
    RELATED_FIELD_TYPES = ('ForeignKey', 'OneToOneField')

    # Generic ForeignKey Fields always skip for autocomplete, since auto-completing them causes errors.
    GENERIC_FOREIGNKEY_FIELDS = ('content_object', 'content_type', 'object_id')
    skip_autocomplete_fields = ()

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        fields = [field for field in self.model._meta.get_fields() if field.name not in self.GENERIC_FOREIGNKEY_FIELDS]
        self.related_fields = [
            field.name for field in fields
            if field.get_internal_type() in self.RELATED_FIELD_TYPES
        ]
        for field in self.skip_autocomplete_fields:
            if field in self.autocomplete_fields:
                raise ValueError(f'autocomplete_fields and skip_autocomplete_fields cannot contain same field: {field}')

    def get_autocomplete_fields(self, request):
        autocomplete_fields = set(self.related_fields)
        autocomplete_fields.update(self.autocomplete_fields)
        if self.skip_autocomplete_fields:
            return autocomplete_fields - set(self.skip_autocomplete_fields)
        return autocomplete_fields


class CustomModelAdmin(AutoCompleteMixin, admin.ModelAdmin):
    """
    All of our model admins should use this as parent class so we can control all global behaviours
    through this
    """
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget}
    }

    def has_delete_permission(self, request, obj=None):
        """We want to disable delete action by default. Use DeleteActionMixin to change this behaviour"""
        return False if settings.IS_PROD else True


class DeleteActionMixin:
    """This mixin enables the delete action on list page and delete button on detail page of admin"""

    def has_delete_permission(self, request, obj=None):
        return True


class CSVActionMixin(CSVFileOrEmailModelMixin):
    """
    A Mixin which adds an action to Model's Admin to download selected rows as CSV.
    All fields mentioned in `list_download` will be included in CSV file. If `list_download` is not defined,
    `list_display` will be used.
    All fields mentioned in `list_skip_download` will be skipped.
    CSVActionMixin must be included before ModelAdmin otherwise it won't work

    To override downloaded file name, assign new name to `csv_file_name` class attribute
    """
    csv_file_name = None
    list_download = ()
    list_skip_download = ()
    actions = ['download_as_csv']

    @classmethod
    def initialize_instance(cls, *args, model=None, **kwargs):
        for site in admin.sites.all_sites:
            try:
                return site._registry[model]
            except KeyError:
                pass

    def download_as_csv(self, request, queryset):
        try:
            buffer = self.generate_csv(request, queryset)
        except CSVTooLarge as exc:
            self.message_user(request, str(exc))
            return HttpResponseRedirect(request.get_full_path())

        compressed, buffer = self.conditional_compress(buffer)
        if compressed:
            response = FileResponse(buffer, content_type='application/gzip')
            response['Content-Disposition'] = 'attachment; filename={}.csv.gz'.format(self.get_csv_file_name())
            response['Content-Length'] = file_size(buffer)
        else:
            response = HttpResponse(buffer, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename={}.csv'.format(self.get_csv_file_name())
        return response

    download_as_csv.short_description = 'Download selected rows as CSV'

    def get_columns(self, request, queryset):
        _list_download = self.list_download or self.get_list_display(request)
        return [field for field in _list_download if field not in self.list_skip_download]

    def get_buffer(self, queryset, columns):
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, columns)
        writer.writeheader()
        for item in queryset.iterator():
            row = {}
            for field_name in columns:
                _, _, value = lookup_field(field_name, item, self)
                row[field_name] = value
            writer.writerow(row)

        buffer.seek(0, os.SEEK_SET)
        return buffer

    def get_csv_file_name(self):
        return self.csv_file_name or self.model._meta.verbose_name_plural


class ReadOnlyMixin:
    """Mixin class to disable operations on the model admin

    This mixin disables all update, create and delete actions on the ModelAdmin it is included with
    """

    # pylint: disable=no-self-use
    def has_add_permission(self, request):
        """Disable create on this model admin"""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable update on this model admin"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable delete on this model admin"""
        return False


class EstimateCountQuerySet:
    """
    Custom queryset class that uses table descriptors to return counts for unfiltered queries instead of exact
    count. This helps reduce query times for models with very large tables and avoids issues (timeouts) with pagination
    on Django model admins for those models.
    """

    def count(self):
        """
        Sources:
         https://gist.github.com/ketanbhatt/846644beb59457485a3decd8dec6a4c4#file-paginator-py
         https://stackoverflow.com/questions/10433173/prevent-django-admin-from-running-select-count-on-the-list-form
        Warning: Postgresql only hack

        Overrides the count method of QuerySet objects to get an estimate instead of actual count when not filtered.
        However, this estimate can be stale and hence not fit for situations where the count of objects actually
        matter.
        """
        if getattr(self, '_count', None) is not None:
            return self._count

        query = self.query
        if not query.where:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT reltuples FROM pg_class WHERE relname = %s", [query.model._meta.db_table])
                    self._count = int(cursor.fetchone()[0])
            except:  # nopep8
                self._count = super().count()
        else:
            self._count = super().count()
        return self._count


class EstimateCountAdminMixin:
    show_full_result_count = False

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Compose EstimateCountQuerySet and the current queryset class into one so we can utilize
        # the estimated count functionality on the resulting queryset while retaining any other custom
        # functionality that might have been added to the original queryset class.
        EstimateQuerySet = type('EstimateQuerySet', (EstimateCountQuerySet, qs.__class__), {})

        return EstimateQuerySet(model=qs.model, query=qs.query, using=qs._db, hints=qs._hints)


def CustomTitledFilter(title, filter_class):
    class Wrapper(FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = filter_class(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


class SimpleDropdownFilter(SimpleListFilter):
    template = 'admin/filters/dropdown_filter.html'


class DropdownFilter(AllValuesFieldListFilter):
    template = 'admin/filters/dropdown_filter.html'


class ChoiceDropdownFilter(ChoicesFieldListFilter):
    template = 'admin/filters/dropdown_filter.html'


class RelatedDropdownFilter(RelatedFieldListFilter):
    template = 'admin/filters/dropdown_filter.html'


class RelatedOnlyDropdownFilter(RelatedOnlyFieldListFilter):
    template = 'admin/filters/dropdown_filter.html'


class RelatedOnlyMultiSelectFilter(RelatedOnlyFieldListFilter):
    """Filter class that works as a multi-select"""
    template = 'admin/filters/multi_select_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.lookup_kwarg = f'{field_path}__{field.target_field.name}__in'
        self.lookup_val = params.get(self.lookup_kwarg)
        self.lookup_val_isnull = params.get(self.lookup_kwarg_isnull)

    def choices(self, changelist):
        yield {
            'selected': self.lookup_val is None and not self.lookup_val_isnull,
            'display': 'All',
            'value': 'all',
            'lookup': self.lookup_kwarg,
        }
        selected_vals = self.lookup_val.split(',') if self.lookup_val else []
        for lookup, title in self.lookup_choices:
            yield {
                'selected': str(lookup) in selected_vals,
                'display': title,
                'value': lookup,
                'lookup': self.lookup_kwarg,
            }
        if self.include_empty_choice:
            yield {
                'selected': bool(self.lookup_val_isnull),
                'display': self.empty_value_display,
                'value': 'null',
                'lookup': self.lookup_kwarg,
            }


class ChoiceMultiSelectFilter(ChoiceDropdownFilter):
    """Choice filter that works as a multi-select"""
    template = 'admin/filters/multi_select_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.lookup_kwarg = f'{field_path}__in'
        self.lookup_val = params.get(self.lookup_kwarg)

    def choices(self, changelist):
        yield {
            'selected': self.lookup_val is None and not self.lookup_val_isnull,
            'display': 'All',
            'value': 'all',
            'lookup': self.lookup_kwarg,
        }
        selected_vals = self.lookup_val.split(',') if self.lookup_val else []
        for lookup, title in self.field.flatchoices:
            yield {
                'selected': str(lookup) in selected_vals,
                'display': title,
                'value': lookup,
                'lookup': self.lookup_kwarg,
            }


class LastMonthDateFilter(DateFieldListFilter):
    def __init__(self, field, *args, **kwargs):
        super().__init__(field, *args, **kwargs)
        now = timezone.now()
        # When time zone support is enabled, convert "now" to the user's time
        # zone so Django's definition of "Today" matches what the user expects.
        if timezone.is_aware(now):
            now = timezone.localtime(now)

        if isinstance(field, DateTimeField):
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # field is a models.DateField
            today = now.date()
        if today.month == 1:
            previous_month = today.replace(
                year=today.year - 1, month=12, day=1)
        else:
            previous_month = today.replace(month=today.month - 1, day=1)
        self.links += (
            ('Last month', {
                self.lookup_kwarg_since: str(previous_month),
                self.lookup_kwarg_until: str(today.replace(day=1)),
            }),
        )


class MonthYearListFilter(admin.DateFieldListFilter):
    title = 'month and year'
    template = 'filters/month_year_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):  # pylint: disable=too-many-arguments
        self.lookup_kwarg = f'{field_path}__month'
        self.lookup_kwarg_year = f'{field_path}__year'
        self.lookup_val = request.GET.get(self.lookup_kwarg), request.GET.get(self.lookup_kwarg_year)
        super().__init__(field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg, self.lookup_kwarg_year]

    def choices(self, changelist):
        month_year_choices = [[], []]
        currently_selected = {}

        if self.lookup_val[0]:
            currently_selected[self.lookup_kwarg] = self.lookup_val[0]
        if self.lookup_val[1]:
            currently_selected[self.lookup_kwarg_year] = self.lookup_val[1]

        unset_choice_month = currently_selected.copy()
        unset_choice_month.pop(self.lookup_kwarg, None)
        month_year_choices[0].append({
            'selected': self.lookup_val[0] is None,
            'query_string': changelist.get_query_string(unset_choice_month, [self.field.name]),
            'display': 'All',
        })

        unset_choice_year = currently_selected.copy()
        unset_choice_year.pop(self.lookup_kwarg_year, None)
        month_year_choices[1].append({
            'selected': self.lookup_val[1] is None,
            'query_string': changelist.get_query_string(unset_choice_year, [self.field.name]),
            'display': 'All',
        })

        for month in range(1, 13):
            choice = {
                'selected': self.lookup_val[0] == str(month),
                'query_string': changelist.get_query_string(
                    {**currently_selected, self.lookup_kwarg: month},
                    [self.field.name]
                ),
                'display': calendar.month_name[month]
            }
            month_year_choices[0].append(choice)

        current_year = timezone.now().year
        for year in range(2019, current_year + 1):
            choice = {
                'selected': self.lookup_val[1] == str(year),
                'query_string': changelist.get_query_string(
                    {**currently_selected, self.lookup_kwarg_year: year},
                    [self.field.name]
                ),
                'display': str(year)
            }
            month_year_choices[1].append(choice)
        return month_year_choices


class QueryStringMixin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self._query_params = None

    def changelist_view(self, request, extra_context=None):
        self._query_params = request.GET
        return super().changelist_view(request, extra_context=extra_context)

    def get_query_string_params(self) -> str:
        return urlencode(self._query_params.dict()) if self._query_params else ''
