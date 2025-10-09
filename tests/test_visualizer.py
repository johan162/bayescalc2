"""
Tests for the network visualization module.
"""

import unittest
import os
import tempfile
from bayescalc.lexer import Lexer
from bayescalc.parser import Parser


class TestVisualization(unittest.TestCase):
    """Test network visualization functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test network."""
        net_str = """
        boolean Rain
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

    def test_visualizer_import(self):
        """Test that visualizer can be imported."""
        try:
            from bayescalc.visualizer import NetworkVisualizer  # noqa: F401

            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"graphviz not installed: {e}")

    def test_create_visualizer(self):
        """Test creating a NetworkVisualizer instance."""
        try:
            from bayescalc.visualizer import NetworkVisualizer

            visualizer = NetworkVisualizer(self.network)
            self.assertIsNotNone(visualizer)
            self.assertEqual(visualizer.network, self.network)
        except ImportError:
            self.skipTest("graphviz not installed")

    def test_generate_pdf(self):
        """Test generating PDF visualization."""
        try:
            from bayescalc.visualizer import NetworkVisualizer
        except ImportError:
            self.skipTest("graphviz not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test_network")

            try:
                visualizer = NetworkVisualizer(self.network)
                result_path = visualizer.generate_graph(
                    output_file=output_file, format="pdf", show_cpt=True
                )

                # Check that file was created
                self.assertTrue(os.path.exists(result_path))
                self.assertTrue(result_path.endswith(".pdf"))

                # Check file is not empty
                self.assertGreater(os.path.getsize(result_path), 0)
            except Exception as e:
                if "graphviz" in str(e).lower() or "dot" in str(e).lower():
                    self.skipTest(f"graphviz system package not installed: {e}")
                else:
                    raise

    def test_generate_png(self):
        """Test generating PNG visualization."""
        try:
            from bayescalc.visualizer import NetworkVisualizer
        except ImportError:
            self.skipTest("graphviz not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test_network")

            try:
                visualizer = NetworkVisualizer(self.network)
                result_path = visualizer.generate_graph(
                    output_file=output_file, format="png", show_cpt=False
                )

                self.assertTrue(os.path.exists(result_path))
                self.assertTrue(result_path.endswith(".png"))
                self.assertGreater(os.path.getsize(result_path), 0)
            except Exception as e:
                if "graphviz" in str(e).lower() or "dot" in str(e).lower():
                    self.skipTest(f"graphviz system package not installed: {e}")
                else:
                    raise

    def test_generate_svg(self):
        """Test generating SVG visualization."""
        try:
            from bayescalc.visualizer import NetworkVisualizer
        except ImportError:
            self.skipTest("graphviz not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test_network")

            try:
                visualizer = NetworkVisualizer(self.network)
                result_path = visualizer.generate_graph(
                    output_file=output_file, format="svg", show_cpt=True
                )

                self.assertTrue(os.path.exists(result_path))
                self.assertTrue(result_path.endswith(".svg"))
                self.assertGreater(os.path.getsize(result_path), 0)
            except Exception as e:
                if "graphviz" in str(e).lower() or "dot" in str(e).lower():
                    self.skipTest(f"graphviz system package not installed: {e}")
                else:
                    raise

    def test_different_layouts(self):
        """Test different layout engines."""
        try:
            from bayescalc.visualizer import NetworkVisualizer
        except ImportError:
            self.skipTest("graphviz not installed")

        layouts = ["dot", "neato", "fdp", "circo"]

        with tempfile.TemporaryDirectory() as tmpdir:
            for layout in layouts:
                output_file = os.path.join(tmpdir, f"test_{layout}")

                try:
                    visualizer = NetworkVisualizer(self.network)
                    result_path = visualizer.generate_graph(
                        output_file=output_file,
                        format="pdf",
                        show_cpt=False,
                        layout=layout,
                    )

                    self.assertTrue(os.path.exists(result_path))
                    self.assertGreater(os.path.getsize(result_path), 0)
                except Exception as e:
                    if "graphviz" in str(e).lower() or "dot" in str(e).lower():
                        self.skipTest(f"graphviz system package not installed: {e}")
                    else:
                        raise

    def test_invalid_format(self):
        """Test that invalid format raises ValueError."""
        try:
            from bayescalc.visualizer import NetworkVisualizer
        except ImportError:
            self.skipTest("graphviz not installed")

        visualizer = NetworkVisualizer(self.network)

        with self.assertRaises(ValueError) as context:
            visualizer.generate_graph(output_file="test", format="invalid")

        self.assertIn("Invalid format", str(context.exception))

    def test_invalid_layout(self):
        """Test that invalid layout raises ValueError."""
        try:
            from bayescalc.visualizer import NetworkVisualizer
        except ImportError:
            self.skipTest("graphviz not installed")

        visualizer = NetworkVisualizer(self.network)

        with self.assertRaises(ValueError) as context:
            visualizer.generate_graph(output_file="test", layout="invalid")

        self.assertIn("Invalid layout", str(context.exception))

    def test_simple_graph_method(self):
        """Test the convenience method for simple graphs."""
        try:
            from bayescalc.visualizer import NetworkVisualizer
        except ImportError:
            self.skipTest("graphviz not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "simple_network")

            try:
                visualizer = NetworkVisualizer(self.network)
                result_path = visualizer.generate_simple_graph(
                    output_file=output_file, format="pdf"
                )

                self.assertTrue(os.path.exists(result_path))
                self.assertTrue(result_path.endswith(".pdf"))
            except Exception as e:
                if "graphviz" in str(e).lower() or "dot" in str(e).lower():
                    self.skipTest(f"graphviz system package not installed: {e}")
                else:
                    raise


class TestVisualizeCommand(unittest.TestCase):
    """Test the visualize command in CommandHandler."""

    @classmethod
    def setUpClass(cls):
        """Set up test network."""
        net_str = """
        boolean A
        variable B {Yes, No}

        A { P(True) = 0.3 }
        B | A {
            P(Yes | True) = 0.8
            P(Yes | False) = 0.2
        }
        """
        lexer = Lexer(net_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        cls.network = parser.parse()

    def test_visualize_command_registered(self):
        """Test that visualize command is registered."""
        from bayescalc.commands import CommandHandler

        cmd_handler = CommandHandler(self.network)
        self.assertIn("visualize", cmd_handler.commands)
        self.assertIn("viz", cmd_handler.alias_to_command)

    def test_visualize_is_command(self):
        """Test that visualize is recognized as a command."""
        from bayescalc.commands import CommandHandler

        cmd_handler = CommandHandler(self.network)
        self.assertTrue(cmd_handler.is_command("visualize(output.pdf)"))
        self.assertTrue(cmd_handler.is_command("viz(output.png)"))

    def test_visualize_command_execution(self):
        """Test executing visualize command."""
        from bayescalc.commands import CommandHandler

        try:
            import graphviz  # noqa: F401
        except ImportError:
            self.skipTest("graphviz not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test_output")

            cmd_handler = CommandHandler(self.network)

            try:
                result = cmd_handler.execute(f"visualize({output_file}.pdf)")

                self.assertIn("saved to", result.lower())
                # File should exist
                self.assertTrue(os.path.exists(f"{output_file}.pdf"))
            except Exception as e:
                if "graphviz" in str(e).lower() or "dot" in str(e).lower():
                    self.skipTest(f"graphviz system package not installed: {e}")
                else:
                    raise

    def test_visualize_with_options(self):
        """Test visualize command with options."""
        from bayescalc.commands import CommandHandler

        try:
            import graphviz  # noqa: F401
        except ImportError:
            self.skipTest("graphviz not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test_options")

            cmd_handler = CommandHandler(self.network)

            try:
                result = cmd_handler.execute(
                    f"visualize({output_file}.png, show_cpt=False, layout=neato)"
                )

                self.assertIn("saved to", result.lower())
                self.assertTrue(os.path.exists(f"{output_file}.png"))
            except Exception as e:
                if "graphviz" in str(e).lower() or "dot" in str(e).lower():
                    self.skipTest(f"graphviz system package not installed: {e}")
                else:
                    raise


if __name__ == "__main__":
    unittest.main()
