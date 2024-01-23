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

def fetch_all(table_name, where_column, value_match):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM {} WHERE {} = {}'.format(table_name, where_column, value_match))
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, row)) for row in data]
    return result


def fetch_one(query_string, id):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute(query_string, (id, ))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

def fetch_one_column(column, table_name, where_column, value_match):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute('SELECT {} FROM {} WHERE {} = {}'.format(column, table_name, where_column, value_match))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

def update_one(query_string, new_value, id):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute(query_string, (new_value, id,))
    connection.commit()
    cursor.close()
    connection.close()

def update_one_column(table_name, column_to_set, new_value, where_column, value_match):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute('UPDATE {} SET {}={} WHERE {} = {}'.format(table_name, column_to_set, new_value, where_column, value_match))
    connection.commit()
    cursor.close()
    connection.close()


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
        result = fetch_all("wallets", "wallet_id", id)
        return jsonify(result)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/hasChips', methods=['GET'])
def has_chips():
    id = 1
    denomination = request.args.get('denomination')
    quantity = request.args.get('quantity')
    column = "chip_ones"
    if denomination == "TWO_FIFTY":
        column = "chip_twofifties"
    if denomination == "FIVE":
        column = "chip_fives"
    if denomination == "TWENTY_FIVE":
        column = "chip_twentyfives"
    if denomination == "HUNDRED":
        column = "chip_hundreds"
    data = fetch_one_column(column, "wallets", "wallet_id", id)
    if data[0] >= int(quantity):
        return jsonify(True)
    else:
        return jsonify(False)

@app.route('/feeling', methods=["GET"])
def get_feeling():
    try:
        id = request.args.get('id')
        data = fetch_one_column("feeling", "players" , "player_id", id)
        return jsonify(data[0])
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500    

@app.route('/hydration/subtract', methods=["POST"])
def subtract_hydration():
    try:
        id = request.json["playerId"]
        data = fetch_one_column("hydration", "players", "player_id", id)
        if data is not None:
            newHydration = data[0] - 1
            update_one_column("players", "hydration", newHydration, "player_id", id)
            socketio.emit('data_changed', namespace='/')
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

        wallet_data = fetch_one_column(billDenominationRequired, "wallets", "wallet_id", id)
        if (wallet_data[0] >= billQuantityRequired):
            player_data = fetch_one_column(attribute, "players", "player_id", id)
            if player_data is not None:
                newValue = player_data[0] + itemStrength
                update_one_column("players", attribute, newValue, "player_id", id)
                newWalletValue = wallet_data[0] - billQuantityRequired
                update_one_column("wallets", billDenominationRequired, newWalletValue, "wallet_id", id)
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

        given_bill_data = fetch_one_column(givenBillType, "wallets", "wallet_id", id)

        if (given_bill_data[0] >= 1):
            received_bill_data = fetch_one_column(receivedBillType, "wallets", "wallet_id", id)
            if received_bill_data is not None:
                newReceivedBillQuantity = received_bill_data[0] + receivedBillQuantity
                update_one_column("wallets", receivedBillType, newReceivedBillQuantity, "wallet_id", id)
                newGivenBillQuantity = given_bill_data[0] - 1
                update_one_column("wallets", givenBillType, newGivenBillQuantity, "wallet_id", id)
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

        given_bill_data = fetch_one_column(givenBillType, "wallets", "wallet_id", id)
        if (given_bill_data[0] >= 1):
            received_chip_data = fetch_one_column(receivedChipType, "wallets", "wallet_id", id)
            if received_chip_data is not None:
                newReceivedChipQuantity = received_chip_data[0] + receivedChipQuantity
                update_one_column("wallets", receivedChipType, newReceivedChipQuantity, "wallet_id", id)
                newGivenBillQuantity = given_bill_data[0] - 1
                update_one_column("wallets", givenBillType, newGivenBillQuantity, "wallet_id", id)
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

        given_chip_data = fetch_one_column(givenChipType, "wallets", "wallet_id", id)

        if (given_chip_data[0] >= givenChipQuantity):
            received_bill_data = fetch_one_column(receivedBillType, "wallets", "wallet_id", id)
            if received_bill_data is not None:
                newReceivedBillQuantity = received_bill_data[0] + 1
                update_one_column("wallets", receivedBillType, newReceivedBillQuantity, "wallet_id", id)
                newGivenChipQuantity = given_chip_data[0] - givenChipQuantity
                update_one_column("wallets", givenChipType, newGivenChipQuantity, "wallet_id", id)
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
        payload = request.json["playerId"]
        id = payload
        data = fetch_one_column("fullness", "players", "player_id", id)
        if data is not None:
            newFullness = data[0] - 1
            update_one_column("players", "fullness", newFullness, "player_id", id)
            socketio.emit('data_changed', namespace='/')
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
        data = fetch_one_column("hydration", "players", "player_id", id)
        return jsonify(data[0])
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500  
    
@app.route('/fullness', methods=["GET"])
def get_fullness():
    try:
        id = request.args.get('id')
        data = fetch_one_column("fullness", "players", "player_id", id)
        return jsonify(data[0])
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500  
    
@app.route('/balance', methods=["GET"])
def get_balance():
    try:
        id = request.args.get('id')
        data = fetch_one_column("account_balance", "players", "player_id", id)
        return jsonify(data[0])
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500  

@app.route('/atms', methods=["GET"])
def get_atm():
    try:
        id = request.args.get('id')
        result = fetch_all("atms", "atm_id", id)
        return jsonify(result)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500  

@app.route('/playersClub', methods=['POST'])
def post_players_club():
    try:
        payload = request.json["inClub"]
        update_one_column("wallets", "players_club", payload, "wallet_id", "1")
        socketio.emit('data_changed', namespace='/')
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500
    
@app.route('/debitCardInWallet', methods=['POST'])
def post_debit_card_in_wallet():
    try:
        payload = request.json["debitCardInWallet"]
        update_one_column("wallets", "debit_card", payload, "wallet_id", "1")
        socketio.emit('data_changed', namespace='/')
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/insertOrRemoveDebitCard', methods=['POST'])
def insert_or_remove_card():
    try:
        payload = request.json
        id = payload["id"]
        debit_card_in_wallet = fetch_one_column("debit_card", "wallets", "wallet_id", id)[0]
        if (debit_card_in_wallet):
            update_one_column("wallets", "debit_card", False, "wallet_id", "1")
            update_one_column("atms", "display_state", "'home'", "atm_id", "1")
            update_one_column("atms", "entry", "0", "atm_id", "1")
        else:
            print("in else")
            update_one_column("wallets", "debit_card", True, "wallet_id", "1")
            update_one_column("atms", "display_state", "'insert'", "atm_id", "1")
        socketio.emit('data_changed', namespace='/')
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500  

@app.route('/pressATMControlButton', methods=['POST'])
def press_atm_control_button():
    try:
        payload = request.json
        id = payload["id"]
        button_index = payload["button_index"]

        data = fetch_one_column("display_state", "atms", "atm_id", id)
        display_state = data[0]
        if button_index == 0:
            if display_state == "home":
                update_one_column("atms", "display_state", "'balance'", "atm_id", id)
        elif button_index == 1:
            if display_state == "home":
                update_one_column("atms", "entry", "0", "atm_id", id)
                update_one_column("atms", "display_state", "'initiate'", "atm_id", id)
            elif display_state == "confirm":
                update_one_column("atms", "display_state", "'home'", "atm_id", id)
                entry_data = fetch_one_column("entry", "atms", "atm_id", id)
                entry = entry_data[0]
                balance_data = fetch_one_column("account_balance", "players", "player_id", id)
                balance = balance_data[0]
                if int(entry) > 0 and int(entry) <= balance + 3:
                    balance = balance - int(entry) - 3
                    update_one_column("players", "account_balance", balance, "player_id", id)
                    new_stack = ItemStack.generate_bill_stack_from_total(int(entry))
                    ones_data = fetch_one_column("ones", "wallets", "wallet_id", id)
                    fives_data = fetch_one_column("fives", "wallets", "wallet_id", id)
                    tens_data = fetch_one_column("tens", "wallets", "wallet_id", id)
                    twenties_data = fetch_one_column("twenties", "wallets", "wallet_id", id)
                    fifties_data = fetch_one_column("fifties", "wallets", "wallet_id", id)
                    hundreds_data = fetch_one_column("hundreds", "wallets", "wallet_id", id)
                    billMap = {"ONE": ones_data[0], "FIVE": fives_data[0], "TEN": tens_data[0], "TWENTY": twenties_data[0], "FIFTY": fifties_data[0], "HUNDRED": hundreds_data[0]}
                    bill_stack = ItemStack(billMap)
                    bill_stack = bill_stack.add_stack(new_stack)
                    update_one_column("wallets", "ones", bill_stack.count_type_of_item("ONE"), "wallet_id", id)
                    update_one_column("wallets", "fives", bill_stack.count_type_of_item("FIVE"), "wallet_id", id)
                    update_one_column("wallets", "tens", bill_stack.count_type_of_item("TEN"), "wallet_id", id)
                    update_one_column("wallets", "twenties", bill_stack.count_type_of_item("TWENTY"), "wallet_id", id)
                    update_one_column("wallets", "fifties", bill_stack.count_type_of_item("FIFTY"), "wallet_id", id)
                    update_one_column("wallets", "hundreds", bill_stack.count_type_of_item("HUNDRED"), "wallet_id", id)
        elif button_index == 2:
            if display_state == "home":
                update_one_column("atms", "display_state", "'activity'", "atm_id", id)
        elif button_index == 3:
            if display_state == "home":
                update_one_column("atms", "entry", "0", "atm_id", id)
                update_one_column("atms", "display_state", "'deposit'", "atm_id", id)
            elif display_state == "balance":
                update_one_column("atms", "display_state", "'home'", "atm_id", id)
            elif display_state == "initiate":
                # TODO check if entry is > 0
                update_one_column("atms", "display_state", "'confirm'", "atm_id", id)
            elif display_state == "confirm":
                update_one_column("atms", "display_state", "'home'", "atm_id", id)
            elif display_state == "deposit":
                # TODO deposit bills
                update_one_column("atms", "display_state", "'home'", "atm_id", id)
        socketio.emit('data_changed', namespace='/')
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500 
    
@app.route('/pressATMWordButton', methods=['POST'])
def press_atm_word_button():
    try:
        payload = request.json
        id = payload["id"]
        button_word = payload["button_word"]
        data = fetch_one_column("display_state", "atms", "atm_id", id)
        display_state = data[0]
        if button_word == "cancel":
            if display_state != "insert":
                update_one_column("atms", "display_state", "'home'", "atm_id", id)
        elif button_word == "clear":
            if display_state == "balance" or display_state == "activity":
                update_one_column("atms", "display_state", "'home'", "atm_id", id)
            elif display_state == "initiate" or display_state == "deposit":
                update_one_column("atms", "entry", "0", "atm_id", id)
        elif button_word == "enter":
            if display_state == "initiate":
                # check entry is greater than 0
                update_one_column("atms", "display_state", "'confirm'", "atm_id", id)
            elif display_state == "confirm":
                # check entry + fee < bank balance
                # withdraw bills and subtract amount + fee from bank balance
                update_one_column("atms", "display_state", "'home'", "atm_id", id)
            elif display_state == "balance" or display_state == "activity":
                update_one_column("atms", "display_state", "'home'", "atm_id", id)
            elif display_state == "deposit":
                # deposit cash
                update_one_column("atms", "display_state", "'home'", "atm_id", id)
        socketio.emit('data_changed', namespace='/')
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500 
    
@app.route('/debitCard', methods=['GET'])
def debit_card():
    try:
        id = request.args.get('id')
        data = fetch_one_column("debit_card", "wallets", "wallet_id", id)
        return jsonify(data[0])
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500  

@app.route('/appendDigitToATM', methods=['POST'])
def append_atm_digit():
    try:
        payload = request.json
        id = payload["id"]
        digit = payload["digit"]
        display_state_data = fetch_one_column("display_state", "atms", "atm_id", id)
        display_state = display_state_data[0]
        if display_state == "deposit" or display_state == "initiate":
            data = fetch_one_column("entry", "atms", "atm_id", id)
            entry = data[0]
            new_entry = entry
            if (entry is None):
                new_entry = digit
                update_one_column("atms", "entry", new_entry, "atm_id", id)
            elif (len(entry) < 9):
                new_entry = entry + str(digit)
                update_one_column("atms", "entry", new_entry, "atm_id", id)
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

@app.route('/bills', methods=['PUT'])
def modify_bills():
    try:
        double_param = float(request.args.get('exactValue', default=0.0))
        denomination_param = str(request.args.get('denomination', default=""))
        quantity = int(request.args.get('quantity', default=0))
        id = 1
        ones_data = fetch_one_column("ones", "wallets", "wallet_id", id)
        fives_data = fetch_one_column("fives", "wallets", "wallet_id", id)
        tens_data = fetch_one_column("tens", "wallets", "wallet_id", id)
        twenties_data = fetch_one_column("twenties", "wallets", "wallet_id", id)
        fifties_data = fetch_one_column("fifties", "wallets", "wallet_id", id)
        hundreds_data = fetch_one_column("hundreds", "wallets", "wallet_id", id)
        billMap = {"ONE": ones_data[0], "FIVE": fives_data[0], "TEN": tens_data[0], "TWENTY": twenties_data[0], "FIFTY": fifties_data[0], "HUNDRED": hundreds_data[0]}
        bill_stack = ItemStack(billMap)
    
        if double_param > 0:
            new_stack = ItemStack.generate_bill_stack_from_total(double_param)
            bill_stack = bill_stack.add_stack(new_stack)
        elif double_param < 0:
            stack_to_remove = bill_stack.find_bill_combination(double_param * -1)
            bill_stack = bill_stack.subtract_stack(stack_to_remove)
        else:
            bill_stack = bill_stack.modify_items(denomination_param, quantity)

        update_one_column("wallets", "ones", bill_stack.count_type_of_item("ONE"), "wallet_id", id)
        update_one_column("wallets", "fives", bill_stack.count_type_of_item("FIVE"), "wallet_id", id)
        update_one_column("wallets", "tens", bill_stack.count_type_of_item("TEN"), "wallet_id", id)
        update_one_column("wallets", "twenties", bill_stack.count_type_of_item("TWENTY"), "wallet_id", id)
        update_one_column("wallets", "fifties", bill_stack.count_type_of_item("FIFTY"), "wallet_id", id)
        update_one_column("wallets", "hundreds", bill_stack.count_type_of_item("HUNDRED"), "wallet_id", id)
        
        socketio.emit('data_changed', namespace='/')
        return jsonify(True)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for modifying bills"}), 400

@app.route('/chips', methods=['PUT'])
def modify_chips():
    try:
        double_param = float(request.args.get('exactValue', default=0.0))
        denomination_param = str(request.args.get('denomination', default=""))
        quantity = int(request.args.get('quantity', default=0))
        id = 1
        ones_data = fetch_one_column("chip_ones", "wallets", "wallet_id", id)
        twofifties_data = fetch_one_column("chip_twofifties", "wallets", "wallet_id", id)
        fives_data = fetch_one_column("chip_fives", "wallets", "wallet_id", id)
        twentyfives_data = fetch_one_column("chip_twentyfives", "wallets", "wallet_id", id)
        hundreds_data = fetch_one_column("chip_hundreds", "wallets", "wallet_id", id)
        chipMap = {"ONE": ones_data[0], "FIVE": fives_data[0], "TWO_FIFTY": twofifties_data[0], "TWENTY_FIVE": twentyfives_data[0], "HUNDRED": hundreds_data[0]}
        chip_stack = ItemStack(chipMap)
        
        if double_param > 0:
            new_stack = ItemStack.generate_chip_stack_from_total(double_param)
            chip_stack = chip_stack.add_stack(new_stack)
        elif double_param < 0:
            stack_to_remove = chip_stack.find_chip_combination(double_param)
            chip_stack = chip_stack.subtract_stack(stack_to_remove)
        else:
            chip_stack = chip_stack.modify_items(denomination_param, quantity)

        update_one_column("wallets", "chip_ones", chip_stack.count_type_of_item("ONE"), "wallet_id", id)
        update_one_column("wallets", "chip_twofifties", chip_stack.count_type_of_item("TWO_FIFTY"), "wallet_id", id)
        update_one_column("wallets", "chip_fives", chip_stack.count_type_of_item("FIVE"), "wallet_id", id)
        update_one_column("wallets", "chip_twentyfives", chip_stack.count_type_of_item("TWENTY_FIVE"), "wallet_id", id)
        update_one_column("wallets", "chip_hundreds", chip_stack.count_type_of_item("HUNDRED"), "wallet_id", id)

        socketio.emit('data_changed', namespace='/')
        return jsonify(True)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for modifying chips"}), 400

@app.route('/clearBillsAndChips', methods=['PUT'])
def clear_bills_and_chips():
    try:
        id = 1

        update_one_column("wallets", "chip_ones", "0", "wallet_id", id)
        update_one_column("wallets", "chip_twofifties", "0", "wallet_id", id)
        update_one_column("wallets", "chip_fives", "0", "wallet_id", id)
        update_one_column("wallets", "chip_twentyfives", "0", "wallet_id", id)
        update_one_column("wallets", "chip_hundreds", "0", "wallet_id", id)

        update_one_column("wallets", "ones", "0", "wallet_id", id)
        update_one_column("wallets", "fives", "0", "wallet_id", id)
        update_one_column("wallets", "tens", "0", "wallet_id", id)
        update_one_column("wallets", "twenties", "0", "wallet_id", id)
        update_one_column("wallets", "fifties", "0", "wallet_id", id)
        update_one_column("wallets", "hundreds", "0", "wallet_id", id)

        socketio.emit('data_changed', namespace='/')
        return jsonify(True)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for clearing bills and chips"}), 400

@app.route('/bills/value', methods=['GET', 'POST'])
def get_bill_value():
    try:
        id = 1
        ones_data = fetch_one_column("ones", "wallets", "wallet_id", id)
        fives_data = fetch_one_column("fives", "wallets", "wallet_id", id)
        tens_data = fetch_one_column("tens", "wallets", "wallet_id", id)
        twenties_data = fetch_one_column("twenties", "wallets", "wallet_id", id)
        fifties_data = fetch_one_column("fifties", "wallets", "wallet_id", id)
        hundreds_data = fetch_one_column("hundreds", "wallets", "wallet_id", id)
        cover_value_param = float(request.args.get('coverValue', default=0.0))
        billMap = {"ONE": ones_data[0], "FIVE": fives_data[0], "TEN": tens_data[0], "TWENTY": twenties_data[0], "FIFTY": fifties_data[0], "HUNDRED": hundreds_data[0]}
        bill_stack = ItemStack(billMap)
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

@app.route('/chips/value', methods=['GET', 'POST'])
def get_chip_stack_value():
    try:
        chip_freq_map = request.get_json()
        stack = ItemStack(chip_freq_map)
        return jsonify(stack.get_stack_value())
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for getting chip value"}), 400

@app.route('/chips/db/value', methods=['GET', 'POST'])
def get_chip_db_value():
    try:
        id = 1
        ones_data = fetch_one_column("chip_ones", "wallets", "wallet_id", id)
        twofifties_data = fetch_one_column("chip_twofifties", "wallets", "wallet_id", id)
        fives_data = fetch_one_column("chip_fives", "wallets", "wallet_id", id)
        twentyfives_data = fetch_one_column("chip_twentyfives", "wallets", "wallet_id", id)
        hundreds_data = fetch_one_column("chip_hundreds", "wallets", "wallet_id", id)
        chipMap = {"ONE": ones_data[0], "TWO_FIFTY": twofifties_data[0], "FIVE": fives_data[0], "TWENTY_FIVE": twentyfives_data[0], "HUNDRED": hundreds_data[0]}
        print(chipMap)
        chip_stack = ItemStack(chipMap)
        print(str(chip_stack.get_stack_value()))
        return jsonify(chip_stack.get_stack_value())
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for getting chip db value"}), 400

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

def verify_keys(save_state):
    required_keys = ['playerBankAccountBalance']
    for key in required_keys:
        if key not in save_state:
            return jsonify({'error': f'save_state missing required key: {key}'}), 400
    return None

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=5000)
