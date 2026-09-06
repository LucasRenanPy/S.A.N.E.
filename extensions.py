from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

from MySQLdb.cursors import DictCursor

mysql = MySQL()
bcrypt = Bcrypt()
sess = Session()

csrf = CSRFProtect()

def get_cursor():
    return mysql.connection.cursor(DictCursor)