from spy import Spy

class search_algorithms:

    def __init__(self):
        self.spy_list = []
        self.starting_quantities = Spy()
        self.current_board = self.get_current_board()
    
    def get_current_board(self):
        return self.starting_quantities.get_current_board()

    def linear_search(spy_list, name):
        for spy in spy_list:
            if spy.name == name:
                return spy
        return None

    def breadth_first_search(spy_list, name):
        queue = [spy_list[0]]
        while queue:
            spy = queue.pop(0)
            if spy.name == name:
                return spy
            for neighbor in spy.neighbors:
                queue.append(neighbor)
        return None

    def depth_first_search(spy_list, name):
        stack = [spy_list[0]]
        while stack:
            spy = stack.pop()
            if spy.name == name:
                return spy
            for neighbor in spy.neighbors:
                stack.append(neighbor)
        return None

    def best_first_search(spy_list, name):
        queue = [spy_list[0]]
        while queue:
            spy = queue.pop(0)
            if spy.name == name:
                return spy
            for neighbor in spy.neighbors:
                queue.append(neighbor)
        return None

    def a_star_search(spy_list, name):
        queue = [spy_list[0]]
        while queue:
            spy = queue.pop(0)
            if spy.name == name:
                return spy
            for neighbor in spy.neighbors:
                queue.append(neighbor)
        return None
    