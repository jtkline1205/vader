from flask import Flask, jsonify, request
from item_stack import ItemStack
from resource_finder import ResourceFinder
import logging

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


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
    required_keys = ['playerBankAccountBalance', 'playerFullness', 'playerFeeling']
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
    app.run(debug=True, host='0.0.0.0', port=5000)




