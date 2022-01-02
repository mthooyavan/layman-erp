from drf_yasg.inspectors import SwaggerAutoSchema


class CustomAutoSchema(SwaggerAutoSchema):
    def get_operation_id(self, operation_keys=None):
        operation_id = super(CustomAutoSchema, self).get_operation_id(operation_keys) # pylint: disable=super-with-arguments
        operation_array = operation_id.split('_')
        return ' '.join([operation_array[1], operation_array[0]]).capitalize()

    def get_tags(self, operation_keys=None):
        tags = super(CustomAutoSchema, self).get_tags(operation_keys) # pylint: disable=super-with-arguments
        return [tag.capitalize() for tag in tags]
