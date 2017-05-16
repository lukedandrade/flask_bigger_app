from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import Email, DataRequired, Length, EqualTo, Optional, Required

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    c_password = PasswordField('Confirm Password', validators=[DataRequired()])
    img_link = StringField('Image link for Profile Picture', validators=[Optional()],
                           default='http://www.publicdomainpictures.net/pictures/130000/velka/clip-art-smiley-face.jpg')
    submit = SubmitField('Sign In')

class EditForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()])
    about_me = StringField('about_me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Save Changes')

class Edit_for_adminForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()])
    about_me = StringField('about_me', validators=[Length(min=0, max=140)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role_id = IntegerField('Role ID', validators=[DataRequired()])
    img_link = StringField('Image link for Profile Picture', validators=[Optional()],
                           default='http://www.publicdomainpictures.net/pictures/130000/velka/clip-art-smiley-face.jpg')
    submit = SubmitField('Save Changes')

class PostForm(FlaskForm):
    body = TextAreaField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditPostForm(FlaskForm):
    new_body = TextAreaField("New post", validators=[DataRequired()])
    submit = SubmitField('Submit')