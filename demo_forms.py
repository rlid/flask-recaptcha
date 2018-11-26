from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField

from recaptcha2 import RecaptchaField
from recaptcha3 import Recaptcha3Field


class Recaptcha2Form(FlaskForm):
    message = TextField(label="Message")
    recaptcha = RecaptchaField(invisible_on_load=False)
    submit = SubmitField(label="Submit")


class Recaptcha2InvisibleForm(FlaskForm):
    message = TextField(label="Message")
    recaptcha = RecaptchaField(label="Submit", invisible_on_load=True)


class Recaptcha3Form(FlaskForm):
    message = TextField(label="Message")
    recaptcha = Recaptcha3Field(action="TestAction", execute_on_load=True)
    submit = SubmitField(label="Submit")
