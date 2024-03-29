from flask import Blueprint, jsonify, request
from app.services.postgres_connector import fetch_all, fetch_one_column, fetch_one, update_one, update_one_column, update_one_column_with_two_conditions, fetch_all_with_two_conditions
from app.services.item_stack import ItemStack
from app.services.resource_finder import ResourceFinder

other_bp = Blueprint('other', __name__)


def can_spend_bills(bill_denomination, quantity, wallet_id):
    wallet_data = fetch_one_column(bill_denomination, "wallets", "wallet_id", wallet_id)
    return wallet_data[0] >= quantity

def spend_bills(bill_denomination, quantity, wallet_id):
    wallet_data = fetch_one_column(bill_denomination, "wallets", "wallet_id", wallet_id)
    new_wallet_value = wallet_data[0] - quantity
    update_one_column("wallets", bill_denomination, new_wallet_value, "wallet_id", wallet_id)

#App.js
@other_bp.route('/wallets', methods=['GET'])
def get_wallets():
    try:
        id = request.args.get('id')
        result = fetch_all("wallets", "wallet_id", id)
        return jsonify(result)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500
    
@other_bp.route('/bets', methods=['GET'])
def get_bets():
    try:
        id = request.args.get('id')
        game = '\'' + request.args.get('game') + '\''
        result = fetch_all_with_two_conditions("bets", "player_id", id, "game", game)
        return jsonify(result)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500
    
@other_bp.route('/houses', methods=['GET'])
def get_house():
    try:
        id = request.args.get('id')
        result = fetch_all("houses", "house_id", id)
        return jsonify(result)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500
    
@other_bp.route('/winnings', methods=['GET'])
def get_winnings():
    try:
        id = request.args.get('id')
        game = '\'' + request.args.get('game') + '\''
        result = fetch_all_with_two_conditions("winnings", "player_id", id, "game", game)
        return jsonify(result)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500
    
@other_bp.route('/winnings', methods=['PUT'])
def put_winnings():
    try:
        id = request.args.get('id')
        quantity = request.args.get('quantity')
        game = '\'' + request.args.get('game') + '\''
        update_one_column_with_two_conditions("winnings", "chip_fives", quantity, "player_id", id, "game", game)
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@other_bp.route('/slot/bets', methods=['GET'])
def get_slot_bet():
    try:
        id = request.args.get('id')
        result = fetch_one_column("chip_fives", "bets", "player_id", id)
        return jsonify(result[0])
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@other_bp.route('/bets/clear', methods=['PUT'])
def clear_bet():
    try:
        id = request.args.get('id')
        game = '\'' + request.args.get('game') + '\''
        update_one_column_with_two_conditions("bets", "chip_fives", 0, "player_id", id, "game", game)
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@other_bp.route('/slot/reels', methods=['GET'])
def get_slot_reels():
    try:
        id = request.args.get('id')
        result = fetch_all("slots", "slot_id", id)
        return jsonify(result)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500
    
@other_bp.route('/slot/reels', methods=['PUT'])
def set_slot_reels():
    try:
        id = request.args.get('id')
        first = '\'' + request.args.get('first') + '\''
        second = '\'' + request.args.get('second') + '\''
        third = '\'' + request.args.get('third') + '\''
        update_one_column("slots", "reel_1", first, "slot_id", id)
        update_one_column("slots", "reel_2", second, "slot_id", id)
        update_one_column("slots", "reel_3", third, "slot_id", id)
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@other_bp.route('/dice/rolls', methods=['GET'])
def get_dice_rolls():
    try:
        id = request.args.get('id')
        result = fetch_all("craps", "craps_id", id)
        return jsonify(result)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500
    
@other_bp.route('/dice/rolls', methods=['PUT'])
def set_dice_rolls():
    try:
        id = request.args.get('id')
        first = '\'' + request.args.get('first') + '\''
        second = '\'' + request.args.get('second') + '\''
        update_one_column("craps", "die_1", first, "craps_id", id)
        update_one_column("craps", "die_2", second, "craps_id", id)
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@other_bp.route('/house/chips', methods=['PUT'])
def set_house_chips():
    try:
        id = request.args.get('id')
        quantity = request.args.get('quantity')
        update_one_column("houses", "chip_fives", quantity, "house_id", id)
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@other_bp.route('/items', methods=["POST"])
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
   
@other_bp.route('/players', methods=["GET"])
def get_player():
    try:
        id = request.args.get('id')
        quality = request.args.get('quality')
        data = fetch_one_column(quality, "players", "player_id", id)
        return jsonify(data[0])
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500 
    
@other_bp.route('/players/locations', methods=["GET"])
def get_player_location():
    try:
        id = request.args.get('id')
        data = fetch_one_column("location", "players", "player_id", id)
        return jsonify(data[0])
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500 
    
@other_bp.route('/players/locations', methods=["PUT"])
def update_player_location():
    try:
        id = request.args.get('id')
        name = '\'' + request.args.get('name') + '\''
        update_one_column("players", "location", name, "player_id", id)
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500 

@other_bp.route('/atms', methods=["GET"])
def get_atm():
    try:
        id = request.args.get('id')
        result = fetch_all("atms", "atm_id", id)
        return jsonify(result)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500  
 
@other_bp.route('/plastics', methods=['POST'])
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

@other_bp.route('/resources', methods=['GET'])
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

@other_bp.route('/doubles', methods=['GET'])
def denomination_value_route():
    try:
        denomination_name = str(request.args.get('name'))
        resource_name = ItemStack.denomination_value(denomination_name)
        return jsonify({"value": resource_name})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid denomination name"}), 400

@other_bp.route('/stacks/value', methods=['GET', 'POST'])
def get_chip_stack_value():
    try:
        chip_freq_map = request.get_json()
        stack = ItemStack(chip_freq_map)
        return jsonify(stack.get_stack_value())
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for getting chip value"}), 400

@other_bp.route('/transactions', methods=['GET', 'POST'])
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

@other_bp.route('/stacks/multiply', methods=['GET', 'POST'])
def multiply_stack():
    try:
        factor_param = float(request.args.get('factor', default=0.0))
        stack_json = request.get_json()
        stack = ItemStack(stack_json)
        stack = stack.multiply_stack_by_factor(factor_param)
        return jsonify(stack.item_frequencies)
    except Exception as e:
        return jsonify({'error': str(e)}), 500









