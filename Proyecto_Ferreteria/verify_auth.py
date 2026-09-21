from app import app
import sqlite3

client = app.test_client()

conn = sqlite3.connect('data/ferreteria.db')
conn.execute("DELETE FROM usuarios WHERE usuario = 'Ericksanchez'")
conn.commit()
conn.close()

resp = client.post('/registro', data={'usuario': 'Ericksanchez', 'password': 'Erick2000', 'confirm_password': 'Erick2000'}, follow_redirects=False)
print('REGISTER_STATUS', resp.status_code)
print('REGISTER_LOCATION', resp.headers.get('Location'))

conn = sqlite3.connect('data/ferreteria.db')
row = conn.execute("SELECT usuario, password FROM usuarios WHERE usuario = 'Ericksanchez'").fetchone()
print('DB_ROW', row)
print('HASH_OK', row is not None and any(row[1].startswith(prefix) for prefix in ('pbkdf2:', 'scrypt', 'argon2')))
conn.close()

resp = client.post('/login', data={'usuario': 'Ericksanchez', 'password': 'wrongpass'}, follow_redirects=False)
print('BADLOGIN_STATUS', resp.status_code)
print('BADLOGIN_DATA', b'Credenciales incorrectas' in resp.data)

resp = client.post('/login', data={'usuario': 'Ericksanchez', 'password': 'Erick2000'}, follow_redirects=False)
print('GOODLOGIN_STATUS', resp.status_code)
print('GOODLOGIN_LOCATION', resp.headers.get('Location'))

resp = client.get('/productos', follow_redirects=False)
print('PROTECTED_STATUS', resp.status_code)
print('PROTECTED_DATA', b'Productos' in resp.data)

resp = client.get('/logout', follow_redirects=False)
print('LOGOUT_STATUS', resp.status_code)
print('LOGOUT_LOCATION', resp.headers.get('Location'))

resp = client.get('/productos', follow_redirects=False)
print('AFTER_LOGOUT_STATUS', resp.status_code)
print('AFTER_LOGOUT_LOCATION', resp.headers.get('Location'))
