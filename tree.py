#   Author: Josh Gillum              .
#   Date: 18 July 2025              ":"         __ __
#                                  __|___       \ V /
#                                .'      '.      | |
#                                |  O       \____/  |
#^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~
#
#    This is a general use tree class. It can handle arbitrary depths,
#    and can hold nodes of either strings or additional tree objects.
#    The tree works by building the tree from the deepest point up,
#    allowing it to figure out the size needed for shallower elements.
#
#    Also supports setting the display characters to either fancy or basic.
#    Basic display uses characters only found within 7 bit ASCII, while
#    fance uses other characters. If the tree's branches aren't displaying
#    correctly or are weird characters, try setting the fancy value to False.
#
#    Updates to the tree object will only affect this level. To update deeper
#    levels as well, the cascading_update line of functions must be used.
#    These will recursively update the deeper nodes, then the current nodes.
#
#
#^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~~^~

from .formatString import tabulate


class Tree:
    def __init__(
        self,
        name: str = None,
        nodes: list | None = None,
        fancy=False,
        wrap: int = None,
        width: int = None,
    ):
        """Class modelling a general purpose tree. All values specified here can later be updated
        with one of the set_x or cascading_update or cascading_set_x functions.

        Args:
            name (str, optional): The name of the tree. Printed at the current level before its child nodes. Defaults to None.
            nodes (list | dict | None, optional): The children nodes of the tree. Defaults to None.
            fancy (bool, optional): Whether fancy (7-bit ASCII) characters will be used. Defaults to False.
            wrap (int, optional): The max width of a single node when printed. Defaults to None.
            width (int, optional): The max width of the entire tree when printed. Defaults to None.
        """
        self.set_name(name)
        self.set_nodes(nodes)
        self.set_fancy(fancy)
        self.dirty = True
        if width is None:
            width = -1
        if wrap is None:
            wrap = -1
        self.set_term_size(width)
        self.set_line_wrap(wrap)

    def set_name(self, name: str):
        """Sets the name of the tree object

        Args:
            name (str): The new name of the tree
        """
        self.name = name
        self.dirty = True

    def set_nodes(self, nodes: list | dict | None):
        """Sets the nodes of the tree. Overwrites any previous nodes

        Args:
            nodes (list | dict | None): A list or dict of nodes for the tree
        """
        if not isinstance(nodes, list) and not isinstance(nodes,dict):
            nodes = [nodes]
        self.nodes = nodes
        self.dirty = True

    def add_node(self, node, key=None):
        if self.nodes is None:
            if key is None:
                self.nodes = [node]
                return self.nodes[-1]
            else:
                self.nodes = {key:node}
                return self.nodes[key]
        elif isinstance(self.nodes,dict):
            if key is not None:
                self.nodes |= {key:node}
                return self.nodes[key]
            else:
                return None
        elif isinstance(self.nodes,list):
            self.nodes.append(node)
            return self.nodes[-1]
        return None


    def __cascade(self,functions,args):
        if not isinstance(functions,list):
            functions = [functions]
        if not isinstance(args,list):
            args = [args]
        if not len(functions) == len(args):
            return

        if self.nodes is not None:
            items = self.nodes
            if isinstance(self.nodes,dict):
                items = self.nodes.values()

            if isinstance(items,list):
                for item in items:
                    if isinstance(item, Tree):
                        for i in range(len(functions)):
                            fun = getattr(item,functions[i])
                            fun(*(args[i]))


    def search(self,key):
        if isinstance(self.nodes,dict):
            try:
                return self.nodes[key]
            except KeyError:
                return None

        # List search does not work for some reason
        if isinstance(self.nodes,list):
            for item in self.nodes:
                if str(item.name).lower() == str(key).lower():
                    return item
        return None


    def set_fancy(self, set_fancy: bool, cascade=False):
        """Sets the fancy variable for this tree (whether non 7-bit ASCII characters will be used when printing)

        Args:
            set_fancy (bool): Whether to use fancy characters or not
        """
        self.fancy = set_fancy
        self.__set_characters()
        if cascade:
            self.__cascade("set_fancy",(set_fancy,cascade))


    def __set_characters(self):
        """Sets the characters to be used by the tree when printing. Should not be called
        from outside of the class. Only needed when self.fancy is changed.
        """
        if self.fancy:
            self.pipe = "│"
            self.branch = "├─"
            self.end = "└─"
            self.space = " "
            self.nameless = "┐"
        else:
            self.pipe = "|"
            self.branch = "|->"
            self.end = "|->"
            self.space = "  "
            self.nameless = "\\"
        self.split_line = "~"

    def set_term_size(self, width=80, cascade=False):
        """Sets the max width of the tree when printed

        Args:
            width (int, optional): The terminal size the tree will be printed on (max width of tree). Defaults to 80.
        """
        if width is not None:
            self.width = width
        if cascade:
            self.__cascade("set_term_size",(width,cascade))

    def set_line_wrap(self, line_width: int, cascade=False):
        """Sets the line_wrap variable

        Args:
            line_width (int): The max width of any single node in this tree
        """
        if line_width is not None:
            self.line_wrap = line_width
        if cascade:
            self.__cascade("set_line_wrap",(line_width,cascade))


    def update(
        self, set_fancy: bool = None, line_width: int = None, term_width: int = None, cascade=False
    ):
        """Updates the tree and optionally, all of its child Tree objects

        Args:
            set_fancy (bool, optional): Determines whether non 7-bit ASCII characters will be used when printing the tree. Defaults to None.
            line_width (int, optional): The max width of a single node when printed. Defaults to None.
            term_width (int, optional): The max width of the entire tree when printed. Defaults to None.
            cascade: Whether to cascade the update down the tree or not.
        """

        funs = []
        args = []
        if set_fancy is not None:
            self.set_fancy(set_fancy,cascade=False)
            funs.append("set_fancy")
            args.append((set_fancy,cascade))
        if line_width is not None:
            self.set_line_wrap(line_width,cascade=False)
            funs.append("set_line_wrap")
            args.append((line_width,cascade))
        if term_width is not None:
            self.set_term_size(term_width,cascade=False)
            funs.append("set_term_size")
            args.append((term_width,cascade))

        if cascade:
            self.__cascade(funs,args)


    def print(self, as_a_string=False, remove_root_branch=True) -> str | list:
        """Provides the tree in a printable form.

        Args:
            as_a_string (bool, optional): Will return a string instead of a list of lines if set to True. Defaults to False.
            remove_root_branch (bool, optional): Removes the preceeding root branch character if set to True. Defaults to True.

        Returns:
            (str|list): A string or a list. The list will contain the lines to be printed. There will not be
            a newline character at the end of each string. The string will contain newline characters indicating the
            end of each line. This is toggled with the `as_a_string` parameter.
        """
        # if self.dirty: # Doesn't regenerate tree if no changes have been made.
        # Sets entire tree as the single child node of tree. Necessary for proper spacing
        # Saves values so they can be restored after building tree
        name = self.name
        nodes = self.nodes
        child = Tree(
            name, nodes, fancy=self.fancy, wrap=self.line_wrap, width=self.width
        )
        self.name = None
        self.nodes = [child]
        # Gets the tree, as a list of lines
        self.list = self.__recursive_generation(last=True, root=True)
        # Converts the list to a single string
        self.string = ""
        for i in range(len(self.list)):
            if isinstance(self.list[i], str):
                if remove_root_branch:
                    self.list[i] = self.list[i][len(self.end) :]
                self.string += f"{self.list[i]}\n"
            else:
                del self.list[i]
        # Restores the original values of the name and nodes.
        self.name = name
        self.nodes = nodes
        self.dirty = False
        return self.string if as_a_string else self.list

    def __recursive_generation(self, last=False, prior_prefix=0, root=False):
        """Generates the lines of the tree for printing. This function is recursive and generates
        child trees as they are encountered. Should not be called from outside of the class. See Tree.print().

        Args:
            last (bool, optional): Indicates whether this Tree object is the last of its parent's nodes. Defaults to False.
            prior_prefix (int, optional): The length of the prefix before each node (Number of spaces or pipe characters from upstream branches). Defaults to 0.

        Returns:
            list: a list of lines representing the tree.
        """
        string = []
        # if str(self) != "":
        name = str(self)
        if (
            name or not root
        ):  # If the name exists or (it doesn't and this isn't the root node)
            if not name:  # Name is empty string
                name = self.nameless
            prefix = (
                self.end if last else self.branch
            )  # Determine if this is the last child of its parent, and sets branch character accordingly
            try:
                if (
                    self.line_wrap > 0
                ):  # If their is a max text width set, split into multiple lines
                    # Splits the text into a number of lines with max lengths of self.line_wrap
                    temp = tabulate(name, self.line_wrap, 0)
                    temp = temp.split(
                        "\n"
                    )  # Converts string of lines into a list of lines
                    for j in range(len(temp)):  # Loops through each line in the text
                        if (
                            temp[j].strip() != ""
                        ):  # Ensures that this is not a blank line
                            if j == 0:
                                string.append(
                                    f"{prefix}{temp[j]}"
                                )  # Adds branch character
                            else:  # Or character indicating that this is continuing from the previous line.
                                string.append(f"{self.split_line}{temp[j]}")
                else:  # No line-wrapping, so just add branch character and text
                    string.append(f"{prefix}{name}")
            except AttributeError:
                string.append(f"{prefix}{name}")
        if self.nodes is not None:  # This object has some children nodes
            keys = []
            if isinstance(self.nodes,list):
                keys = [x for x in range(len(self.nodes))]
            elif isinstance(self.nodes,dict):
                keys = self.nodes.keys()
            for i in keys:  # Loops through each node
                item = self.nodes[i]
                if isinstance(
                    item, Tree
                ):  # If the child node is another Tree object, generate that object.
                    child_last = (
                        i == len(self.nodes) - 1
                    )  # Boolean as to whether this is the last child of this node
                    prefix = (
                        self.end if last else self.branch
                    )  # Determines if this is the last child node of its parent, and sets branch character accordingly
                    # Generate the child node, indicating whether it is the last node.
                    child = item.__recursive_generation(
                        child_last, len(prefix) + prior_prefix
                    )
                    for j in range(
                        1, len(child)
                    ):  # Loops through all lines returned from child node
                        line = child[j]
                        # Set prefix according to whether this is the last child node or not
                        if i != len(self.nodes) - 1:
                            child[j] = self.pipe
                        else:
                            child[j] = self.space
                        if len(line) > 0 and line[0] != self.split_line:
                            child[j] += self.space
                        child[j] += (
                            line  # Add the lines from the inner tree back to the prefixes.
                        )
                    string += (
                        child  # Add the lines of the child to the lines of this tree
                    )
                else:
                    if item is not None:
                        item = str(item)
                        # If the node is just text, decide if this is the last child of its parent's tree
                        # Change the branch character if it is, otherwise use standard branch character.
                        prefix = self.end if (i == len(self.nodes) - 1) else self.branch
                        # Does the same process as with the name, determining if the text needs to be
                        # split across several lines, and doing so if needed.
                        try:
                            wrap = None  # The max length of each line that will be printed here.
                            if self.line_wrap is not None and self.line_wrap > 0:
                                wrap = self.line_wrap
                            if self.width is not None and self.width > 0:
                                # Determines the max width that the text can be. It is equal to the max width minus
                                # the length of the current prefix and the length of all of the prior prefixes
                                wrap = self.width - len(prefix) - prior_prefix
                            if wrap is not None:
                                temp = tabulate(item, wrap, 0)
                                temp = temp.split("\n")
                                for j in range(len(temp)):
                                    if temp[j].strip() != "":
                                        if j == 0:
                                            string.append(f"{prefix}{temp[j]}")
                                        else:
                                            # Determines which character to use for indicating that this is wrapping.
                                            # Typically will use a pipe to extend the node if needed, but if
                                            # it is the last node, will only use a space. Regardless, it also uses the
                                            # typical split line character.
                                            # Ex normal node:         Ex last node:
                                            # -> This is a test       -> This is a test
                                            # |~ of the line           ~ of the line
                                            # |~ wrapping function.    ~ wrapping function.
                                            if i == len(self.nodes) - 1:
                                                wrap_prefix = self.space
                                            else:
                                                wrap_prefix = self.pipe
                                            string.append(
                                                f"{wrap_prefix}{self.split_line}{temp[j]}"
                                            )
                            else:
                                string.append(f"{prefix}{item}")
                        except AttributeError:
                            string.append(f"{prefix}{item}")
        return string  # Return the lines of this tree level back to the parent

    def __str__(self):
        if self.name:
            return str(self.name)
        else:
            return ""
