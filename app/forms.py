from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, RadioField, SubmitField, IntegerField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange

#Custom validator to check if email is a University of Birmingham email address
def is_uni_email(form, field):
    if field.data[-19:] != '@student.bham.ac.uk' and field.data[-11:] != '@bham.ac.uk':
        raise ValidationError("Email must be a University of Birmingham email address.")

#Custom validator to check if password contains at least one number
def contains_number(form, field):
    if not any(char in "0123456789" for char in field.data):
        raise ValidationError("Password must contain at least one number.")

#Custom validator to check if user has consented to data collection
def must_accept_consent(form, field):
    if field.data != 'yes':
        raise ValidationError("You must consent to data collection to register.")

#Registration form with custom validators for email, password, and consent
class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(message = "Username required")])
    email = EmailField("Email", validators=[DataRequired(message = "Email required"), is_uni_email])
    course = StringField("Course", validators=[DataRequired(message = "Course required")])
    year_of_study = RadioField("Year of Study", choices=[('1', '1st Year'), ('2', '2nd Year'), ('3', '3rd Year'), ('4', '4th Year')], validators=[DataRequired(message = "Year of study required")])
    password = PasswordField("Password", validators=[DataRequired(message = "Password required"), Length(min=8), contains_number])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(message = "Please confirm password"), EqualTo("password", message = "Passwords must match")])
    consent = RadioField("Consent to Data Collection", choices=[('yes', 'Yes'), ('no', 'No')], validators=[DataRequired(message = "Consent required"), must_accept_consent])
    submit = SubmitField("Register")

class WellbeingForm(FlaskForm):
    stress = IntegerField("Stress Level", validators=[DataRequired(), NumberRange(min=1, max=5)])
    sleep = IntegerField("Sleep Level", validators=[DataRequired(), NumberRange(min=1, max=5)])
    social = IntegerField("Social Level", validators=[DataRequired(), NumberRange(min=1, max=5)])
    academic = IntegerField("Academic Level", validators=[DataRequired(), NumberRange(min=1, max=5)])
    activity = IntegerField("Activity Level", validators=[DataRequired(), NumberRange(min=1, max=5)])

    notes = TextAreaField("Additional Notes (Optional)")

    submit = SubmitField("Submit Form")


#Login form
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(message="Email required"), is_uni_email])
    password = PasswordField("Password", validators=[DataRequired(message="Password required"), Length(min=8), contains_number])
    submit = SubmitField("login")


class ResourceForm(FlaskForm):
    title = StringField("Resource Title", validators=[DataRequired(message="Title Required")])
    category = StringField("Category", validators=[DataRequired(message='Category Required')])
    url = StringField("Website link", validators=[DataRequired(message="Website link Required")])
    submit = SubmitField("Submit")
