from flask import Blueprint, render_template, jsonify, request
from postgres_connector import fetch_all, fetch_one_column, fetch_one, update_one, update_one_column
from item_stack import ItemStack

bill_bp = Blueprint('bill', __name__)

#BreakBillButton.js
@bill_bp.route('/bills/break', methods=["POST"])
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
                return jsonify(True)
            else:
                return jsonify({'error': 'Player not found'}), 404
        else:
            return jsonify(False)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

#ExchangeCashButton.js
@bill_bp.route('/bills/exchange', methods=["POST"])
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
                return jsonify(True)
            else:
                return jsonify({'error': 'Player not found'}), 404
        else:
            return jsonify(False)
    except Exception as e:
        print('Error executing query:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

#AccountingServiceConnector.scala
@bill_bp.route('/bills/clear', methods=['PUT'])
def clear_bills():
    try:
        id = 1

        update_one_column("wallets", "ones", "0", "wallet_id", id)
        update_one_column("wallets", "fives", "0", "wallet_id", id)
        update_one_column("wallets", "tens", "0", "wallet_id", id)
        update_one_column("wallets", "twenties", "0", "wallet_id", id)
        update_one_column("wallets", "fifties", "0", "wallet_id", id)
        update_one_column("wallets", "hundreds", "0", "wallet_id", id)

        return jsonify(True)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid request for clearing bills"}), 400

#AccountingServiceConnector.scala
@bill_bp.route('/bills/value', methods=['GET', 'POST'])
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












