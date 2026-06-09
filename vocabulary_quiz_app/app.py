from __future__ import annotations

import random
import tkinter as tk
from collections import deque  # [보강 1] 성능 최적화를 위한 덱(Deque) 자료구조 import

from tkinter import ttk, font

from vocabulary_quiz_app.quiz_logic import Word, check_answer, draw_word


class VocabularyQuizApp:
    def __init__(self, root: tk.Tk, words: list[Word]) -> None:
        self.words = words
        self.rng = random.Random()
        self.current: Word | None = None
        self.checked = False
        self.score = 0
        self.total = 0
        
        # [기능추가] 최근 출제된 단어를 기억하는 큐 (FIFO 구조) 및 콤보 시스템
        self.recent_queue: deque[Word] = deque() 
        self.combo = 0

        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="NanumGothic", size=12)

        root.title("Vocabulary Quiz")
        root.geometry("420x300")  # 콤보 라벨을 위해 높이를 아주 살짝(20px) 늘림
        root.resizable(False, False)

        self.word_var = tk.StringVar(value="단어를 불러오는 중...")
        self.feedback_var = tk.StringVar(value="")
        self.score_var = tk.StringVar(value="Score: 0/0")
        self.combo_var = tk.StringVar(value="")  # [보강 2] 콤보 UI 변수

        ttk.Label(root, text="영단어").pack(pady=(16, 4))
        ttk.Label(root, textvariable=self.word_var, font=("NanumGothic", 24)).pack()

        self.answer_entry = ttk.Entry(root, font=("NanumGothic", 14))
        self.answer_entry.pack(pady=12, ipadx=6, ipady=4)

        buttons = ttk.Frame(root)
        buttons.pack(pady=6)
        self.check_button = ttk.Button(buttons, text="채점", command=self.check_current)
        self.check_button.pack(side=tk.LEFT, padx=6)
        ttk.Button(buttons, text="다음", command=self.next_word).pack(
            side=tk.LEFT, padx=6
        )

        ttk.Label(root, textvariable=self.feedback_var).pack(pady=4)
        
        # [보강 2] 콤보를 표시할 라벨 추가 (눈에 띄게 주황색 처리)
        ttk.Label(root, textvariable=self.combo_var, font=("NanumGothic", 10, "bold"), foreground="darkorange").pack(pady=2)
        ttk.Label(root, textvariable=self.score_var).pack()

        self.next_word()

    def next_word(self) -> None:
        """단어 목록에서 새로운 단어를 무작위로 선택하되, 최근 출제된 단어는 제외합니다."""
        if not self.words:
            self.word_var.set("단어가 없습니다!")
            self.check_button.state(["disabled"])
            return

        candidate = draw_word(self.words, self.rng)
        
        queue_limit = min(3, len(self.words) - 1) 
        
        if queue_limit > 0:
            while candidate in self.recent_queue:
                candidate = draw_word(self.words, self.rng)
        
        self.current = candidate
        
        self.recent_queue.append(self.current)
        if len(self.recent_queue) > queue_limit:
            # [보강 1] 시간 복잡도 O(N)인 pop(0) 대신 O(1)인 popleft() 사용!
            self.recent_queue.popleft()

        self.word_var.set(self.current.term)
        self.answer_entry.delete(0, tk.END)
        self.feedback_var.set("")
        self.checked = False
        self.check_button.state(["!disabled"])
        self.answer_entry.focus()

    def check_current(self) -> None:
        if self.current is None or self.checked:
            return
        self.checked = True
        self.total += 1
        user_input = self.answer_entry.get()
        
        if check_answer(self.current, user_input):
            self.score += 1
            self.combo += 1  # 정답 시 콤보 1 증가
            self.feedback_var.set("정답입니다!")
            
            # 2연속 정답부터 화면에 콤보 표시
            if self.combo >= 2:
                self.combo_var.set(f"🔥 {self.combo}연속 정답! 🔥")
        else:
            self.combo = 0  # 오답 시 콤보 초기화
            self.combo_var.set("")
            self.feedback_var.set(f"오답입니다. 정답: {self.current.meaning}")
            
        self.score_var.set(f"Score: {self.score}/{self.total}")
        self.check_button.state(["disabled"])