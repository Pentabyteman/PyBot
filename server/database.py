import MySQLdb
import uuid
import hashlib

DATABASE = 'db_pybot'
DB_HOST = 'localhost'
DB_USER = 'pybot_user'
DB_PWD = 'pybot_pwd'


class SQLConnection:

    def __init__(self):
        self.connection = MySQLdb.connect(host=DB_HOST,
                                          user=DB_USER,
                                          passwd=DB_PWD,
                                          db=DATABASE)
        self.cursor = self.connection.cursor()

    def query(self, command):
        self.cursor.execute(command)
        return self.cursor.fetchall()

    def commit(self):
        self.connection.commit()


class Database:

    instance = None

    def __new__(cls, *args, **kwargs):
        if Database.instance is None:
            Database.instance = object.__new__(cls, *args, **kwargs)
        return Database.instance  # makes sure there is only one instance

    def __init__(self):
        self.conn = SQLConnection()
        if self.get_table('users') is None:
            self.init_users()

    def init_users(self):
        self.create_table('users', """id INTEGER AUTO_INCREMENT PRIMARY KEY,
                                      name VARCHAR(20),
                                      password VARCHAR(128),
                                      salt VARCHAR(32)
                                   """)

    def add_user(self, name, password):
        salt = get_salt()
        password = hash_pwd(password, salt)
        users = self.get_table('users')
        users.insert({"name": "'{}'".format(name),
                      "password": "'{}'".format(password),
                      "salt": "'{}'".format(salt)})

    def get_user(self, name):
        users = self.get_table('users')
        matches = users.select(conditions="name='{}'".format(name))
        if len(matches) == 0:
            raise KeyError("User not found")
        elif len(matches) > 1:
            raise KeyError("Username is not distinct")
        user = matches[0]
        return {'name': user[1], 'password': user[2], 'salt': user[3]}

    def verify(self, username, password):
        try:
            user = self.get_user(username)
        except KeyError:
            return False
        return hash_pwd(password, user['salt']) == user['password']

    def get_table(self, name):
        tables = self.conn.query("""SHOW TABLES LIKE '{}'""".format(name))
        if len(tables) == 0:
            return None
        return Table(tables[0][0], self.conn)

    def create_table(self, name, columns):
        """
        Creates a table in this database

        Arguments:
        name -- name of the new table
        columns -- list of strings or one string of pattern "key OPTION, ..."
        """
        if type(columns) == list:
            columns = ",".join(columns)
        cmd = "CREATE TABLE {name} ({columns})".format(name=name,
                                                       columns=columns)
        self.conn.query(cmd)
        self.conn.commit()


class Table:

    def __init__(self, name, db):
        self.name = name
        self.db = db

    def __repr__(self):
        return str(self.db.query("""SELECT * FROM {0}""".format(self.name)))

    def insert(self, entries):
        """
        Insert the given entries into the table

        Arguments:
        entries -- dictionary
        """
        keys, vals = list(entries.keys()), list(entries.values())
        cmd_raw = "INSERT INTO {name} ({keys}) VALUES ({values});"
        cmd = cmd_raw.format(name=self.name,
                             keys=",".join(keys),
                             values=",".join(vals))
        self.db.query(cmd)
        self.db.commit()

    def select(self, columns=None, conditions=None, distinct=False):
        """
        Selects the given columns from the table filtered by the conditions

        Keyword arguments:
        columns -- string of pattern: 'key, ..." or list of keys (Default: *)
        conditions -- string of pattern: 'key=value AND ...' (Default: nothing)
        distinct -- wether to show only distinct matches (Default: False)
        """
        if not columns:
            columns = "*"
        elif type(columns) == list:
            columns = ",".join(columns)

        if not conditions:
            cmd = "SELECT {distinct} {columns} FROM {name}"\
                .format(distinct="DISTINCT" if distinct else "",
                        name=self.name,
                        columns=columns)
        else:
            cmd = "SELECT {distinct} {columns} FROM {name} WHERE {conditions}"\
                .format(distinct="DISTINCT" if distinct else "",
                        name=self.name,
                        columns=columns,
                        conditions=conditions)
        result = self.db.query(cmd)
        return result


def hash_pwd(pwd, salt):
    return hashlib.sha512(pwd.encode() + salt.encode()).hexdigest()


def get_salt():
    return uuid.uuid4().hex
