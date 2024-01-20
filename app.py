from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from item_stack import ItemStack
from resource_finder import ResourceFinder

import logging
import psycopg2

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")  # Allow connections from http://localhost:3000
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

db_params = {
    'dbname': 'neptune-data',
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'port': '5432',
}

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@socketio.on('connect', namespace='/')
def connect():
    print('Client connected')

@socketio.on('disconnect', namespace='/')
def disconnect():
    print('Client disconnected')

@socketio.on('data_changed', namespace = '/')
def handle_data_change():
    emit('data_changed', broadcast=True)

@app.route('/wallets', methods=['GET'])
def get_wallets():
    try:
        id = request.args.get('id')
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM wallets WHERE wallet_id = ' + id)
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in data]
        return jsonify(result)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/wallets', methods=['POST'])
def post_wallets():
    try:
        payload = request.json
        ones = payload.get('ONE', 0)
        fives = payload.get('FIVE', 0)
        tens = payload.get('TEN', 0)
        twenties = payload.get('TWENTY', 0)
        fifties = payload.get('FIFTY', 0)
        hundreds = payload.get('HUNDRED', 0)

        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute('UPDATE wallets set ones = %s WHERE wallet_id = 1', (ones,))
        cursor.execute('UPDATE wallets set fives = %s WHERE wallet_id = 1', (fives,))
        cursor.execute('UPDATE wallets set tens = %s WHERE wallet_id = 1', (tens,))
        cursor.execute('UPDATE wallets set twenties = %s WHERE wallet_id = 1', (twenties,))
        cursor.execute('UPDATE wallets set fifties = %s WHERE wallet_id = 1', (fifties,))
        cursor.execute('UPDATE wallets set hundreds = %s WHERE wallet_id = 1', (hundreds,))

        connection.commit()
        cursor.close()
        connection.close()
        # Notify clients about the data change
        socketio.emit('data_changed', namespace='/')
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/feeling', methods=["GET"])
def get_feeling():
    try:
        id = request.args.get('id')
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute('SELECT feeling FROM players WHERE player_id = %s', (id,))
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        # columns = [col[0] for col in cursor.description]
        # result = [dict(zip(columns, row)) for row in data]
        return jsonify(data[0][0])
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500    

@app.route('/hydration/subtract', methods=["POST"])
def subtract_hydration():
    try:
        payload = request.json
        id = payload
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute('SELECT hydration FROM players WHERE player_id = %s', (id,))
        data = cursor.fetchone()
        if data is not None:
            newHydration = data[0] - 1
            cursor.execute('UPDATE players SET hydration=%s WHERE player_id = %s', (newHydration, id,))
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify(True)
        else:
            return jsonify({'error': 'Player not found'}), 404
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/purchaseItem', methods=["POST"])
def purchase_item():
    try:
        payload = request.json
        id = payload["id"]
        itemName = payload["itemName"]
        connection = psycopg2.connect(**db_params)
        attribute = "fullness"
        itemStrength = 50
        billQuantityRequired = 1
        billDenominationRequired = "tens"
        if itemName == 'pizza':
            itemStrength = 30
            billDenominationRequired = "fives"
        if itemName == 'drink':
            attribute = "hydration"
            itemStrength = 20
            billQuantityRequired = 2
            billDenominationRequired = "ones"
        cursor = connection.cursor()

        cursor.execute('SELECT {} FROM wallets WHERE wallet_id = %s'.format(billDenominationRequired), (id,))
        wallet_data = cursor.fetchone()

        if (wallet_data[0] >= billQuantityRequired):
            cursor.execute('SELECT {} FROM players WHERE player_id = %s'.format(attribute), (id,))
            player_data = cursor.fetchone()
            if player_data is not None:
                newValue = player_data[0] + itemStrength
                cursor.execute('UPDATE players SET {}=%s WHERE player_id = %s'.format(attribute), (newValue, id,))
                newWalletValue = wallet_data[0] - billQuantityRequired
                cursor.execute('UPDATE wallets SET {}=%s WHERE wallet_id = %s'.format(billDenominationRequired), (newWalletValue, id,))
                connection.commit()
                cursor.close()
                connection.close()
                socketio.emit('data_changed', namespace='/')
                return jsonify(True)
            else:
                return jsonify({'error': 'Player not found'}), 404
        else:
            return jsonify(False)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/breakBill', methods=["POST"])
def break_bill():
    try:
        payload = request.json
        id = payload["id"]
        denomination = payload["denomination"]
        connection = psycopg2.connect(**db_params)
        receivedBillType = "ones"
        receivedBillQuantity = 5
        givenBillType = "fives"
        if denomination == 20:
            receivedBillType = "fives"
            givenBillType = "twenties"
            receivedBillQuantity = 4
        if denomination == 100:
            receivedBillType = "twenties"
            givenBillType = "hundreds"
            receivedBillQuantity = 5
        cursor = connection.cursor()

        cursor.execute('SELECT {} FROM wallets WHERE wallet_id = %s'.format(givenBillType), (id,))
        given_bill_data = cursor.fetchone()

        if (given_bill_data[0] >= 1):
            cursor.execute('SELECT {} FROM wallets WHERE wallet_id = %s'.format(receivedBillType), (id,))
            received_bill_data = cursor.fetchone()
            if received_bill_data is not None:
                newReceivedBillQuantity = received_bill_data[0] + receivedBillQuantity
                cursor.execute('UPDATE wallets SET {}=%s WHERE wallet_id = %s'.format(receivedBillType), (newReceivedBillQuantity, id,))
                newGivenBillQuantity = given_bill_data[0] - 1
                cursor.execute('UPDATE wallets SET {}=%s WHERE wallet_id = %s'.format(givenBillType), (newGivenBillQuantity, id,))
                connection.commit()
                cursor.close()
                connection.close()
                socketio.emit('data_changed', namespace='/')
                return jsonify(True)
            else:
                return jsonify({'error': 'Player not found'}), 404
        else:
            return jsonify(False)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/exchangeCash', methods=["POST"])
def exchange_cash():
    try:
        payload = request.json
        id = payload["id"]
        denomination = payload["denomination"]
        connection = psycopg2.connect(**db_params)
        receivedChipType = "chip_ones"
        receivedChipQuantity = 1
        givenBillType = "ones"
        if denomination == 5:
            receivedChipType = "chip_fives"
            receivedChipQuantity = 1
            givenBillType = "fives"
        if denomination == 10:
            receivedChipType = "chip_fives"
            receivedChipQuantity = 2
            givenBillType = "tens"
        if denomination == 20:
            receivedChipType = "chip_fives"
            receivedChipQuantity = 4
            givenBillType = "twenties"
        if denomination == 50:
            receivedChipType = "chip_twentyfives"
            receivedChipQuantity = 2
            givenBillType = "fifties"
        if denomination == 100:
            receivedChipType = "chip_hundreds"
            receivedChipQuantity = 1
            givenBillType = "hundreds"
        cursor = connection.cursor()

        cursor.execute('SELECT {} FROM wallets WHERE wallet_id = %s'.format(givenBillType), (id,))
        given_bill_data = cursor.fetchone()

        if (given_bill_data[0] >= 1):
            cursor.execute('SELECT {} FROM wallets WHERE wallet_id = %s'.format(receivedChipType), (id,))
            received_chip_data = cursor.fetchone()
            if received_chip_data is not None:
                newReceivedChipQuantity = received_chip_data[0] + receivedChipQuantity
                cursor.execute('UPDATE wallets SET {}=%s WHERE wallet_id = %s'.format(receivedChipType), (newReceivedChipQuantity, id,))
                newGivenBillQuantity = given_bill_data[0] - 1
                cursor.execute('UPDATE wallets SET {}=%s WHERE wallet_id = %s'.format(givenBillType), (newGivenBillQuantity, id,))
                connection.commit()
                cursor.close()
                connection.close()
                socketio.emit('data_changed', namespace='/')
                return jsonify(True)
            else:
                return jsonify({'error': 'Player not found'}), 404
        else:
            return jsonify(False)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500
    
@app.route('/exchangeChips', methods=["POST"])
def exchange_chips():
    try:
        payload = request.json
        id = payload["id"]
        denomination = payload["denomination"]
        connection = psycopg2.connect(**db_params)
        receivedBillType = "ones"
        givenChipQuantity = 1
        givenChipType = "chip_ones"
        if denomination == 5:
            receivedBillType = "fives"
            givenChipQuantity = 1
            givenChipType = "chip_fives"
        if denomination == 10:
            receivedBillType = "tens"
            givenChipQuantity = 2
            givenChipType = "chip_fives"
        if denomination == 20:
            receivedBillType = "twenties"
            givenChipQuantity = 4
            givenChipType = "chip_fives"
        if denomination == 50:
            receivedBillType = "fifties"
            givenChipQuantity = 2
            givenChipType = "chip_twentyfives"
        if denomination == 100:
            receivedBillType = "hundreds"
            givenChipQuantity = 1
            givenChipType = "chip_hundreds"
        cursor = connection.cursor()

        cursor.execute('SELECT {} FROM wallets WHERE wallet_id = %s'.format(givenChipType), (id,))
        given_chip_data = cursor.fetchone()

        if (given_chip_data[0] >= givenChipQuantity):
            cursor.execute('SELECT {} FROM wallets WHERE wallet_id = %s'.format(receivedBillType), (id,))
            received_bill_data = cursor.fetchone()
            if received_bill_data is not None:
                newReceivedBillQuantity = received_bill_data[0] + 1
                cursor.execute('UPDATE wallets SET {}=%s WHERE wallet_id = %s'.format(receivedBillType), (newReceivedBillQuantity, id,))
                newGivenChipQuantity = given_chip_data[0] - givenChipQuantity
                cursor.execute('UPDATE wallets SET {}=%s WHERE wallet_id = %s'.format(givenChipType), (newGivenChipQuantity, id,))
                connection.commit()
                cursor.close()
                connection.close()
                socketio.emit('data_changed', namespace='/')
                return jsonify(True)
            else:
                return jsonify({'error': 'Player not found'}), 404
        else:
            return jsonify(False)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/fullness/subtract', methods=["POST"])
def subtract_fullness():
    try:
        payload = request.json
        id = payload
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute('SELECT fullness FROM players WHERE player_id = %s', (id,))
        data = cursor.fetchone()
        if data is not None:
            newFullness = data[0] - 1
            cursor.execute('UPDATE players SET fullness=%s WHERE player_id = %s', (newFullness, id,))
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify(True)
        else:
            return jsonify({'error': 'Player not found'}), 404
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/hydration', methods=["GET"])
def get_hydration():
    try:
        id = request.args.get('id')
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute('SELECT hydration FROM players WHERE player_id = %s', (id,))
        data = cursor.fetchall()
        # print(data)
        cursor.close()
        connection.close()
        # columns = [col[0] for col in cursor.description]
        # print(columns)
        # result = [dict(zip(columns, row)) for row in data]
        # print(result)
        return jsonify(data[0][0])
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500  
    
@app.route('/fullness', methods=["GET"])
def get_fullness():
    try:
        id = request.args.get('id')
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute('SELECT fullness FROM players WHERE player_id = %s', (id,))
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        # columns = [col[0] for col in cursor.description]
        # result = [dict(zip(columns, row)) for row in data]
        return jsonify(data[0][0])
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500  

@app.route('/playerChips', methods=['POST'])
def post_player_chips():
    try:
        payload = request.json
        chip_ones = payload.get('ONE', 0)
        chip_twofifties = payload.get('TWO_FIFTY', 0)
        chip_fives = payload.get('FIVE', 0)
        chip_twentyfives = payload.get('TWENTY_FIVE', 0)
        chip_hundreds = payload.get('HUNDRED', 0)

        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute('UPDATE wallets set chip_ones = %s WHERE wallet_id = 1', (chip_ones,))
        cursor.execute('UPDATE wallets set chip_twofifties = %s WHERE wallet_id = 1', (chip_twofifties,))
        cursor.execute('UPDATE wallets set chip_fives = %s WHERE wallet_id = 1', (chip_fives,))
        cursor.execute('UPDATE wallets set chip_twentyfives = %s WHERE wallet_id = 1', (chip_twentyfives,))
        cursor.execute('UPDATE wallets set chip_hundreds = %s WHERE wallet_id = 1', (chip_hundreds,))

        connection.commit()
        cursor.close()
        connection.close()
        # Notify clients about the data change
        socketio.emit('data_changed', namespace='/')
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/playersClub', methods=['POST'])
def post_players_club():
    try:
        payload = request.json

        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute('UPDATE wallets set players_club = %s WHERE wallet_id = 1', (payload,))

        connection.commit()
        cursor.close()
        connection.close()
        # Notify clients about the data change
        socketio.emit('data_changed', namespace='/')
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500
    
@app.route('/debitCardInWallet', methods=['POST'])
def post_debit_card_in_wallet():
    try:
        payload = request.json

        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        cursor.execute('UPDATE wallets set debit_card = %s WHERE wallet_id = 1', (payload,))

        connection.commit()
        cursor.close()
        connection.close()
        # Notify clients about the data change
        socketio.emit('data_changed', namespace='/')
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/resource', methods=['GET'])
def get_resource():
    try:
        chip_value_for_color = float(request.args.get('chipColorValue', default=0.0))
        dollar_value_for_jpeg = float(request.args.get('dollarJpegValue', default=0.0))
        chip_value_for_string = float(request.args.get('chipChangeStringValue', default=0.0))
        bill_value_for_chip_string = float(request.args.get('billForChipStringValue', default=0.0))
        resource_finder = ResourceFinder()
        if chip_value_for_color > 0:
            return jsonify({"chip_color": resource_finder.get_resource(chip_value_for_color, "color")})
        if dollar_value_for_jpeg > 0:
            return jsonify({"dollar_jpeg_name": resource_finder.get_resource(dollar_value_for_jpeg, "dollar_jpeg")})
        if chip_value_for_string > 0:
            return jsonify({"chip_change_string": resource_finder.get_resource(chip_value_for_string, "chip_change")})
        if bill_value_for_chip_string > 0:
            return jsonify({"chip_name": resource_finder.get_resource(bill_value_for_chip_string, "bill_to_chip")})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid resource request"}), 400

@app.route('/images/exchange', methods=['GET'])
def exchange_filename():
    try:
        bill_value_cash = float(request.args.get('billValue', default=0.0))
        chip_value_cash = float(request.args.get('chipValue', default=0.0))
        resource_finder = ResourceFinder()
        if bill_value_cash > 0:
            return jsonify({"filename": resource_finder.get_resource(bill_value_cash, "cash_exchange")})
        else:
            return jsonify({"filename": resource_finder.get_resource(chip_value_cash, "chip_exchange")})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid bill value"}), 400

@app.route('/doubles', methods=['GET'])
def denomination_value_route():
    try:
        denomination_name = str(request.args.get('name'))
        resource_name = ItemStack.denomination_value(denomination_name)
        return jsonify({"value": resource_name})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid denomination name"}), 400

def verify_keys(save_state):
    required_keys = ['playerBankAccountBalance']
    for key in required_keys:
        if key not in save_state:
            return jsonify({'error': f'save_state missing required key: {key}'}), 400
    return None

@app.route('/saveState/bills', methods=['PUT'])
def modify_bills():
    try:
        double_param = float(request.args.get('exactValue', default=0.0))
        denomination_param = str(request.args.get('denomination', default=""))
        quantity = int(request.args.get('quantity', default=0))
        save_state = request.get_json()
        verify_result = verify_keys(save_state)
        if verify_result is not None:
            return verify_result
        bill_stack = ItemStack(save_state['playerBills'])
        if double_param > 0:
            new_stack = ItemStack.generate_bill_stack_from_total(double_param)
            bill_stack = bill_stack.add_stack(new_stack)
        elif double_param < 0:
            stack_to_remove = bill_stack.find_bill_combination(double_param * -1)
            bill_stack = bill_stack.subtract_stack(stack_to_remove)
        else:
            bill_stack = bill_stack.modify_items(denomination_param, quantity)
        save_state['playerBills'] = bill_stack.item_frequencies
        return jsonify(save_state)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for modifying bills"}), 400

@app.route('/saveState/chips', methods=['PUT'])
def modify_chips():
    try:
        double_param = float(request.args.get('exactValue', default=0.0))
        denomination_param = str(request.args.get('denomination', default=""))
        quantity = int(request.args.get('quantity', default=0))
        save_state = request.get_json()
        verify_result = verify_keys(save_state)
        if verify_result is not None:
            return verify_result
        chip_stack = ItemStack(save_state['playerChips'])
        if double_param > 0:
            new_stack = ItemStack.generate_chip_stack_from_total(double_param)
            chip_stack = chip_stack.add_stack(new_stack)
        elif double_param < 0:
            stack_to_remove = chip_stack.find_chip_combination(double_param)
            chip_stack = chip_stack.subtract_stack(stack_to_remove)
        else:
            chip_stack = chip_stack.modify_items(denomination_param, quantity)
        save_state['playerChips'] = chip_stack.item_frequencies
        return jsonify(save_state)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for modifying chips"}), 400

@app.route('/saveState/bills/value', methods=['GET', 'POST'])
def get_bill_value():
    try:
        cover_value_param = float(request.args.get('coverValue', default=0.0))
        save_state = request.get_json()
        bill_stack = ItemStack(save_state['playerBills'])
        if cover_value_param > 0.0:
            found_stack = bill_stack.find_bill_combination(cover_value_param)
            if found_stack:
                return jsonify(0.0)
            else:
                return jsonify(1.0)
        else:
            return jsonify(bill_stack.get_stack_value())
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for getting bill value"}), 400

@app.route('/saveState/chips/value', methods=['GET', 'POST'])
def get_save_state_chip_value():
    try:
        save_state = request.get_json()
        chip_stack = ItemStack(save_state['playerChips'])
        return jsonify(chip_stack.get_stack_value())
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for getting chip value"}), 400

@app.route('/chips/value', methods=['GET', 'POST'])
def get_chip_stack_value():
    try:
        chip_freq_map = request.get_json()
        stack = ItemStack(chip_freq_map)
        return jsonify(stack.get_stack_value())
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for getting chip value"}), 400

@app.route('/saveState/chips', methods=['GET', 'POST'])
def get_count_of_chips():
    try:
        chip_denom_param = str(request.args.get('chipDenomination', default=""))
        save_state = request.get_json()
        chip_stack = ItemStack(save_state['playerChips'])
        return jsonify(chip_stack.count_type_of_item(chip_denom_param))
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for getting chip value"}), 400

@app.route('/saveState/transactions', methods=['GET', 'POST'])
def get_transactions():
    try:
        k_param = int(request.args.get('k', default=0))
        n_param = int(request.args.get('n', default=1))
        data = request.get_json()
        transactions = data.get('transactionHistory', [])
        selected_transactions = transactions[k_param:k_param + n_param]
        return jsonify(selected_transactions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stack/multiply', methods=['GET', 'POST'])
def multiply_stack():
    try:
        factor_param = float(request.args.get('factor', default=0.0))
        stack_json = request.get_json()
        stack = ItemStack(stack_json)
        stack = stack.multiply_stack_by_factor(factor_param)
        return jsonify(stack.item_frequencies)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=5000)
