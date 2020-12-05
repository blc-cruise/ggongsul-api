from django.template import loader
from rest_framework import serializers
from rest_framework.renderers import HTMLFormRenderer


class ImageHTMLFormRenderer(HTMLFormRenderer):
    def render_field(self, field, parent_style):
        if isinstance(field._field, serializers.HiddenField):
            return ""

        style = {}
        if hasattr(field, "_proxy_class"):
            if field._proxy_class is serializers.ImageField:
                style = {"template": "image_input.html", "input_type": "file"}
            elif field._proxy_class is serializers.ChoiceField:
                style = {"base_template": "radio.html"}

        if not style:
            style = self.default_style[field].copy()

        style.update(field.style)
        if "template_pack" not in style:
            style["template_pack"] = parent_style.get(
                "template_pack", self.template_pack
            )
        style["renderer"] = self

        # Get a clone of the field with text-only value representation.
        field = field.as_form_field()

        if style.get("input_type") == "datetime-local" and isinstance(field.value, str):
            field.value = field.value.rstrip("Z")

        if "template" in style:
            template_name = style["template"]
        else:
            template_name = (
                style["template_pack"].strip("/") + "/" + style["base_template"]
            )

        template = loader.get_template(template_name)
        context = {"field": field, "style": style}
        return template.render(context)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render serializer data and return an HTML form, as a string.
        """
        renderer_context = renderer_context or {}
        form = data.serializer

        style = renderer_context.get("style", {})
        if "template_pack" not in style:
            style["template_pack"] = self.template_pack
        style["renderer"] = self

        template_pack = style["template_pack"].strip("/")
        template_name = template_pack + "/" + self.base_template
        template = loader.get_template(template_name)
        context = {"form": form, "style": style}

        return template.render(context)
