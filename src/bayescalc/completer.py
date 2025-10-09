"""
This module implements the autocompletion logic for the REPL,
using the prompt_toolkit library.
"""

from prompt_toolkit.completion import Completer, Completion
from .network_model import BayesianNetwork
import re
import os


class PromptToolkitCompleter(Completer):
    def __init__(self, network: BayesianNetwork):
        self.network = network
        self.commands = [
            "P(",
            "printCPT(",
            "printJPT()",
            "parents(",
            "children(",
            "showGraph()",
            "isindependent(",
            "iscondindependent(",
            "entropy(",
            "conditional_entropy(",
            "mutual_information(",
            "marginals(",
            "condprobs(",
            "load(",
            "visualize(",
            "viz(",
            "help",
            "exit",
            "ls",
            "vars",
        ]

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        word_before_cursor = document.get_word_before_cursor(WORD=True)

        # Check if we're inside a probability query
        if "P(" in text_before_cursor:
            # Find the last opening P(
            p_idx = text_before_cursor.rfind("P(")
            text_inside_p = text_before_cursor[p_idx + 2 :]

            # Case 1: Completing a value after an '='
            match = re.search(r"(\w+)\s*=\s*([\w]*)$", text_inside_p)
            if match:
                var_name = match.group(1)
                val_prefix = match.group(2)
                if var_name in self.network.variables:
                    var = self.network.variables[var_name]
                    for val in var.domain:
                        if val.startswith(val_prefix):
                            yield Completion(val, start_position=-len(val_prefix))
                return

            # Case 2: Completing a variable name
            # Find the last token we're trying to complete
            # This could be after a comma, pipe, opening parenthesis, or tilde
            tokens = re.split(r"[,|()]", text_inside_p)
            last_token = tokens[-1].strip()

            # Handle negation prefix
            if last_token.startswith("~"):
                last_token = last_token[1:]
                prefix_len = len(last_token)
                negation_prefix = "~"
            else:
                prefix_len = len(last_token)
                negation_prefix = ""

            # Complete variables
            for var_name in self.network.variables:
                if var_name.startswith(last_token):
                    var = self.network.variables[var_name]
                    # For boolean variables, we don't need to add = (with shorthand syntax)
                    # For non-boolean, we must add = since there's no default value
                    add_equals = not var.is_boolean
                    completion_text = (
                        negation_prefix + var_name + ("=" if add_equals else "")
                    )
                    yield Completion(
                        completion_text,
                        start_position=-prefix_len - len(negation_prefix),
                    )

            return

        # Check if we're inside a command with parentheses (e.g., printCPT(Ma...)
        command_match = re.match(r"(\w+)\((.*?)$", text_before_cursor)
        if command_match:
            command_name = command_match.group(1)
            args_part = command_match.group(2)

            # Commands that take variable names as arguments
            variable_arg_commands = [
                "printCPT",
                "parents",
                "children",
                "entropy",
                "isindependent",
                "iscondindependent",
                "mutual_information",
                "conditional_entropy",
            ]

            if command_name in variable_arg_commands:
                # Find the current argument we're completing
                # Split by comma to handle multiple arguments
                args = [arg.strip() for arg in args_part.split(",")]
                current_arg = args[-1] if args else ""

                # Handle special cases for commands with "|" (conditional commands)
                if "|" in current_arg:
                    # For conditional commands, complete after the |
                    pipe_parts = current_arg.split("|")
                    if len(pipe_parts) > 1:
                        current_arg = pipe_parts[-1].strip()

                # Complete variable names
                for var_name in self.network.variables:
                    if var_name.startswith(current_arg):
                        yield Completion(var_name, start_position=-len(current_arg))
                return

            # File path completion for load command
            if command_name == "load":
                current_path = args_part.strip()

                # Remove quotes if present
                if current_path.startswith('"') or current_path.startswith("'"):
                    current_path = current_path[1:]

                # Expand user home directory
                current_path = os.path.expanduser(current_path)

                # Get directory and file prefix
                if current_path == "":
                    search_dir = "."
                    prefix = ""
                elif os.path.isdir(current_path):
                    search_dir = current_path
                    prefix = ""
                else:
                    search_dir = os.path.dirname(current_path) or "."
                    prefix = os.path.basename(current_path)

                # Find matching files and directories
                try:
                    if os.path.isdir(search_dir):
                        for entry in os.listdir(search_dir):
                            if entry.startswith(prefix) or prefix == "":
                                full_path = os.path.join(search_dir, entry)

                                # Only show .net files and directories
                                if os.path.isdir(full_path):
                                    completion_text = entry + "/"
                                    yield Completion(
                                        completion_text, start_position=-len(prefix)
                                    )
                                elif entry.endswith(".net"):
                                    yield Completion(entry, start_position=-len(prefix))
                except (OSError, PermissionError):
                    # Ignore errors accessing directories
                    pass
                return

            # File path completion for visualize command (suggest output filenames)
            if command_name in ["visualize", "viz"]:
                # Get first argument (current path being typed)
                args = [arg.strip() for arg in args_part.split(",")]

                if len(args) == 1:
                    # First argument: suggest output filenames with common formats
                    current_arg = args[0]

                    # Remove quotes if present
                    if current_arg.startswith('"') or current_arg.startswith("'"):
                        current_arg = current_arg[1:]

                    # Suggest common filenames if nothing typed yet
                    if not current_arg:
                        suggestions = [
                            "network.pdf",
                            "network.png",
                            "network.svg",
                            "network_simple.pdf",
                        ]
                        for suggestion in suggestions:
                            yield Completion(suggestion, start_position=0)
                    else:
                        # Complete existing filename
                        prefix = os.path.basename(current_arg)
                        search_dir = os.path.dirname(current_arg) or "."

                        # Suggest directories
                        try:
                            if os.path.isdir(search_dir):
                                for entry in os.listdir(search_dir):
                                    if entry.startswith(prefix) or prefix == "":
                                        full_path = os.path.join(search_dir, entry)
                                        if os.path.isdir(full_path):
                                            completion_text = entry + "/"
                                            yield Completion(
                                                completion_text,
                                                start_position=-len(prefix),
                                            )
                        except (OSError, PermissionError):
                            pass
                else:
                    # Subsequent arguments: suggest options
                    options = [
                        "format=pdf",
                        "format=png",
                        "format=svg",
                        "show_cpt=True",
                        "show_cpt=False",
                        "layout=dot",
                        "layout=neato",
                        "layout=fdp",
                        "layout=circo",
                        "rankdir=TB",
                        "rankdir=LR",
                        "scale=1.0",
                        "page_size=A3",
                        "page_size=A4",
                        "page_size=A5",
                        "page_size=297x210",
                    ]
                    current_arg = args[-1] if args else ""
                    for option in options:
                        if option.startswith(current_arg):
                            yield Completion(option, start_position=-len(current_arg))
                return

        # Command completion (when not inside a P() query or command arguments)
        for cmd in self.commands:
            if cmd.startswith(word_before_cursor):
                yield Completion(cmd, start_position=-len(word_before_cursor))
