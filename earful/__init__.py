import os
import re
from logging import (
    getLogger,
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL,
    )


logger = getLogger(__name__)

try:
    import jinja2
except ImportError:
    logger.warning("No Jinja2 support")

try:
    import markdown
except ImportError:
    logger.warning("No Markdown support")


LEVEL_NAMES = {
    DEBUG: 'Debug',
    INFO: 'Info',
    WARNING: 'Warning',
    ERROR: 'Error',
    CRITICAL: 'Critical',
}


class Message(object):
    def __init__(self, level, summary, url=None, **context):
        self.level = level
        self.url = None
        self.context = {
            'level': level,
            'levelname': LEVEL_NAMES[level],
            'url': url,
        }
        self.context.update(context)
        self.summary = summary.format(**self.context)
        self.context['summary'] = self.summary


    def __str__(self):
        return "{}: {}".format(LEVEL_NAMES[self.level], self.summary)


class Template(object):
    OUTPUT_FORMATS = {'htm': 'html', 'html': 'html', 'md': 'markdown', 'markdown': 'markdown', 'txt': 'text', 'text': 'text'}
    TEMPLATE_FORMATS = {'python': 'python', 'jinja': 'jinja', 'jinja2': 'jinja', 'txt': 'text', 'text': 'text'}

    def __init__(self, template_dir=None, template_file=None, template_string=None, template_format=None, output_format=None):
        try:
            assert template_file or template_string, "One of template_file or template_string is required"
            if template_string:
                assert template_format, "If template_string is given then template_format is required"

            if output_format:
                try:
                    output_format = self.OUTPUT_FORMATS[output_format]
                except KeyError:
                    raise AssertionError("Invalid output format: " + output_format)
            else:
                if template_file:
                    # Try to get the output file off the end of the given file
                    try:
                        output_format = os.path.splitext(template_file)[1]
                        output_format = self.OUTPUT_FORMATS[output_format]
                    except IndexError:
                        raise AssertionError("No output format found in " + template_file)
                    except KeyError:
                        raise AssertionError("Invalid output format: " + output_format)
                else:
                    # We can default this
                    output_format = 'text'

            if template_format:
                try:
                    template_format = self.TEMPLATE_FORMATS[template_format]
                except KeyError:
                    raise AssertionError("Invalid template_format: " + template_format)
            else:
                # We can't default this
                assert template_file, "Trying to get a template format with no filename"
                # Try to get the output file off the end of the given file
                try:
                    template_format = os.path.splitext(os.path.splitext(template_file)[0])[1]
                    template_format = self.TEMPLATE_FORMATS[template_format]
                except IndexError:
                    raise AssertionError("No template format found in " + template_file)
                except KeyError:
                    raise AssertionError("Invalid template format: " + template_format)
        except AssertionError as e:
            raise ValueError(str(e))

        self.template_dir = template_dir
        self.template_file = template_file
        self.template_string = template_string
        self.template_format = template_format
        self.output_format = output_format
        self.template = None

    def get_template(self):
        if self.template is None:
            if self.template_format == 'jinja':
                try:
                    jinja2
                except NameError:
                    raise RuntimeError("No Jinja2 support")

                if self.template_string:
                    self.template = jinja2.Template(self.template_string)
                else:
                    self.template = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_dir)).get_template(self.template_file)
            elif self.template_format in ('python', 'text'):
                if self.template_string:
                    self.template = self.template_string
                else:
                    with open(os.path.join(self.template_dir, self.template_file), 'r') as fp:
                        self.template = fp.read()
            else:
                raise RuntimeError("Invalid template format: " + self.template_format)
        return self.template

    def render(self, message):
        rendered = {'text': None, 'html': None}
        rendered_first_pass = None

        if self.template_format == 'jinja':
            rendered_first_pass = self.template.render(**message.context)
        elif self.template_format == 'python':
            rendered_first_pass = self.template.format(**message.context)
        elif self.template_format == 'text':
            rendered_first_pass = self.template
        else:
            raise RuntimeError("Invalid template format: " + self.template_format)

        if self.output_format == 'html':
            rendered['html'] = rendered_first_pass
        elif self.output_format == 'markdown':
            rendered['text'] = rendered_first_pass
            try:
                rendered['html'] = markdown.markdown(rendered_first_pass)
            except NameError:
                raise RuntimeError("No Markdown support")
        elif self.output_format == 'text':
            rendered['text'] = rendered_first_pass
        else:
            raise RuntimeError("Invalid template format: " + self.template_format)
