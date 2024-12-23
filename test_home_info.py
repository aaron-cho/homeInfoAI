import unittest
from home_info import AddressValidator

class TestAddressValidator(unittest.TestCase):

    def test_validate_street(self):
        self.assertTrue(AddressValidator.validate_street("123 Main St"))
        self.assertFalse(AddressValidator.validate_street("123"))  # Too short
        self.assertFalse(AddressValidator.validate_street("Avenue"))  # No number
        self.assertFalse(AddressValidator.validate_street("12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"))  # Too long

    def test_validate_city(self):
        self.assertTrue(AddressValidator.validate_city("Los Angeles"))
        self.assertFalse(AddressValidator.validate_city("Los Angeles 123"))  # Contains numbers
        self.assertFalse(AddressValidator.validate_city(""))  # Empty
        self.assertFalse(AddressValidator.validate_city("A" * 51))  # Too long

    def test_validate_state(self):
        self.assertTrue(AddressValidator.validate_state("CA"))
        self.assertFalse(AddressValidator.validate_state("ZZ"))  # Invalid state
        self.assertFalse(AddressValidator.validate_state("C"))  # Too short
        self.assertFalse(AddressValidator.validate_state("California"))  # Too long

    def test_validate_zipcode(self):
        self.assertTrue(AddressValidator.validate_zipcode("90210"))
        self.assertTrue(AddressValidator.validate_zipcode("90210-1234"))
        self.assertFalse(AddressValidator.validate_zipcode("1234"))  # Too short
        self.assertFalse(AddressValidator.validate_zipcode("123456"))  # Too long
        self.assertFalse(AddressValidator.validate_zipcode("ABCDE"))  # Invalid format

if __name__ == '__main__':
    unittest.main()