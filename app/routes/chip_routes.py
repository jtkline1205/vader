from flask import Blueprint, render_template, jsonify, request
from app.services.postgres_connector import fetch_all, fetch_one_column, fetch_one, update_one, update_one_column, update_one_column_with_two_conditions
from app.services.item_stack import ItemStack

chip_bp = Blueprint('chip', __name__)

@chip_bp.route('/chips', methods=['GET'])
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
    
@chip_bp.route('/chips/exchange', methods=["POST"])
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
                return jsonify(True)
            else:
                return jsonify({'error': 'Player not found'}), 404
        else:
            return jsonify(False)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500
    
@chip_bp.route('/chips/bet', methods=["POST"])
def bet_chips():
    try:
        payload = request.json
        id = payload["id"]
        denomination = payload["denomination"]
        game = '\'' + payload["game"] + '\''
        if (denomination == 5):
            update_one_column_with_two_conditions("bets", "chip_fives", 1, "player_id", 1, "game", game)
        ones_data = fetch_one_column("chip_ones", "wallets", "wallet_id", id)
        twofifties_data = fetch_one_column("chip_twofifties", "wallets", "wallet_id", id)
        fives_data = fetch_one_column("chip_fives", "wallets", "wallet_id", id)
        twentyfives_data = fetch_one_column("chip_twentyfives", "wallets", "wallet_id", id)
        hundreds_data = fetch_one_column("chip_hundreds", "wallets", "wallet_id", id)
        chipMap = {"ONE": ones_data[0], "FIVE": fives_data[0], "TWO_FIFTY": twofifties_data[0], "TWENTY_FIVE": twentyfives_data[0], "HUNDRED": hundreds_data[0]}
        chip_stack = ItemStack(chipMap)
        if (denomination == 5):
            chip_stack = chip_stack.modify_items("FIVE", -1)
        update_one_column("wallets", "chip_ones", chip_stack.count_type_of_item("ONE"), "wallet_id", id)
        update_one_column("wallets", "chip_twofifties", chip_stack.count_type_of_item("TWO_FIFTY"), "wallet_id", id)
        update_one_column("wallets", "chip_fives", chip_stack.count_type_of_item("FIVE"), "wallet_id", id)
        update_one_column("wallets", "chip_twentyfives", chip_stack.count_type_of_item("TWENTY_FIVE"), "wallet_id", id)
        update_one_column("wallets", "chip_hundreds", chip_stack.count_type_of_item("HUNDRED"), "wallet_id", id)
        return jsonify(True)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@chip_bp.route('/chips', methods=['PUT'])
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
        return jsonify(True)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for modifying chips"}), 400
    
@chip_bp.route('/chips/clear', methods=['PUT'])
def clear_chips():
    try:
        id = 1

        update_one_column("wallets", "chip_ones", "0", "wallet_id", id)
        update_one_column("wallets", "chip_twofifties", "0", "wallet_id", id)
        update_one_column("wallets", "chip_fives", "0", "wallet_id", id)
        update_one_column("wallets", "chip_twentyfives", "0", "wallet_id", id)
        update_one_column("wallets", "chip_hundreds", "0", "wallet_id", id)

        return jsonify(True)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for clearing chips"}), 400

@chip_bp.route('/chips/db/value', methods=['GET', 'POST'])
def get_chip_db_value():
    try:
        id = 1
        ones_data = fetch_one_column("chip_ones", "wallets", "wallet_id", id)
        twofifties_data = fetch_one_column("chip_twofifties", "wallets", "wallet_id", id)
        fives_data = fetch_one_column("chip_fives", "wallets", "wallet_id", id)
        twentyfives_data = fetch_one_column("chip_twentyfives", "wallets", "wallet_id", id)
        hundreds_data = fetch_one_column("chip_hundreds", "wallets", "wallet_id", id)
        chipMap = {"ONE": ones_data[0], "TWO_FIFTY": twofifties_data[0], "FIVE": fives_data[0], "TWENTY_FIVE": twentyfives_data[0], "HUNDRED": hundreds_data[0]}
        chip_stack = ItemStack(chipMap)
        return jsonify(chip_stack.get_stack_value())
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for getting chip db value"}), 400







