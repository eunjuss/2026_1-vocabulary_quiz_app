from __future__ import annotations

import random
import tkinter as tk

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

        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="NanumGothic", size=12)

        root.title("Vocabulary Quiz")
        root.geometry("420x280")
        root.resizable(False, False)

        self.word_var = tk.StringVar(value="단어를 불러오는 중...")
        self.feedback_var = tk.StringVar(value="")
        self.score_var = tk.StringVar(value="Score: 0/0")

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

        # [기능추가] 단어장 관리(조회, 삭제, 추가) 팝업을 띄우는 버튼 추가
        self.manage_words_btn = ttk.Button(buttons, text="단어장", command=self.manage_words)
        self.manage_words_btn.pack(side=tk.LEFT, padx=6)

        ttk.Label(root, textvariable=self.feedback_var).pack(pady=8)
        ttk.Label(root, textvariable=self.score_var).pack()

        self.next_word()

    def next_word(self) -> None:
        # [기능추가] 사용자가 단어를 모두 삭제하여 리스트가 비었을 때 오류가 발생하는 것을 방지하는 예외 처리
        if not self.words:
            self.word_var.set("단어가 없습니다!")
            self.check_button.state(["disabled"])
            return
            
        self.current = draw_word(self.words, self.rng)
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
            self.feedback_var.set("정답입니다!")
        else:
            self.feedback_var.set(f"오답입니다. 정답: {self.current.meaning}")
        self.score_var.set(f"Score: {self.score}/{self.total}")
        self.check_button.state(["disabled"])

    # ==========================================
    # [기능추가] 단어장 통합 관리 팝업 로직 시작
    # ==========================================
    def manage_words(self) -> None:
        """현재 단어 목록 조회, 선택 삭제, 새로운 단어 추가를 수행하는 팝업 UI를 생성합니다."""
        popup = tk.Toplevel()
        popup.title("단어장 통합 관리")
        popup.geometry("320x420")
        popup.resizable(False, False)
        
        # 팝업 창이 메인 창 뒤로 숨지 않도록 포커스 고정
        popup.transient(popup.master)
        popup.grab_set()

        # 단어 목록 조회 (Listbox UI 구성)
        ttk.Label(popup, text="현재 단어 목록", font=("NanumGothic", 10, "bold")).pack(pady=(10, 2))
        list_frame = ttk.Frame(popup)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        word_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("NanumGothic", 10), selectmode=tk.SINGLE)
        word_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=word_listbox.yview)

        # 목록 새로고침 함수
        def refresh_list():
            """원본 단어 리스트(self.words)의 최신 상태를 Listbox 화면에 반영합니다."""
            word_listbox.delete(0, tk.END)
            for w in self.words:
                word_listbox.insert(tk.END, f"{w.term} : {w.meaning}")

        refresh_list()

        # 선택한 단어 삭제 기능
        def delete_word():
            """Listbox에서 선택된 항목을 확인하고, 원본 리스트에서 해당 단어를 삭제합니다."""
            selected = word_listbox.curselection()
            if not selected:
                self.feedback_var.set("⚠️ 삭제할 단어를 목록에서 선택해 주세요.")
                return
            idx = selected[0]
            deleted = self.words.pop(idx) # 원본 데이터에서 삭제
            refresh_list()
            self.feedback_var.set(f"🗑️ '{deleted.term}' 단어가 삭제되었습니다.")

        ttk.Button(popup, text="선택 단어 삭제", command=delete_word).pack(pady=(0, 10))

        ttk.Separator(popup, orient='horizontal').pack(fill='x', padx=20, pady=5)

        # 새 단어 추가 기능
        ttk.Label(popup, text="새 영단어 추가", font=("NanumGothic", 10, "bold")).pack(pady=(5, 2))
        
        input_frame = ttk.Frame(popup)
        input_frame.pack(pady=5)
        
        ttk.Label(input_frame, text="단어:").grid(row=0, column=0, padx=5, pady=2)
        term_entry = ttk.Entry(input_frame, width=15)
        term_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(input_frame, text="뜻:").grid(row=1, column=0, padx=5, pady=2)
        meaning_entry = ttk.Entry(input_frame, width=15)
        meaning_entry.grid(row=1, column=1, padx=5, pady=2)

        def save_word() -> None:
            """입력된 단어와 뜻을 검증한 후, 새 Word 객체로 만들어 원본 리스트에 추가합니다."""
            new_term = term_entry.get().strip()
            new_meaning = meaning_entry.get().strip()
            
            # 둘 다 입력된 경우에만 리스트에 추가
            if new_term and new_meaning:
                new_word = Word(term=new_term, meaning=new_meaning)
                self.words.append(new_word)
                refresh_list() # 추가 후 목록 새로고침

                # 다음 입력을 위해 입력창 초기화
                term_entry.delete(0, tk.END)
                meaning_entry.delete(0, tk.END)
                self.feedback_var.set(f"✨ '{new_term}' 단어가 추가되었습니다!")
            else:
                self.feedback_var.set("⚠️ 단어와 뜻을 모두 입력해 주세요.")

        ttk.Button(popup, text="목록에 추가하기", command=save_word).pack(pady=(5, 10))