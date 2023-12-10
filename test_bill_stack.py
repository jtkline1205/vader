import unittest
from bill_stack import BillStack


class TestBillStack(unittest.TestCase):
    def test_add_bills(self):
        bill_stack = BillStack()

        bill_stack.add_bills("ONE", 5)
        self.assertEqual(bill_stack.bill_frequencies["ONE"], 5)

        bill_stack.add_bills("FIVE", 3)
        self.assertEqual(bill_stack.bill_frequencies["FIVE"], 3)

        bill_stack.add_bills("ONE", 2)
        self.assertEqual(bill_stack.bill_frequencies["ONE"], 7)

    def test_find_bill_combination(self):
        bill_stack = BillStack().add_bills("HUNDRED", 1)
        combination = bill_stack.find_bill_combination(100)
        self.assertEqual(combination.count_type_of_bill("HUNDRED"), 1)
        bill_stack = bill_stack.add_bills("FIFTY", 1)
        self.assertEqual(bill_stack.find_bill_combination(150).count_type_of_bill("FIFTY"), 1)
        bill_stack = BillStack().add_bills("ONE", 20)
        self.assertEqual(bill_stack.find_bill_combination(20).count_type_of_bill("ONE"), 20)

    def test_create_stack(self):
        self.assertEqual(BillStack.create_stack_with_quantity("HUNDRED", 1).count_type_of_bill("HUNDRED"), 1)


if __name__ == '__main__':
    unittest.main()