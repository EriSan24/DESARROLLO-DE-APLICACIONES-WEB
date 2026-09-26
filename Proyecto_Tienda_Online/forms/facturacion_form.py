from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, SelectField, StringField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange


class FacturaForm(FlaskForm):
    numero = StringField(
        "Número de factura",
        validators=[DataRequired(message="El número de factura es obligatorio."), Length(min=3, max=25, message="El número debe tener entre 3 y 25 caracteres.")],
    )
    id_cliente = SelectField(
        "Cliente",
        coerce=int,
        choices=[],
        validators=[DataRequired(message="Seleccione un cliente.")],
    )
    fecha = DateField(
        "Fecha",
        validators=[DataRequired(message="La fecha es obligatoria.")],
        format="%Y-%m-%d",
    )
    estado = SelectField(
        "Estado",
        choices=[("Pendiente", "Pendiente"), ("Pagada", "Pagada")],
        validators=[DataRequired(message="El estado es obligatorio.")],
    )
    descuento_pct = FloatField(
        "Descuento (%)",
        default=0,
        validators=[InputRequired(message="El descuento es obligatorio."), NumberRange(min=0, max=100, message="Use un descuento entre 0 y 100%.")],
    )
