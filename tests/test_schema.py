"""
Unit tests for the hxl.schema module
David Megginson
November 2014

License: Public Domain
"""

import unittest
import os
from hxl.model import HXLColumn, HXLRow
from hxl.parser import HXLReader
from hxl.schema import HXLSchema, HXLSchemaRule, readHXLSchema
from hxl.taxonomy import HXLTaxonomy, HXLTerm

class TestSchema(unittest.TestCase):

    def setUp(self):
        self.errors = []
        self.schema = HXLSchema(
            rules=[
                HXLSchemaRule('#sector', minOccur=1),
                HXLSchemaRule('#affected_num', dataType=HXLSchemaRule.TYPE_NUMBER)
                ],
            callback = lambda error: self.errors.append(error)
            )
        self.row = HXLRow(
            columns = [
                HXLColumn(hxlTag='#affected_num', columnNumber=0),
                HXLColumn(hxlTag='#sector', columnNumber=1),
                HXLColumn(hxlTag='#sector', columnNumber=2)
            ],
            rowNumber = 1,
            sourceRowNumber = 2
        )


    def test_row(self):
        self.try_schema(['35', 'WASH', ''])
        self.try_schema(['35', 'WASH', 'Health'])

        self.try_schema(['35', '', ''], 1)
        self.try_schema(['abc', 'WASH', ''], 2)

    def try_schema(self, row_values, errors_expected = 0):
        self.row.values = row_values
        if errors_expected == 0:
            self.assertTrue(self.schema.validateRow(self.row))
        else:
            self.assertFalse(self.schema.validateRow(self.row))
        self.assertEquals(len(self.errors), errors_expected)
        
class TestSchemaRule(unittest.TestCase):

    def setUp(self):
        self.errors = []
        self.rule = HXLSchemaRule('#x_test', callback=lambda error: self.errors.append(error))

    def test_type_none(self):
        self._try_rule('')
        self._try_rule(10)
        self._try_rule('hello, world')

    def test_type_text(self):
        self.rule.dataType = HXLSchemaRule.TYPE_TEXT
        self._try_rule('')
        self._try_rule(10)
        self._try_rule('hello, world')

    def test_type_num(self):
        self.rule.dataType = HXLSchemaRule.TYPE_NUMBER
        self._try_rule(10)
        self._try_rule(' -10.1 ');
        self._try_rule('ten', 1)

    def test_type_url(self):
        self.rule.dataType = HXLSchemaRule.TYPE_URL
        self._try_rule('http://www.example.org')
        self._try_rule('hello, world', 1)

    def test_type_email(self):
        self.rule.dataType = HXLSchemaRule.TYPE_EMAIL;
        self._try_rule('somebody@example.org')
        self._try_rule('hello, world', 1)

    def test_type_phone(self):
        self.rule.dataType = HXLSchemaRule.TYPE_PHONE
        self._try_rule('+1-613-555-1111 x1234')
        self._try_rule('(613) 555-1111')
        self._try_rule('123', 1)
        self._try_rule('123456789abc', 1)

    def test_type_taxonomy(self):
        # No level specified
        self.rule.taxonomy = make_taxonomy()
        self._try_rule('AAA') # level 1
        self._try_rule('BBB') # level 2
        self._try_rule('CCC', 1) # not defined

        # Explicit level
        self.rule.taxonomyLevel = 1
        self._try_rule('AAA') # level 1
        self._try_rule('BBB', 1) # level 2
        self._try_rule('CCC', 1) # not defined

    def test_value_range(self):
        self.rule.minValue = 3.5
        self.rule.maxValue = 4.5
        self._try_rule(4.0)
        self._try_rule('4')
        self._try_rule('3.49', 1)
        self._try_rule(5.0, 1)

    def test_value_pattern(self):
        self.rule.valuePattern = '^a+b$'
        self._try_rule('ab', 0)
        self._try_rule('aab', 0)
        self._try_rule('bb', 1)

    def test_value_enumeration(self):
        self.rule.valueEnumeration=['aa', 'bb', 'cc']

        self.rule.caseSensitive = True
        self._try_rule('bb')
        self._try_rule('BB', 1)
        self._try_rule('dd', 1)

        self.rule.caseSensitive = False
        self._try_rule('bb')
        self._try_rule('BB')
        self._try_rule('dd', 1)

    def test_row_restrictions(self):
        row = HXLRow(
            columns=[
                HXLColumn(hxlTag='#x_test'),
                HXLColumn(hxlTag='#subsector'),
                HXLColumn(hxlTag='#x_test')
                ],
            rowNumber = 1
            );
        row.values = ['WASH', '', ''];

        self.rule.minOccur = 1
        self._try_rule(row)

        self.rule.minOccur = 2
        self._try_rule(row, 1)

        self.rule.minOccur = None

        self.rule.maxOccur = 1
        self._try_rule(row)

        self.rule.maxOccur = 0
        self._try_rule(row, 1)

    def test_load_default(self):
        schema = readHXLSchema()
        self.assertTrue(0 < len(schema.rules))
        dataset = HXLReader(open(resolve_file('data-good.csv'), 'r'))
        self.assertTrue(schema.validate(dataset))

    def test_load_good(self):
        schema = readHXLSchema(HXLReader(open(resolve_file('schema-basic.csv'), 'r')))
        dataset = HXLReader(open(resolve_file('data-good.csv'), 'r'))
        self.assertTrue(schema.validate(dataset))

    def test_load_bad(self):
        schema = readHXLSchema(HXLReader(open(resolve_file('schema-basic.csv'), 'r')))
        schema.callback = lambda e: True # to avoid seeing error messages
        dataset = HXLReader(open(resolve_file('data-bad.csv'), 'r'))
        self.assertFalse(schema.validate(dataset))

    def test_load_taxonomy(self):
        schema = readHXLSchema(HXLReader(open(resolve_file('schema-taxonomy.csv'), 'r')), baseDir=file_dir)
        # schema.callback = lambda e: True # to avoid seeing error messages
        dataset = HXLReader(open(resolve_file('data-taxonomy-good.csv'), 'r'))
        self.assertTrue(schema.validate(dataset))

    def _try_rule(self, value, errors_expected = 0):
        """
        Validate a single value with a HXLSchemaRule
        """
        if isinstance(value, HXLRow):
            result = self.rule.validateRow(value)
        else:
            result = self.rule.validate(value)
        if errors_expected == 0:
            self.assertTrue(result)
        else:
            self.assertFalse(result)
        self.assertEqual(len(self.errors), errors_expected)
        self.errors = [] # clear errors for the next run

########################################################################
# Support functions
########################################################################

root_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))
file_dir = os.path.join(root_dir, 'tests', 'files', 'test_schema')

def resolve_file(name):
    """
    Resolve a file name in the test directory.
    """
    return os.path.join(file_dir, name)

def make_taxonomy():
    return HXLTaxonomy(terms={
        'AAA': HXLTerm('AAA', level=1),
        'BBB': HXLTerm('BBB', level=2)
        })

# end
