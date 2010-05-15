from formencode import Invalid, htmlfill, Schema, validators

from WebKit.Page import Page


page_style = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
 <head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8">
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

 </body></html>'''

form_template = '''
<form action="" method="POST">

<p>Your name:<br>
<form:error name="name">
<input type="text" name="name"></p>

<p>Your age:<br>
<form:error name="age">
<input type="text" name="age"></p>

<p>Your favorite color:<br>
<form:error name="color">
<input type="checkbox" value="red" name="color"> Red<br>
<input type="checkbox" value="blue" name="color"> Blue<br>
<input type="checkbox" value="black" name="color"> Black<br>
<input type="checkbox" value="green" name="color"> Green<br>
<input type="checkbox" value="pink" name="color"> Pink</p>

<input type="submit" name="_action_save" value="Submit">
</form>'''

response_template = '''
<h2>Hello, %(name)s!</h2>
<p>You are %(age)d years old
and your favorite color is %(color)s.</p>'''


class FormSchema(Schema):
    name = validators.String(not_empty=True)
    age = validators.Int(min=13, max=99)
    color = validators.OneOf(['red', 'blue', 'black', 'green'])
    filter_extra_fields = True
    allow_extra_fields = True


class index(Page):

    def awake(self, trans):
        Page.awake(self, trans)
        self.rendered_form = None

    def actions(self):
        return ['save']

    def save(self):
        fields = self.request().fields()
        try:
            fields = FormSchema.to_python(fields, self)
        except Invalid, e:
            errors = dict((k, v.encode('utf-8'))
                for k, v in e.unpack_errors().iteritems())
            print "Errors:", errors
            self.rendered_form = htmlfill.render(form_template,
                defaults=fields, errors=errors)
            self.writeHTML()
        else:
            self.doAction(fields)

    def doAction(self, fields):
        print "Fields:", fields
        self.rendered_form = response_template % fields
        self.writeHTML()

    def writeHTML(self):
        if self.rendered_form is None:
            self.rendered_form = htmlfill.render(form_template,
                defaults=self.getDefaults())
        self.write(page_style % self.rendered_form)

    def getDefaults(self):
        return dict(age='enter your age', color=['blue'])

    def preAction(self, trans):
        pass
    postAction = preAction
