from flask import Blueprint, jsonify, request
from app.services.postgres_connector import fetch_all, fetch_one_column, fetch_one, update_one, update_one_column
from app.services.item_stack import ItemStack

button_bp = Blueprint('button', __name__)

#ATMControlButton.js
@button_bp.route('/buttons/atm/control', methods=['POST'])
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
@button_bp.route('/buttons/atm/word', methods=['POST'])
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
@button_bp.route('/buttons/atm/digit', methods=['POST'])
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


