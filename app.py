from flask import Flask, jsonify, request
from bill_stack import BillStack
import logging

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

ZERO = 0.0
ONE = 1.0
TWO_FIFTY = 2.50
FIVE = 5.0
TEN = 10.0
TWENTY = 20.0
TWENTY_FIVE = 25.0
FIFTY = 50.0
HUNDRED = 100.0

the_map = {
    ONE: {
        "color": "white",
        "dollar_jpeg": "one_dollar_bill.jpg",
        "chip_change": "1 White",
        "bill_to_chip": "ONE",
        "cash_exchange": "one_to_white.png",
        "chip_exchange": "white_to_one.png",
    },
    TWO_FIFTY: {
        "color": "blue",
        "dollar_jpeg": "",
        "chip_change": "",
        "bill_to_chip": "",
        "cash_exchange": "",
        "chip_exchange": "",
    },
    FIVE: {
        "color": "red",
        "dollar_jpeg": "five_dollar_bill.png",
        "chip_change": "1 Red",
        "bill_to_chip": "FIVE",
        "cash_exchange": "five_to_red.png",
        "chip_exchange": "red_to_five.png",
    },
    TEN: {
        "dollar_jpeg": "ten_dollar_bill.jpg",
        "chip_change": "2 Red",
        "bill_to_chip": "FIVE",
        "cash_exchange": "ten_to_red.png",
        "chip_exchange": "red_to_ten.png",
    },
    TWENTY: {
        "dollar_jpeg": "twenty_dollar_bill.jpg",
        "chip_change": "4 Red",
        "bill_to_chip": "FIVE",
        "cash_exchange": "twenty_to_red.png",
        "chip_exchange": "red_to_twenty.png",
    },
    TWENTY_FIVE: {
        "color": "green",
        "dollar_jpeg": "",
        "chip_change": "",
        "bill_to_chip": "",
        "cash_exchange": "",
        "chip_exchange": "",
    },
    FIFTY: {
        "dollar_jpeg": "fifty_dollar_bill.jpg",
        "chip_change": "2 Green",
        "bill_to_chip": "TWENTY_FIVE",
        "cash_exchange": "fifty_to_green.png",
        "chip_exchange": "green_to_fifty.png",
    },
    HUNDRED: {
        "color": "black",
        "dollar_jpeg": "hundred_dollar_bill.jpg",
        "chip_change": "1 Black",
        "bill_to_chip": "HUNDRED",
        "cash_exchange": "hundred_to_black.png",
        "chip_exchange": "black_to_hundred.png",
    },
}


@app.route('/colors/chips', methods=['GET'])
def chip_color():
    try:
        return jsonify({"color": the_map[float(request.args.get('double'))]["color"]})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid chip value"}), 400


@app.route('/images/bills', methods=['GET'])
def dollar_jpeg_name():
    try:
        return jsonify({"dollar_jpeg_name": the_map[float(request.args.get('double'))]['dollar_jpeg']})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid bill value"}), 400


@app.route('/strings/chips/change', methods=['GET'])
def chip_change_string():
    try:
        return jsonify({"chip_change_string": the_map[float(request.args.get('double'))]['chip_change']})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid chip value"}), 400


@app.route('/strings/bills/chips', methods=['GET'])
def bill_to_chip_string():
    try:
        return jsonify({"chip_name": the_map[float(request.args.get('billValue'))]['bill_to_chip']})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid bill name"}), 400


@app.route('/images/bills/change', methods=['GET'])
def cash_exchange_filename():
    try:
        return jsonify({"cash_exchange_filename": the_map[float(request.args.get('billValue'))]['cash_exchange']})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid bill value"}), 400


@app.route('/images/chips/change', methods=['GET'])
def chip_exchange_filename():
    try:
        return jsonify({"chip_exchange_filename": the_map[float(request.args.get('chipValue'))]['chip_exchange']})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid chip value"}), 400


@app.route('/doubles', methods=['GET'])
def denomination_value_route():
    try:
        denomination_name = str(request.args.get('name'))
        resource_name = BillStack.denomination_value(denomination_name)
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
        double_param = float(request.args.get('double', default=0.0))
        denomination_param = str(request.args.get('denomination', default=""))
        quantity = int(request.args.get('quantity', default=0))
        save_state = request.get_json()
        verify_result = verify_keys(save_state)
        if verify_result is not None:
            return verify_result
        bill_stack = BillStack(save_state['playerBills'])
        if double_param > 0:
            new_stack = BillStack.generate_stack_from_total(double_param)
            bill_stack = bill_stack.add_stack(new_stack)
        elif double_param < 0:
            stack_to_remove = bill_stack.find_bill_combination(double_param)
            bill_stack = bill_stack.subtract_stack(stack_to_remove)
        else:
            bill_stack = bill_stack.modify_bills(denomination_param, quantity)
        save_state['playerBills'] = bill_stack.bill_frequencies
        return jsonify(save_state)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for adding bills"}), 400


@app.route('/saveState/bills/value', methods=['GET', 'POST'])
def get_bill_value():
    try:
        cover_value_param = float(request.args.get('coverValue', default=0.0))
        save_state = request.get_json()
        bill_stack = BillStack(save_state['playerBills'])
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)




