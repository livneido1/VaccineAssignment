import inspect


def orm(cursor, dto_type):
    args = inspect.getfullargspec(dto_type.__init__).args
    args = args[1:]
    col_names = [column[0] for column in cursor.description]
    col_mapping =[col_names.index(arg) for arg in args]
    return [row_map(row, col_mapping, dto_type) for row in cursor.fetchall()]


def row_map(row, col_mapping , dto_type):
    ctor_args = [row[idx] for idx in col_mapping]
    return dto_type(*ctor_args)


class DAO:
    def __init__(self, dto_type, conn):
        self.conn = conn
        self.dto_type = dto_type
        self.table_name = dto_type.__name__.lower() + 's'

    def insert(self, dto):
        ins_dict = vars(dto)
        columns_name = ','.join(ins_dict.keys())
        params = list(ins_dict.values())
        qmarks = ','.join(['?'] * len(ins_dict))
        stmt = 'INSERT INTO {} ({}) VALUES  ({})'.format(self.table_name, columns_name, qmarks)
        c = self.conn.cursor()
        c.execute(stmt, params)

    def find_all(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM {}'.format(self.table_name))
        return orm(c, self.dto_type)

    def find(self, **kwargs):
        column_names = list(kwargs.keys())
        params = list(kwargs.values())

        stmt = 'SELECT * FROM {} WHERE {}'.format(self.table_name, ' AND '.join(col + '=?' for col in column_names))
        c = self.conn.cursor()
        c.execute(stmt, params)
        return orm(c, self.dto_type)

    def delete(self, **kwargs):
        column_name = list(kwargs.keys())
        params = list(kwargs.values())
        stmt = 'DELETE FROM {} WHERE {}'.format(self.table_name, ' AND '.join(col + '=?' for col in column_name))
        self.conn.execute(stmt, params)

    def update(self, set_values, cond):
        set_column_name = list(set_values.keys())
        set_params = list(set_values.values())
        cond_column_names = list(cond.keys())
        cond_params = list(cond.values())
        params = set_params + cond_params
        stmt = 'UPDATE {} SET {} WHERE {}'.format(self.table_name, ', '.join([s + '=?' for s in set_column_name]),
                                                  ' AND '.join([cond + '=?' for cond in cond_column_names]))
        self.conn.execute(stmt, params)






    def get_last_id(self):
        c = self.conn.cursor()
        stmt = 'SELECT MAX(ID) FROM {} '.format(self.table_name)
        c.execute(stmt)
        return c.fetchone()[0]

    def find_all_by_order(self, column, order):
        c = self.conn.cursor()
        c.execute('SELECT * FROM {} ORDER BY {} {}'.format(self.table_name, column, order))
        return orm(c, self.dto_type)



