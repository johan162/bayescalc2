"""
Network visualization using graphviz.

This module provides functionality to generate visual representations of Bayesian networks
with optional CPT tables displayed alongside nodes.
"""

import graphviz
from typing import List, Tuple
from .network_model import BayesianNetwork, Variable


class NetworkVisualizer:
    """Generate visual representations of Bayesian networks."""

    def __init__(self, network: BayesianNetwork):
        """
        Initialize the visualizer with a Bayesian network.

        Args:
            network: The BayesianNetwork to visualize
        """
        self.network = network

    def generate_graph(
        self,
        output_file: str = "network",
        format: str = "pdf",
        show_cpt: bool = True,
        layout: str = "dot",
        rankdir: str = "TB",
        page_size: str = None,
        scale: float = 1.0,
    ) -> str:
        """
        Generate network visualization.

        Args:
            output_file: Output filename (without extension)
            format: Output format ('pdf', 'png', 'svg', 'jpg')
            show_cpt: Include CPT tables beside nodes
            layout: graphviz layout engine ('dot', 'neato', 'fdp', 'circo', 'twopi')
            rankdir: Graph direction ('TB'=top-bottom, 'LR'=left-right, 'BT', 'RL')
            page_size: PDF page size ('A3', 'A4', 'A5', or 'HxW' in mm, e.g. '297x210')
            scale: Optional scale factor for the graph (default 1.0)

        Returns:
            Path to generated file

        Raises:
            ImportError: If graphviz is not installed
            ValueError: If invalid format or layout specified
        """
        valid_formats = ["pdf", "png", "svg", "jpg", "jpeg", "ps"]
        valid_layouts = ["dot", "neato", "fdp", "circo", "twopi", "sfdp"]
        valid_rankdirs = ["TB", "LR", "BT", "RL"]
        valid_page_sizes = {
            "A3": (420, 297),
            "A4": (297, 210),
            "A5": (210, 148),
        }

        if format.lower() not in valid_formats:
            raise ValueError(
                f"Invalid format '{format}'. Valid formats: {', '.join(valid_formats)}"
            )

        if layout not in valid_layouts:
            raise ValueError(
                f"Invalid layout '{layout}'. Valid layouts: {', '.join(valid_layouts)}"
            )

        if rankdir not in valid_rankdirs:
            raise ValueError(
                f"Invalid rankdir '{rankdir}'. Valid directions: {', '.join(valid_rankdirs)}"
            )

        try:
            dot = graphviz.Digraph(name="BayesianNetwork", format=format, engine=layout)

            # Configure graph appearance
            dot.attr(rankdir=rankdir)
            dot.attr("graph", fontname="Arial", fontsize="10")
            dot.attr(
                "node",
                shape="box",
                style="rounded,filled",
                fillcolor="lightblue",
                fontname="Arial",
                fontsize="10",
            )
            dot.attr("edge", color="gray40", arrowsize="0.8")

            # PDF page size and scale
            if format.lower() == "pdf":
                if page_size:
                    if page_size in valid_page_sizes:
                        width_mm, height_mm = valid_page_sizes[page_size]
                    else:
                        # Parse custom size: '297x210'
                        try:
                            width_mm, height_mm = map(
                                float, page_size.lower().split("x")
                            )
                        except Exception:
                            raise ValueError(
                                f"Invalid page_size '{page_size}'. Use 'A3', 'A4', 'A5' or 'WxH' in mm."
                            )
                    # Set page size in inches (1 inch = 25.4 mm)
                    width_in = width_mm / 25.4
                    height_in = height_mm / 25.4
                    
                    # Apply scale to the graph size
                    if scale and scale != 1.0:
                        # Scale down the maximum size the graph can occupy
                        graph_width = width_in * scale
                        graph_height = height_in * scale
                        # Set maximum size and let graph fit within it
                        dot.attr("graph", size=f"{graph_width},{graph_height}")
                        dot.attr("graph", ratio="compress")
                        # Set the actual page size for the PDF
                        dot.attr("graph", page=f"{width_in},{height_in}")
                        dot.attr("graph", center="true")
                    else:
                        # Fill the page completely when scale is 1.0
                        dot.attr("graph", size=f"{width_in},{height_in}!")
                elif scale and scale != 1.0:
                    # Set the default size to A4 at 100% scale
                    # A4 size in inches is approximately 8.27 x 11.69
                    width_in = 8.27
                    height_in = 11.69
                    default_graph_width = width_in * scale
                    default_graph_height = height_in * scale
                    dot.attr("graph", size=f"{default_graph_width},{default_graph_height}!")
                    dot.attr("graph", page=f"{width_in},{height_in}")
                    dot.attr("graph", center="true")


            # Add nodes with optional CPT tables
            for var_name in sorted(self.network.variables.keys()):
                var = self.network.variables[var_name]
                label = self._create_node_label(var, show_cpt)
                dot.node(var.name, label=label)

            # Add edges (parent -> child relationships)
            for var_name, var in self.network.variables.items():
                parents = self.network.get_parents(var_name)
                for parent_name in parents:
                    dot.edge(parent_name, var_name)

            # Render and return path
            output_path = dot.render(output_file, cleanup=True)
            return output_path

        except ImportError as e:
            raise ImportError(
                "graphviz package not installed. Install it with: pip install graphviz"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Error generating visualization: {e}") from e

    def _create_node_label(self, variable: Variable, show_cpt: bool) -> str:
        """
        Create node label with optional CPT.

        Args:
            variable: The variable to create a label for
            show_cpt: Whether to include CPT table in the label

        Returns:
            HTML-like label string for graphviz
        """
        if not show_cpt:
            return variable.name

        # Get CPT from network
        cpt = self.network.factors.get(variable.name)
        if not cpt:
            return variable.name

        # Use HTML-like label for table formatting
        label = '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">'

        # Header with variable name
        label += (
            f'<TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>{variable.name}</B></TD></TR>'
        )

        # Add domain information
        domain_str = ", ".join(str(v) for v in variable.domain)
        label += (
            f'<TR><TD COLSPAN="2" BGCOLOR="lightyellow"><I>{domain_str}</I></TD></TR>'
        )

        # Get parents if any
        parents = self.network.get_parents(variable.name)

        if not parents:
            # Prior probability - show all values
            for value in variable.domain:
                prob = cpt.probabilities.get((value,), 0.0)
                label += f'<TR><TD ALIGN="LEFT">P({value})</TD><TD ALIGN="RIGHT">{prob:.4f}</TD></TR>'
        else:
            # Conditional probability - show subset of entries
            # Group by parent assignments
            entries = self._format_cpt_entries(variable, cpt, list(parents))

            # Show first 10 entries, then indicate if there are more
            max_entries = 10
            for i, (condition, value, prob) in enumerate(entries):
                if i >= max_entries:
                    remaining = len(entries) - max_entries
                    label += f'<TR><TD COLSPAN="2" BGCOLOR="lightgray"><I>... {remaining} more entries ...</I></TD></TR>'
                    break

                label += f'<TR><TD ALIGN="LEFT" PORT="left">P({value}|{condition})</TD>'
                label += f'<TD ALIGN="RIGHT">{prob:.4f}</TD></TR>'

        label += "</TABLE>>"
        return label

    def _format_cpt_entries(
        self, variable: Variable, cpt, parents: List[str]
    ) -> List[Tuple[str, str, float]]:
        """
        Format CPT entries for display.

        Args:
            variable: The variable
            cpt: The CPT factor
            parents: List of parent variable names

        Returns:
            List of tuples (condition_str, value, probability)
        """
        entries = []

        # Get parent variables
        parent_vars = [self.network.variables[p] for p in parents]

        # Iterate through CPT entries
        for assignment, prob in sorted(cpt.probabilities.items()):
            # assignment is a tuple: (parent1_val, parent2_val, ..., var_val)
            # Last element is the variable's value, rest are parent values
            if len(assignment) == len(parents) + 1:
                parent_values = assignment[:-1]
                var_value = assignment[-1]

                # Create condition string
                conditions = []
                for pvar, pval in zip(parent_vars, parent_values):
                    conditions.append(f"{pvar.name}={pval}")
                condition_str = ", ".join(conditions)

                entries.append((condition_str, str(var_value), prob))

        return entries

    def generate_simple_graph(
        self, output_file: str = "network_simple", format: str = "pdf"
    ) -> str:
        """
        Generate a simple network visualization without CPT tables.

        This is a convenience method for quickly visualizing network structure.

        Args:
            output_file: Output filename (without extension)
            format: Output format ('pdf', 'png', 'svg', 'jpg')

        Returns:
            Path to generated file
        """
        return self.generate_graph(
            output_file=output_file, format=format, show_cpt=False, layout="dot"
        )


# Convenience function for quick visualization
def visualize_network(
    network: BayesianNetwork,
    output_file: str = "network",
    format: str = "pdf",
    show_cpt: bool = True,
) -> str:
    """
    Quick visualization function.

    Args:
        network: The BayesianNetwork to visualize
        output_file: Output filename (without extension)
        format: Output format
        show_cpt: Whether to show CPT tables

    Returns:
        Path to generated file
    """
    visualizer = NetworkVisualizer(network)
    return visualizer.generate_graph(output_file, format, show_cpt)
