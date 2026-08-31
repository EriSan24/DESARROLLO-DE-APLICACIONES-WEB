from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange


class ProductoForm(FlaskForm):
    codigo = StringField(
        "Código",
        validators=[DataRequired(message="El código es obligatorio."), Length(min=3, max=20, message="El código debe tener entre 3 y 20 caracteres.")],
    )
    nombre = StringField(
        "Nombre",
        validators=[DataRequired(message="El nombre es obligatorio."), Length(min=3, max=100, message="El nombre debe tener entre 3 y 100 caracteres.")],
    )
    categoria = StringField(
        "Categoría",
        validators=[DataRequired(message="La categoría es obligatoria."), Length(min=3, max=50, message="La categoría debe tener entre 3 y 50 caracteres.")],
    )
    precio = FloatField(
        "Precio",
        validators=[DataRequired(message="El precio es obligatorio."), NumberRange(min=0, message="El precio debe ser mayor o igual a 0.")],
    )
    stock = IntegerField(
        "Stock",
        validators=[DataRequired(message="El stock es obligatorio."), NumberRange(min=0, message="El stock no puede ser negativo.")],
    )
