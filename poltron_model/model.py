from random import sample, shuffle


def get_circle_cases(r: int, x0: int, y0: int) -> set:
    cases: set = set()
    # using manhattan distance
    for x in range(0, r + 1, 1):
        cases.add((x + x0, r - x + y0))
        cases.add((-x + x0, -(r - x) + y0))
        cases.add((x + x0, -(r - x) + y0))
        cases.add((-x + x0, r - x + y0))

    return cases


def get_radius_cases(r_max: int, x0: int, y0: int) -> set:
    cases: set = set()
    for r in range(1, r_max + 1, 1):
        cases = cases.union(cases, get_circle_cases(r, x0, y0))
    return cases


class Model:

    def __init__(self, m: int, n: int, c: int, ds: int, dc: int):
        self.m: int = 0
        self.n: int = 0
        self.c: int = 0
        self.ds: int = 0
        self.dc: int = 0
        self.walls: set = set()
        self.balls_pos: set = set()
        self.balls_to_pos: dict = {}
        self.pos_to_balls: dict = {}
        self.balls_order: list = []
        self.tick: int = 0
        self.victory: bool = False
        self.deaths: list = []
        self.initial_positions: list = []
        self.initial_order: list = []
        self.important_moments: list = []
        self.m = m
        self.n = n
        self.c = c
        self.dc = dc
        self.ds = ds
        self.balls_order = [x for x in range(c + 1)]
        shuffle(self.balls_order)
        rand_pos = sample([(x % m, x // m) for x in range(m * n)], c + 1)

        for ball in range(c + 1):
            self.balls_to_pos[ball] = rand_pos[ball]
            self.pos_to_balls[rand_pos[ball]] = ball
            self.balls_pos.add(rand_pos[ball])
            self.walls.add(rand_pos[ball])
            self.initial_positions.append(
                (ball, rand_pos[ball][0], rand_pos[ball][1]))
            self.initial_order.append(
                (ball, self.balls_order[ball]))  # self.display()

    def c_death(self) -> int:
        if not self.victory:
            return self.c - len(self.balls_order)
        return self.c - len(self.balls_order) - 1

    def nb_walls(self) -> int:
        return len(self.walls)

    def calculate_depth(self, x: int, y: int, r: int) -> int:
        return len(self.get_visible_cases(x, y, r))

    def calculate_distance_to_solo(self, x: int, y: int) -> float:
        x_s, y_s = self.balls_to_pos[0]
        return ((x_s - x) ** 2 + (y_s - y) ** 2) ** 0.5

    def get_visible_cases(self, x: int, y: int, r: int) -> set:
        cases = set()
        if (x, y) in self.walls or x >= self.m or x < 0 or y >= self.n or y < 0:
            return cases
        # check axis
        cases.add((x, y))
        for x_c in range(x + 1, x + r + 1):
            if (x_c, y) in self.walls or x_c >= self.m:
                break
            cases.add((x_c, y))
        for x_c in range(x - 1, x - r - 1, -1):
            if (x_c, y) in self.walls or x_c < 0:
                break
            cases.add((x_c, y))

        for y_c in range(y + 1, y + r + 1):
            if (x, y_c) in self.walls or y_c >= self.n:
                break
            cases.add((x, y_c))
        for y_c in range(y - 1, y - r - 1, -1):
            if (x, y_c) in self.walls or y_c < 0:
                break
            cases.add((x, y_c))
        # check intermediairies
        cases = cases.union(cases,
                            self.propagate_case_search(x + 1, y + 1, 1, 1,
                                                       r - 1))
        cases = cases.union(cases,
                            self.propagate_case_search(x - 1, y + 1, -1, 1,
                                                       r - 1))
        cases = cases.union(cases,
                            self.propagate_case_search(x + 1, y - 1, 1, -1,
                                                       r - 1))
        cases = cases.union(cases,
                            self.propagate_case_search(x - 1, y - 1, -1, -1,
                                                       r - 1))
        return cases

    def propagate_case_search(self, x: int, y: int, dx: int, dy: int,
                              r: int) -> set:
        cases: set = set()
        if (x, y) in self.walls or x >= self.m or x < 0 or y >= self.n or y < 0:
            return cases
        cases.add((x, y))
        if r != 0:
            cases = cases.union(cases,
                                self.propagate_case_search(x + dx, y, dx, dy,
                                                           r - 1))
            cases = cases.union(cases,
                                self.propagate_case_search(x, y + dy, dx, dy,
                                                           r - 1))
        return cases

    def has_ended(self) -> bool:
        return self.victory or len(self.balls_order) <= 1

    def destroy_ball(self, ball: int) -> None:
        self.pos_to_balls[self.balls_to_pos[ball]] = None
        self.balls_pos.remove(self.balls_to_pos[ball])
        self.balls_to_pos[ball] = None

    def display(self) -> None:
        for x in range(self.m):
            for y in range(self.n):
                if (x, y) in self.balls_pos:
                    if self.pos_to_balls[(x, y)] == 0:
                        print('S', end='')
                    else:
                        print('C', end='')
                elif (x, y) in self.walls:
                    print('w', end='')
                else:
                    print('.', end='')
            print(' ')
        print('==========')

    def move_ball(self, ball: int, old_x: int, old_y: int, new_x: int,
                  new_y: int) -> None:
        self.pos_to_balls[(old_x, old_y)] = None
        self.balls_pos.remove((old_x, old_y))

        self.balls_to_pos[ball] = (new_x, new_y)
        self.pos_to_balls[(new_x, new_y)] = ball
        self.balls_pos.add(self.balls_to_pos[ball])
        self.walls.add(self.balls_to_pos[ball])

    def next_tick(self) -> None:
        self.tick += 1
        new_order: list = []
        important: bool = False
        current_deaths: list = []
        for ball in self.balls_order:
            if self.has_ended():
                break
            x, y = self.balls_to_pos[ball]
            if ball == 0:
                r = self.ds
            else:
                r = self.dc
            right = self.calculate_depth(x + 1, y, r)
            left = self.calculate_depth(x - 1, y, r)
            down = self.calculate_depth(x, y - 1, r)
            up = self.calculate_depth(x, y + 1, r)
            max_depth = max(right, left, up, down)
            if max_depth == 0:
                important = True
                self.destroy_ball(ball)
                if ball == 0:
                    self.victory = True
                current_deaths.append(ball)
            else:
                new_order.append(ball)

                if ball != 0:
                    # attractive force to the solo player
                    right += (1 / (
                                1 + self.calculate_distance_to_solo(x + 1, y)))
                    left += (1 / (
                                1 + self.calculate_distance_to_solo(x - 1, y)))
                    down += (1 / (
                                1 + self.calculate_distance_to_solo(x, y - 1)))
                    up += (1 / (1 + self.calculate_distance_to_solo(x, y + 1)))

                max_interest = max(right, left, up, down)

                if max_interest == right:
                    self.move_ball(ball, x, y, x + 1, y)
                elif max_interest == left:
                    self.move_ball(ball, x, y, x - 1, y)
                elif max_interest == down:
                    self.move_ball(ball, x, y, x, y - 1)
                else:
                    self.move_ball(ball, x, y, x, y + 1)
        if important:
            self.important_moments.append(
                (self.tick, self.nb_walls(), self.c_death()))
        if len(current_deaths) > 0:
            self.deaths.append((self.tick, current_deaths))
        self.balls_order = new_order  # self.display()

    def run(self) -> None:
        while not self.has_ended():
            self.next_tick()

    def __str__(self) -> str:
        elements: list = []
        for x in range(self.m):
            for y in range(self.n):
                if (x, y) in self.balls_pos:
                    if self.pos_to_balls[(x, y)] == 0:
                        elements.append('S')
                    else:
                        elements.append('C')
                elif (x, y) in self.walls:
                    elements.append('w')
                else:
                    elements.append('.')
        return "".join(elements)
