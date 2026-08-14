from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_session import Session

from MySQLdb.cursors import DictCursor

mysql = MySQL()
bcrypt = Bcrypt()
sess = Session()

def get_cursor():
    return mysql.connection.cursor(DictCursor)