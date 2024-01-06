from django.http import JsonResponse
from django.utils.encoding import force_str
from django.db.models.fields.files import ImageFieldFile

from phonenumber_field.phonenumber import PhoneNumber


class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(self.get_data(context), **response_kwargs, safe=False)

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context

    def ajax_response_form(self, form):
        form_spec = {
            "fields": {},
            "field_order": [],
            "errors": form.non_field_errors(),
        }
        for field in form:
            field_spec = {
                "label": force_str(field.label),
                "value": field.value(),
                "help_text": force_str(field.help_text),
                "errors": [force_str(e) for e in field.errors],
                "widget": {
                    "attrs": {
                        k: force_str(v) for k, v in field.field.widget.attrs.items()
                    }
                },
            }

            if type(field_spec['value']) is PhoneNumber:
                field_spec['value'] = field_spec['value'].raw_input

            elif type(field_spec['value']) is ImageFieldFile:
                print('this is vlaue: ', str(field_spec['value']))
                field_spec['value'] = str(field_spec['value'])

            form_spec["fields"][field.html_name] = field_spec
            form_spec["field_order"].append(field.html_name)
        return form_spec
