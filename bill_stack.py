from app import denomination_value


class BillStack:

    denomination_list_ascending = ["ONE", "FIVE", "TEN", "TWENTY", "FIFTY", "HUNDRED"]
    denomination_list_descending = ["HUNDRED", "FIFTY", "TWENTY", "TEN", "FIVE", "ONE"]

    def __init__(self, bill_freqs=None):
        self.bill_freqs = bill_freqs or {}

    def add_bills(self, denomination, quantity):
        new_quantity = self.bill_freqs.get(denomination, 0) + quantity
        self.bill_freqs[denomination] = new_quantity
        return BillStack(self.bill_freqs.copy())

    def subtract_bills(self, denomination, quantity):
        current_quantity = self.bill_freqs.get(denomination, 0)
        new_quantity = max(current_quantity - quantity, 0)
        self.bill_freqs[denomination] = new_quantity
        return BillStack(self.bill_freqs.copy())

    def count_type_of_bill(self, denomination):
        return self.bill_freqs.get(denomination, 0)

    def add_stack(self, stack_to_add):
        new_map = self.bill_freqs.copy()
        for denomination in stack_to_add.bill_freqs.keys():
            new_map[denomination] = new_map.get(denomination, 0) + stack_to_add.bill_freqs[denomination]
        return BillStack(new_map)

    def subtract_stack(self, stack_to_subtract):
        new_map = self.bill_freqs.copy()
        for denomination in stack_to_subtract.bill_freqs.keys():
            new_quantity = new_map.get(denomination, 0) - stack_to_subtract.bill_freqs[denomination]
            new_map[denomination] = max(0, new_quantity)
        return BillStack(new_map)

    def contains_stack(self, stack):
        for denomination in stack.bill_freqs.keys():
            if denomination not in self.bill_freqs or self.bill_freqs[denomination] < stack.bill_freqs[denomination]:
                return False
        return True

    def get_stack_value(self):
        return sum(self.bill_freqs[denom] * denomination_value(denom) for denom in self.bill_freqs.keys())

    def is_empty(self):
        return self.get_stack_value() == 0.0

    def find_bill_combination(self, total):
        bill_list = [denom for denom in self.denomination_list_descending for _ in range(self.bill_freqs.get(denom, 0))]

        combination = self._find_bill_combination(total, bill_list)

        if combination is None:
            return BillStack()
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
            new_target = target - denomination_value(bill)
            with_bill = self._find_bill_combination(new_target, bills[1:])
            if with_bill or len(with_bill) == 0:
                with_bill.append(bill)
                return with_bill
            without_bill = self._find_bill_combination(target, bills[1:])
            return without_bill


    @classmethod
    def create_empty_stack(cls):
        stack = cls()
        for denom in cls.denomination_list_ascending:
            stack = stack.add_bills(denom, 0)
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

        for denom in cls.denomination_list_descending:
            value = denomination_value(denom)
            number_of_bills = int(remainder / value)
            remainder = remainder % value
            bill_stack = bill_stack.add_bills(denom, number_of_bills)

        return bill_stack
