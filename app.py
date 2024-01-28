from flask import Flask, jsonify, request
from flask_cors import CORS
from socketio_instance import socketio
from item_stack import ItemStack
from resource_finder import ResourceFinder
from routes.chip_routes import chip_bp
from routes.bill_routes import bill_bp
from postgres_connector import fetch_all, fetch_one_column, fetch_one, update_one, update_one_column

import logging

app = Flask(__name__)
app.register_blueprint(chip_bp)
app.register_blueprint(bill_bp)
socketio.init_app(app)
CORS(app, origins="http://localhost:3000")  # Allow connections from http://localhost:3000
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)    

def can_spend_bills(bill_denomination, quantity, wallet_id):
    wallet_data = fetch_one_column(bill_denomination, "wallets", "wallet_id", wallet_id)
    return wallet_data[0] >= quantity

def spend_bills(bill_denomination, quantity, wallet_id):
    wallet_data = fetch_one_column(bill_denomination, "wallets", "wallet_id", wallet_id)
    new_wallet_value = wallet_data[0] - quantity
    update_one_column("wallets", bill_denomination, new_wallet_value, "wallet_id", wallet_id)

#App.js
@app.route('/wallets', methods=['GET'])
def get_wallets():
    try:
        id = request.args.get('id')
        result = fetch_all("wallets", "wallet_id", id)
        return jsonify(result)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

#PurchaseItemButton.js
@app.route('/items', methods=["POST"])
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

        if (can_spend_bills(billDenominationRequired, billQuantityRequired, id)):
            player_data = fetch_one_column(attribute, "players", "player_id", id)
            if player_data is not None:
                newValue = player_data[0] + itemStrength
                update_one_column("players", attribute, newValue, "player_id", id)
                spend_bills(billDenominationRequired, billQuantityRequired, id)
                return jsonify(True)
            else:
                return jsonify({'error': 'Player not found'}), 404
        else:
            return jsonify(False)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500
   
#App.js
@app.route('/players', methods=["GET"])
def get_player():
    try:
        id = request.args.get('id')
        quality = request.args.get('quality')
        data = fetch_one_column(quality, "players", "player_id", id)
        return jsonify(data[0])
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500 

#App.js
@app.route('/atms', methods=["GET"])
def get_atm():
    try:
        id = request.args.get('id')
        result = fetch_all("atms", "atm_id", id)
        return jsonify(result)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500  
 
#InsertDebitCardButton.js
@app.route('/plastics', methods=['POST'])
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
            update_one_column("wallets", "debit_card", True, "wallet_id", "1")
            update_one_column("atms", "display_state", "'insert'", "atm_id", "1")
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500  

#ATMControlButton.js
@app.route('/buttons/atm/control', methods=['POST'])
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
                entry_data = fetch_one_column("entry", "atms", "atm_id", id)
                entry = entry_data[0]
                if int(entry) > 0:
                    update_one_column("atms", "display_state", "'confirm'", "atm_id", id)
            elif display_state == "confirm":
                update_one_column("atms", "display_state", "'home'", "atm_id", id)
            elif display_state == "deposit":
                entry_data = fetch_one_column("entry", "atms", "atm_id", id)
                entry = entry_data[0]
                ones_data = fetch_one_column("ones", "wallets", "wallet_id", id)
                fives_data = fetch_one_column("fives", "wallets", "wallet_id", id)
                tens_data = fetch_one_column("tens", "wallets", "wallet_id", id)
                twenties_data = fetch_one_column("twenties", "wallets", "wallet_id", id)
                fifties_data = fetch_one_column("fifties", "wallets", "wallet_id", id)
                hundreds_data = fetch_one_column("hundreds", "wallets", "wallet_id", id)
                billMap = {"ONE": ones_data[0], "FIVE": fives_data[0], "TEN": tens_data[0], "TWENTY": twenties_data[0], "FIFTY": fifties_data[0], "HUNDRED": hundreds_data[0]}
                bill_stack = ItemStack(billMap)
                stack_to_remove = bill_stack.find_bill_combination(int(entry))
                if stack_to_remove is not None:
                    bill_stack = bill_stack.subtract_stack(stack_to_remove)
                    account_balance_data = fetch_one_column("account_balance", "players", "player_id", id)
                    newAccountBalance = account_balance_data[0] + int(entry)
                    update_one_column("wallets", "ones", bill_stack.count_type_of_item("ONE"), "wallet_id", id)
                    update_one_column("wallets", "fives", bill_stack.count_type_of_item("FIVE"), "wallet_id", id)
                    update_one_column("wallets", "tens", bill_stack.count_type_of_item("TEN"), "wallet_id", id)
                    update_one_column("wallets", "twenties", bill_stack.count_type_of_item("TWENTY"), "wallet_id", id)
                    update_one_column("wallets", "fifties", bill_stack.count_type_of_item("FIFTY"), "wallet_id", id)
                    update_one_column("wallets", "hundreds", bill_stack.count_type_of_item("HUNDRED"), "wallet_id", id)
                    update_one_column("players", "account_balance", newAccountBalance, "player_id", id)
                    update_one_column("atms", "display_state", "'home'", "atm_id", id)
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500 
    
#ATMWordButton.js
@app.route('/buttons/atm/word', methods=['POST'])
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
                entry_data = fetch_one_column("entry", "atms", "atm_id", id)
                entry = entry_data[0]
                if int(entry) > 0:
                    update_one_column("atms", "display_state", "'confirm'", "atm_id", id)
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
            elif display_state == "balance" or display_state == "activity":
                update_one_column("atms", "display_state", "'home'", "atm_id", id)
            elif display_state == "deposit":
                entry_data = fetch_one_column("entry", "atms", "atm_id", id)
                entry = entry_data[0]
                ones_data = fetch_one_column("ones", "wallets", "wallet_id", id)
                fives_data = fetch_one_column("fives", "wallets", "wallet_id", id)
                tens_data = fetch_one_column("tens", "wallets", "wallet_id", id)
                twenties_data = fetch_one_column("twenties", "wallets", "wallet_id", id)
                fifties_data = fetch_one_column("fifties", "wallets", "wallet_id", id)
                hundreds_data = fetch_one_column("hundreds", "wallets", "wallet_id", id)
                billMap = {"ONE": ones_data[0], "FIVE": fives_data[0], "TEN": tens_data[0], "TWENTY": twenties_data[0], "FIFTY": fifties_data[0], "HUNDRED": hundreds_data[0]}
                bill_stack = ItemStack(billMap)
                stack_to_remove = bill_stack.find_bill_combination(int(entry))
                if stack_to_remove is not None:
                    bill_stack = bill_stack.subtract_stack(stack_to_remove)
                    account_balance_data = fetch_one_column("account_balance", "players", "player_id", id)
                    newAccountBalance = account_balance_data[0] + int(entry)
                    update_one_column("wallets", "ones", bill_stack.count_type_of_item("ONE"), "wallet_id", id)
                    update_one_column("wallets", "fives", bill_stack.count_type_of_item("FIVE"), "wallet_id", id)
                    update_one_column("wallets", "tens", bill_stack.count_type_of_item("TEN"), "wallet_id", id)
                    update_one_column("wallets", "twenties", bill_stack.count_type_of_item("TWENTY"), "wallet_id", id)
                    update_one_column("wallets", "fifties", bill_stack.count_type_of_item("FIFTY"), "wallet_id", id)
                    update_one_column("wallets", "hundreds", bill_stack.count_type_of_item("HUNDRED"), "wallet_id", id)
                    update_one_column("players", "account_balance", newAccountBalance, "player_id", id)
                    update_one_column("atms", "display_state", "'home'", "atm_id", id)
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500 

#ATMDigitButton.js
@app.route('/buttons/atm/digit', methods=['POST'])
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
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

#AccountingServiceConnector.scala
@app.route('/resources', methods=['GET'])
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

#AccountingServiceConnector.scala
@app.route('/doubles', methods=['GET'])
def denomination_value_route():
    try:
        denomination_name = str(request.args.get('name'))
        resource_name = ItemStack.denomination_value(denomination_name)
        return jsonify({"value": resource_name})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid denomination name"}), 400

#AccountingServiceConnector.scala
@app.route('/stacks/value', methods=['GET', 'POST'])
def get_chip_stack_value():
    try:
        chip_freq_map = request.get_json()
        stack = ItemStack(chip_freq_map)
        return jsonify(stack.get_stack_value())
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for getting chip value"}), 400

#unused?
@app.route('/transactions', methods=['GET', 'POST'])
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

#AccountingServiceConnector.scala
@app.route('/stacks/multiply', methods=['GET', 'POST'])
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
