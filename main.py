import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os


class TopDownParser:
    def __init__(self, grammar):
        """Initializes the parser with the provided grammar."""
        self.original_grammar = {nt: rules[:] for nt, rules in grammar.items()}
        self.grammar = grammar
        self.start_symbol = list(grammar.keys())[0]
        self.parse_tree = None

    def display_grammar(self):
        """Displays the original and current grammar rules."""
        print("\n" + "-" * 100)
        print("\t\tCurrent Grammar Rules ")
        print("_" * 100 + "\n")
        rule_id = 1
        for nt, rules in self.grammar.items():
            for rule in rules:
                print(f"\t {rule_id}. {nt} -> {rule}")
                rule_id += 1
        print("_" * 50)

    def parse_string(self, input_string):
        """Performs recursive descent parsing."""
        try:
            self.parse_tree = None
            stack = [(self.start_symbol, [])]
            input_list = list(input_string)
            print(f"The input String: {input_list}")
            # print(f"The rest of unchecked string: {[]}")
            while stack:
                top, children = stack.pop()
                if not input_list:
                    break

                if top in self.grammar:
                    matched_rule = next(
                        (
                            rule
                            for rule in self.grammar[top]
                            if rule[0] == input_list[0]
                        ),
                        None,
                    )
                    if matched_rule:
                        current_node = (top, [])
                        if not self.parse_tree:
                            self.parse_tree = current_node
                        else:
                            children.append(current_node)
                        for symbol in reversed(matched_rule):
                            stack.append((symbol, current_node[1]))
                    else:
                        print(f"Rule not found for {top} -> {input_list[0]}❌.")
                        return False, stack, input_list

                else:
                    if top == input_list[0]:
                        input_list.pop(0)
                    else:
                        return False, stack, input_list
            print(f"Stack after checking: {input_list}")
            print(f"The rest of unchecked string: {stack}")
            return not stack and not input_list, stack, input_list
        except Exception as e:
            print(f"Error during parsing: {e}")
            return False, [], input_string

    def visualize_tree(self, title="Parse Tree"):
        """Visualizes the parse tree."""
        try:
            if self.parse_tree:
                plot_tree(self.parse_tree, title)
            else:
                print("No parse tree to display❌.")
        except Exception as e:
            print(f"Error visualizing tree❌: {e}")

    @classmethod
    def from_user_input(cls):
        """Collects grammar rules from user input."""
        print("\n" + "=" * 150)
        print("\t\t\t\t\t\t\tTop-Down Parser Setup 🆓")
        print("=" * 150 + "\n")
        try:
            grammar = {}
            grammar_input = input(
                "=> Enter non-terminals and their rule count (e.g., S,2 & B,2): "
            ).strip()
            grammar_definitions = grammar_input.split("&")
            for grammar_item in grammar_definitions:
                non_terminal, num_rules = grammar_item.split(",")
                non_terminal = non_terminal.strip()
                num_rules = int(num_rules.strip())
                grammar[non_terminal] = []
                for i in range(num_rules):
                    rule = input(
                        f"\t - Enter rule {i + 1} for '{non_terminal}': "
                    ).strip()
                    grammar[non_terminal].append(rule)

            print("-" * 100 + "\n\t\tGrammar Successfully Added!✅ \n " + "_" * 100)
            for idx, (nt, rules) in enumerate(grammar.items(), start=1):
                print(f" {idx}. {nt} -> {', '.join(rules)}")
            return cls(grammar)
        except Exception as e:
            print(f"Error gathering grammar❌: {e}")
            return None

    def edit_rules(self):
        """Allows editing of grammar rules."""
        try:
            while True:
                self.display_grammar()
                choice = input(
                    "\n\t- If you need to Edit? \n\t \t=>Enter rule-ID to edit, or 'no' to finish: "
                ).strip()

                if choice.lower() in ["no", "done", ""]:
                    break

                if choice.isdigit():
                    rule_id = int(choice)
                    current_id = 1
                    for nt, rules in self.grammar.items():
                        for idx, rule in enumerate(rules):
                            if current_id == rule_id:
                                print(f"Editing Rule: {nt} -> {rule}")
                                new_rule = input("Enter new rule: ").strip()
                                if new_rule:
                                    self.grammar[nt][idx] = new_rule
                                    print(f"Updated Rule: {nt} -> {new_rule}")
                                else:
                                    print("No changes made.")
                                print("\n")
                                return
                            current_id += 1
                    print("Invalid rule ID❌.")
                else:
                    print("Invalid input❌. Try again.")
        except Exception as e:
            print(f"Error editing rules❌: {e}")


def draw_parser_tree(tree, x=0, y=0, x_offset=0.4, level=0, ax=None, max_level=3):
    """Draw the parser tree progressively up to a maximum depth (max_level)."""
    if level > max_level:
        return

    # Display the current node
    ax.text(
        x,
        y + 0.5,
        tree[0],
        ha="center",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.1", facecolor="lightyellow", edgecolor="gray"),
    )

    if len(tree) > 1:
        children = tree[1]
        for i, child in enumerate(children):
            child_x = x + (i - (len(children) - 1) / 2) * x_offset
            child_y = y - 0.4
            ax.plot(
                [x, child_x], [y + 0.5 - 0.05, child_y + 0.5 + 0.05], color="gray", lw=1
            )
            draw_parser_tree(
                child,
                child_x,
                child_y,
                x_offset / 1.5,
                level + 1,
                ax=ax,
                max_level=max_level,
            )


def plot_tree(tree, title):
    fig = plt.figure(figsize=(8, 5))
    gs = fig.add_gridspec(2, 1, height_ratios=[0.1, 0.9])

    ax_title = fig.add_subplot(gs[0])
    ax_title.text(
        0.5, 0.5, title, ha="center", fontsize=20, fontweight="bold", color="navy"
    )
    ax_title.axis("off")

    ax_tree = fig.add_subplot(gs[1])
    ax_tree.set_xlim(-1, 1)
    ax_tree.set_ylim(-1, 1)
    ax_tree.axis("off")

    def update(frame):
        ax_tree.clear()
        ax_tree.axis("off")

        zoom_factor = 1 + (frame / 10)
        ax_tree.set_xlim(-zoom_factor, zoom_factor)
        ax_tree.set_ylim(-zoom_factor, zoom_factor)

        draw_parser_tree(tree, ax=ax_tree, max_level=frame)

    # Create an animated plot
    ani = animation.FuncAnimation(
        fig,
        update,
        frames=np.arange(0, 10),
        repeat=True,
        interval=500,  # 500ms delay between frames ==>.5s
    )

    # Save animation as a GIF
    # check if image name is already present, if yes then change the name
    if "tree.gif" in os.listdir():
        i = 1
        ani.save(f"tree{i}.gif", writer="pillow", fps=1)
        i += 1
    else:
        ani.save("tree.gif", writer="pillow", fps=1)
    print("\n The parse tree is saved as 'tree.gif' in the current directory.✅")
    plt.tight_layout()
    plt.show()


def main():
    try:
        while True:
            parser = TopDownParser.from_user_input()
            if not parser:
                print("Error creating parser.❌\n Exiting.......❌")
                return

            parser.edit_rules()

            while True:
                parser.display_grammar()
                input_string = input("\n\tEnter a string to parse: ").strip()
                print("\n" + "_" * 50)
                is_valid, _, _ = parser.parse_string(input_string)
                print("\n" + "-" * 40)
                if is_valid:
                    print(f"\t The string '{input_string}' is ACCEPTED.✅✅✅")
                    print("-" * 40)
                    parser.visualize_tree(title="Top-Down Parsing Tree")
                else:
                    print(f"\t\tThe string '{input_string}' is REJECTED.❌❌❌")
                    print("-" * 40)

                print(
                    "\n"
                    + "_" * 50
                    + "\n\tOptions:"
                    + "\n\t    1- Enter Another Grammar🔁\n\t    2- Enter Another String🔁\n\t    3- Exit🚫",
                )
                choice = input("\tPlease,Enter your choice🤔: ").strip()
                if choice == "1":
                    break
                elif choice == "2":
                    continue
                elif choice == "3":
                    print("\n" + "=" * 140)
                    print(
                        "\n\t\t\t👋👋Thank you for using the Top-Down Parser. Goodbye!👋👋"
                    )
                    print("\n" + "=" * 140, "\n\n")
                    return
                else:
                    print("Invalid choice. Please try again. ❌")
    except Exception as e:
        print(f"Error in main function❌: {e} ")


if __name__ == "__main__":
    main()
