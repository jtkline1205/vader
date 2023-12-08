from flask import Flask, jsonify, request

app = Flask(__name__)
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
def denomination_value():
    resource_name_map = {
        "ZERO": ZERO,
        "ONE": ONE,
        "TWO_FIFTY": TWO_FIFTY,
        "FIVE": FIVE,
        "TEN": TEN,
        "TWENTY": TWENTY,
        "TWENTY_FIVE": TWENTY_FIVE,
        "FIFTY": FIFTY,
        "HUNDRED": HUNDRED
    }
    try:
        denomination_name = str(request.args.get('name'))
        resource_name = resource_name_map[denomination_name]
        return jsonify({"value": resource_name})
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid denomination name"}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)




