from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RequestForm(FlaskForm):
    To = StringField('To', validators=[DataRequired()])
    From = StringField('From')
    product1 = StringField('product1', validators=[DataRequired()])
    quantity1 = IntegerField('quantity1', validators=[DataRequired()])
    product2 = StringField('product2', validators=[DataRequired()])
    quantity2 = IntegerField('quantity2', validators=[DataRequired()])
    payment = IntegerField('Payment') 
    submit = SubmitField('Submit')

class PaymentForm(FlaskForm):
    To = StringField('To', validators=[DataRequired()])
    From = StringField('From')
    payment = IntegerField('Payment',validators=[DataRequired()]) 
    submit = SubmitField('Submit')
    
