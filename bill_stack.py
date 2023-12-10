class BillStack:

    denomination_list_ascending = ["ONE", "FIVE", "TEN", "TWENTY", "FIFTY", "HUNDRED"]
    denomination_list_descending = ["HUNDRED", "FIFTY", "TWENTY", "TEN", "FIVE", "ONE"]

    def __init__(self, bill_frequencies=None):
        self.bill_frequencies = bill_frequencies or {}

    def add_bills(self, denomination, quantity):
        new_quantity = self.bill_frequencies.get(denomination, 0) + quantity
        self.bill_frequencies[denomination] = new_quantity
        return BillStack(self.bill_frequencies.copy())

    def subtract_bills(self, denomination, quantity):
        current_quantity = self.bill_frequencies.get(denomination, 0)
        new_quantity = max(current_quantity - quantity, 0)
        self.bill_frequencies[denomination] = new_quantity
        return BillStack(self.bill_frequencies.copy())

    def count_type_of_bill(self, denomination):
        return self.bill_frequencies.get(denomination, 0)

    def add_stack(self, stack_to_add):
        new_map = self.bill_frequencies.copy()
        for denomination in stack_to_add.bill_frequencies.keys():
            new_map[denomination] = new_map.get(denomination, 0) + stack_to_add.bill_frequencies[denomination]
        return BillStack(new_map)

    def subtract_stack(self, stack_to_subtract):
        new_map = self.bill_frequencies.copy()
        for denomination in stack_to_subtract.bill_frequencies.keys():
            new_quantity = new_map.get(denomination, 0) - stack_to_subtract.bill_frequencies[denomination]
            new_map[denomination] = max(0, new_quantity)
        return BillStack(new_map)

    def contains_stack(self, stack):
        for denomination in stack.bill_frequencies.keys():
            if denomination not in self.bill_frequencies or self.bill_frequencies[denomination] < stack.bill_frequencies[denomination]:
                return False
        return True

    def get_stack_value(self):
        return sum(self.bill_frequencies[denomination] * BillStack.denomination_value(denomination) for denomination in self.bill_frequencies.keys())

    def is_empty(self):
        return self.get_stack_value() == 0.0

    def find_bill_combination(self, total):
        bill_list = [denomination for denomination in self.denomination_list_descending for _ in range(self.bill_frequencies.get(denomination, 0))]

        combination = self._find_bill_combination(total, bill_list)

        if combination is None:
            return None
        else:
            stack = BillStack()
            for bill in combination:
                stack = stack.add_bills(bill, 1)
            return stack

    def _find_bill_combination(self, target, bills):
        if target == 0:
            return []
        elif target < 0 or not bills:
            return None
        else:
            bill = bills[0]
            new_target = target - BillStack.denomination_value(bill)
            with_bill = self._find_bill_combination(new_target, bills[1:])
            if with_bill is not None:
                with_bill.append(bill)
                return with_bill
            else:
                without_bill = self._find_bill_combination(target, bills[1:])
                return without_bill

    @classmethod
    def create_empty_stack(cls):
        stack = cls()
        for denomination in cls.denomination_list_ascending:
            stack = stack.add_bills(denomination, 0)
        return stack

    @classmethod
    def create_stack_from_existing(cls, stack_to_copy):
        return cls.create_empty_stack().add_stack(stack_to_copy)

    @classmethod
    def create_stack_with_quantity(cls, denomination, quantity):
        return cls.create_empty_stack().add_bills(denomination, quantity)

    @classmethod
    def generate_stack_from_total(cls, total):
        bill_stack = cls.create_empty_stack()
        remainder = total

        for denomination in cls.denomination_list_descending:
            value = BillStack.denomination_value(denomination)
            number_of_bills = int(remainder / value)
            remainder = remainder % value
            bill_stack = bill_stack.add_bills(denomination, number_of_bills)

        return bill_stack

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
