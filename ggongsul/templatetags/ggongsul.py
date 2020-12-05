from django import template

from ggongsul.core.renderers import ImageHTMLFormRenderer

register = template.Library()


@register.simple_tag
def render_image_form(serializer, template_pack=None):
    style = {"template_pack": template_pack} if template_pack else {}
    renderer = ImageHTMLFormRenderer()
    return renderer.render(serializer.data, None, {"style": style})


@register.simple_tag
def render_field(field, style):
    renderer = style.get("renderer", ImageHTMLFormRenderer())
    return renderer.render_field(field, style)


@register.filter(name="dict_key")
def dict_key(d, k):
    """Returns the given key from a dictionary."""
    return d[k]
