#This file is used to send mass data from zkt to odoo

from zk import ZK, const
from pprint import pprint
from datetime import datetime, timedelta
import odoorpc

# Prepare the connection to the server
odoo = odoorpc.ODOO('url', port=80)

# Login
odoo.login('dbname', 'email', 'password')

attend = odoo.env['x_iol'].search([('x_studio_status', '=', 'status2')])
intern = []
for att in attend:
    intdata = odoo.env['x_iol'].browse(att)
    if intdata.x_studio_attendance_id != 0:
        intern.append([att, intdata.x_studio_zkt_id, intdata.x_name])

# harini = date.today().strftime("%Y-%m-%d")
harini = ""

conn = None
zk = ZK('IP1', port=4370, timeout=5)
zk2 = ZK('IP2', port=4370, timeout=5)

n = 0

dateb = 50
for x in range(dateb):
    output = [[None, None, None, None, None, None]] * 10000
    harini = (datetime.now() - timedelta(days=dateb - x)).strftime("%Y-%m-%d")
    try:
        conn = zk.connect()
        conn.disable_device()
        logs = conn.get_attendance()
        for log in logs:
            out = str(log).split(" ")
            if out[3] == harini:
                for intn in intern:
                    if int(out[1]) == int(intn[1]):
                        if output[int(intn[1])][4] is not None:
                            output[int(intn[1])][5] = out[4]
                        else:
                            if int((out[4].split(':'))[0]) < 10:
                                output[int(intn[1])] = [intn[1], intn[0], intn[2], out[3], out[4], None]
                            else:
                                output[int(intn[1])] = [intn[1], intn[0], intn[2], out[3], None, out[4]]

        conn.enable_device()

        conn2 = zk2.connect()
        conn2.disable_device()
        logs = conn2.get_attendance()
        for log in logs:
            out = str(log).split(" ")
            if out[3] == harini:
                for intn in intern:
                    if int(out[1]) == int(intn[1]):
                        if output[int(intn[1])][4] is not None:
                            output[int(intn[1])][5] = out[4]
                        else:
                            if int((out[4].split(':'))[0]) < 10:
                                output[int(intn[1])] = [intn[1], intn[0], intn[2], out[3], out[4], None]
                            else:
                                output[int(intn[1])] = [intn[1], intn[0], intn[2], out[3], None, out[4]]

        conn2.enable_device()

    except Exception as e:
        print("Process terminate : {}".format(e))
    finally:
        if conn:
            conn.disconnect()

    for out in output:
        if out[0] is not None:
            print(out)
            attend = odoo.env['x_intern.att'].create({
                'x_name': out[2],
                'x_studio_date': out[3],
                'x_studio_time_in': out[4],
                'x_studio_time_out': out[5],
                'x_studio_intern_name': out[1]
            })
