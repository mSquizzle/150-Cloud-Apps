#!/usr/bin/env python

from wtforms.widgets.core import HTMLString

class BootstrapRadioWidget(object):
    """
    A wtforms widget to render radio butons using bootstrap components
    """
    def __call__(self, field, **kwargs):
        html = ['<div class="btn-group btn-group-justified" data-toggle="buttons">']
        for val, label, selected in field.iter_choices():
            if selected: 
                html.append('<label class="btn btn-primary active">')
                html.append('<input type="radio" name="' + field.id + '" value="' + val + '" autocomplete="off" checked>' + label)
            else:
                html.append('<label class="btn btn-primary">')
                html.append('<input type="radio" name="' + field.id + '" value="' + val + '" autocomplete="off">' + label)
            html.append('</label>')
        html.append('</div>')
        return HTMLString(u'\n'.join(html))

class InlineRadioWidget(object):
    """
    A nice description
    """
    def __call__(self, field, **kwargs):
        html = ['<div class="form-group">']
        for val, label, selected in field.iter_choices():
            html.append('<label class="radio-inline">')
            html.append('<input type="radio" name="' + field.id + '" value="' + val + '" autocomplete="off">' + label)
            html.append('</label>')
        html.append('</div>')
        return HTMLString(u'\n'.join(html))
