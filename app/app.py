from flask import Flask, json, request, jsonify, Response, render_template
from flask_cors import CORS
import pymysql
import io
import csv
import xlwt

api = Flask(__name__)
CORS(api)
api.config["DEBUG"] = True
api.config['JSON_SORT_KEYS'] = False

# connect to database
def koneksi_db():
    db = pymysql.connect(
        host='db', 
        database='db_monitoring_ebt',
        user='root', 
        password='root')
    return db

# table name in database
tb_name = 'monitoring_ebt'

# ---------------------------- HOME PAGE ROUTING API -------------------- #
@api.route('/', methods=['GET'])
def home():
    return render_template('home.html')

# ---------------------------- DOWNLOAD PAGE ROUTING API -------------------- #
@api.route("/ebt/download")
def download():
    return render_template('download.html')

# ---------------------------- DOWNLOAD .CSV FILE -------------------- #
@api.route("/ebt/download/report/csv")
def download_report_csv():
    db = koneksi_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    
    parameter = str(request.args['data'])
    waktu1 = str(request.args['from'])
    waktu2 = str(request.args['to'])

    if parameter == "suryaDC":
        client_id = 6
    if parameter == "suryaAC":
        client_id = 7
    if parameter == "turbin":
        client_id = 8
    
    sql = """SELECT *
            FROM {tb_name} 
            WHERE client_id = {client_id} 
            AND CAST(db_created_at AS DATE) 
            BETWEEN '{waktu1}' AND '{waktu2}'
            ORDER BY 'db_created_at'""".format(tb_name=tb_name, client_id=client_id, waktu1=waktu1, waktu2=waktu2)
    cursor.execute(sql)
    all_data = cursor.fetchall()
    
    output = io.StringIO()
    writer = csv.writer(output)

    line = ['data_id', 'client_id', 'db_created_at', 'send_to_db_at', 'processing_time', 'voltage', 'current', 'power', 'energy', 'power_factor']
    writer.writerow(line)

    for i in all_data:
        line = [i['data_id'],i['client_id'],i['db_created_at'],i['send_to_db_at'],i['processing_time'],i['voltage'],i['current'],i['power'],i['energy'],i['power_factor']]
        writer.writerow(line)
    
    output.seek(0)

    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=monitoring_{parameter}_report_from_{waktu1}_to_{waktu2}.csv".format(parameter=parameter, waktu1=waktu1, waktu2=waktu2)})

# ---------------------------- DOWNLOAD .XLS FILE -------------------- #
@api.route("/ebt/download/report/xls")
def download_report_xls():
    db = koneksi_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    
    parameter = str(request.args['data'])
    waktu1 = str(request.args['from'])
    waktu2 = str(request.args['to'])

    if parameter == "suryaDC":
        client_id = 6
    if parameter == "suryaAC":
        client_id = 7
    if parameter == "turbin":
        client_id = 8
    
    sql = """SELECT *
            FROM {tb_name} 
            WHERE client_id = {client_id} 
            AND CAST(db_created_at AS DATE) 
            BETWEEN '{waktu1}' AND '{waktu2}'
            ORDER BY 'db_created_at'""".format(tb_name=tb_name, client_id=client_id, waktu1=waktu1, waktu2=waktu2)
    cursor.execute(sql)
    all_data = cursor.fetchall()
    
    output = io.BytesIO()
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Report',cell_overwrite_ok=True)
    
    # header
    ws.write(0, 0, 'data_id')
    ws.write(0, 1, 'client_id')
    ws.write(0, 2, 'db_created_at')
    ws.write(0, 3, 'send_to_db_at')
    ws.write(0, 4, 'processing_time')
    ws.write(0, 5, 'voltage')
    ws.write(0, 6, 'current')
    ws.write(0, 7, 'power')
    ws.write(0, 8, 'energy')
    ws.write(0, 9, 'power_factor')

    line = 0
    for i in all_data:
        ws.write(line+1, 0, i['data_id'])
        ws.write(line+1, 1, i['client_id'])
        ws.write(line+1, 2, str(i['db_created_at']))
        ws.write(line+1, 3, str(i['send_to_db_at']))
        ws.write(line+1, 4, str(i['processing_time']))
        ws.write(line+1, 5, i['voltage'])
        ws.write(line+1, 6, i['current'])
        ws.write(line+1, 7, i['power'])
        ws.write(line+1, 8, i['energy'])
        ws.write(line+1, 9, i['power_factor'])
        line += 1
        
    wb.save(output)
    output.seek(0)

    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=monitoring_{parameter}_report_from_{waktu1}_to_{waktu2}.xls".format(parameter=parameter, waktu1=waktu1, waktu2=waktu2)})

# --------------- POST DATA TO DATABASE ------------- #
@api.route("/monitoring_ebt", methods=['POST','GET'])
def monitoring_ebt():
    db = koneksi_db()
    cursor = db.cursor()
    
    if request.method == 'GET':
        return "Succes"
    
    if request.method == 'POST':
        data = request.json
        client_id = data['client_id']
        send_to_db_at = data["data"]["send_to_db_at"]
        processing_time = data["data"]["processing_time"]
        voltage = data["data"]["voltage"]
        current = data["data"]["current"]
        power = data["data"]["power"]
        energy = data["data"]["energy"]
        power_factor = data["data"]["power_factor"]

        if voltage == 999999 and current == 999999 and power == 999999 and energy == 999999 and power_factor == 999999 :
            dataIn = cursor.execute(""" INSERT INTO {tb_name}(client_id, db_created_at, send_to_db_at, processing_time,
                                        voltage, current, power, energy, power_factor)
                                        VALUES({client_id}, current_timestamp(6)+INTERVAL 7 HOUR, 
                                        "{send_to_db_at}", "{processing_time}", null, null, null, null, null)"""
                                        .format(tb_name=tb_name, 
                                                client_id=client_id,
                                                send_to_db_at=send_to_db_at,
                                                processing_time=processing_time
                                                )
                                        )
            db.commit()

        else:
            dataIn = cursor.execute(""" INSERT INTO {tb_name}(client_id, db_created_at, send_to_db_at, processing_time,
                                            voltage, current, power, energy, power_factor)
                                            VALUES({client_id}, current_timestamp(6)+INTERVAL 7 HOUR, 
                                            "{send_to_db_at}", "{processing_time}",{voltage},{current},
                                            {power},{energy},{power_factor})"""
                                            .format(tb_name=tb_name, 
                                                    client_id=client_id,
                                                    send_to_db_at=send_to_db_at,
                                                    processing_time=processing_time,
                                                    voltage=voltage,
                                                    current=current,
                                                    power=power,
                                                    energy=energy,
                                                    power_factor=power_factor
                                                    )
                                            )
            db.commit()

    db.close()
    hasil = jsonify(data)
    return hasil

# --------------- API 5 DATA REALTIME TERAKHIR ------------- #
@api.route("/ebt", methods=["GET"])
def ebt():
    db = koneksi_db()
    cursor = db.cursor()
    parameter = str(request.args['data'])
    
    if parameter == "suryaDC":
        sql = """SELECT *
                FROM {tb_name} WHERE client_id = 6 
                ORDER BY 'db_created_at'""".format(tb_name=tb_name)
        cursor.execute(sql)
        all_data = cursor.fetchall()
        hasil = {
            "suryaDC_id": 6,
            "units": [{"voltage": "V", "current": "A", "power": "W", "energy":"Wh"}],
            "value": []
        }
        for i in range(len(all_data)-5, len(all_data)):
            data = {
                "client_id": all_data[i][1],
                "db_created_at" : str(all_data[i][2]),
                "send_to_db_at" : str(all_data[i][3]),
                "processing_time" : str(all_data[i][4]),
                "voltage" : all_data[i][5],
                "current" : all_data[i][6],
                "power" : all_data[i][7],
                "energy" : all_data[i][8]
                }
            hasil["value"].append(data)

    if parameter == "suryaAC":
        sql = """SELECT *
                FROM {tb_name} WHERE client_id = 7
                ORDER BY 'db_created_at'""".format(tb_name=tb_name)
        cursor.execute(sql)
        all_data = cursor.fetchall()
        hasil = {
            "suryaAC_id": 7,
            "units": [{"voltage": "V", "current": "A", "power": "W", "energy":"Wh"}],
            "value": []
        }
        for i in range(len(all_data)-5, len(all_data)):
            data = {
                "client_id": all_data[i][1],
                "db_created_at" : str(all_data[i][2]),
                "send_to_db_at" : str(all_data[i][3]),
                "processing_time" : str(all_data[i][4]),
                "voltage" : all_data[i][5],
                "current" : all_data[i][6],
                "power" : all_data[i][7],
                "energy" : all_data[i][8],
                "power_factor" : all_data[i][9]
                }
            hasil["value"].append(data)

    if parameter == "turbin":
        sql = """SELECT *
                FROM {tb_name} WHERE client_id = 8 
                ORDER BY 'db_created_at'""".format(tb_name=tb_name)
        cursor.execute(sql)
        all_data = cursor.fetchall()
        hasil = {
            "turbin_id": 8,
            "units": [{"voltage": "V", "current": "A", "power": "W", "energy":"Wh"}],
            "value": []
        }
        for i in range(len(all_data)-5, len(all_data)):
            data = {
                "client_id": all_data[i][1],
                "db_created_at" : str(all_data[i][2]),
                "send_to_db_at" : str(all_data[i][3]),
                "processing_time" : str(all_data[i][4]),
                "voltage" : all_data[i][5],
                "current" : all_data[i][6],
                "power" : all_data[i][7],
                "energy" : all_data[i][8],
                }
            hasil["value"].append(data)

    return jsonify(hasil)

# --------------- API SEMUA DATA TIAP 5 MENIT DALAM 1 HARI -------------- #
@api.route("/ebt/harian", methods=["GET"])
def tanggal():
    db = koneksi_db()
    cursor = db.cursor()
    parameter = str(request.args['data'])
    waktu = str(request.args['waktu'])

    if parameter == "suryaDC":
        sql = """SELECT *
                FROM {tb_name} WHERE client_id = 6 
                AND DATE(db_created_at) = '{waktu}'
                AND HOUR(db_created_at) BETWEEN 0 and 24
                ORDER BY 'db_created_at'""".format(tb_name=tb_name, waktu=waktu)
        cursor.execute(sql)
        all_data = cursor.fetchall()
        hasil = {
            "suryaDC_id": 6,
            "units": [{"voltage": "V", "current": "A", "power": "W", "energy":"Wh"}],
            "value": []
        }
        for i in range(0, len(all_data)):
            data = {
                "db_created_at" : str(all_data[i][2]),
                "value": {
                    "client_id": all_data[i][1],
                    "send_to_db_at" : str(all_data[i][3]),
                    "processing_time" : str(all_data[i][4]),
                    "voltage" : all_data[i][5],
                    "current" : all_data[i][6],
                    "power" : all_data[i][7],
                    "energy" : all_data[i][8]
                }}
            hasil["value"].append(data)

    if parameter == "suryaAC":
        sql = """SELECT *
                FROM {tb_name} WHERE client_id = 7 
                AND DATE(db_created_at) = '{waktu}'
                AND HOUR(db_created_at) BETWEEN 0 and 24
                ORDER BY 'db_created_at'""".format(tb_name=tb_name, waktu=waktu)
        cursor.execute(sql)
        all_data = cursor.fetchall()
        hasil = {
            "suryaAC_id": 7,
            "units": [{"voltage": "V", "current": "A", "power": "W", "energy":"Wh"}],
            "value": []
        }
        for i in range(0, len(all_data)):
            data = {
                "db_created_at" : str(all_data[i][2]),
                "value": {
                    "client_id": all_data[i][1],
                    "send_to_db_at" : str(all_data[i][3]),
                    "processing_time" : str(all_data[i][4]),
                    "voltage" : all_data[i][5],
                    "current" : all_data[i][6],
                    "power" : all_data[i][7],
                    "energy" : all_data[i][8],
                    "power_factor" : all_data[i][9]
                }}
            hasil["value"].append(data)

    if parameter == "turbin":
        sql = """SELECT *
                FROM {tb_name} WHERE client_id = 8
                AND DATE(db_created_at) = '{waktu}'
                AND HOUR(db_created_at) BETWEEN 0 and 24
                ORDER BY 'db_created_at'""".format(tb_name=tb_name, waktu=waktu)
        cursor.execute(sql)
        all_data = cursor.fetchall()
        hasil = {
            "turbin_id": 8,
            "units": [{"voltage": "V", "current": "A", "power": "W", "energy":"Wh"}],
            "value": []
        }
        for i in range(0, len(all_data)):
            data = {
                "db_created_at" : str(all_data[i][2]),
                "value": {
                    "client_id": all_data[i][1],
                    "send_to_db_at" : str(all_data[i][3]),
                    "processing_time" : str(all_data[i][4]),
                    "voltage" : all_data[i][5],
                    "current" : all_data[i][6],
                    "power" : all_data[i][7],
                    "energy" : all_data[i][8]
                }}
            hasil["value"].append(data)

    return jsonify(hasil)

# --------------- API AKUMULASI DATA HARIAN DALAM 1 BULAN -------------- #
@api.route("/ebt/akumulasi/harian/suryaDC", methods=["GET"])
def harian_suryaDC():
    db = koneksi_db()
    cursor = db.cursor()
    bulan = str(request.args['bulan'])
    tahun = str(request.args['tahun'])

    sql = """SET SESSION sql_mode = sys.list_drop(@@SESSION.sql_mode, 'ONLY_FULL_GROUP_BY');"""
    cursor.execute(sql)
    sql = """SELECT DATE(db_created_at) as day,
            WEEK(db_created_at) as week,
            MONTH(db_created_at) as month,
            YEAR(db_created_at) as year,
            ROUND(AVG(voltage),2) as avg_harian_tegangan,
            ROUND(AVG(current),2) as avg_harian_arus,
            ROUND(SUM(power),2) as sum_harian_daya,
            ROUND(SUM(energy),2) as sum_harian_energi,
            client_id
            FROM {} 
            WHERE client_id = 6
            AND MONTH(db_created_at)={}
            AND YEAR(db_created_at)={}
            GROUP BY day
            """.format(tb_name, bulan, tahun)
    cursor.execute(sql)
    all_data = cursor.fetchall()
    hasil = {  
        "suryaDC_id": 6,
        "bulan": bulan,
        "tahun": tahun,
        "units": [{"avg_harian_tegangan": "V", "avg_harian_arus": "A", "sum_harian_daya": "W", "sum_harian_energi":"Wh"}],
        "value": []
        }   
    for i in range(0, len(all_data)):
        data = [{
            "tanggal": all_data[i][0],
            "value": {
                "avg_harian_tegangan": all_data[i][4],
                "avg_harian_arus": all_data[i][5],
                "sum_harian_daya": all_data[i][6],
                "sum_harian_energi": all_data[i][7],
            }
            }]
        hasil["value"].append(data[0])
    return jsonify(hasil)

@api.route("/ebt/akumulasi/harian/suryaAC", methods=["GET"])
def harian_suryaAC():
    db = koneksi_db()
    cursor = db.cursor()
    bulan = str(request.args['bulan'])
    tahun = str(request.args['tahun'])

    sql = """SET SESSION sql_mode = sys.list_drop(@@SESSION.sql_mode, 'ONLY_FULL_GROUP_BY');"""
    cursor.execute(sql)
    sql = """SELECT DATE(db_created_at) as day,
            WEEK(db_created_at) as week,
            MONTH(db_created_at) as month,
            YEAR(db_created_at) as year,
            ROUND(AVG(voltage),2) as avg_harian_tegangan,
            ROUND(AVG(current),2) as avg_harian_arus,
            ROUND(SUM(power),2) as sum_harian_daya,
            ROUND(SUM(energy),2) as sum_harian_energi,
            client_id
            FROM {} 
            WHERE client_id = 7
            AND MONTH(db_created_at)={}
            AND YEAR(db_created_at)={}
            GROUP BY day
            """.format(tb_name, bulan, tahun)
    cursor.execute(sql)
    all_data = cursor.fetchall()
    hasil = {  
        "suryaAC_id": 7,
        "bulan": bulan,
        "tahun": tahun,
        "units": [{"avg_harian_tegangan": "V", "avg_harian_arus": "A", "sum_harian_daya": "W", "sum_harian_energi":"Wh"}],
        "value": []
        }   
    for i in range(0, len(all_data)):
        data = [{
            "tanggal": all_data[i][0],
            "value": {
                "avg_harian_tegangan": all_data[i][4],
                "avg_harian_arus": all_data[i][5],
                "sum_harian_daya": all_data[i][6],
                "sum_harian_energi": all_data[i][7],
            }
            }]
        hasil["value"].append(data[0])
    return jsonify(hasil)

@api.route("/ebt/akumulasi/harian/turbin", methods=["GET"])
def harian_turbin():
    db = koneksi_db()
    cursor = db.cursor()
    bulan = str(request.args['bulan'])
    tahun = str(request.args['tahun'])

    sql = """SET SESSION sql_mode = sys.list_drop(@@SESSION.sql_mode, 'ONLY_FULL_GROUP_BY');"""
    cursor.execute(sql)
    sql = """SELECT DATE(db_created_at) as day,
            WEEK(db_created_at) as week,
            MONTH(db_created_at) as month,
            YEAR(db_created_at) as year,
            ROUND(AVG(voltage),2) as avg_harian_tegangan,
            ROUND(AVG(current),2) as avg_harian_arus,
            ROUND(SUM(power),2) as sum_harian_daya,
            ROUND(SUM(energy),2) as sum_harian_energi,
            client_id
            FROM {} 
            WHERE client_id = 8 
            AND MONTH(db_created_at)={} 
            AND YEAR(db_created_at)={}
            GROUP BY day
            """.format(tb_name, bulan, tahun)
    cursor.execute(sql)
    all_data = cursor.fetchall()
    hasil = {  
        "turbin_id": 8,
        "bulan": bulan,
        "tahun": tahun,
        "units": [{"avg_harian_tegangan": "V", "avg_harian_arus": "A", "sum_harian_daya": "W", "sum_harian_energi":"Wh"}],
        "value": []
        }   
    for i in range(0, len(all_data)):
        data = [{
            "tanggal": all_data[i][0],
            "value": {
                "avg_harian_tegangan": all_data[i][4],
                "avg_harian_arus": all_data[i][5],
                "sum_harian_daya": all_data[i][6],
                "sum_harian_energi": all_data[i][7],
            }
            }]
        hasil["value"].append(data[0])
    return jsonify(hasil)

# --------------- API AKUMULASI DATA MINGGUAN DALAM 1 BULAN ---------- #
@api.route("/ebt/akumulasi/mingguan/suryaDC", methods=["GET"])
def mingguan_suryaDC():
    db = koneksi_db()
    cursor = db.cursor()
    bulan = str(request.args['bulan'])
    tahun = str(request.args['tahun'])

    sql = """SET SESSION sql_mode = sys.list_drop(@@SESSION.sql_mode, 'ONLY_FULL_GROUP_BY');"""
    cursor.execute(sql)
    sql = """SELECT DATE(db_created_at) as day,
            WEEK(db_created_at) as week,
            MONTH(db_created_at) as month,
            YEAR(db_created_at) as year,
            ROUND(AVG(voltage),2) as avg_mingguan_tegangan,
            ROUND(AVG(current),2) as avg_mingguan_arus,
            ROUND(SUM(power),2) as sum_mingguan_daya,
            ROUND(SUM(energy),2) as sum_mingguan_energi,
            client_id
            FROM {} 
            WHERE client_id = 6
            AND MONTH(db_created_at)={}
            AND YEAR(db_created_at)={}
            GROUP BY week
            """.format(tb_name, bulan, tahun)
    cursor.execute(sql)
    all_data = cursor.fetchall()
    hasil = {  
        "suryaDC_id": 6,
        "bulan": bulan,
        "tahun": tahun,
        "units": [{"avg_mingguan_tegangan": "V", "avg_mingguan_arus": "A", "sum_mingguan_daya": "W", "sum_mingguan_energi":"Wh"}],
        "value": []
        }   
    for i in range(0, len(all_data)):
        data = [{
            "minggu_ke": all_data[i][1],
            "value": {
                "avg_mingguan_tegangan": all_data[i][4],
                "avg_mingguan_arus": all_data[i][5],
                "sum_mingguan_daya": all_data[i][6],
                "sum_mingguan_energi": all_data[i][7],
            }
            }]
        hasil["value"].append(data[0])
    return jsonify(hasil)

@api.route("/ebt/akumulasi/mingguan/suryaAC", methods=["GET"])
def mingguan_suryaAC():
    db = koneksi_db()
    cursor = db.cursor()
    bulan = str(request.args['bulan'])
    tahun = str(request.args['tahun'])

    sql = """SET SESSION sql_mode = sys.list_drop(@@SESSION.sql_mode, 'ONLY_FULL_GROUP_BY');"""
    cursor.execute(sql)
    sql = """SELECT DATE(db_created_at) as day,
            WEEK(db_created_at) as week,
            MONTH(db_created_at) as month,
            YEAR(db_created_at) as year,
            ROUND(AVG(voltage),2) as avg_mingguan_tegangan,
            ROUND(AVG(current),2) as avg_mingguan_arus,
            ROUND(SUM(power),2) as sum_mingguan_daya,
            ROUND(SUM(energy),2) as sum_mingguan_energi,
            client_id
            FROM {} 
            WHERE client_id = 7
            AND MONTH(db_created_at)={}
            AND YEAR(db_created_at)={}
            GROUP BY week
            """.format(tb_name, bulan, tahun)
    cursor.execute(sql)
    all_data = cursor.fetchall()
    hasil = {  
        "suryaAC_id": 7,
        "bulan": bulan,
        "tahun": tahun,
        "units": [{"avg_mingguan_tegangan": "V", "avg_mingguan_arus": "A", "sum_mingguan_daya": "W", "sum_mingguan_energi":"Wh"}],
        "value": []
        }   
    for i in range(0, len(all_data)):
        data = [{
            "minggu_ke": all_data[i][1],
            "value": {
                "avg_mingguan_tegangan": all_data[i][4],
                "avg_mingguan_arus": all_data[i][5],
                "sum_mingguan_daya": all_data[i][6],
                "sum_mingguan_energi": all_data[i][7],
            }
            }]
        hasil["value"].append(data[0])
    return jsonify(hasil)

@api.route("/ebt/akumulasi/mingguan/turbin", methods=["GET"])
def mingguan_turbin():
    db = koneksi_db()
    cursor = db.cursor()
    bulan = str(request.args['bulan'])
    tahun = str(request.args['tahun'])

    sql = """SET SESSION sql_mode = sys.list_drop(@@SESSION.sql_mode, 'ONLY_FULL_GROUP_BY');"""
    cursor.execute(sql)
    sql = """SELECT DATE(db_created_at) as day,
            WEEK(db_created_at) as week,
            MONTH(db_created_at) as month,
            YEAR(db_created_at) as year,
            ROUND(AVG(voltage),2) as avg_mingguan_tegangan,
            ROUND(AVG(current),2) as avg_mingguan_arus,
            ROUND(SUM(power),2) as sum_mingguan_daya,
            ROUND(SUM(energy),2) as sum_mingguan_energi,
            client_id
            FROM {} 
            WHERE client_id = 8
            AND MONTH(db_created_at)={}
            AND YEAR(db_created_at)={}
            GROUP BY week
            """.format(tb_name, bulan, tahun)
    cursor.execute(sql)
    all_data = cursor.fetchall()
    hasil = {  
        "turbin_id": 8,
        "bulan": bulan,
        "tahun": tahun,
        "units": [{"avg_mingguan_tegangan": "V", "avg_mingguan_arus": "A", "sum_mingguan_daya": "W", "sum_mingguan_energi":"Wh"}],
        "value": []
        }   
    for i in range(0, len(all_data)):
        data = [{
            "minggu_ke": all_data[i][1],
            "value": {
                "avg_mingguan_tegangan": all_data[i][4],
                "avg_mingguan_arus": all_data[i][5],
                "sum_mingguan_daya": all_data[i][6],
                "sum_mingguan_energi": all_data[i][7],
            }
            }]
        hasil["value"].append(data[0])
    return jsonify(hasil)

# --------------- API AKUMULASI DATA BULANAN DALAM 1 TAHUN ---------- #
@api.route("/ebt/akumulasi/bulanan/suryaDC", methods=["GET"])
def bulanan_suryaDC():
    db = koneksi_db()
    cursor = db.cursor()
    tahun = str(request.args['tahun'])

    sql = """SET SESSION sql_mode = sys.list_drop(@@SESSION.sql_mode, 'ONLY_FULL_GROUP_BY');"""
    cursor.execute(sql)
    sql = """SELECT DATE(db_created_at) as day,
            WEEK(db_created_at) as week,
            MONTH(db_created_at) as month,
            YEAR(db_created_at) as year,
            ROUND(AVG(voltage),2) as avg_bulanan_tegangan,
            ROUND(AVG(current),2) as avg_bulanan_arus,
            ROUND(SUM(power),2) as sum_bulanan_daya,
            ROUND(SUM(energy),2) as sum_bulanan_energi,
            client_id
            FROM {} 
            WHERE client_id = 6 
            AND YEAR(db_created_at)={}
            GROUP BY month""".format(tb_name, tahun)
    cursor.execute(sql)
    all_data = cursor.fetchall()
    hasil = { 
        "suryaDC_id": 6, 
        "tahun": tahun,
        "units": [{"avg_bulanan_tegangan": "V", "avg_bulanan_arus": "A", "sum_bulanan_daya": "W", "sum_bulanan_energi":"Wh"}],
        "value": []
        }   
    for i in range(0, len(all_data)):
        data = [{
            "bulan_ke": all_data[i][2],
            "value": {
                "avg_bulanan_tegangan": all_data[i][4],
                "avg_bulanan_arus": all_data[i][5],
                "sum_bulanan_daya": all_data[i][6],
                "sum_bulanan_energi": all_data[i][7],
            }
            }]
        hasil["value"].append(data[0])
    return jsonify(hasil)

@api.route("/ebt/akumulasi/bulanan/suryaAC", methods=["GET"])
def bulanan_suryaAC():
    db = koneksi_db()
    cursor = db.cursor()
    tahun = str(request.args['tahun'])

    sql = """SET SESSION sql_mode = sys.list_drop(@@SESSION.sql_mode, 'ONLY_FULL_GROUP_BY');"""
    cursor.execute(sql)
    sql = """SELECT DATE(db_created_at) as day,
            WEEK(db_created_at) as week,
            MONTH(db_created_at) as month,
            YEAR(db_created_at) as year,
            ROUND(AVG(voltage),2) as avg_bulanan_tegangan,
            ROUND(AVG(current),2) as avg_bulanan_arus,
            ROUND(SUM(power),2) as sum_bulanan_daya,
            ROUND(SUM(energy),2) as sum_bulanan_energi,
            client_id
            FROM {} 
            WHERE client_id = 7 
            AND YEAR(db_created_at)={}
            GROUP BY month""".format(tb_name, tahun)
    cursor.execute(sql)
    all_data = cursor.fetchall()
    hasil = {  
        "suryaAC_id": 7,
        "tahun": tahun,
        "units": [{"avg_bulanan_tegangan": "V", "avg_bulanan_arus": "A", "sum_bulanan_daya": "W", "sum_bulanan_energi":"Wh"}],
        "value": []
        }   
    for i in range(0, len(all_data)):
        data = [{
            "bulan_ke": all_data[i][2],
            "value": {
                "avg_bulanan_tegangan": all_data[i][4],
                "avg_bulanan_arus": all_data[i][5],
                "sum_bulanan_daya": all_data[i][6],
                "sum_bulanan_energi": all_data[i][7],
            }
            }]
        hasil["value"].append(data[0])
    return jsonify(hasil)

@api.route("/ebt/akumulasi/bulanan/turbin", methods=["GET"])
def bulanan_turbin():
    db = koneksi_db()
    cursor = db.cursor()
    tahun = str(request.args['tahun'])

    sql = """SET SESSION sql_mode = sys.list_drop(@@SESSION.sql_mode, 'ONLY_FULL_GROUP_BY');"""
    cursor.execute(sql)
    sql = """SELECT DATE(db_created_at) as day,
            WEEK(db_created_at) as week,
            MONTH(db_created_at) as month,
            YEAR(db_created_at) as year,
            ROUND(AVG(voltage),2) as avg_bulanan_tegangan,
            ROUND(AVG(current),2) as avg_bulanan_arus,
            ROUND(SUM(power),2) as sum_bulanan_daya,
            ROUND(SUM(energy),2) as sum_bulanan_energi,
            client_id
            FROM {} 
            WHERE client_id = 8 
            AND YEAR(db_created_at)={}
            GROUP BY month""".format(tb_name, tahun)
    cursor.execute(sql)
    all_data = cursor.fetchall()
    hasil = { 
        "turbin_id": 8, 
        "tahun": tahun,
        "units": [{"avg_bulanan_tegangan": "V", "avg_bulanan_arus": "A", "sum_bulanan_daya": "W", "sum_bulanan_energi":"Wh"}],
        "value": []
        }   
    for i in range(0, len(all_data)):
        data = [{
            "bulan_ke": all_data[i][2],
            "value": {
                "avg_bulanan_tegangan": all_data[i][4],
                "avg_bulanan_arus": all_data[i][5],
                "sum_bulanan_daya": all_data[i][6],
                "sum_bulanan_energi": all_data[i][7],
            }
            }]
        hasil["value"].append(data[0])
    return jsonify(hasil)

if __name__ == '__main__':
    api.run(debug=True, host="0.0.0.0", port=5000)
