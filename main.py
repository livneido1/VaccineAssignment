import sqlite3
import sys
from DAO import DAO
from Supplier import Supplier
from Logistic import Logistic
from Clinic import Clinic
from Vaccine import Vaccine


def createConnection(path):
    sqlite3_con = sqlite3.connect(path)
    return sqlite3_con


def create_tabels():
    dbCon = sqlite3.connect('database.db')
    with dbCon:
        cursor = dbCon.cursor()
        cursor.execute("""
         CREATE TABLE IF NOT EXISTS vaccines (
            id  INTEGER PRIMARY KEY,
            date    DATE    NOT NULL,
            supplier    INTEGER REFERENCES supplier(id),
            quantity    INTEGER NOT NULL
            );
            """)

        cursor.execute("""
         CREATE TABLE IF NOT EXISTS suppliers (
            id  INTEGER PRIMARY KEY,
            name    TEXT    NOT NULL,
            logistic    INTEGER REFERENCES logistic(id)
            );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clinics (
            id  INTEGER PRIMARY KEY,
            location    TEXT    NOT NULL,
            demand  INTEGER NOT NULL,
            logistic    INTEGER REFERENCES logistic(id)
            );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logistics(
            id  INTEGER PRIMARY KEY,
            name    TEXT NOT NULL,
            count_sent INTEGER NOT NULL,
            count_received INTEGER NOT NULL
            );
        """)

        cursor.execute("""CREATE TRIGGER IF NOT EXISTS Receive_Shipment
                          AFTER
                          Update ON vaccines
                          BEGIN 
                          DELETE FROM vaccines WHERE (vaccines.quantity = 0);
                          END
        """)


def fix_dates(lst):
    '''
    lst is either a list of lists or a list of tuples.
    will return a list/tuple where a dates of YYYY-MM-D been replaced with YYYY-MM-DD
    '''
    for j, l in enumerate(lst):
        nl = list(l)
        for i, v in enumerate(nl):
            if isinstance(v, str) and v.count('-') == 2:
                v = v.split('-')
                v[-1] = '0' + v[-1] if len(v[-1]) == 1 else v[-1]
                nl[i] = '-'.join(v)
        lst[j] = nl if isinstance(l, list) else tuple(nl)
    return lst


def swap_seperators(lst):
    for j, l in enumerate(lst):
        nl = list(l)
        for i, v in enumerate(nl):
            if isinstance(v, str):
                nl[i] = v.replace('−', '-')
        lst[j] = nl if isinstance(l, list) else tuple(nl)
    return lst


def read_from_file(conn, path):
    with open(path, "r") as f:
        v_dao = DAO(Vaccine, conn)
        c_dao = DAO(Clinic, conn)
        l_dao = DAO(Logistic, conn)
        s_dao = DAO(Supplier, conn)
        curr_var = 0
        splitted = f.readline().split(',')
        for var in splitted:  # runs through the numbers
            for i in range(int(var)):  # runs as long as the numbers says
                inputs = f.readline().split(',')
                if curr_var == 0:
                    curr_vaccine = Vaccine(*inputs)
                    v_dao.insert(curr_vaccine)
                elif curr_var == 1:
                    curr_supplier = Supplier(*inputs)
                    s_dao.insert(curr_supplier)
                elif curr_var == 2:
                    curr_clinic = Clinic(*inputs)
                    c_dao.insert(curr_clinic)
                else:
                    curr_logistic = Logistic(*inputs)
                    l_dao.insert(curr_logistic)

            curr_var = curr_var + 1

        conn.commit()


def read_orders(conn, path, summary):
    f = open(path)
    lines = f.readlines()
    leng = len(lines)
    i= 0
    cond = False
    for line in lines:
        if (i == leng):
            cond = True
        line = line.strip('\n')
        split = line.split(',')
        if len(split) == 3:
            receive_shipment(conn, split, summary, cond)
        else:
            send_shipment(conn, split, summary, cond)


def receive_shipment(conn, var_list, summery, sum_cond):
    name = var_list[0]
    amount = var_list[1]
    date = var_list[2]
    args = {'name': name}
    supplier = DAO(Supplier, conn).find(**args)[0]
    sup_id = supplier.get_id()
    # adds the new Vaccines to the DB
    last_id = DAO(Vaccine, conn).get_last_id()
    v = Vaccine(last_id + 1, date, sup_id, amount)
    DAO(Vaccine, conn).insert(v)
    args_s = {"id": supplier.logistic}

    logistic = DAO(Logistic, conn).find(**args_s)[0]
    new_count_received = logistic.get_count_received() + int(amount)
    update = {'count_received': new_count_received}
    cond = {'id': sup_id}
    # updates the supplier's count_received in the db
    DAO(Logistic, conn).update(update, cond)

    conn.commit()
    write_to_summery(conn, summery, sum_cond)


def send_shipment(conn, var_list, summery, sum_cond):
    location = var_list[0]
    amount = var_list[1]
    args = {'location': location}
    # finds the wanted clinic
    clinics = DAO(Clinic, conn).find(**args)
    # updates the clinic's demand
    clinic = clinics[0]

    new_amount = clinic.get_demand() - int(amount)
    c_args = {'demand': new_amount}
    DAO(Clinic, conn).update(c_args, args)
    # updates the Vaccines table
    vaccines = DAO(Vaccine, conn).find_all_by_order('date', 'ASC')  # TODO need to check whether it s ASC
    for vac in vaccines:
        num = vac.get_quantity()
        # if it has less then needed, take all
        if num < int(amount):
            args = {'quantity': 0}
            amount = int(amount) - num
        # otherwise -  take only amount needed
        else:
            args = {'quantity': (num - int(amount))}
            amount = 0

        cond = {'id': vac.get_id()}
        DAO(Vaccine, conn).update(args, cond)

        if int(amount) == 0:
            break

    # now updates the logistic table
    logistic_id = clinic.get_logistic()
    l_cond = {'id': logistic_id}
    logistic = DAO(Logistic, conn).find(**l_cond)[0]
    new_sent = logistic.get_count_sent() + int(var_list[1])
    l_args = {"count_sent": new_sent}
    DAO(Logistic, conn).update(l_args, l_cond)

    conn.commit()
    write_to_summery(conn, summery, sum_cond)


def write_to_summery(conn, summery , sum_cond):
    f = open(summery, "a")
    vaccines = DAO(Vaccine, conn).find_all()
    amount = 0
    for v in vaccines:
        amount = amount + v.get_quantity()
    clinics = DAO(Clinic, conn).find_all()
    demand = 0
    for c in clinics:
        demand = demand + c.get_demand()
    logistics = DAO(Logistic, conn).find_all()
    sent = 0
    rec = 0
    for l in logistics:
        sent = sent + l.get_count_sent()
        rec = rec + l.get_count_received()

    if (sum_cond):
        stmt = str(amount) + "," + str(demand) + "," + str(rec) + "," + str(sent)
    else:
        stmt = str(amount) + "," + str(demand) + "," + str(rec) + "," + str(sent) + '\n'

    f.write(stmt)


def main():
    create_tabels()
    conn = createConnection("database.db")
    read_from_file(conn, sys.argv[1])
    read_orders(conn, sys.argv[2], sys.argv[3])


if __name__ == '__main__':
    main()
