#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from wicd import misc

class TestMisc(unittest.TestCase):
    def test_misc_run(self):
        output = misc.Run(['echo', 'hi']).strip()
        self.assertEqual('hi', output)

    def test_valid_ip_1(self):
        self.assertTrue(misc.IsValidIP('0.0.0.0'))

    def test_valid_ip_2(self):
        self.assertTrue(misc.IsValidIP('255.255.255.255'))

    def test_valid_ip_3(self):
        self.assertTrue(misc.IsValidIP('10.0.1.1'))

    def test_valid_ip_4(self):
        self.assertTrue(misc.IsValidIP('::'))

    def test_valid_ip_5(self):
        self.assertTrue(misc.IsValidIP('::1'))

    def test_valid_ip_6(self):
        self.assertTrue(misc.IsValidIP('FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF'))

    def test_valid_ip_7(self):
        self.assertTrue(misc.IsValidIP('2001:0db8:85a3:0000:0000:8a2e:0370:7334'))

    def test_invalid_ip_1(self):
        self.assertFalse(misc.IsValidIP('-10.0.-1.-1'))

    def test_invalid_ip_2(self):
        self.assertFalse(misc.IsValidIP('256.0.0.1'))

    def test_invalid_ip_3(self):
        self.assertFalse(misc.IsValidIP('1000.0.0.1'))

    def test_invalid_ip_4(self):
        self.assertFalse(misc.IsValidIP(':'))

    def test_invalid_ip_5(self):
        self.assertFalse(misc.IsValidIP('1:'))

    def test_invalid_ip_6(self):
        self.assertFalse(misc.IsValidIP('ZZZZ:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF'))

    def test_invalid_ip_7(self):
        self.assertFalse(misc.IsValidIP('2001:0db8:85Z3:0000:0000:8a2e:0370:7334'))

    def test_run_valid_regex(self):
        import re
        regex = re.compile('.*(ABC.EFG).*')
        found = misc.RunRegex(regex, '01234ABCDEFG56789')
        self.assertEqual(found, 'ABCDEFG')

    def test_run_invalid_regex(self):
        import re
        regex = re.compile('.*(ABC.EFG).*')
        found = misc.RunRegex(regex, '01234ABCEDFG56789')
        self.assertEqual(found, None)

    def test_to_boolean_false(self):
        self.assertFalse(misc.to_bool('False'))

    def test_to_boolean_0(self):
        self.assertFalse(misc.to_bool('0'))

    def test_to_boolean_true(self):
        self.assertTrue(misc.to_bool('True'))

    def test_to_boolean_true(self):
        self.assertTrue(misc.to_bool('1'))

    def test_noneify_1(self):
        self.assertEqual(misc.Noneify('None'), None)

    def test_noneify_2(self):
        self.assertEqual(misc.Noneify(''), None)

    def test_noneify_3(self):
        self.assertEqual(misc.Noneify(None), None)

    def test_noneify_4(self):
        self.assertFalse(misc.Noneify('False'))

    def test_noneify_5(self):
        self.assertFalse(misc.Noneify('0'))

    def test_noneify_6(self):
        self.assertFalse(misc.Noneify(False))

    def test_noneify_7(self):
        self.assertTrue(misc.Noneify('True'))

    def test_noneify_8(self):
        self.assertTrue(misc.Noneify('1'))

    def test_noneify_9(self):
        self.assertTrue(misc.Noneify(True))

    def test_noneify_10(self):
        self.assertEqual(misc.Noneify('randomtext'), 'randomtext')

    def test_noneify_11(self):
        self.assertEqual(misc.Noneify(5), 5)

    def test_noneify_12(self):
        self.assertEqual(misc.Noneify(1, False), 1)

    def test_noneify_13(self):
        self.assertEqual(misc.Noneify(0, False), 0)

    def test_none_to_string_1(self):
        self.assertEqual(misc.noneToString(None), 'None')

    def test_none_to_string_2(self):
        self.assertEqual(misc.noneToString(''), 'None')

    def test_none_to_string_3(self):
        self.assertEqual(misc.noneToString(None), 'None')

    ####################################################################
    # misc.to_unicode actually converts to utf-8, which is type str    #
    ####################################################################

    def test_to_unicode_1(self):
        self.assertEqual(misc.to_unicode('邪悪'), '邪悪')

    def test_to_unicode_2(self):
        self.assertEqual(misc.to_unicode('邪悪'), '邪悪')

    def test_to_unicode_3(self):
        self.assertEqual(misc.to_unicode('abcdef'), 'abcdef')

    def test_to_unicode_4(self):
        self.assertEqual(type(misc.to_unicode('abcdef'.encode('latin-1'))), str)

    def test_to_unicode_5(self):
        self.assertEqual(misc.to_unicode("berkåk"), "berkåk")

    def test_to_unicode_6(self):
        self.assertEqual(misc.to_unicode('berk\xe5k'), "berkåk")

    def test_none_to_blank_string_1(self):
        self.assertEqual(misc.noneToBlankString(None), '')

    def test_none_to_blank_string_2(self):
        self.assertEqual(misc.noneToBlankString('None'), '')

    def test_string_to_none_1(self):
        self.assertEqual(misc.stringToNone(''), None)

    def test_string_to_none_2(self):
        self.assertEqual(misc.stringToNone('None'), None)

    def test_string_to_none_3(self):
        self.assertEqual(misc.stringToNone(None), None)

    def test_string_to_none_4(self):
        self.assertEqual(misc.stringToNone('abcdef'), 'abcdef')

def suite():
	suite = unittest.TestSuite()
	tests = []
	[ tests.append(test) for test in dir(TestMisc) if test.startswith('test') ]
	for test in tests:
		suite.addTest(TestMisc(test))
	return suite

if __name__ == '__main__':
	unittest.main()
