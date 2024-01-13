# 파이썬 1팀 팀 프로젝트 - 지뢰찾기
# 팀장 김민상 (202311388)
# 팀원 김민우 (202311389)
# 팀원 윤태성 (202311424)

# tkinter 및 랜덤(랜덤 지뢰 위치) 기능 이용을 위해 모듈 불러옴
from tkinter import *
import random

# 루트 윈도우 (Tk 창) 생성
window0 = Tk()
window0.geometry("300x200")

def validate():
    try:
        size_x = int(entry_x.get())
        size_y = int(entry_y.get())
        mines = int(entry_mines.get())
        if size_x * size_y <= mines or size_x < 1  or size_y < 1 or mines < 1 :
            print("잘못된 값입니다. 다시 입력해주세요.")
        else:
            global SIZE_X, SIZE_Y, MINES
            SIZE_X = size_x
            SIZE_Y = size_y
            MINES = mines
            window0.destroy()  # 창을 완전히 닫습니다.
    except ValueError:
        print("잘못된 값입니다. 다시 입력해주세요.")

label_x = Label(window0, text="가로 길이: ")
label_x.pack()
entry_x = Entry(window0)
entry_x.pack()

label_y = Label(window0, text="세로 길이: ")
label_y.pack()
entry_y = Entry(window0)
entry_y.pack()

label_mines = Label(window0, text="지뢰 개수: ")
label_mines.pack()
entry_mines = Entry(window0)
entry_mines.pack()

submit_button = Button(window0, text="확인", command=validate)
submit_button.pack()

window0.mainloop()

# 루트 윈도우 (Tk 창) 생성
window = Tk()

# 게임 세팅 변수들 (네모칸 x길이, y길이, 지뢰 개수)
SIZE_X = SIZE_X
SIZE_Y = SIZE_Y
MINES = MINES

# 지뢰찾기 클래스
class Minesweeper:
    # 생성자 메소드 : 인스턴스 변수 생성
    def __init__(self):
        # 버튼(기본 상태 : [정사각형(가로2, 세로1), 배경 회색, '닫혀있음'(경계선 안쪽이 바깥보다 볼록한)])을 이차원 리스트 함축으로 형성
        # 지뢰 : 빈 리스트 (랜덤으로 채워질 예정)
        # 깃발 : 빈 리스트 (우클릭 하면 추가될 예정)
        # 게임오버 상태 : false(게임이 끝나지 않음)
        # 처음 클릭 여부 (첫 클릭은 지뢰가 무조건 없어야 함) : true(아직 클릭 안 함)
        # [0. 버튼 만드는 함수]호출 : 자동으로 게임판을 설정함
        self.buttons = [[Label(window, width = 2, height = 1, bg = 'gray', relief = 'raised') for n in range(SIZE_X)] for n in range(SIZE_Y)]
        self.mines = []
        self.flags = []
        self.gameover = False
        self.first_click = True
        self.create_button()

    # [0. 버튼 만드는 함수]
    def create_button(self):
        # 0-1. 이중 반복문 : X * Y 만큼의 네모 격자 버튼 생성
        for i in range(SIZE_Y):
            for j in range(SIZE_X):
                # 이차원 버튼 형성 (i + 2인 이유 : 1, 2행에 남은 지뢰 개수, 재시작 버튼을 만들기 위함)
                # 버튼을 마우스 좌클릭시 : 람다식을 통해 해당 버튼 좌표를 매개변수로 해서 [2. 좌클릭 함수]로 이동함 (칸 열기)
                # 버튼을 마우스 우클릭시 : [3. 우클릭 함수]로 이동함 (깃발 꽂기)
                # 버튼을 마우스 더블 클릭시 : [4. 더블 클릭 함수]로 이동함 (깃발 제외 주변 칸 열기)
                self.buttons[i][j].grid(row=i+2, column=j)
                self.buttons[i][j].bind('<Button-1>', lambda event, i=i, j=j: self.click(i, j))
                self.buttons[i][j].bind('<Button-3>', lambda event, i=i, j=j: self.flag(i, j))
                self.buttons[i][j].bind('<Double-Button-1>', lambda e, i=i, j=j: self.double_click(i, j))

        # 0-2. 남은 지뢰 개수 상태 출력
        self.status = Label(window, text=f"Mines: {MINES}", bg='white')     # f-문자열 사용
        self.status.grid(row=0, column=0, columnspan=SIZE_X)                # 상태창의 할당 크기를 x 크기와 동일하게 설정하여 글씨가 가운데 정렬처럼 보이게 함

        # 0-3. 재시작 버튼 출력
        self.restart = Button(window, text="Restart", command=self.reset)   # 누르면 0-3. reset 함수 호출
        self.restart.grid(row=1, column=0, columnspan=SIZE_X)               # 가운데 정렬처럼 보이게 설정

    # [0-3. 재시작 함수]
    def reset(self):
        # 모든 세팅을 시작 전으로 초기화시킴
        self.mines = []
        self.flags = []
        self.gameover = False
        self.first_click = True
        self.status.config(text=f"Mines: {MINES}")
        # 격자 칸도 클릭 전 상태로 초기화
        for i in range(SIZE_Y):
            for j in range(SIZE_X):
                self.buttons[i][j].config(text="", bg='gray', relief='raised')

    # [1. 랜덤 지뢰 배정] : 첫 클릭 위치엔 무조건 지뢰가 없도록 배치
    def place_mines(self, i, j):
        # [2. 마우스 좌클릭 함수]의 first_click에서 넘어온 (i, j) 좌표를 제외한 나머지를 cells에 저장함
        cells = []
        for x in range(SIZE_Y):
            for y in range(SIZE_X):
                if (x, y) != (i, j):
                    cells.append((x, y))
        # cells 리스트 안에 있는 좌표 중 MINES 개수 만큼 랜덤으로 선택해 mines 리스트에 저장 (지뢰 좌표 선택)
        self.mines = random.sample(cells, MINES)

    # [2. 마우스 좌클릭 함수] (칸 열기)
    def click(self, i, j):
        # 게임오버 검사 : 맞으면 클릭 안 먹힘
        if self.gameover :
            return

        # first_click이 True라면 (아직 첫 클릭을 하지 않은 상태에서 클릭을 했다면)
        if self.first_click:
            # [1. 랜덤 지뢰 배정 함수]에 처음 클릭한 좌표를 매개변수로 넘겨주고, first_click 상태를 false로 변경
            self.place_mines(i, j)
            self.first_click = False

        # 좌클릭한 좌표에 깃발이 꽂혀있지 않고, 좌클릭한 좌표의 상태가 ['열려있음(테두리보다 오목하게 들어간 상태)']이 아니라면
        if (i, j) not in self.flags and self.buttons[i][j]['relief'] != 'sunken':

            # 2-1. 좌클릭한 좌표가 지뢰가 있는 위치라면 (게임오버)
            if (i, j) in self.mines:
                # 좌클릭한 좌표의 상태를 [텍스트 "M" 표시, '열려있음', 배경 빨간색]으로 변경하고, 상태창 글씨를 게임 오버로 변경 & 게임오버 상태를 true로 변경하고, [7. 지뢰 표시 함수]호출
                self.buttons[i][j].config(text="M", relief='sunken', bg='red', fg = "black")
                self.status.config(text="Game Over")
                self.gameover = True
                self.reveal_mines()

            # 2-2. 좌클릭한 좌표가 지뢰가 있는 위치가 아니라면
            else:
                # 좌클릭한 좌표 기준 주위 8칸(자기 자신 포함해서 9칸을 검사하지만, 자기 자신은 지뢰가 없으므로)이 지뢰 리스트에 포함되어 있는지 검사, 있다면 count + 1
                count = 0
                for mine_y in range(i - 1, i + 2):
                    for mine_x in range(j - 1, j + 2):
                        if (mine_y, mine_x) in self.mines:
                            count += 1

                # 2-2-1. 카운트 결과 주변 지뢰가 없다면
                if count == 0:
                    # 좌클릭한 좌표 버튼의 상태를 [텍스트 없음, '열려있는(테두리보다 오목)', 배경 흰색]으로 설정후, [2-3. 인접한 8칸을 전부 여는 함수] 호출
                    self.buttons[i][j].config(text=" ", relief='sunken', bg='white')
                    self.open_adjacent(i, j)

                # 2-2-2 카운트 결과 주변 지뢰가 1개라도 있다면
                else:
                    # 클릭한 좌표의 상태를 [텍스트 "지뢰 수", 열린 상태, 배경 흰색, 텍스트 색상 "[6. 색상 반환 함수]반환값"]으로 설정
                    self.buttons[i][j].config(text=str(count), relief='sunken', bg='white', fg=self.number_colors(count))

                # 승리 조건을 만족했다면 게임오버(실패가 아닌 성공의 의미)
                if self.check_win():
                    self.status.config(text="You Win!")     # 상태창 글씨 "성공"
                    self.gameover = True                    # 게임오버 상태 : true

    # [2-3. 인접한 8칸을 전부 여는 함수]
    def open_adjacent(self, i, j):
        # 이중 반복문을 돌려 주변 8칸을 전부 염(2. 마우스 좌클릭 함수 재호출)
        for x in range(max(i-1, 0), min(i+2, SIZE_Y)):
            for y in range(max(j-1, 0), min(j+2, SIZE_X)):
                if self.buttons[x][y]['relief'] != 'sunken':
                    self.click(x, y)

    # [3. 마우스 우클릭 함수] (깃발 꽂기)
    def flag(self, i, j):
        # 게임오버 검사 : 맞으면 클릭 안 먹힘
        if self.gameover:
            return

        # 우클릭한 좌표의 상태가 '열려있음'이 아니라면
        if self.buttons[i][j]['relief'] != 'sunken':

            # 3-1. 깃발 리스트에 우클릭한 좌표가 없고, 깃발 개수가 지뢰 개수보다 작다면 (기본 -> 깃발)
            if (i, j) not in self.flags and len(self.flags) < MINES:
                # 우클릭한 좌표 상태를 [텍스트 "F", 배경 오렌지색]으로 변경하고, 깃발 리스트에 좌표 등록하고, 지뢰 개수를 리스트의 길이로 설정 (-1)
                self.buttons[i][j].config(text="F", bg='orange', fg = "black")
                self.flags.append((i, j))
                self.status.config(text=f"Mines: {MINES - len(self.flags)}")

            # 3-2. 깃발 리스트에 우클릭한 좌표가 있다면 (깃발 -> 기본)
            elif (i, j) in self.flags:
                # 우클릭한 좌표 상태를 [텍스트 "빈칸", 배경 회색]으로 변경하고, 깃발 리스트에 있는 좌표를 삭제하고, 지뢰 개수를 리스트의 길이로 설정 (+1)
                self.buttons[i][j].config(text="", bg='gray')
                self.flags.remove((i, j))
                self.status.config(text=f"Mines: {MINES - len(self.flags)}")

    # [4. 마우스 더블클릭 함수] (깃발 제외 칸 열기)
    def double_click(self, i, j):
        # 게임오버 검사 : 맞으면 클릭 안 먹힘
        if self.gameover:
            return

        # 버튼이 '열려있음' 상태라면
        if self.buttons[i][j]['relief'] == 'sunken':
            # 주변 8칸의 지뢰 개수를 카운트
            count = 0
            for x in range(i - 1, i + 2):
                for y in range(j - 1, j + 2):
                    if (x, y) in self.mines:
                        count += 1

            # 주변 8칸의 깃발 개수를 카운트
            flag_count = 0
            for x in range(i - 1, i + 2):
                for y in range(j - 1, j + 2):
                    if (x, y) in self.flags:
                        flag_count += 1

            # 깃발 개수와 주변 8칸의 지뢰 개수가 동일하다면 [2-3. 인접한 8칸을 전부 여는 함수]호출 (좌표가 동일한지는 상관없이 개수만 체크)
            if count == flag_count:
                self.open_adjacent(i, j)

    # [5. 승리조건 검사 함수]
    def check_win(self):
        # 모든 좌표를 검사해서 하나라도 '닫혀있음' 상태인 좌표가 있다면 false, 모두 '열려있음' 상태라면 true 반환
        for i in range(SIZE_Y):
            for j in range(SIZE_X):
                if (i, j) not in self.mines and self.buttons[i][j]['relief'] != 'sunken':
                    return False
        return True

    # [6. 색상 반환 함수]
    def number_colors(self, count):
        # 주변 8칸 지뢰 개수에 따른 색상을 다르게 반환
        if count == 1:
            return 'blue'
        elif count == 2:
            return 'green'
        elif count == 3:
            return 'red'
        elif count == 4:
            return 'purple'
        elif count == 5:
            return 'maroon'
        elif count == 6:
            return 'turquoise'
        elif count == 7:
            return 'black'
        else:
            return 'gray'

    # [7. 지뢰 표시 함수]
    def reveal_mines(self):
        for mine in self.mines:
            # 지뢰 좌표를 (i,j) 분배
            # 지뢰 위치에 깃발이 꽂혀있다면 [텍스트 "M", 배경 오렌지색] 변경
            # 깃발이 없다면 [텍스트 "M", 배경 빨간색] 변경
            i, j = mine
            if (i, j) in self.flags:
                self.buttons[i][j].config(text="M", bg='orange', fg = "black")
            else:
                self.buttons[i][j].config(text="M", relief='sunken', bg='red', fg = "black")

Minesweeper()
window.mainloop()
