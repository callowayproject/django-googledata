import unittest
from django import template
from django.template import Template, Context
from django.conf import settings

class TestTemplateTag(unittest.TestCase):
    def render(self, test_string):
        print_results = "{% for item in top_pages %}{{ item.title }}\n{% endfor %}-----------------------\n"
        t = Template('{% load google_data %}'+test_string+print_results)
        c = Context()
        print t.render(c)
    
    
    def test_template_tag(self):
        test_string = '{% get_top_pages "' + settings.GDATA_TEST_TABLEID + '" as top_pages %}'
        self.render(test_string)
        test_string = '{% get_top_pages "' + settings.GDATA_TEST_TABLEID + '" "num_results=5" as top_pages %}'
        self.render(test_string)
        test_string = '{% get_top_pages "' + settings.GDATA_TEST_TABLEID + '" "days_past=2" as top_pages %}'
        self.render(test_string)
        test_string = '{% get_top_pages "' + settings.GDATA_TEST_TABLEID + '" "path_filter=/news/*" as top_pages %}'
        self.render(test_string)
        test_string = '{% get_top_pages "' + settings.GDATA_TEST_TABLEID + '" "title_sep=|" as top_pages %}'
        self.render(test_string)
        test_string = '{% get_top_pages "' + settings.GDATA_TEST_TABLEID + '" "num_results=5" "path_filter=/news/*" "title_sep=|" as top_pages %}'
        self.render(test_string)
        


if __name__ == "__main__":
    unittest.main()
