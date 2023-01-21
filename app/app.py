from flask import Flask, json, request, jsonify
import mysql.connector
#from time import sleep

api = Flask(__name__)
api.config["DEBUG"] = True
api.config['JSON_SORT_KEYS'] = False

"""CONNECT DATABASE"""
"""for i in range(10):
    try:
        db = mysql.connector.connect(host='db', user='root', password='root', database='db_komunikasi_data') #host='localhost', user='root', password='', database='db_komunikasi_data', buffered=True
    except:
        pass
    sleep(1)
tb_name = 'dummy_data_v2'
cursor = db.cursor()
"""
@api.route('/', methods=['GET'])
def coba():
    return 'Hallo EBT!!!'

@api.route("/dummy_komunikasi_data_v2", methods=['POST','GET'])
def dummy():
    db = mysql.connector.connect(host='db', user='root', password='root', database='db_komunikasi_data') #host='localhost', user='root', password='', database='db_komunikasi_data', buffered=True
    tb_name = 'dummy_data_v2'
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

if __name__ == '__main__':
    api.run(debug=True, host="0.0.0.0", port=5000)
