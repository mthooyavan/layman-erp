import csv
import io
from typing import List

from django.db.models import QuerySet
from rest_framework import serializers

from utils.time import convert_to_milliseconds
from utils.file import CSVFileCompressionMixin


class TimestampField(serializers.Field):

    def to_representation(self, value):
        if not value:
            return None
        return convert_to_milliseconds(value)


class CSVTooLarge(Exception):
    """
    raised when rows count is greater than a set limit
    """
    pass


class CSVFileOrEmailModelMixin(CSVFileCompressionMixin):
    """
    This mixin doesn't generate CSV, instead it enables those that do generate (CSVActionMixin, CSVMixin)
    to either do it inline or through a celery task depending upon the size of queryset
    """

    MAX_INLINE_LIMIT = 500
    LARGE_CSV_MSG = 'The requested file is too large to download.'
    EMAIL_CSV_MSG = 'You will receive an email with the report once completed.'
    email_templates_path = 'emails/csv_download'
    csv_file_name = None

    def generate_csv(self, request, queryset) -> io.StringIO:
        """
        This method is main API to generate CSV buffer. It will
         - either
           - create and return CSV buffer if queryset count is <= MAX_INLINE_LIMIT
         - or
           - raise CSVTooLarge exception
           - initialize a celery task to generate and email CSV file to user (optional)

        :raise CSVTooLarge
        """
        if not isinstance(queryset, QuerySet):
            model = self.get_csv_model()
            queryset = model.objects.filter(pk__in=(o.pk for o in queryset))

        columns = self.get_columns(request, queryset)
        if queryset.count() <= self.MAX_INLINE_LIMIT:
            return self.get_buffer(queryset, columns)

        msg = self.LARGE_CSV_MSG
        raise CSVTooLarge(msg)

    def get_buffer(self, queryset, columns) -> io.StringIO:
        """
        Supposed to be implemented by child class, need to return A CSV buffer
        """
        raise NotImplementedError

    def get_columns(self, request, queryset) -> List[str]:
        """
        Supposed to be implemented by child class, need to return a list of column names.
        This method is used inline because columns list creation may need help from request object
        which isn't available in celery task
        """
        raise NotImplementedError

    def get_csv_too_large_buffer(self) -> io.StringIO:
        """
        It returns an alternative CSV buffer with an appropriate msg to inform user
        """
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, [f'{self.LARGE_CSV_MSG} {self.EMAIL_CSV_MSG}'])
        writer.writeheader()
        buffer.seek(0)
        return buffer

    def get_csv_model(self):
        """
        This method is supposed to return the model class which provides data for CSV
        """
        return getattr(self, 'model', None)

    def get_csv_file_name(self) -> str:
        return self.csv_file_name or self.get_csv_model()._meta.verbose_name_plural


class CSVMixin(CSVFileOrEmailModelMixin):
    """
    This mixin provides a CSV stream of all readable fields of a Serializer
    For it to work properly
        - serializer class should include CSVMixin
        - serializer.Meta.list_serializer_class should point to CSVListSerializer or a subclass of it (optional)

    By default Meta.list_serializer_class doesn't need to be defined
    """

    @classmethod
    def initialize_instance(cls, *args, queryset=None, **kwargs):
        return cls(queryset, many=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_many = False

        # when many=True is used while initializing serializer, DRF uses
        # serializer.Meta.list_serializer_class or serializers.ListSerializer
        # to serialize objects
        # so here we are setting list_serializer_class to CSVListSerializer if not defined
        # or if it is defined, we are making sure that it inherits from CSVListSerializer

        list_serializer_class = getattr(self.Meta, 'list_serializer_class', None)
        if list_serializer_class is None:
            setattr(self.Meta, 'list_serializer_class', CSVListSerializer)
        elif not issubclass(list_serializer_class, CSVListSerializer):
            raise serializers.ValidationError(
                f'{self.__class__.__name__}.Meta.list_serializer_class must be an instance of CSVListSerializer'
            )

    def bind(self, field_name, parent):
        """This method is called by ListSerializer so we are setting csv_many to True"""
        super().bind(field_name, parent)
        self.csv_many = True

    @staticmethod
    def prefixed_name(prefix, name):
        """
        This method decides the pattern column names will follow i.e.
        class SerializerB:
            c = str
            d = str

        class SerializerA:
            a = str
            b = SerializerB

        here column names for SerializerA will be: a, b_c, b_d
        """
        return f'{prefix}_{name}' if prefix else name

    @staticmethod
    def serializer_reference(serializer):
        """
        if it's a list serializer, then serializer.child will have a reference to actual serializer
        """
        return getattr(serializer, 'child', serializer)

    def skip_fields(self, serializer):
        """
        Any fields defined at serializer.Meta.csv_skip_fields will be skipped while creating CSV stream
        """
        serializer = self.serializer_reference(serializer)
        meta = getattr(serializer, 'Meta', None)
        return getattr(meta, 'csv_skip_fields', [])

    def parse_csv_column(self, serializer, columns, column_prefix=None):
        """
        this method takes a serializer/field and translates it's fields as columns
        """
        skip_fields = self.skip_fields(serializer)
        for field in self.serializer_reference(serializer)._readable_fields:
            name = field.field_name
            if name in skip_fields:
                continue
            elif isinstance(field, serializers.Serializer):
                self.parse_csv_column(field, columns, column_prefix=name)
            else:
                columns.append(self.prefixed_name(column_prefix, name))

    def parse_csv_row(self, name, value, row, column_prefix=None):
        """
        takes a field name, its value and row (dict) and updates row with proper column name and value/s
        """
        if isinstance(value, dict):
            for sub_name, sub_value in value.items():
                self.parse_csv_row(sub_name, sub_value, row, column_prefix=name)
        else:
            name = self.prefixed_name(column_prefix, name)
            if name in self._columns_set:
                row[name] = value

    def serializer_representation(self):
        if self.csv_many:
            return self.parent.to_representation(self.instance)
        return [self.to_representation(self.instance)]

    def csv_data(self, request):
        """
        returns a CSV stream and boolean to tell if its the actual CSV or placeholder
        """
        try:
            return True, self.generate_csv(request, self.instance)
        except CSVTooLarge:
            return False, self.get_csv_too_large_buffer()

    def get_csv_model(self):
        return self.Meta.model

    def get_buffer(self, queryset, columns):

        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, columns)
        writer.writeheader()
        writer.writerows(self.get_rows(columns))
        buffer.seek(0)

        return buffer

    def get_columns(self, request, queryset):
        columns= []
        self.parse_csv_column(self, columns)
        return columns

    def get_rows(self, columns):
        self._columns_set = set(columns)
        rows = []
        for instance in self.serializer_representation():
            row = {}
            for name, value in instance.items():
                self.parse_csv_row(name, value, row)
            rows.append(row)
        return rows


class CSVListSerializer(serializers.ListSerializer):

    """when many=True is used, DRF returns ListSerializer (CSVListSerializer in this case) while keeping a reference to
    actual serializer at instance.child. So we are forwarding all CSV related actions to self.child. Because that will
    be the one inheriting from CSVMixin"""

    def __getattr__(self, attr):
        return getattr(self.child, attr)
