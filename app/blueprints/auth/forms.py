from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from flask_login import current_user
from app.models.usuario import Usuario
from app.extensions import db


class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=4)])
    remember_me = BooleanField("Lembrar de mim")
    submit = SubmitField("Entrar")


class ProfileForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    username = StringField("Nome de Usuário", validators=[DataRequired(), Length(max=64)])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    foto = FileField("Foto de Perfil", validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Apenas imagens!')])
    password = PasswordField("Nova Senha", validators=[Optional(), Length(min=4)])
    confirm_password = PasswordField("Confirmar Nova Senha", validators=[EqualTo('password', message="Senhas devem coincidir")])
    current_password = PasswordField("Senha Atual", validators=[Optional()])
    submit = SubmitField("Salvar Alterações")

    def validate_current_password(self, field):
        # Require password only if sensitive fields are changed or new password is set
        sensitive_change = (
            self.email.data.lower() != current_user.email.lower() or
            self.username.data != current_user.username or
            self.password.data
        )
        if sensitive_change and not field.data:
            raise ValidationError("Sua senha atual é necessária para alterar e-mail, usuário ou senha.")
        if field.data and not current_user.check_password(field.data):
            raise ValidationError("Senha atual incorreta.")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = db.session.execute(db.select(Usuario).where(Usuario.username == username.data)).scalar_one_or_none()
            if user:
                raise ValidationError('Este nome de usuário já está em uso.')

    def validate_email(self, email):
        if email.data.lower() != current_user.email.lower():
            user = db.session.execute(db.select(Usuario).where(Usuario.email == email.data.lower())).scalar_one_or_none()
            if user:
                raise ValidationError('Este e-mail já está em uso.')
