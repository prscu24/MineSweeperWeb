import pygame
import random

# Pygame 초기화
pygame.init()

# 게임 설정
GRID_SIZE = 20  # 격자 크기 (15x15)
CELL_SIZE = 40  # 각 셀 크기 (px)
MINES_COUNT = 30  # 지뢰 개수 증가 (난이도 조정)

WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE + 40  # 인디케이터 공간 추가
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

# 색상 정의
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)  # 안전한 경우 (지뢰 없음)
BLUE = (0, 0, 255)  # 깃발 표시
YELLOW = (255, 255, 100)  # 미리보기 색상
ORANGE = (255, 165, 0)  # 지뢰가 있을 때 강조

# 폰트 설정
FONT = pygame.font.Font(None, 30)

# 전역 변수 선언
preview_cells = set()
highlight_cells = set()
current_preview_target = None
shift_pressed = False
mouse_held = False
game_over = False
game_won = False
safe_click = False  # 안전한 클릭인지 체크
# flags는 2차원 리스트 (True/False)로 관리
flags = []  

# 보드 초기화 함수
def reset_game():
    global board, revealed, flags, game_over, game_won, preview_cells, current_preview_target, highlight_cells, safe_click
    board = create_board()
    revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    flags = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    game_over = False
    game_won = False
    preview_cells.clear()
    highlight_cells.clear()
    current_preview_target = None
    safe_click = False

# 보드 생성
def create_board():
    board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    mines = set()
    
    while len(mines) < MINES_COUNT:
        x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        if (x, y) not in mines:
            mines.add((x, y))
            board[y][x] = -1  # 지뢰 배치
    
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if board[y][x] == -1:
                continue
            count = sum((board[ny][nx] == -1) for ny in range(max(0, y-1), min(GRID_SIZE, y+2))
                        for nx in range(max(0, x-1), min(GRID_SIZE, x+2)))
            board[y][x] = count
    
    return board

# 게임 초기화
reset_game()

# 빈 칸을 클릭하면 주변 빈 칸도 자동으로 열림
def reveal_empty_cells(x, y):
    queue = [(x, y)]
    while queue:
        cx, cy = queue.pop(0)
        for ny in range(max(0, cy-1), min(GRID_SIZE, cy+2)):
            for nx in range(max(0, cx-1), min(GRID_SIZE, cx+2)):
                if not revealed[ny][nx] and board[ny][nx] != -1 and not flags[ny][nx]:
                    revealed[ny][nx] = True
                    if board[ny][nx] == 0:
                        queue.append((nx, ny))

# 시프트 클릭 시 미리보기 강조
def highlight_preview_cells(x, y):
    global highlight_cells, safe_click
    highlight_cells.clear()
    mine_count = sum(board[ny][nx] == -1 for ny in range(max(0, y-1), min(GRID_SIZE, y+2))
                     for nx in range(max(0, x-1), min(GRID_SIZE, x+2)))

    safe_click = mine_count == 0

    for ny in range(max(0, y-1), min(GRID_SIZE, y+2)):
        for nx in range(max(0, x-1), min(GRID_SIZE, x+2)):
            if not revealed[ny][nx]:
                highlight_cells.add((nx, ny))

# Shift + 클릭 시 9칸 오픈
def shift_click_open(x, y):
    for ny in range(max(0, y-1), min(GRID_SIZE, y+2)):
        for nx in range(max(0, x-1), min(GRID_SIZE, x+2)):
            if not revealed[ny][nx] and board[ny][nx] != -1 and not flags[ny][nx]:
                revealed[ny][nx] = True
                if board[ny][nx] == 0:
                    reveal_empty_cells(nx, ny)

# 게임 상태 확인
def check_game_status():
    global game_won
    if game_over:
        return
    remaining_cells = sum(1 for y in range(GRID_SIZE) for x in range(GRID_SIZE) if not revealed[y][x])
    if remaining_cells == MINES_COUNT:
        game_won = True

# 보드 그리기
def draw_board():
    SCREEN.fill(WHITE)
    
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            # 게임 오버 시, 모든 지뢰(숨겨진 지뢰 포함)를 표시합니다.
            if game_over and board[y][x] == -1:
                pygame.draw.rect(SCREEN, GRAY, rect)
                pygame.draw.circle(SCREEN, RED, rect.center, CELL_SIZE // 3)
            else:
                if (x, y) in highlight_cells:
                    pygame.draw.rect(SCREEN, GREEN if safe_click else ORANGE, rect)
                elif (x, y) in preview_cells:
                    pygame.draw.rect(SCREEN, YELLOW, rect)
                elif revealed[y][x]:
                    pygame.draw.rect(SCREEN, GRAY, rect)
                    if board[y][x] > 0:
                        text = FONT.render(str(board[y][x]), True, BLACK)
                        SCREEN.blit(text, rect.move(10, 10))
                    elif board[y][x] == -1:
                        pygame.draw.circle(SCREEN, RED, rect.center, CELL_SIZE // 3)
                else:
                    pygame.draw.rect(SCREEN, BLACK, rect)
            
                pygame.draw.rect(SCREEN, BLACK, rect, 1)
            
                # 깃발(우클릭) : 게임 오버 시에도 지뢰가 아닌 셀에 깃발이 있으면 그대로 표시됩니다.
                if flags[y][x]:
                    pygame.draw.line(SCREEN, BLUE, rect.topleft, rect.bottomright, 3)
                    pygame.draw.line(SCREEN, BLUE, rect.topright, rect.bottomleft, 3)
    
    # 게임 오버 시, 화면 하단에 "Game Over" 문구 표시
    if game_over:
        game_over_text = FONT.render("Game Over", True, RED)
        text_rect = game_over_text.get_rect(center=(WIDTH / 2, GRID_SIZE * CELL_SIZE + 20))
        SCREEN.blit(game_over_text, text_rect)
    else:
        # 도움말 메시지 표시
        help_text = FONT.render("Left Click to Open | Right Click to Flag | Shift+Left Click to Preview", True, BLACK)
        text_rect = help_text.get_rect(center=(WIDTH / 2, GRID_SIZE * CELL_SIZE + 20))
        SCREEN.blit(help_text, text_rect)

# 게임 루프
running = True

while running:
    shift_pressed = bool(pygame.key.get_mods() & pygame.KMOD_LSHIFT)
    draw_board()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            x, y = mx // CELL_SIZE, my // CELL_SIZE

            if game_over or game_won:
                reset_game()
                continue

            if event.button == 1:  # 좌클릭
                if shift_pressed:
                    highlight_preview_cells(x, y)
                elif not flags[y][x]:
                    revealed[y][x] = True
                    if board[y][x] == -1:
                        game_over = True  # 지뢰 발견 시 게임오버
                    elif board[y][x] == 0:
                        reveal_empty_cells(x, y)
                    check_game_status()
            elif event.button == 3:  # 우클릭 (깃발 표시)
                if not revealed[y][x]:
                    flags[y][x] = not flags[y][x]  # 깃발 토글

        elif event.type == pygame.MOUSEBUTTONUP:
            highlight_cells.clear()
            if shift_pressed and safe_click:
                shift_click_open(x, y)
