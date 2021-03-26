import random
import pickle

class Session:

    def __init__(self, k):
        self.k = k # количество клеток

        #создает простейшее судоку поле
        self.field_answer = []
        for j in range(1, 10):
            self.field_answer.append([((i + 3 * (j - 1)) % 9 + (j - 1) // 3 + 1) if ((i + 3 * (j - 1)) % 9 + (
                        j - 1) // 3 + 1) < 10 else ((i + 3 * (j - 1)) % 9 + (j - 1) // 3 + 1) - 9 for i in range(9)])

        self.field_quest = self.field_answer

    # перемешивает начальное поле, (от перестановки слобцов и строк судоку остается правильным)
    def mash_field(self, n_mashes):

        for i in range(n_mashes):
            axis = random.randint(0, 1)

            # p1: то то
            p1 = random.randint(0, 8)
            p2 = random.randint(p1//3 * 3, p1//3 * 3 + 2)

            if axis == 0:
                for j in range(9):
                    b = self.field_answer[j][p1]
                    self.field_answer[j][p1] = self.field_answer[j][p2]
                    self.field_answer[j][p2] = b

            else:
                for j in range(9):
                    b = self.field_answer[p1][j]
                    self.field_answer[p1][j] = self.field_answer[p2][j]
                    self.field_answer[p2][j] = b

        self.field_quest = self.field_answer

    # красивый вывод на экран
    def draw_field(self):
        for i in self.field_quest:
            print('+---' * 9 + '+')
            print('| ', end= '')
            for j in i:
                print(j, end=' | ')
            print()
        print('+---' * 9 + '+')
        print()

    # из решенного судоку делает нерешенный оставляя k клеток заполненными
    def make_sudoku(self):
        a = set()

        while len(a) < self.k:
            a.add((random.randint(0,8), random.randint(0,8)))

        for i in range(9):
            for j in range(9):
                if (i, j) not in a:
                    self.field_quest[i][j] = ' '

    # заполняет выбранную нами ячейку
    def move(self, x, y, number):
        # добавить проверку на ход
        if self.field_quest[x][y] == ' ': self.field_quest[x][y] = number

    def save_game(self):
        with open('data.pickle', 'wb') as f:
            pickle.dump(self.field_quest, f)

    def load_game(self):
        with open('data.pickle', 'rb') as f:
            self.field_quest = pickle.load(f)

    # сессия сохраняет каждый ход
    def play(self):
        n_mashes = 10

        print('Load game? yes/no')
        to_load = input()
        if to_load == 'yes':
            self.load_game()
        elif to_load == 'no':
            self.mash_field(n_mashes)
            self.make_sudoku()

        while True:
            self.draw_field()
            x, y, number = map(int, input().split())
            self.move(x-1, y-1, number)

            self.save_game()




s1 = Session(30)
s1.play()

