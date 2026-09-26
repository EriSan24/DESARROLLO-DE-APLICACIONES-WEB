from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange


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
        "Tipo de prenda",
        validators=[DataRequired(message="El tipo de prenda es obligatorio."), Length(min=3, max=50, message="El tipo debe tener entre 3 y 50 caracteres.")],
    )
    marca = StringField(
        "Marca",
        validators=[DataRequired(message="La marca es obligatoria."), Length(min=2, max=60)],
    )
    talla = StringField(
        "Talla",
        validators=[DataRequired(message="La talla es obligatoria."), Length(min=1, max=20)],
    )
    color = StringField(
        "Color",
        validators=[DataRequired(message="El color es obligatorio."), Length(min=2, max=40)],
    )
    genero = SelectField(
        "Línea",
        choices=[("Mujer", "Mujer"), ("Hombre", "Hombre"), ("Unisex", "Unisex")],
        validators=[DataRequired(message="Seleccione una línea." )],
    )
    precio = FloatField(
        "Precio",
        validators=[InputRequired(message="El precio es obligatorio."), NumberRange(min=0, message="El precio debe ser mayor o igual a 0.")],
    )
    stock = IntegerField(
        "Stock",
        validators=[InputRequired(message="El stock es obligatorio."), NumberRange(min=0, message="El stock no puede ser negativo.")],
    )
    id_proveedor = SelectField("Proveedor", coerce=int, choices=[(0, "Sin proveedor")])
