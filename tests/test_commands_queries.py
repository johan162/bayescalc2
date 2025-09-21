"""
Tests for the commands and queries modules.
"""
import unittest
import numpy as np
from bayescalc.lexer import Lexer
from bayescalc.parser import Parser
from bayescalc.commands import CommandHandler
from bayescalc.queries import QueryParser

class TestCommandsAndQueries(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Using the proper network format
        net_str = """
        variable A {True, False}
        variable B {True, False}
        
        A {
            P(True) = 0.5
        }
        
        B | A {
            P(True | True) = 0.5
            P(False | True) = 0.5
            P(True | False) = 0.5
            P(False | False) = 0.5
        }
        """
        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        cls.network = parser.parse()
        cls.cmd_handler = CommandHandler(cls.network)
        cls.query_parser = QueryParser(cls.network)

    def test_query_parser(self):
        # Using the new API format for variable_elimination
        result = self.query_parser.parse_and_execute("P(A | B=True)")
        # The format of result.probabilities has changed - result now comes with a tuple format
        for assignment, prob in result.probabilities.items():
            if "True" in assignment:
                self.assertAlmostEqual(prob, 0.5)
            elif "False" in assignment:
                self.assertAlmostEqual(prob, 0.5)

    def test_is_independent(self):
        # In this network, A and B are independent
        self.assertTrue(self.cmd_handler.execute("isindependent(A, B)"))

    def test_entropy(self):
        # H(A) = - (0.5 * log2(0.5) + 0.5 * log2(0.5)) = 1.0
        self.assertAlmostEqual(self.cmd_handler.execute("entropy(A)"), 1.0)

    def test_mutual_information(self):
        # I(A;B) = H(A) - H(A|B) = H(A) - (P(B=T)H(A|B=T) + P(B=F)H(A|B=F))
        # Since they are independent, H(A|B) = H(A), so I(A;B) = 0
        self.assertAlmostEqual(self.cmd_handler.execute("mutual_information(A, B)"), 0.0)

    def test_print_cpt(self):
        output = self.cmd_handler.execute("printCPT(B)")
        # 'B     | A          | P     \n------+------------+-------\nTrue  | True       | 0.5000\nTrue  | False      | 0.5000\nFalse | True       | 0.5000\nFalse | False      | 0.5000'
        self.assertIn("B     | A          | P", output)
        self.assertIn("True  | True       | 0.5000", output)

if __name__ == '__main__':
    unittest.main()

# 'B     | A      | P     \n------+--------+-------\nTrue  | True   | 0.5000\nTrue  | False  | 0.5000\nFalse | True   | 0.5000\nFalse | False  | 0.5000'