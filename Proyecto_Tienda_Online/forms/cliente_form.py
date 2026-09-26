from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email, Length


class ClienteForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[DataRequired(message="El nombre es obligatorio."), Length(min=3, max=100, message="El nombre debe tener entre 3 y 100 caracteres.")],
    )
    cedula = StringField(
        "Cédula",
        validators=[DataRequired(message="La cédula es obligatoria."), Length(min=10, max=10, message="La cédula debe tener 10 dígitos.")],
    )
    telefono = StringField(
        "Teléfono",
        validators=[DataRequired(message="El teléfono es obligatorio."), Length(min=10, max=10, message="El teléfono debe tener 10 dígitos.")],
    )
    correo = StringField(
        "Correo",
        validators=[DataRequired(message="El correo es obligatorio."), Email(message="Ingrese un correo válido.")],
    )
