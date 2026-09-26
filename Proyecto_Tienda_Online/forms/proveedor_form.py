from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email, Length


class ProveedorForm(FlaskForm):
    empresa = StringField(
        "Empresa",
        validators=[DataRequired(message="La empresa es obligatoria."), Length(min=3, max=100, message="La empresa debe tener entre 3 y 100 caracteres.")],
    )
    contacto = StringField(
        "Contacto",
        validators=[DataRequired(message="El contacto es obligatorio."), Length(min=3, max=100, message="El contacto debe tener entre 3 y 100 caracteres.")],
    )
    telefono = StringField(
        "Teléfono",
        validators=[DataRequired(message="El teléfono es obligatorio."), Length(min=10, max=10, message="El teléfono debe tener 10 dígitos.")],
    )
    correo = StringField(
        "Correo",
        validators=[DataRequired(message="El correo es obligatorio."), Email(message="Ingrese un correo válido.")],
    )
