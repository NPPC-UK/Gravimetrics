"""
This will generate the form required
for the user to login to the database
"""

from web import form


def createLoginForm():
    """
    This is the actual form we return
    """
    return form.Form(
        form.Textbox('User', form.notnull),
        form.Textbox('Host', form.notnull),
        form.Textbox('Database', form.notnull),
        form.Password('Password', form.notnull),
        form.Button('Login'))


loginForm = createLoginForm()
