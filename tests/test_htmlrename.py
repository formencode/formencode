from formencode.htmlrename import rename, add_prefix

def test_rename():
    assert (rename('<input type="text" name="a_name">', lambda name: name.upper())
            == '<input type="text" name="A_NAME">')
    assert (add_prefix('<input type="text" name="a_name"><input type="text" name="">', 'test', dotted=True)
            == '<input type="text" name="test.a_name"><input type="text" name="test">')
    
