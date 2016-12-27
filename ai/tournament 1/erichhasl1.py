# AI written for the first tournament.
# This AI won the tournament.

from itertools import product as pd, cycle as cl, islice as ic
import heapq
A = [(-1, 0), (0, 1), (1, 0), (0, -1)]
I = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
RA, SA = (0, 2), (1, 3)
ai = None


class B:
    def __init__(self, w, h, obs, own_color):
        self.width, self.height, self.obs = w, h, obs
        self.enemy, self.colors, self.own_color = (-1, -1), {}, own_color

    def ib(self, p):
        return all([0 <= x < b for x, b in zip(p, (self.width, self.height))])

    def ps(self, p):
        return p not in self.obs and self.ib(p)

    def bounds(self, r, c, i):
        t = [(r, c, 0 if a > 3 else 3 if a < 0 else a) for a in (i + 1, i - 1)]
        t.extend([(r + y, c + x, i) for y, x in (A[i],
                                                 rep_idx(A, i + 2))])
        return filter(lambda x: self.ps(x[:2]), t)

    def set_color(self, r, c, rot=None):
        self.obs = [x for x in self.obs if x not in self.enemy]
        res = list(filter(lambda x: self.ps(x),
                          [(r + y, c + x) for y, x in [A[i] for i in rot]]))
        res.append((r, c))
        self.obs.extend(res)
        self.enemy = res

    def speed(self, p):
        c = self.colors.get(p[:2], -1)
        return 1 if c != -1 and c != self.own_color else 2 if c == -1 else 10


class C:
    def __init__(self, pos, rot, a):
        self.pos, self.rot, self.aff, self.cns = pos, rot, a, cl(I)
        os = [p for p in pd(range(9), range(9)) if not any(a(*p)[::2])]
        self.team, self.en_p, self.en_a = a(*self.pos)[1], [], []
        self.gr, self.follows = B(9, 9, os, self.team), cl((4, 2))
        self.cur_corn, self.main = None, self.follow
        self.cur_spi, self.cur_idx = next(self.follows), 0

    def rotate(self, direction):
        self.rot += direction
        self.rot = 0 if self.rot >= 4 else 3 if self.rot <= -1 else self.rot
        return "rotate {0}".format(direction)

    def move(self, d):
        self.pos = tuple([p + d * r for p, r in zip(self.pos, A[self.rot])])
        return "move {0}".format(d)

    def set_pos(self, ts):
        self.pos, en, colors = self.invalidate()
        if len(self.en_p) == 0 or self.en_p[0] != en:
            self.en_p.insert(0, en)
            self.en_a.insert(0, 1)
            if len(self.en_p) > 1:
                i = A.index(tuple([(n - o) for n, o in zip(self.en_p[0],
                                                           self.en_p[1])]))
                self.en_rots = (i, rep_idx((0, 1, 2, 3), i + 2))
            else:
                self.en_rots = RA if ts % 2 == 0 else SA
        elif self.en_p[0] == en:
            self.en_rots = tuple([rep_idx((0, 1, 2, 3), i + 1) for i in
                                  self.en_rots])
            self.en_a.insert(0, 0)
        self.gr.set_color(*en, rot=self.en_rots)
        self.gr.colors = colors
        avg = sum(self.en_a[:min(len(self.en_a), 9)]) / min(len(self.en_a), 9)
        if not self.main == self.spiral and avg > 0.6:
            self.main = self.spiral
        elif not self.main == self.follow and avg < 0.5:
            self.main = self.follow
        return self.main()

    def follow(self):
        if self.cur_corn is None or\
                self.pos == self.cur_corn or not self.gr.ps(self.cur_corn):
            if self.cur_idx == 4:
                self.cur_idx, self.cur_spi = 0, next(self.follows)
            self.cur_corn = tuple(x * self.cur_spi + 4 for x in next(self.cns))
            self.cur_idx += 1

        return self.flee(self.cur_corn, op=True)

    def spiral(self):
        return self.flee((0, 0, True)
                         if len(self.en_p) < 3 else self.en_p[2])

    def flee(self, target, op=False):
        if self.pos == target or not self.gr.ps(target):
            return self.rotate(1)
        r, c, i = find_enemy(self.gr, self.pos + (self.rot,), target, op=op)
        d = 1 if tuple([t - s for t, s in zip((r, c), self.pos)]) ==\
            A[self.rot] else -1
        return self.move(d) if i == self.rot else self.rotate(1)\
            if i > self.rot or (i == 0 and self.rot == 3) else self.rotate(-1)

    def invalidate(self):
        c, en, s = {}, None, None
        for o in pd(range(9), range(9)):
            p, t, e = self.aff(*o)
            en, c[o] = o if e and t != self.team else en, t
            s = o if e and t == self.team else s
        return (s, en, {k: v for k, v in c.items() if v is not None})


def get_action(aff, turns, position=None, rotation=None):
    global ai
    try:
        if ai is None:
            ai = C(position, rotation, aff)
        return ai.set_pos(turns)
    except:
        return "rotate 1"


def rep_idx(iterable, idx):
    return next(ic(cl(iterable), idx, idx + 1))


def find_enemy(grid, goal, start, op=False):
    fr, tried, bl = [], {}, {}
    tried[goal], bl[goal] = goal, 0
    heapq.heappush(fr, (0, goal))
    while not len(fr) == 0:
        cur = heapq.heappop(fr)[1]
        if cur[:len(start)] == start:
            start = cur
            break
        for next in grid.bounds(*cur):
            new_speed = bl[cur] + (grid.speed(next) if op else 1)
            if next not in bl or new_speed < bl[next]:
                bl[next], tried[next] = new_speed, cur
                heapq.heappush(fr, (new_speed, next))
    first, x1 = start, [start]
    while first != goal:
        first = tried[first]
        x1.append(first)
    return x1[-2]
