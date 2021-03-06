"""
Unit tests for the hxl.taxonomy module
David Megginson
January 2015

License: Public Domain
"""

import os
import unittest
from hxl.parser import HXLReader
from hxl.taxonomy import HXLTaxonomyException, HXLTaxonomy, HXLTerm, readTaxonomy

class TestTaxonomy(unittest.TestCase):
    """Test the HXLTaxonomy class"""
    
    def test_good(self):
        """A normal taxonomy should load correctly"""
        taxonomy = read_taxonomy("taxonomy_good.csv")
        self.assertTrue(taxonomy.is_valid())
        self.assertEquals(10, len(taxonomy.terms))

    def test_nocode(self):
        """Reading should fail with a missing #term_id"""
        self.assertFalse(try_loaded("taxonomy_nocode.csv"))

    def test_duplicate(self):
        """Reading should fail with a duplicate #term_id"""
        self.assertFalse(try_loaded("taxonomy_duplicate.csv"))

    def test_noparent(self):
        """A dangling parent code makes the taxonomy invalid"""
        self.assertFalse(try_valid("taxonomy_noparent.csv"))

    def test_loop(self):
        """A loop in ancestors makes the taxonomy invalid"""
        self.assertFalse(try_valid("taxonomy_loop.csv"))


class TestTerm(unittest.TestCase):
    """Test the HXLTerm class"""

    def test_properties(self):
        term = HXLTerm('XXX', 'YYY', 3)
        self.assertEquals('XXX', term.code)
        self.assertEquals('YYY', term.parent_code)
        self.assertEquals(3, term.level)


#
# Local utility functions
#

def try_loaded(name):
    """
    Report whether a taxonomy loads without an exception
    """
    is_loaded = True
    try:
        read_taxonomy(name)
    except HXLTaxonomyException:
        is_loaded = False
    return is_loaded

def try_valid(name):
    """
    Report whether a taxonomy loads and validates
    """
    taxonomy = read_taxonomy(name)
    return taxonomy.is_valid()

def read_taxonomy(name):
    """
    Read a taxonomy test file
    """
    return readTaxonomy(HXLReader(open(resolve_file(name), 'r')))

root_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))

def resolve_file(name):
    """
    Resolve a file name in the test directory.
    """
    return os.path.join(root_dir, 'tests', 'files', 'test_taxonomy', name)
    
