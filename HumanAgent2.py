import pygame

class HumanAgent:
    def __init__(self):
        pygame.init()
        info = pygame.display.get_desktop_sizes()[0]  # אם יש כמה מסכים – לוקח את הראשון
        self.width, self.height = info

        self.GRID_ORIGIN_Y = self.height / 10
        self.GRID_SIZE = self.width / 30
        self.GRID_ORIGIN_X = (self.width / 2) - (self.GRID_SIZE * 4)
        self.GRID_MARGIN = 4

        self.selected_block = None  # הבלוק שנבחר לגרירה
        self.offset_x = 0  # מרחק אופקי בין העכבר לבלוק
        self.offset_y = 0  # מרחק אנכי בין העכבר לבלוק

    def get_action(self, state, events=None):
        
        if events is None:
            events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"

            # התחלת גרירה
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                for block in state.Blocks:
                    # בדיקה אם העכבר נמצא מעל אחד התאים של הבלוק
                    for y, row in enumerate(block.shape):
                        for x, cell in enumerate(row):
                            if cell == 1:  # תא פעיל בבלוק
                                cell_rect = pygame.Rect(
                                    block.rect.x + x * self.GRID_SIZE,
                                    block.rect.y + y * self.GRID_SIZE,
                                    self.GRID_SIZE,
                                    self.GRID_SIZE
                                )
                                if cell_rect.collidepoint(mouse_x, mouse_y):
                                    self.selected_block = block
                                    self.offset_x = block.rect.x - mouse_x
                                    self.offset_y = block.rect.y - mouse_y
                                    return None  # לא מחזירים כלום בשלב זה

            # גרירה
            elif event.type == pygame.MOUSEMOTION:
                if self.selected_block:
                    mouse_x, mouse_y = event.pos
                    self.selected_block.rect.x = mouse_x + self.offset_x
                    self.selected_block.rect.y = mouse_y + self.offset_y

            # שחרור הבלוק
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.selected_block:
                    # חישוב המיקום שבו שוחרר הבלוק
                    drop_x = self.selected_block.rect.x
                    drop_y = self.selected_block.rect.y
                    block = self.selected_block
                    self.selected_block = None
                    return block, (drop_x, drop_y)  # מחזירים את הבלוק ואת המיקום