from random import sample
from time import time, sleep
try:
    import customtkinter as ctk
except ImportError:
    import pip
    pip.main(["install", "--user", "customtkinter"])
    sleep(10)
    import customtkinter as ctk

class CC:
    card_count = 10

class App(ctk.CTk):

    def __init__(self):
        super().__init__(fg_color="#DBCEBD")
        self.geometry("400x200")
        self.resizable(False, False)
        self.title("Bubble Sort - By HANSHI")
        self.start_frame()
        self.show_instruction()
        self.mainloop()
        self.attributes("alpha", 0.5)

    def set_card_size(self):
        sw_index = self.winfo_screenwidth() // CC.card_count
        sw_index = (self.winfo_screenwidth()- 2*sw_index) // CC.card_count
        Card.TILE_SIZE[0] = sw_index
        Card.TILE_SIZE[1] = int(sw_index * 1.618)

    def start_frame(self):
        self.start_window = ctk.CTkFrame(self, fg_color='transparent')
        self.cc = ctk.StringVar(value='10')
        start_btn = ctk.CTkButton(self.start_window, text='start', command=self.start)
        instruction_text = ctk.CTkLabel(self.start_window, text=
        'Bubble Sorting Game\nSpace to select next pair\nEnter to swap\n'
        'Sort to ascending list\nR to restart',
        font=ctk.CTkFont('Clear Sans', 18), text_color='#0F0F0F')

        card_entry_frame = ctk.CTkFrame(self.start_window, fg_color='transparent')
        card_entry_label = ctk.CTkLabel(card_entry_frame, text='Card Count',
        font=ctk.CTkFont('Clear Sans', 18), text_color='#0F0F0F')
        card_entry_entry = ctk.CTkEntry(card_entry_frame, textvariable=self.cc,
        fg_color="#EEE4DA", font=ctk.CTkFont('Clear Sans', 18),
        text_color='#0F0F0F')

        card_entry_label.grid(row=0, column=0, sticky='nesw', padx=(0,10))
        card_entry_entry.grid(row=0, column=1, sticky='nesw')
        start_btn.pack(expand=True)
        card_entry_frame.pack()
        self.start_window.pack(expand=True, fill='both', padx=5, pady=10)

    def show_instruction(self):
        self.ins_button = ctk.CTkButton(self, text='Help', command=lambda: Instructions())
        self.ins_button.place(relx=0, rely=0, relwidth=0.2, relheight=0.1)

    def start(self):
        try:
            CC.card_count = int(self.cc.get())
        except TypeError | ValueError:
            CC.card_count = 10
        if CC.card_count > 20 or CC.card_count < 4:
            CC.card_count = 10
        self.set_card_size()
        self.start_window.pack_forget()
        self.ins_button.place_forget()
        self.geometry(f"{CC.card_count * Card.TILE_SIZE[0] + 10}x{Card.TILE_SIZE[1] * 1.5 + 20}")
        self.stats = StatFrame(self)
        self.board = Board(self)
        self.stats.pack(fill='both', anchor='center')
        self.board.pack(expand=True)
        self.ins_button.place(relx=0, rely=0, relwidth=0.2, relheight=0.1)
        self.bind("<space>", lambda _: self.board.select_cards())
        self.bind("<Return>", lambda _: self.board.swap())
        self.bind("<r>", lambda _: self.board.scramble_cards())


class StatFrame(ctk.CTkFrame):
    def __init__(self, root: App):
        super().__init__(root, fg_color='transparent')
        self.root = root
        self.start_time = 0.0
        self.timer = ctk.CTkLabel(self, text=f'{self.start_time:.2f} s',
                                  font=ctk.CTkFont(family="Clear Sans", size=18, weight="bold"),
                                  text_color='#0F0F0F')
        self.timer.pack(anchor='center')

    def start_timer(self):
        self.start_time = time()
        self.timer.configure(text=f'{self.start_time:.2f} s')
        self.increment_time()

    def increment_time(self):
        uid = self.root.after(10, self.increment_time)
        if self.root.board.complete:
            self.timer.configure(text=f'You\'ve Won in {time()-self.start_time:.2f} s !')
            self.root.after_cancel(uid)
            return
        self.timer.configure(text=f'{time()-self.start_time:.2f} s')


class Board(ctk.CTkCanvas):

    def __init__(self, root: App):
        super().__init__(root, width=10000 #CARD_COUNT*Card.TILE_SIZE[0]+10
                         ,height=Card.TILE_SIZE[1]*1.5, bg="#DBCEBD")
        self.complete = False
        self.sel_pair = None
        self.root = root
        self.cards = [Card(self, self.root, i, i) for i in range(CC.card_count)]
        self.moving = False
        self.index = 0  # type: ignore
        self.sel_pair = (self.cards[self.index], self.cards[self.index + 1])  # type: ignore
        self.scroll_x = ctk.CTkScrollbar(root, orientation="horizontal", command=self.xview)
        self.configure(xscrollcommand=self.scroll_x.set)
        self.scroll_x.pack(side="bottom", fill="x")
        self.scramble_cards()

    def scramble_cards(self):
        if self.moving: return
        self.complete = False
        self.moving = True
        self.deselect_all()
        iterate = True
        randoms = sample(range(CC.card_count), CC.card_count)
        while iterate:
            if [*randoms] == [*range(CC.card_count)]:
                randoms = sample(range(CC.card_count), CC.card_count)
            else: iterate = False
        for i, card in enumerate(self.cards):
            card.move(randoms[i], 2)
        self.cards = Board.merge_sort(self.cards)
        self.index = 0  # type: ignore
        self.select_cards()
        self.check_animation_completion()
        self.start_timer()

    def start_timer(self):
        if self.moving: self.root.after(10, self.start_timer)
        else: self.root.stats.start_timer()

    def check_animation_completion(self):
        if any(card.is_moving for card in self.cards):
            self.after(5, self.check_animation_completion)
            return
        else: self.moving = False

    def check_sorted(self):
        if tuple(card.display_value for card in self.cards) == tuple(range(CC.card_count)):
            print("Complete!")
            self.complete = True

    def select_cards(self):
        if self.moving or self.complete: self.root.after(2, self.select_cards); return
        if self.index == CC.card_count-1:
            self.index = 0  # type: ignore
        self.cards = Board.merge_sort(self.cards)
        self.deselect_all()
        self.sel_pair = (self.cards[self.index], self.cards[self.index+1])  # type: ignore
        self.sel_pair[0].select(); self.sel_pair[1].select()
        self.index += 1  # type: ignore
        self.check_sorted()
        if self.sel_pair[0].x < self.xview()[0] or self.sel_pair[0].x > self.xview()[1]:
            self.scroll_to_card(self.sel_pair[0])

    def swap(self):
        if self.moving or self.complete: return
        self.moving = True
        x1 = self.sel_pair[0].x  # type: ignore
        x2 = self.sel_pair[1].x  # type: ignore
        self.sel_pair[0].move(x2, 2)  # type: ignore
        self.sel_pair[1].move(x1, 2)  # type: ignore
        self.select_cards()
        self.check_animation_completion()

    def scroll_to_card(self, card):
        x0, x1 = self.xview()
        width = x1 - x0
        card_x = card.x * Card.TILE_SIZE[0]
        if card_x < x0:
            self.xview("moveto", 0)
        elif card_x > x0 + width:
            self.xview("moveto", (card_x - width) / (self.winfo_width() - width))

    @staticmethod
    def merge_sort(data: list['Card']) -> list:
        if len(data) <= 1: return data
        middle = len(data) // 2
        left = Board.merge_sort(data[:middle])
        right = Board.merge_sort(data[middle:])
        queue = []
        while len(left) > 0 and len(right) > 0:
            if left[0] < right[0]:
                queue.append(left.pop(0))
            else:
                queue.append(right.pop(0))
        queue += left + right
        return queue

    def deselect_all(self):
        for card in self.cards:
            card.deselect()

    @staticmethod
    def show_instructions():
        _ = Instructions()


class Instructions(ctk.CTkToplevel):
    def __init__(self):
        super().__init__(fg_color="#DBCEBD")
        self.title("Help")
        self.geometry("300x200")
        self.grab_set()
        self.label = ctk.CTkLabel(self, text='Bubble Sorting Game\n'
        'Space to select next pair\nEnter to swap\n'
        'Sort to ascending list\nR to restart',
        font=ctk.CTkFont('Clear Sans', 18), text_color='#0F0F0F')
        self.label.pack(expand=True)


class Card:
    TILE_SIZE = [0, 0]
    def __init__(self, canvas: Board, root: App, x: int, value: int):
        self.display_value = value
        self.root = root
        self.x = x
        self.y = self.TILE_SIZE[1]//4-4
        self.canvas = canvas
        self.rect_id = None
        self.text_id = None
        self.selected = False
        self.is_moving = False
        self.show()

    def __str__(self):
        return f"value:{self.display_value} x:{self.x}"

    def __gt__(self, other: 'Card'):
        return self.x > other.x

    def __lt__(self, other: 'Card'):
        return self.x < other.x

    def show(self, colour: str = "#EEE4DA"):
        x1 = self.x * self.TILE_SIZE[0] + 5
        y1 = self.y
        x2 = x1 + self.TILE_SIZE[0]
        y2 = y1 + self.TILE_SIZE[1]
        self.rect_id = self.canvas.create_rectangle(x1, y1, x2, y2,
        fill=colour, outline='#CFBCA3', width=5)
        self.text_id = self.canvas.create_text(x1 + self.TILE_SIZE[0] / 2,
        y1 + self.TILE_SIZE[1] / 2, text=str(self.display_value + 1),
        font=ctk.CTkFont(family="Clear Sans", size=self.TILE_SIZE[0] // 5,
        weight="bold"), fill="black")

    def hide(self):
        self.canvas.delete(self.rect_id)  # type: ignore
        self.canvas.delete(self.text_id)  # type: ignore

    def select(self):
        self.selected = True
        self.hide()
        self.show("#EDE0C8")

    def deselect(self):
        self.selected = False
        self.hide()
        self.show()

    def move(self, new_pos: int, iter_dist: int, i: int = 1, block_bypass = False):
        if not block_bypass and self.is_moving: return
        self.is_moving = True
        dir_move = 1 if (new_pos - self.x) >= 0 else -1
        if i % (self.TILE_SIZE[0] // iter_dist) == 0:
            self.x += dir_move
        self.canvas.move(self.rect_id, iter_dist * dir_move, 0)
        self.canvas.move(self.text_id, iter_dist * dir_move, 0)
        if self.x == new_pos:
            self.is_moving = False
        else:
            self.root.after(2, lambda: self.move(new_pos, iter_dist, i + 1,
            block_bypass=True))


if __name__ == '__main__':
    App()
