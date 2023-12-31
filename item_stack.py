class ItemStack:

    bill_denomination_list_ascending = ["ONE", "FIVE", "TEN", "TWENTY", "FIFTY", "HUNDRED"]
    bill_denomination_list_descending = ["HUNDRED", "FIFTY", "TWENTY", "TEN", "FIVE", "ONE"]
    chip_denomination_list_ascending = ["ONE", "TWO_FIFTY", "FIVE", "TWENTY_FIVE", "HUNDRED"]
    chip_denomination_list_descending = ["HUNDRED", "TWENTY_FIVE", "FIVE", "TWO_FIFTY", "ONE"]

    def __init__(self, item_frequencies=None):
        self.item_frequencies = item_frequencies or {}

    def modify_items(self, denomination, quantity):
        new_items = self.item_frequencies.copy()
        if quantity > 0:
            new_quantity = new_items.get(denomination, 0) + quantity
            new_items[denomination] = new_quantity
        else:
            current_quantity = new_items.get(denomination, 0)
            new_quantity = max(current_quantity + quantity, 0)
            new_items[denomination] = new_quantity
        return ItemStack(new_items)

    def count_type_of_item(self, denomination):
        return self.item_frequencies.get(denomination, 0)

    def add_stack(self, stack_to_add):
        new_map = self.item_frequencies.copy()
        for denomination in stack_to_add.item_frequencies.keys():
            new_map[denomination] = new_map.get(denomination, 0) + stack_to_add.item_frequencies[denomination]
        return ItemStack(new_map)

    def subtract_stack(self, stack_to_subtract):
        new_map = self.item_frequencies.copy()
        if stack_to_subtract is not None:
            for denomination in stack_to_subtract.item_frequencies.keys():
                new_quantity = new_map.get(denomination, 0) - stack_to_subtract.item_frequencies[denomination]
                new_map[denomination] = max(0, new_quantity)
        return ItemStack(new_map)

    def multiply_stack_by_factor(self, factor):
        new_map = self.item_frequencies.copy()
        if factor == 1.5:
            for denomination, operand_chips in self.item_frequencies.items():
                if operand_chips > 0:
                    half_list = {
                        "HUNDRED": [("TWENTY_FIVE", 2)],
                        "TWENTY_FIVE": [("FIVE", 2), ("TWO_FIFTY", 1)],
                        "FIVE": [("TWO_FIFTY", 1)],
                        "TWO_FIFTY": [("ONE", 1)],
                        "ONE": [],
                    }.get(denomination, [])

                    for denom, quantity in half_list:
                        original_quantity = new_map.get(denom, 0)
                        new_map[denom] = original_quantity + (quantity * operand_chips)
        else:
            for denomination in new_map.keys():
                new_map[denomination] = int(new_map.get(denomination, 0) * factor)

        return ItemStack(new_map)

    def contains_stack(self, stack):
        for denomination in stack.item_frequencies.keys():
            if denomination not in self.item_frequencies or self.item_frequencies[denomination] < stack.item_frequencies[denomination]:
                return False
        return True

    def get_stack_value(self):
        return sum(self.item_frequencies[denomination] * ItemStack.denomination_value(denomination) for denomination in self.item_frequencies.keys())

    def is_empty(self):
        return self.get_stack_value() == 0.0

    def find_bill_combination(self, total):
        item_list = [denomination for denomination in self.bill_denomination_list_descending for _ in range(self.item_frequencies.get(denomination, 0))]

        combination = self._find_item_combination(total, item_list)

        if combination is None:
            return None
        else:
            stack = ItemStack()
            for item in combination:
                stack = stack.modify_items(item, 1)
            return stack

    def find_chip_combination(self, double_param):
        pass

    def _find_item_combination(self, target, items):
        if target == 0:
            return []
        elif target < 0 or not items:
            return None
        else:
            item = items[0]
            new_target = target - ItemStack.denomination_value(item)
            with_item = self._find_item_combination(new_target, items[1:])
            if with_item is not None:
                with_item.append(item)
                return with_item
            else:
                without_item = self._find_item_combination(target, items[1:])
                return without_item

    @classmethod
    def create_empty_bill_stack(cls):
        stack = cls()
        for denomination in cls.bill_denomination_list_ascending:
            stack = stack.modify_items(denomination, 0)
        return stack

    @classmethod
    def create_bill_stack_from_existing(cls, stack_to_copy):
        return cls.create_empty_bill_stack().add_stack(stack_to_copy)

    @classmethod
    def create_bill_stack_with_quantity(cls, denomination, quantity):
        return cls.create_empty_bill_stack().modify_items(denomination, quantity)

    @classmethod
    def generate_bill_stack_from_total(cls, total):
        bill_stack = cls.create_empty_bill_stack()
        remainder = total

        for denomination in cls.bill_denomination_list_descending:
            value = ItemStack.denomination_value(denomination)
            number_of_bills = int(remainder / value)
            remainder = remainder % value
            bill_stack = bill_stack.modify_items(denomination, number_of_bills)

        return bill_stack

    @classmethod
    def generate_chip_stack_from_total(cls, total):
        chip_stack = cls.create_empty_chip_stack()
        remainder = total

        for denomination in cls.chip_denomination_list_descending:
            value = ItemStack.denomination_value(denomination)
            number_of_chips = int(remainder / value)
            remainder = remainder % value
            chip_stack = chip_stack.modify_items(denomination, number_of_chips)

        return chip_stack

    @classmethod
    def denomination_value(cls, denomination):
        resource_name_map = {
            "ZERO": 0.0,
            "ONE": 1.0,
            "TWO_FIFTY": 2.50,
            "FIVE": 5.0,
            "TEN": 10.0,
            "TWENTY": 20.0,
            "TWENTY_FIVE": 25.0,
            "FIFTY": 50.0,
            "HUNDRED": 100.0
        }
        return resource_name_map[denomination]

    @classmethod
    def create_empty_chip_stack(cls):
        stack = cls()
        for denomination in cls.chip_denomination_list_ascending:
            stack = stack.modify_items(denomination, 0)
        return stack




