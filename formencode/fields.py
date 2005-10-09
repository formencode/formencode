## FunFormKit, a Webware Form processor
## Copyright (C) 2001, Ian Bicking <ianb@colorstudy.com>
##  
## This library is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public
## License as published by the Free Software Foundation; either
## version 2.1 of the License, or (at your option) any later version.
##
## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public
## License along with this library; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
## NOTE: In the context of the Python environment, I interpret "dynamic
## linking" as importing -- thus the LGPL applies to the contents of
## the modules, but make no requirements on code importing these
## modules.
"""
Fields for use with Forms.  The Field class gives the basic interface,
and then there's bunches of classes for the specific kinds of fields.
"""

import urllib
PILImage = None
import os
from htmlgen import html
True, False = (1==1), (0==1)
from declarative import Declarative

class NoDefault: pass

class none_dict(dict):

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError
        return self.get(attr)

class Context(object):

    def __init__(self, name_prefix='', id_prefix='', defaults=None,
                 **kw):
        self.name_prefix = name_prefix
        self.id_prefix = id_prefix
        self.defaults = defaults
        for name, value in kw.items():
            setattr(name, value)
        self.options = none_dict(kw)

    def name(self, field, adding=None):
        if not field.name:
            assert self.name_prefix, (
                "Field has not name, and context has no name_prefix")
            name = self.name_prefix
        elif self.name_prefix:
            name = self.name_prefix + field.name
        else:
            name = field.name
        if adding:
            return name + '.' + adding
        else:
            return name

    def id(self, field):
        return self.id_prefix + field.name

    def default(self, field):
        if self.defaults:
            name = self.name(field)
            return self.defaults.get(name)
        else:
            return None

    def push_attr(self, **kw):
        if 'add_name' in kw:
            if self.name_prefix:
                kw['name_prefix'] = self.name_prefix+'.'+kw.pop('add_name')
            else:
                kw['name_prefix'] = kw.pop('add_name')
        restore = {}
        for name, value in kw.items():
            restore[name] = getattr(self, name, PopValue.no_value)
            setattr(self, name, value)
        return PopValue(self, restore)

class PopValue(object):

    no_value = []

    def __init__(self, object, restore_values):
        self.object = object
        self.restore_values = restore_values

    def pop_attr(self):
        for name, value in self.restore_values.items():
            if value is self.no_value:
                delattr(self.object, name)
            else:
                setattr(self.object, name, value)

class Field(Declarative):

    description = None
    id = None
    static = False
    hidden = False
    requires_label = True
    default = None
    name = None
    width = None
    enctype = None

    def __init__(self, *args, **kw):
        if args:
            context = args[0]
            args = args[1:]
            kw['name'] = context.name_prefix + kw.get('name', '')
        super(Field, self).__init__(*args, **kw)

    def render(self, context):
        if self.hidden:
            return self.html_hidden(context)
        elif self.static:
            return self.html_static(context)
        else:
            return self.html(context)

    def html_hidden(self, context):
        """The HTML for a hidden input (<input type="hidden">)"""
        return html.input(
            type='hidden',
            id=context.id(self),
            name=context.name(self),
            value=context.default(self))

    def html_static(self, context):
        return html(
            self.html_hidden(context),
            context.default(self))

    def html(self, context):
        """The HTML input code"""
        raise NotImplementedError

    def style_width(self):
        if self.width:
            if isinstance(self.width, int):
                return 'width: %s%%' % self.width
            else:
                return 'width: %s' % self.width
        else:
            return None

    style_width = property(style_width)

    def load_javascript(self, filename):
        f = open(os.path.join(os.path.dirname(__file__),
                              'javascript', filename))
        c = f.read()
        f.close()
        return c

class Form(Declarative):

    action = None
    id = None
    method = "POST"
    fields = []
    form_name = None
    enctype = None

    def __init__(self, *args, **kw):
        Declarative.__init__(self, *args, **kw)

    def render(self, context):
        assert self.action, "You must provide an action"
        contents = html(
            [f.render(context) for f in self.fields])
        enctype = self.enctype
        for field in self.fields:
            if field.enctype:
                if enctype is None or enctype == field.enctype:
                    enctype = field.enctype
                else:
                    raise ValueError(
                        "Conflicting enctypes; need %r, field %r wants %r"
                        % (enctype, field, field.enctype))
        return html.form(
            action=self.action,
            method=self.method,
            name=context.name(self),
            id=context.id(self),
            enctype=enctype,
            c=contents)

class Layout(Field):

    append_to_label = ':'
    use_fieldset = False
    legend = None
    requires_label = False
    fieldset_class = 'formfieldset'

    def html(self, context):
        normal = []
        hidden = []
        for field in self.fields:
            if field.hidden:
                hidden.append(field.render(context))
            else:
                normal.append(field)
        self.wrap(hidden, normal, options)

    def wrap(self, hidden, normal, context):
        hidden.append(self.wrap_fields(
            [self.wrap_field(field, context) for field in self.normal],
            context))
        return hidden

    def wrap_field(self, field, context):
        return html(self.format_label(field, context),
                    field.render(context),
                    html.br)

    def format_label(self, field, context):
        label = ''
        if self.requires_label:
            label = field.description
            if label:
                label = label + self.append_to_label
        return label

    def wrap_fields(self, rendered_fields, context):
        if not self.use_fieldset:
            return rendered_fields
        legend = self.legend
        if legend:
            legend = html.legend(legend)
        else:
            legend = ''
        return html.fieldset(legend, rendered_fields,
                             class_=self.fieldset_class)

class TableLayout(Layout):

    width = None
    label_class = 'formlabel'
    field_class = 'formfield'
    label_align = None
    table_class = 'formtable'
    

    def wrap_field(self, field, context):
        return html.tr(
            html.td(self.format_label(field, context),
                    align=self.label_align,
                    class_=self.label_class),
            html.td(field.render(context),
                    class_=self.field_class))

    def wrap_fields(self, rendered_fields, context):
        return html.table(rendered_fields,
                          width=self.width,
                          class_=self.table_class,
                          c=rendered_fields)

class FormTableLayout(Layout):

    layout = None
    append_to_label = ''

    def wrap(self, hidden, normal, context):
        fields = {}
        for field in normal:
            fields[field.name] = field
        layout = self.layout
        assert layout, "You must provide a layout for %s" % self
        output = []
        for line in layout:
            if isinstance(line, (str, unicode)):
                line = [line]
            output.append(self.html_line(line, fields, context))
        hidden.append(self.wrap_fields(output, context))
        return hidden

    def html_line(self, line, fields, context):
        """
        Formats lines: '=text' means a literal of 'text', 'name' means
        the named field, ':name' means the named field, but without a
        label.
        """
        cells = []
        for item in line:
            if item.startswith('='):
                cells.append(html.td(item))
                continue
            if item.startswith(':'):
                field = fields[item[1:]]
                label = ''
            else:
                field = fields[item]
                label = self.format_label(field, context)
            if label:
                label = html(label, html.br)
            cells.append(html.td('\n', label, 
                                 field.render(context),
                                 valign="bottom"))
            cells.append('\n')
        return html.table(html.tr(cells))

class SubmitButton(Field):
    """
    Not really a field, but a widget of sorts.

    methodToInvoke is the name (string) of the servlet method that should
    be called when this button is hit.

    You can use suppressValidation for large-form navigation (wizards),
    when you want to save the partially-entered and perhaps invalid
    data (e.g., for the back button on a wizard).  You can load that data
    back in by passing the fields to FormRequest/From as httpRequest.

    The confirm option will use JavaScript to confirm that the user
    really wants to submit the form.  Useful for buttons that delete
    things.

    Examples::

        >>> prfield(SubmitButton(description='submit'))
        <input type="submit" value="submit" name="f" />
        >>> prfield(SubmitButton(confirm='Really?'))
        <input type="submit" value="Submit" onclick="return window.confirm(&apos;Really?&apos;)" name="f" />

    """

    confirm = None
    default_description = "Submit"
    description = ''
    requires_label = False

    def html(self, context):
        if self.confirm:
            query = ('return window.confirm(\'%s\')' % 
                     javascript_quote(self.confirm))
        else:
            query = None
        description = ((self.description) or 
                       self.default_description)
        return html.input(
            type='submit',
            name=context.name(self),
            value=description,
            onclick=query)

    def html_hidden(self, context):
        if context.default(self):
            return html.input.hidden(
                name=context.name(self),
                value=context.default(self))
        else:
            return ''

class ImageSubmit(SubmitButton):

    """
    Like SubmitButton, but with an image.

    Examples::

        >>> prfield(ImageSubmit(img_src='test.gif'))
        <input src="test.gif" name="f" border="0" value="" type="image" alt="" />
    """

    img_height = None
    img_width = None
    border = 0

    def html(self, context):
        return html.input(
            type='image',
            name=context.name(self),
            value=self.description,
            src=self.img_src,
            height=self.img_height,
            width=self.img_width,
            border=self.border,
            alt=self.description)

class Hidden(Field):
    """
    Hidden field.  Set the value using form defaults.

    Since you'll always get string back, you are expected to only pass
    strings in (unless you use a converter like AsInt).

    Examples::

        >>> prfield(Hidden(), defaults={'f': 'a&value'})
        <input id="f" type="hidden" name="f" value="a&amp;value" />
    """

    requires_label = False
    hidden = True

    def html(self, context):
        return self.html_hidden(context)

class Text(Field):

    """
    Basic text field.

    Examples::

        >>> t = Text()
        >>> prfield(t)
        <input type="text" name="f"/>
        >>> prfield(t, defaults={'f': "&whatever&"})
        <input type="text" name="f" value="&amp;whatever&amp;" />
        >>> prfield(t(maxlength=20, size=10))
        <input type="text" name="f" size="10" maxlength="20" />
    """

    size = None
    maxlength = None
    width = None

    def html(self, context):
        return html.input(
            type='text',
            name=context.name(self),
            value=context.default(self),
            maxlength=self.maxlength,
            size=self.size,
            style=self.style_width)

class Textarea(Field):

    """
    Basic textarea field.

    Examples::

        >>> prfield(Textarea(), defaults={'f': '<text>'})
        <textarea name="f" rows="10" cols="60" wrap="SOFT">&lt;text&gt;</textarea>
    """

    rows = 10
    cols = 60
    wrap = "SOFT"
    width = None

    def html(self, context):
        return html.textarea(
            name=context.name(self),
            rows=self.rows,
            cols=self.cols,
            wrap=self.wrap or None,
            style=self.style_width,
            c=context.default(self))

class Password(Text):

    """
    Basic password field.

    Examples::

        >>> prfield(Password(maxlength=10), defaults={'f': 'pass'})
        <input type="password" name="f" maxlength="10" value="pass" />
    """

    def html(self, context):
        return html.input(
            type='password',
            name=context.name(self),
            value=context.default(self),
            maxlength=self.maxlength,
            size=self.size,
            style=self.style_width)

class Select(Field):
    """
    Creates a select field, based on a list of value/description
    pairs.  The values do not need to be strings.

    If nullInput is given, this will be the default value for an
    unselected box.  This would be the "Select One" selection.  If you
    want to give an error if they do not select one, then use the
    NotEmpty() validator.  They will not get this selection if the
    form is being asked for a second time after they already gave a
    selection (i.e., they can't go back to the null selection if
    they've made a selection and submitted it, but are presented the
    form again).  If you always want a null selection available,
    put that directly in the selections.

    Examples::

        >>> prfield(Select(selections=[(1, 'One'), (2, 'Two')]), defaults=dict(f='2'))
        <select name="f">
        <option value="1">One</option>
        <option value="2" selected="selected">Two</option>
        </select>
        >>> prfield(Select(selections=[(1, 'One')], null_input='Choose'))
        <select name="f">
        <option value="">Choose</option>
        <option value="1">One</option>
        </select>
    """

    selections = []
    null_input = None
    size = None

    def html(self, context, subsel=None):
        selections = self.selections
        null_input = self.null_input
        if not context.default(self) and null_input:
            # @@: list()?
            selections = [('', null_input)] + selections
        if subsel:
            return subsel(selections, context)
        else:
            return self.selection_html(selections, context)

    def selection_html(self, selections, context):
        return html.select(
            name=context.name(self),
            size=self.size,
            c=[html.option(desc,
                           value=value,
                           selected=self.selected(value, context.default(self)))
               for (value, desc) in selections])

    def selected(self, key, default):
        if str(key) == str(default):
            return 'selected'
        else:
            return None

class Ordering(Select):

    """
    Rendered as a select field, this allows the user to reorder items.
    The result is a list of the items in the new order.

    Examples::

        >>> o = Ordering(selections=[('a', 'A'), ('b', 'B')])
        >>> prfield(o, chop=('<script ', '</script>'))
        <select name="f.func" size="2">
        <option value="a">A</option>
        <option value="b">B</option>
        </select>
        <br />
        <input type="button" value="up" onclick="up(this)" />
        <input type="button" value="down" onclick="down(this)" />
        <input type="hidden" name="f" value="a b " />
    """

    show_reset = False

    def selection_html(self, selections, context):
        size = len(selections)
        
        if context.default(self):
            new_selections = []
            for default_value in context.default(self):
                for value, desc in selections:
                    if str(value) == str(default_value):
                        new_selections.append((value, desc))
                        break
            assert len(new_selections) == len(selections), (
                "Defaults don't match up with the cardinality of the "
                "selections")
            selections = new_selections

        encoded_value = ''
        for key, value in selections:
            encoded_value = encoded_value + urllib.quote(str(key)) + " "

        result = []
        result.append(
            html.select(
            name=context.name(self, adding='func'),
            size=size,
            c=[html.option(desc, value=value)
               for value, desc in selections]))
        result.append(html.br())
        for name, action in self.buttons(context):
            result.append(html.input(
                type='button',
                value=name,
                onclick=action))
        result.append(html.input(
            type='hidden',
            name=context.name(self),
            value=encoded_value))
        result.append(html.script(
            type='text/javascript',
            c=self.javascript(context)))
        return result

    def buttons(self, context):
        buttons = [('up', 'up(this)'),
                   ('down', 'down(this)')]
        if self.show_reset:
            buttons.append(('reset', 'reset_entries(this)'))
        return buttons

    def javascript(self, context):
        name = context.name(self, adding='func')
        hidden_name = context.name(self)
        return (self.load_javascript('ordering.js')
                % {'name': name, 'hidden_name': hidden_name})

class OrderingDeleting(Ordering):
    """
    Like Ordering, but also allows deleting entries.

    Examples::

        >>> o = OrderingDeleting(selections=[('a', 'A'), ('b', 'B')])
        >>> prfield(o(confirm_on_delete='Yeah?', chop=('<script ', '</script>')))
        <select name="f.func" size="2">
        <option value="a">A</option>
        <option value="b">B</option>
        </select>
        <br />
        <input type="button" value="up" onclick="up(this)" />
        <input type="button" value="down" onclick="down(this)" />
        <input type="button" value="delete"
         onclick="window.confirm('Yeah?') ? delete_entry(this) : false" />
        <input type="hidden" name="f" value="a b " />
        <script type="text/javascript">*</script>
    """

    confirm_on_delete = None

    def buttons(self, context):
        buttons = Ordering.buttons(self, context)
        confirm_on_delete = self.confirm_on_delete
        if confirm_on_delete:
            delete_button = (
                'delete',
                'window.confirm(\'%s\') ? delete_entry(this) : false'
                % javascript_quote(confirm_on_delete))
        else:
            delete_button = ('delete', 'delete_entry(this)')
        new_buttons = []
        for button in buttons:
            if button[1] == 'reset_entries(this)':
                new_buttons.append(delete_button)
                delete_button = None
            new_buttons.append(button)
        if delete_button:
            new_buttons.append(delete_button)
        return new_buttons

    def javascript(self, context):
        js = Ordering.javascript(self, context)
        return js + ('''
        function deleteEntry(formElement) {
            var select;
            select = getSelect(formElement);
            select.options[select.selectedIndex] = null;
            saveValue(select);
        }
        ''')

class Radio(Select):

    """
    Radio selection; very similar to a select, but with a radio.

    Example::

        >>> prfield(Radio(selections=[('a', 'A'), ('b', 'B')]),
        ...         defaults=dict(f='b'))
        <input type="radio" name="f" value="a" id="f_1" />
        <label for="f_1">A</label><br />
        <input type="radio" name="f" value="b" id="f_2" checked="checked" />
        <label for="f_2">B</label><br />
        
    """

    def selection_html(self, selections, context):
        id = 0
        result = []
        for value, desc in selections:
            id = id + 1
            if self.selected(value, context.default(self)):
                checked = 'checked'
            else:
                checked = None
            result.append(html.input(
                type='radio',
                name=context.name(self),
                value=value,
                id="%s_%i" % (context.name(self), id),
                checked=checked))
            result.append(html.label(
                for_='%s_%i' % (context.name(self), id),
                c=desc))
            result.append(html.br())
        return result
            
class MultiSelect(Select):

    """
    Selection that allows multiple items to be selected.

    A list will always be returned.  The size is, by default, the same
    as the number of selections (so no scrolling by the user is
    necessary), up to maxSize.

    Examples::

        >>> sel = MultiSelect(selections=[('&a', '&amp;A'), ('&b', '&amp;B'), (1, 1)])
        >>> prfield(sel)
        <select size="3" multiple="multiple" name="f">
        <option value="&amp;a">&amp;amp;A</option>
        <option value="&amp;b">&amp;amp;B</option>
        <option value="1">1</option>
        </select>
        >>> prfield(sel, defaults=dict(f=['&b', '1']))
        <select size="3" multiple="multiple" name="f">
        <option value="&amp;a">&amp;amp;A</option>
        <option value="&amp;b" selected="selected">&amp;amp;B</option>
        <option value="1" selected="selected">1</option>
        </select>
    """

    size = NoDefault
    max_size = 10

    def selection_html(self, selections, context):
        result = []
        size = self.size
        if size is NoDefault:
            size = min(len(selections), self.max_size)
        result.append(html.select(
            name=context.name(self),
            size=size,
            multiple="multiple",
            c=[html.option(desc,
                           value=value,
                           selected=self.selected(value, context.default(self))
                           and "selected" or None)
               for value, desc in selections]))

    def selected(self, key, default):
        if not isinstance(default, (tuple, list)):
            if default is None:
                return False
            default = [default]
        return str(key) in map(str, default)

    def html_hidden(self, context):
        default = context.default(self)
        if not isinstance(default, (tuple, list)):
            if default is None:
                default = []
            else:
                default = [default]
        return html(
            [html.input.hidden(name=context.name(self),
                               value=value)
             for value in default])

    def selection_html(self, selections, context):
        result = []
        size = self.size
        if size is NoDefault:
            size = min(len(selections), self.max_size)
        result.append(html.select(
            name=context.name(self),
            size=size,
            multiple="multiple",
            c=[html.option(desc,
                           value=value,
                           selected=self.selected(value, context.default(self))
                           and "selected" or None)
               for value, desc in selections]))
        return result

class MultiCheckbox(MultiSelect):

    """
    Like MultiSelect, but with checkboxes.

    Examples::

        >>> sel = MultiCheckbox(selections=[('&a', '&amp;A'), ('&b', '&amp;B'), (1, 1)])
        >>> prfield(sel, defaults=dict(f='&a'))
        <input type="checkbox" value="&amp;a" name="f" checked="checked"
         id="f_1" />
        <label for="f_1">&amp;amp;A</label><br />
        <input type="checkbox" value="&amp;b" name="f" id="f_2" />
        <label for="f_2">&amp;amp;B</label><br />
        <input type="checkbox" value="1" name="f" id="f_3" />
        <label for="f_3">1</label><br />
    """

    def selection_html(self, selections, context):
        result = []
        id = 0
        for value, desc in selections:
            id = id + 1
            result.append(html.input(
                type='checkbox',
                name=context.name(self),
                id="%s_%i" % (context.name(self), id),
                value=value,
                checked=self.selected(value, context.default(self))
                and "checked" or None))
            result.append(html.label(
                " " + str(desc),
                for_="%s_%i" % (context.name(self), id)))
            result.append(html.br())
        return result


class Checkbox(Field):

    """
    Simple checkbox.

    Examples::

        >>> prfield(Checkbox(), defaults=dict(f=0))
        <input type="checkbox" name="f" />
        >>> prfield(Checkbox(), defaults=dict(f=1))
        <input type="checkbox" name="f" checked="checked" />
        
    """

    def html(self, context):
        return html.input(
            type='checkbox',
            name=context.name(self),
            checked = context.default(self) and "checked" or None)

class File(Field):
    """
    accept is the a list of MIME types to accept.  Browsers pay
    very little attention to this, though.

    By default it will return a cgi FieldStorage object -- use .value
    to get the string, .file to get a file object, .filename to get
    the filename.  Maybe other stuff too.  If you set
    returnString=True it will return a string with the contents of the
    uploaded file.

    You can't have any validators unless you do returnString.

    Examples::

        >>> prfield(File())
        <input type="file" name="f" />
    """

    accept = None
    size = None
    enctype = "multipart/form-data"

    def html(self, context):
        accept = self.accept
        if accept and accept is not None:
            mime_list = ",".join(accept)
        else:
            mime_list = None
        return html.input(
            type='file',
            name=context.name(self),
            size=self.size,
            accept=mime_list)
        

class StaticText(Field):

    """
    A static piece of text to be put into the field, useful only
    for layout purposes.

    Examples::

        >>> prfield(StaticText('some <b>HTML</b>'))
        some <b>HTML</b>
        >>> prfield(StaticText('whatever', hidden=1))
    """

    text = ''
    requires_label = False
    __unpackargs__ = ('text',)

    def html(self, context):
        default = context.default(self)
        if default is not None:
            return str(default)
        else:
            return str(self.text)

    def html_hidden(self, context):
        return ''

class ColorPicker(Field):

    """
    This field allows the user to pick a color from a popup window.
    This window contains a pallete of colors.

    They can also enter the hex value of the color.  A color swatch is
    updated with their chosen color.

    Examples::

        >>> cp = ColorPicker(color_picker_url='/colorpick.html')
        >>> prfield(cp, defaults={'f': '#ff0000'})
        <table border="0" cellspacing="0">
        <tr>
        <td id="f.pick"
         style=\"background-color: #ff0000; border: thin black solid;\" width="20">
          </td>
        <td>
          <input name="f"
           onchange="document.getElementById(&apos;f.pick&apos;).style.backgroundColor = this.value; return true"
           size="8" type="text" value=\"#ff0000\"/>
          <input onclick="colorpick(this, &apos;f&apos;, &apos;f.pick&apos;)"
           type="button" value="pick" />
         </td>
         </tr>
         </table>
    """

    color_picker_url = None

    def html(self, context):
        js = self.javascript(context)
        color_picker_url = self.color_picker_url
        assert color_picker_url, (
            'You must give a base URL for the color picker')
        name = context.name(self)
        color_id = context.name(self, adding='pick')
        default_color = context.default(self) or '#ffffff'
        return html.table(
            cellspacing=0, border=0,
            c=[html.tr(
            html.td(width=20, id=color_id,
                    style="background-color: %s; border: thin black solid;" % default_color,
                    c=" "),
            html.td(
            html.input(type='text', size=8,
                       onchange="document.getElementById('%s').style.backgroundColor = this.value; return true" % color_id,
                       name=name, value=context.default(self)),
            html.input(type='button', value="pick",
                       onclick="colorpick(this, '%s', '%s')" % (name, color_id))))])

    def javascript(self, context):
        return """\
function colorpick(element, textFieldName, color_id) {
    win = window.open('%s?form='
                      + escape(element.form.attributes.name.value)
                      + '&field=' + escape(textFieldName)
                      + '&colid=' + escape(color_id),
                      '_blank',
                      'dependent=no,directories=no,width=300,height=130,location=no,menubar=no,status=no,toolbar=no');
}
""" % self.color_picker_url


########################################
## Utility functions
########################################

def javascript_quote(value):
    """
    Quote a Python value as a Javascript literal.
    
    I'm depending on the fact that repr falls back on single quote
    when both single and double quote are there.  Also, JavaScript uses
    the same octal \\ing that Python uses.

    Examples::

        >>> javascript_quote('a')
        'a'
        >>> javascript_quote('\\n')
        '\\\\n'
        >>> javascript_quote('\\\\')
        '\\\\\\\\'
    """
    return repr('"' + str(value))[2:-1]
    

def prfield(field, chop=None, **kw):
    """
    Prints a field, useful for doctests.
    """
    if not kw.has_key('name'):
        kw['name'] = 'f'
    name = kw.pop('name')
    context = Context(**kw)
    context.form = Form()
    result = html.str(field(name=name).render(context))
    if chop:
        pos1 = result.find(chop[0])
        pos2 = result.find(chop[1])
        if pos1 == -1 or pos2 == -1:
            print 'chop (%s) not found' % repr(chop)
        else:
            result = result[:pos1] + result[pos2+len(chop[1]):]
    print result
    
if __name__ == '__main__':
    import doctest
    import doctest_xml_compare
    doctest_xml_compare.install()
    doctest.testmod()
    
