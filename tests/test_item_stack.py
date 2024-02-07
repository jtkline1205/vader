import unittest
from app.services.item_stack import ItemStack


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

    def test_multiply_stack(self):
        item_stack = ItemStack().modify_items("ONE", 5)
        item_stack = item_stack.multiply_stack_by_factor(10)
        self.assertEqual(item_stack.item_frequencies["ONE"], 50)
        item_stack = ItemStack().modify_items("ONE", 5)
        item_stack = item_stack.multiply_stack_by_factor(-1)
        self.assertEqual(item_stack.item_frequencies["ONE"], -5)

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

    def test_stacks(self):
        stack = ItemStack().modify_items("HUNDRED", 1)
        subtracted_stack = ItemStack().modify_items("HUNDRED", 1).multiply_stack_by_factor(-1)
        self.assertEqual(stack.add_stack(subtracted_stack).count_type_of_item("HUNDRED"), 0)
        stack = ItemStack().modify_items("TWENTY_FIVE", 10)
        subtracted_stack = ItemStack().modify_items("TWENTY_FIVE", 4).multiply_stack_by_factor(-1)
        self.assertEqual(stack.add_stack(subtracted_stack).count_type_of_item("TWENTY_FIVE"), 6)
        stack = ItemStack().modify_items("HUNDRED", 1).multiply_stack_by_factor(1.5)
        self.assertEqual(stack.count_type_of_item("HUNDRED"), 1)
        self.assertEqual(stack.count_type_of_item("TWENTY_FIVE"), 2)
        stack = ItemStack().modify_items("TWENTY_FIVE", 1).multiply_stack_by_factor(1.5)
        self.assertEqual(stack.count_type_of_item("TWENTY_FIVE"), 1)
        self.assertEqual(stack.count_type_of_item("FIVE"), 2)
        stack = ItemStack().modify_items("TWENTY_FIVE", 3).multiply_stack_by_factor(1.5)
        self.assertEqual(stack.count_type_of_item("TWENTY_FIVE"), 3)
        self.assertEqual(stack.count_type_of_item("FIVE"), 6)
        self.assertEqual(stack.count_type_of_item("TWO_FIFTY"), 3)
        stack = ItemStack().modify_items("HUNDRED", 3).modify_items("TWENTY_FIVE", 3).modify_items("FIVE", 4).modify_items("TWO_FIFTY", 8).modify_items("ONE", 3)
        stack = stack.multiply_stack_by_factor(1.5)
        self.assertEqual(stack.count_type_of_item("HUNDRED"), 3)
        self.assertEqual(stack.count_type_of_item("TWENTY_FIVE"), 9)
        self.assertEqual(stack.count_type_of_item("FIVE"), 10)
        self.assertEqual(stack.count_type_of_item("TWO_FIFTY"), 15)
        self.assertEqual(stack.count_type_of_item("ONE"), 11)
        stack = ItemStack().modify_items("HUNDRED", 3).modify_items("TWENTY_FIVE", 3).modify_items("FIVE", 4).modify_items("TWO_FIFTY", 8).modify_items("ONE", 3)
        stack = stack.multiply_stack_by_factor(2)
        self.assertEqual(stack.count_type_of_item("HUNDRED"), 6)
        self.assertEqual(stack.count_type_of_item("TWENTY_FIVE"), 6)
        self.assertEqual(stack.count_type_of_item("FIVE"), 8)
        self.assertEqual(stack.count_type_of_item("TWO_FIFTY"), 16)
        self.assertEqual(stack.count_type_of_item("ONE"), 6)


if __name__ == '__main__':
    unittest.main()
