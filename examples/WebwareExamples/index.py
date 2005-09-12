from formencode.htmlform import HTMLForm
from formencode import validators, compound, schema
from WebKit.Page import Page


page_style = """
<html>
 <head>
  <title>Tell me about yourself</title>
  <style type="text/css">
    .error {background-color: #ffdddd}
    .error-message {border: 2px solid #f00}
  </style>
 </head>
 <body>

 <h1>Tell me about yourself</h1>
 <p><i>A FormEncode example</i></p>

 %s

 </body></html>"""

form_template = '''
<form action="" method="POST">
<input type="hidden" name="_action_" value="save">

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

<input type="submit" value="submit">
</form>
'''

class FormSchema(schema.Schema):
    name = validators.String(not_empty=True)
    age = validators.Int(min=13, max=99)
    color = compound.All(validators.Set(),
                         validators.OneOf(['red', 'blue', 'black', 'green']))
    filter_extra_fields = True
    allow_extra_fields = True


class index(Page):

    def awake(self, trans):
        Page.awake(self, trans)
        self.form = HTMLForm(form_template, FormSchema)
        self.rendered_form = None

    def actions(self):
        return ['save']

    def save(self):
        results, errors = self.form.validate(
            self.request().fields(), self)
        if results is not None:
            self.doAction(results)
        else:
            print "Errors:", errors
            self.rendered_form = self.form.render(
                defaults=self.request().fields(),
                errors=errors)
            self.writeHTML()
            
    def writeContent(self):
        if self.rendered_form is None:
            self.rendered_form = self.form.render(
                defaults=self.getDefaults())
        self.write(page_style % self.rendered_form)
        
    def getDefaults(self):
        return dict(
            age='enter your age',
            color=['blue'])

    def preAction(self, trans):
        pass
    postAction = preAction
