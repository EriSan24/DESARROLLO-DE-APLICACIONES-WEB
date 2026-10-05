from flask_login import UserMixin


class Usuario(UserMixin):
    def __init__(self, id_usuario, usuario, password):
        self.id = str(id_usuario)
        self.usuario = usuario
        self.password = password

    def __repr__(self):
        return f"<Usuario {self.usuario}>"
