
class Node:
    def __init__(self, coord, to_list) -> None:

        self.to_list = to_list
        self.__id = coord
        self.value = 0
        self.changed = False

    def get_id(self):
        return self.__id

    def get_value(self):
        return self.value

    def get_to_list(self):
        return self.to_list

    def set_value(self, value):
        if self.changed:
            if self.get_value() > value:
                self.value = value
        else:
            self.value = value
        self.changed = True

    def add_to_node(self, node):
        self.to_list.append(node)

    def not_changed(self):
        self.changed = False

    def update_depth(self, depth):
        self.set_value(depth)

        for node in self.get_to_list():
            if not node.changed:
                node.update_depth(depth + 1)
            else:
                if node.get_value() > depth + 1:
                    node.update_depth(depth + 1)
