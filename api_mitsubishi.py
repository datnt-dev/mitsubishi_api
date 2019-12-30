import json
import decimal
from flask import Flask, request, jsonify
# from flask_restful import marshal
from database import get_connection
# from flask_marshmallow import Marshmallow


app = Flask(__name__)


def json_encode_decimal(obj):
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    raise TypeError(repr(obj) + " is not JSON serializable")

# def get_state(param):
#   connect = get_connection()

#   cursor = connect.cursor()
#   sql = """
#           SELECT MAC_ADDRESS, CURRENT_STATE, TIME_OFF, TIME_GREEN, TIME_RED, TIME_YELLOW, ACTUAL_QTY FROM PATLITE_STATE_CONTROL
#           WHERE MAC_ADDRESS=?
#         """
#   params = param
#   cursor.execute(sql, params)
#   return cursor


@app.route('/api/state/<mac_address>')
def get_state(mac_address):
    try:
        connect = get_connection()

        cursor = connect.cursor()
        sql = """
                { CALL get_state (@mac=?) }
              """
        cursor.execute(sql, mac_address)
        rows = cursor.fetchall()
        
        return {
            'name': rows[0][0],
            'red': rows[0][1],
            'yellow': rows[0][2],
            'green': rows[0][3],
            'led1_on_off': rows[0][4],
            'led2_on_off': rows[0][5],
            'temp': rows[0][6]
        }
            
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connect.close()

@app.route('/api/state')
def get_state_all():
    try:
        connect = get_connection()

        cursor = connect.cursor()
        sql = """
                SELECT MAC_ADDRESS, RED, YELLOW, GREEN, LED1_ON_OFF, LED2_ON_OFF, NHIET_DO FROM PLC_STATE_CONTROL
              """
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        # print(columns)
        results = []

        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))  
        
        return jsonify(results)

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connect.close()

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8069)
