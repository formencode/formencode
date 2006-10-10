# @@: This is experimental

import fields
import validators
import schema
from formgen import makeform
from sqlobject import SQLObject
from sqlobject import col


#@makeform.when('isinstance(obj, SQLObject) or (isinstance(obj, type) and issubclass(obj, SQLObject))')
def makeform_new_sqlobject(obj, context):
    isinst = isinstance(obj, SQLObject)
    sqlmeta = obj.sqlmeta
    layout = fields.Layout()
    s = schema.Schema()
    if isinst:
        secret = context.secret
        layout.fields.append(fields.Hidden(context, name='id'))
        s.fields['id'] = validators.SignedString(secret=context.secret)
    if isinst:
        colclass = obj.__class__
    else:
        colclass = obj
    restore = context.push_attr(column_owner=obj,
                                column_owner_class=colclass)
    try:
        for column in sqlmeta.columnList:
            name = column.name
            name_restore = context.push_attr(column_name=name,
                                             add_name=name)
            try:
                inner_form, inner_schema = makeform(column, context)
                if inner_schema:
                    s.fields[name] = inner_schema
                if isinstance(inner_form, (list, tuple)):
                    layout.fields.extend(inner_form)
                else:
                    layout.fields.append(inner_form)
            finally:
                name_restore.pop_attr()
    finally:
        restore.pop_attr()
    return layout, s

makeform_new_sqlobject = makeform.when('isinstance(obj, SQLObject) or (isinstance(obj, type) and issubclass(obj, SQLObject))')(makeform_new_sqlobject)

def coldesc(col):
    return getattr(col, 'description', col.name)

#@makeform.when('isinstance(obj, col.SOStringLikeCol)')
def makeform_string_col(obj, context):
    return fields.Text(context, description=coldesc(obj)), None

makeform_string_col = makeform.when('isinstance(obj, col.SOStringLikeCol)')(makeform_string_col)

#@makeform.when('isinstance(obj, col.SOBoolCol)')
def makeform_bool_col(obj, context):
    return (fields.Checkbox(context, description=coldesc(obj)),
            validators.Bool())

makeform_bool_col = makeform.when('isinstance(obj, col.SOBoolCol)')(makeform_bool_col)

#@makeform.when('isinstance(obj, col.SOForeignKey) and getattr(obj, "editinline", False)')
def makeform_foreign(obj, context):
    external_class = col.findClass(obj.foreignKey)

makeform_foreign = makeform.when('isinstance(obj, col.SOForeignKey) and getattr(obj, "editinline", False)')(makeform_foreign)

