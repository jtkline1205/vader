from flask import Flask, jsonify, request
from bill_stack import BillStack
import logging

app = Flask(__name__)

# Disable logging for 200 responses
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


@app.route('/colors/chips', methods=['GET'])
def chip_color():
    resource_name_map = {
        ONE: "white",
        TWO_FIFTY: "blue",
        FIVE: "red",
        TWENTY_FIVE: "green",
        HUNDRED: "black",
    }
    try:
        double_param = float(request.args.get('double'))
        resource_name = resource_name_map[double_param]
        return jsonify({"color": resource_name})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid chip value"}), 400


@app.route('/images/bills', methods=['GET'])
def dollar_jpeg_name():
    resource_name_map = {
        ONE: "one_dollar_bill.jpg",
        FIVE: "five_dollar_bill.png",
        TEN: "ten_dollar_bill.jpg",
        TWENTY: "twenty_dollar_bill.jpg",
        FIFTY: "fifty_dollar_bill.jpg",
        HUNDRED: "hundred_dollar_bill.jpg"
    }
    try:
        bill_denomination = float(request.args.get('double'))
        resource_name = resource_name_map[bill_denomination]
        return jsonify({"dollar_jpeg_name": resource_name})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid bill value"}), 400


@app.route('/strings/chips/change', methods=['GET'])
def chip_change_string():
    resource_name_map = {
        ONE: "1 White",
        FIVE: "1 Red",
        TEN: "2 Red",
        TWENTY: "4 Red",
        FIFTY: "2 Green",
        HUNDRED: "1 Black"
    }
    try:
        double_value = float(request.args.get('double'))
        resource_name = resource_name_map[double_value]
        return jsonify({"chip_change_string": resource_name})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid chip value"}), 400


@app.route('/strings/bills/chips', methods=['GET'])
def bill_to_chip_string():
    resource_name_map = {
        "ONE": "ONE",
        "FIVE": "FIVE",
        "TEN": "FIVE",
        "TWENTY": "FIVE",
        "FIFTY": "TWENTY_FIVE",
        "HUNDRED": "HUNDRED",
    }
    try:
        bill_name = str(request.args.get('name'))
        resource_name = resource_name_map[bill_name]
        return jsonify({"chip_name": resource_name})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid bill name"}), 400


@app.route('/images/bills/change', methods=['GET'])
def cash_exchange_filename():
    resource_name_map = {
        "ONE": "one_to_white.png",
        "FIVE": "five_to_red.png",
        "TEN": "ten_to_red.png",
        "TWENTY": "twenty_to_red.png",
        "FIFTY": "fifty_to_green.png",
        "HUNDRED": "hundred_to_black.png"
    }
    try:
        denomination_name = str(request.args.get('name'))
        resource_name = resource_name_map[denomination_name]
        return jsonify({"cash_exchange_filename": resource_name})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid bill value"}), 400


@app.route('/images/chips/change', methods=['GET'])
def chip_exchange_filename():
    resource_name_map = {
        "ONE": "white_to_one.png",
        "FIVE": "red_to_five.png",
        "TEN": "red_to_ten.png",
        "TWENTY": "red_to_twenty.png",
        "FIFTY": "green_to_fifty.png",
        "HUNDRED": "black_to_hundred.png"
    }
    try:
        denomination_name = str(request.args.get('name'))
        resource_name = resource_name_map[denomination_name]
        return jsonify({"chip_exchange_filename": resource_name})
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


@app.route('/saveState/billValueAdd', methods=['PUT'])
def add_bill_value():
    try:
        double_param = float(request.args.get('double'))
        data = request.get_json()
        required_keys = ['playerBankAccountBalance', 'playerFullness', 'playerFeeling']
        for key in required_keys:
            if key not in data:
                return jsonify({'error': f'Missing required key: {key}'}), 400
        bill_stack = BillStack(data['playerBills'])
        new_stack = BillStack.generate_stack_from_total(double_param)
        bill_stack = bill_stack.add_stack(new_stack)
        data['playerBills'] = bill_stack.bill_frequencies
        return jsonify(data)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for adding bill value"}), 400


@app.route('/saveState/billValueSubtract', methods=['PUT'])
def subtract_bill_value():
    try:
        double_param = float(request.args.get('double'))
        data = request.get_json()
        required_keys = ['playerBankAccountBalance', 'playerFullness', 'playerFeeling']
        for key in required_keys:
            if key not in data:
                return jsonify({'error': f'Missing required key: {key}'}), 400
        bill_stack = BillStack(data['playerBills'])
        stack_to_remove = bill_stack.find_bill_combination(double_param)
        bill_stack = bill_stack.subtract_stack(stack_to_remove)
        data['playerBills'] = bill_stack.bill_frequencies
        return jsonify(data)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for subtracting bill value"}), 400


@app.route('/saveState/billAdd', methods=['PUT'])
def add_bills():
    try:
        denomination_param = str(request.args.get('denomination'))
        quantity = int(request.args.get('quantity'))
        data = request.get_json()
        required_keys = ['playerBankAccountBalance', 'playerFullness', 'playerFeeling']
        for key in required_keys:
            if key not in data:
                return jsonify({'error': f'Missing required key: {key}'}), 400
        bill_stack = BillStack(data['playerBills'])
        bill_stack = bill_stack.add_bills(denomination_param, quantity)
        data['playerBills'] = bill_stack.bill_frequencies
        return jsonify(data)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for adding bills"}), 400


@app.route('/saveState/billSubtract', methods=['PUT'])
def subtract_bills():
    try:
        denomination_param = str(request.args.get('denomination'))
        quantity = int(request.args.get('quantity'))
        data = request.get_json()
        required_keys = ['playerBankAccountBalance', 'playerFullness', 'playerFeeling']
        for key in required_keys:
            if key not in data:
                return jsonify({'error': f'Missing required key: {key}'}), 400
        bill_stack = BillStack(data['playerBills'])
        bill_stack = bill_stack.subtract_bills(denomination_param, quantity)
        data['playerBills'] = bill_stack.bill_frequencies
        return jsonify(data)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for subtracting bills"}), 400


@app.route('/saveState/billValue', methods=['GET', "POST"])
def get_bill_value():
    try:
        data = request.get_json()
        print(str(data))
        bill_stack = BillStack(data['playerBills'])
        print(str(bill_stack))
        stack_value = bill_stack.get_stack_value()
        print(str(stack_value))
        json = jsonify(stack_value)
        print(json)
        return json
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for getting bill value"}), 400


@app.route('/saveState/coversBillValue', methods=['GET', "POST"])
def covers_bill_value():
    try:
        bill_value_param = float(request.args.get('billValue'))
        print("covers bill value param = " + str(bill_value_param))
        data = request.get_json()
        bill_stack = BillStack(data['playerBills'])
        print("bill_stack = " + str(bill_stack))
        found_stack = bill_stack.find_bill_combination(bill_value_param)
        if found_stack:
            print("covering bill stack is " + str(found_stack.bill_frequencies))
            return jsonify(True)
        else:
            print("could not cover the bill value")
            return jsonify(False)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for getting bill value"}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)




