import unittest
from bill_stack import BillStack


class TestBillStack(unittest.TestCase):
    def test_add_bills(self):
        bill_stack = BillStack().modify_bills("ONE", 5)
        self.assertEqual(bill_stack.bill_frequencies["ONE"], 5)
        bill_stack = bill_stack.modify_bills("FIVE", 3)
        self.assertEqual(bill_stack.bill_frequencies["FIVE"], 3)
        bill_stack = bill_stack.modify_bills("ONE", 2)
        self.assertEqual(bill_stack.bill_frequencies["ONE"], 7)

    def test_subtract_bills(self):
        bill_stack = BillStack().modify_bills("ONE", 5)
        bill_stack = bill_stack.modify_bills("FIFTY", 10)
        bill_stack = bill_stack.modify_bills("FIFTY", -2)
        bill_stack = bill_stack.modify_bills("TWENTY", -3)
        bill_stack = bill_stack.modify_bills("ONE", -5)
        self.assertEqual(bill_stack.bill_frequencies["FIFTY"], 8)
        self.assertEqual(bill_stack.bill_frequencies["ONE"], 0)

    def test_find_bill_combination(self):
        bill_stack = BillStack().modify_bills("HUNDRED", 1)
        combination = bill_stack.find_bill_combination(100)
        self.assertEqual(combination.count_type_of_bill("HUNDRED"), 1)
        bill_stack = bill_stack.modify_bills("FIFTY", 1)
        self.assertEqual(bill_stack.find_bill_combination(150).count_type_of_bill("FIFTY"), 1)
        bill_stack = BillStack().modify_bills("ONE", 20)
        self.assertEqual(bill_stack.find_bill_combination(20).count_type_of_bill("ONE"), 20)

    def test_create_and_add_stacks(self):
        self.assertEqual(BillStack.create_stack_with_quantity("HUNDRED", 1).count_type_of_bill("HUNDRED"), 1)
        stack_of_hundreds = BillStack().modify_bills("HUNDRED", 5)
        stack_of_twenties = BillStack().modify_bills("TWENTY", 10)
        stack_of_tens = BillStack().modify_bills("TEN", 8)
        bill_stack = BillStack().add_stack(stack_of_twenties).add_stack(stack_of_tens)
        self.assertTrue(bill_stack.contains_stack(stack_of_twenties))
        self.assertFalse(bill_stack.contains_stack(stack_of_hundreds))
        self.assertEqual(bill_stack.count_type_of_bill("TEN"), 8)


if __name__ == '__main__':
    unittest.main()