"""
Tests for the inference module.
"""
import unittest
from bayescalc.lexer import Lexer
from bayescalc.parser import Parser
from bayescalc.inference import Inference

class TestInference(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        net_str = """
        variable Rain {True, False}
        variable Sprinkler {On, Off}
        variable GrassWet {Yes, No}

        Rain { P(True) = 0.2 }

        Sprinkler | Rain {
            P(On | True) = 0.01
            P(On | False) = 0.4
        }

        GrassWet | Rain, Sprinkler {
            P(Yes | True, On) = 0.99
            P(Yes | True, Off) = 0.8
            P(Yes | False, On) = 0.9
            P(Yes | False, Off) = 0.1
        }
        """
        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        cls.network = parser.parse()
        cls.inference = Inference(cls.network)

    def test_query_marginal(self):
        # P(Rain)
        result = self.inference.variable_elimination(["Rain"], {})
        self.assertAlmostEqual(result.probabilities[("True",)], 0.2)
        self.assertAlmostEqual(result.probabilities[("False",)], 0.8)

    def test_query_conditional(self):
        # P(Rain | GrassWet=Yes)
        result = self.inference.variable_elimination(["Rain"], {"GrassWet": "Yes"})
        # Values from manual calculation or other tools
        # P(R|G=y) = alpha * < P(R, S, G=y) >_S
        # P(R=t,S=on,G=y) = 0.2*0.01*0.99 = 0.00198
        # P(R=t,S=off,G=y)= 0.2*0.99*0.8  = 0.1584
        # P(R=f,S=on,G=y) = 0.8*0.4*0.9   = 0.288
        # P(R=f,S=off,G=y)= 0.8*0.6*0.1   = 0.048
        # P(R=t|G=y) = alpha * (0.00198 + 0.1584) = alpha * 0.16038
        # P(R=f|G=y) = alpha * (0.288 + 0.048) = alpha * 0.336
        # alpha = 1 / (0.16038 + 0.336) = 1 / 0.49638
        # P(R=t|G=y) = 0.16038 / 0.49638 = 0.3231
        self.assertAlmostEqual(result.probabilities[("True",)], 0.3231, places=4)
        self.assertAlmostEqual(result.probabilities[("False",)], 1 - 0.3231, places=4)

    def test_query_joint_conditional(self):
        # P(Sprinkler, Rain | GrassWet=Yes)
        result = self.inference.variable_elimination(["Sprinkler", "Rain"], {"GrassWet": "Yes"})
        # Check one value
        # P(S=on, R=t | G=y) = P(S=on, R=t, G=y) / P(G=y)
        # P(S=on, R=t, G=y) = 0.2 * 0.01 * 0.99 = 0.00198
        # P(G=y) = 0.49638 (from above)
        # P(S=on, R=t | G=y) = 0.00198 / 0.49638 = 0.003988
        
        # Need to check order of variables in result factor
        if result.variables[0].name == "Sprinkler":
            self.assertAlmostEqual(result.probabilities[("On", "True")], 0.003988, places=4)
        else:
            self.assertAlmostEqual(result.probabilities[("True", "On")], 0.003988, places=4)


if __name__ == '__main__':
    unittest.main()
