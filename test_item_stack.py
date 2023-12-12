import unittest
from item_stack import ItemStack


class TestItemStack(unittest.TestCase):
    def test_add_items(self):
        item_stack = ItemStack().modify_items("ONE", 5)
        self.assertEqual(item_stack.item_frequencies["ONE"], 5)
        item_stack = item_stack.modify_items("FIVE", 3)
        self.assertEqual(item_stack.item_frequencies["FIVE"], 3)
        item_stack = item_stack.modify_items("ONE", 2)
        self.assertEqual(item_stack.item_frequencies["ONE"], 7)

    def test_subtract_items(self):
        item_stack = ItemStack().modify_items("ONE", 5)
        item_stack = item_stack.modify_items("FIFTY", 10)
        item_stack = item_stack.modify_items("FIFTY", -2)
        item_stack = item_stack.modify_items("TWENTY", -3)
        item_stack = item_stack.modify_items("ONE", -5)
        self.assertEqual(item_stack.item_frequencies["FIFTY"], 8)
        self.assertEqual(item_stack.item_frequencies["ONE"], 0)

    def test_find_bill_combination(self):
        item_stack = ItemStack().modify_items("HUNDRED", 1)
        combination = item_stack.find_bill_combination(100)
        self.assertEqual(combination.count_type_of_item("HUNDRED"), 1)
        item_stack = item_stack.modify_items("FIFTY", 1)
        self.assertEqual(item_stack.find_bill_combination(150).count_type_of_item("FIFTY"), 1)
        item_stack = ItemStack().modify_items("ONE", 20)
        self.assertEqual(item_stack.find_bill_combination(20).count_type_of_item("ONE"), 20)

    def test_create_and_add_stacks(self):
        self.assertEqual(ItemStack.create_bill_stack_with_quantity("HUNDRED", 1).count_type_of_item("HUNDRED"), 1)
        stack_of_hundreds = ItemStack().modify_items("HUNDRED", 5)
        stack_of_twenties = ItemStack().modify_items("TWENTY", 10)
        stack_of_tens = ItemStack().modify_items("TEN", 8)
        bill_stack = ItemStack().add_stack(stack_of_twenties).add_stack(stack_of_tens)
        self.assertTrue(bill_stack.contains_stack(stack_of_twenties))
        self.assertFalse(bill_stack.contains_stack(stack_of_hundreds))
        self.assertEqual(bill_stack.count_type_of_item("TEN"), 8)


if __name__ == '__main__':
    unittest.main()