"""
Wrapper class for use with cgi.FieldStorage types for file uploads
"""


def convert_fieldstorage(fs):
    return fs if fs.filename else None
