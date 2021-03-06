from django import template
from googledata.utils import get_top_pages
import re

register = template.Library()


class GetTopPagesNode(template.Node):
    """
    Renders the top pages to the context variable
    """
    def __init__(self, table_id, var_name, **kwargs):
        self.table_id = table_id
        self.var_name = var_name
        self.kwargs = kwargs
    
    def render(self, context):
        resolved_kwargs = {}
        for key, val in self.kwargs.items():
            try:
                resolved_kwargs[key] = template.Variable(val).resolve(context)
            except template.VariableDoesNotExist:
                resolved_kwargs[key] = val
        context[self.var_name] = get_top_pages(self.table_id, **resolved_kwargs)
        return ''
    

def do_get_top_pages(parser, token):
    """
    Return the top pages based on parameters
    
    Called as {% get_top_pages "ga_table_id" ["num_results=10"] ["days_past=1"] ["path_filter=''"] ["title_sep=''"]  as variable_name %}
    
    Other than the ga_table_id parameter and the "as variable_name", all other parameters are optional
    """
    valid_params = ('num_results', 'days_past', 'path_filter', 'title_sep')
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    
    m = re.search(r'"(..:.+?)"\s*(.*?) as (\w+)', args)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments. It requires at least a ga_tableid and variable name." % tag_name
    table_id, key_args, var_name = m.groups()
    kwargs = {}
    for karg in key_args.split():
        key, val = karg.strip('"').split('=')
        if key in valid_params:
            kwargs[str(key)] = str(val)
    return GetTopPagesNode(table_id, var_name, **kwargs)

register.tag('get_top_pages', do_get_top_pages)