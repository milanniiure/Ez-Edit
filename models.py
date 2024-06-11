class Account:
    def __init__(self, id=None, username=None, email=None, password=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    @staticmethod
    def get_all(mysql):
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM accounts')
        accounts = cursor.fetchall()
        cursor.close()
        return accounts

    @staticmethod
    def get_by_id(mysql, account_id):
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (account_id,))
        account = cursor.fetchone()
        cursor.close()
        return Account(id=account[0], username=account[1], email=account[2], password=account[3])

    def save(self, mysql):
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO accounts (username, email, password) VALUES (%s, %s, %s)',
                       (self.username, self.email, self.password))
        mysql.connection.commit()
        cursor.close()

    def update(self, mysql):
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE accounts SET username = %s, email = %s, password = %s WHERE id = %s',
                       (self.username, self.email, self.password, self.id))
        mysql.connection.commit()
        cursor.close()

    def delete(self, mysql):
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM accounts WHERE id = %s', (self.id,))
        mysql.connection.commit()
        cursor.close()
