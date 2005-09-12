from formencode.htmlform import HTMLForm
from formencode.schema import Schema
from formencode import validators
from WebKit import Page


page_style = """
<html>
 <head>
  <title>Tell me about yourself</title>
 </head>
 <body>

 <h1>Tell me about yourself</h1>
 <p><i>A FormEncode example</i></p>

 %s

 </body></html>"""

form_template = '''
<form action="" method="POST">
<input type="hidden" name="_action" value="save">

Your name:<br>
<form:error name="name">
<input type="text" name="name">
<br>

Your age:<br>
<form:error name="age">
<input type="text" name="age">
<br>

Your favorite color:<br>
<form:error name="color">
<input type="checkbox" value="red"> Red<br>
<input type="checkbox" value="blue"> Blue<br>
<input type="checkbox" value="black"> Black<br>
<input type="checkbox" value="green"> Green<br>
<br>
'''

class FormSchema(Schema):
    name = validators.StringCol(not_empty=True)
    age = validators.IntCol(min=13, max=99)
    color = compound.All(validators.Set(),
                         validators.OneOf(['red', 'blue', 'black', 'green']


class webware_servlet(Page):

    def awake(self, trans):
        Page.awake(self, trans)
        self.form = HTMLForm(form_template, FormSchema)

    def actions(self):
        return ['save']

    def defaultAction(self):
        # No form submitted
        self.rendered_form = self.form.render(
            defaults=self.getDefaults())
        self.showForm()

    def save(self):
        results, errors = self.form.validate(
            self.request().fields(), self)
        if results is not None:
            self.doAction(results)
        else:
            self.rendered_form = self.form.render(
                defaults=self.request().fields(),
                errors=errors)
            self.showForm()
        
    def showForm(self):
        self.write(page_style % self.rendered_form)
        
