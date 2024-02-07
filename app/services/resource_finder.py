class ResourceFinder:

    def __init__(self):
        self.map = {
            1.0: {
                "color": "white",
                "dollar_jpeg": "one_dollar_bill.jpg",
                "chip_change": "1 White",
                "bill_to_chip": "ONE",
                "cash_exchange": "one_to_white.png",
                "chip_exchange": "white_to_one.png",
            },
            2.50: {
                "color": "blue",
                "dollar_jpeg": "",
                "chip_change": "",
                "bill_to_chip": "",
                "cash_exchange": "",
                "chip_exchange": "",
            },
            5.0: {
                "color": "red",
                "dollar_jpeg": "five_dollar_bill.png",
                "chip_change": "1 Red",
                "bill_to_chip": "FIVE",
                "cash_exchange": "five_to_red.png",
                "chip_exchange": "red_to_five.png",
            },
            10.0: {
                "dollar_jpeg": "ten_dollar_bill.jpg",
                "chip_change": "2 Red",
                "bill_to_chip": "FIVE",
                "cash_exchange": "ten_to_red.png",
                "chip_exchange": "red_to_ten.png",
            },
            20.0: {
                "dollar_jpeg": "twenty_dollar_bill.jpg",
                "chip_change": "4 Red",
                "bill_to_chip": "FIVE",
                "cash_exchange": "twenty_to_red.png",
                "chip_exchange": "red_to_twenty.png",
            },
            25.0: {
                "color": "green",
                "dollar_jpeg": "",
                "chip_change": "",
                "bill_to_chip": "",
                "cash_exchange": "",
                "chip_exchange": "",
            },
            50.0: {
                "dollar_jpeg": "fifty_dollar_bill.jpg",
                "chip_change": "2 Green",
                "bill_to_chip": "TWENTY_FIVE",
                "cash_exchange": "fifty_to_green.png",
                "chip_exchange": "green_to_fifty.png",
            },
            100.0: {
                "color": "black",
                "dollar_jpeg": "hundred_dollar_bill.jpg",
                "chip_change": "1 Black",
                "bill_to_chip": "HUNDRED",
                "cash_exchange": "hundred_to_black.png",
                "chip_exchange": "black_to_hundred.png",
            },
        }

    def get_resource(self, key1, key2):
        return self.map[key1][key2]
