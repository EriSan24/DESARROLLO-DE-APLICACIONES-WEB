from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, SelectField, StringField
from wtforms.validators import DataRequired, Length, NumberRange


class FacturaForm(FlaskForm):
    numero = StringField(
        "Número de factura",
        validators=[DataRequired(message="El número de factura es obligatorio."), Length(min=3, max=25, message="El número debe tener entre 3 y 25 caracteres.")],
    )
    cliente = StringField(
        "Cliente",
        validators=[DataRequired(message="El cliente es obligatorio."), Length(min=3, max=100, message="El cliente debe tener entre 3 y 100 caracteres.")],
    )
    fecha = DateField(
        "Fecha",
        validators=[DataRequired(message="La fecha es obligatoria.")],
        format="%Y-%m-%d",
    )
    total = FloatField(
        "Total",
        validators=[DataRequired(message="El total es obligatorio."), NumberRange(min=0, message="El total debe ser mayor o igual a 0.")],
    )
    estado = SelectField(
        "Estado",
        choices=[("Pagada", "Pagada"), ("Pendiente", "Pendiente"), ("Anulada", "Anulada")],
        validators=[DataRequired(message="El estado es obligatorio.")],
    )
