import tkinter as tk
from tkinter import ttk


# ----------------------------------------------------------------------
# QUIZ DATA
# ----------------------------------------------------------------------
QUESTIONS = [
    "How many elements are there in the Periodic table?",
    "Which animal lays the largest egg?",
    "What is the most abundant gas in the Earth's atmosphere?",
    "How many bones are there in the human body?",
    "What is the hottest planet in the solar system?",
]

OPTIONS = [
    [("A", "116"), ("B", "17"), ("C", "118"), ("D", "19")],
    [("A", "Whale"), ("B", "Crocodile"), ("C", "Elephant"), ("D", "Ostrich")],
    [("A", "Nitrogen"), ("B", "Oxygen"), ("C", "Hydrogen"), ("D", "Carbon")],
    [("A", "206"), ("B", "207"), ("C", "208"), ("D", "209")],
    [("A", "Mercury"), ("B", "Venus"), ("C", "Earth"), ("D", "Mars")],
]

ANSWERS = ("C", "D", "A", "A", "B")


# ----------------------------------------------------------------------
# MAIN APPLICATION
# ----------------------------------------------------------------------
class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz Time 🧠")
        self.geometry("640x560")
        self.minsize(560, 520)
        self.configure(bg=BG)

        self.current_q = 0
        self.score = 0
        self.guesses = []
        self.selected = tk.StringVar(value="")
        self.option_frames = {}   # letter -> frame widget (for highlight)
        self.answer_locked = False

        self._build_style()
        self._build_layout()
        self._load_question()

    # ------------------------------------------------------------
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Beige.Horizontal.TProgressbar",
            troughcolor=OPTION_BG,
            background=ACCENT,
            bordercolor=BG,
            lightcolor=ACCENT,
            darkcolor=ACCENT,
            thickness=10,
        )

    # ------------------------------------------------------------
    def _build_layout(self):
        # Outer padding wrapper
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=28, pady=24)

        # Header
        header = tk.Frame(outer, bg=BG)
        header.pack(fill="x")

        tk.Label(
            header, text="🧠 Quick Trivia Quiz", bg=BG, fg=TEXT_DARK,
            font=("Georgia", 20, "bold")
        ).pack(side="left")

        self.progress_label = tk.Label(
            header, text="", bg=BG, fg=TEXT_MUTED, font=("Helvetica", 11)
        )
        self.progress_label.pack(side="right")

        # Progress bar
        self.progress = ttk.Progressbar(
            outer, style="Beige.Horizontal.TProgressbar",
            orient="horizontal", mode="determinate",
            maximum=len(QUESTIONS)
        )
        self.progress.pack(fill="x", pady=(10, 18))

        # Card that holds the question + options
        self.card = tk.Frame(
            outer, bg=CARD_BG, highlightbackground=BORDER,
            highlightthickness=1, bd=0
        )
        self.card.pack(fill="both", expand=True)

        card_inner = tk.Frame(self.card, bg=CARD_BG)
        card_inner.pack(fill="both", expand=True, padx=26, pady=26)

        self.question_label = tk.Label(
            card_inner, text="", bg=CARD_BG, fg=TEXT_DARK,
            font=("Georgia", 15, "bold"), wraplength=520,
            justify="left", anchor="w"
        )
        self.question_label.pack(fill="x", pady=(0, 20))

        self.options_container = tk.Frame(card_inner, bg=CARD_BG)
        self.options_container.pack(fill="x")

        self.feedback_label = tk.Label(
            card_inner, text="", bg=CARD_BG, font=("Helvetica", 11, "bold")
        )
        self.feedback_label.pack(anchor="w", pady=(16, 0))

        # Footer / navigation
        footer = tk.Frame(outer, bg=BG)
        footer.pack(fill="x", pady=(18, 0))

        self.score_label = tk.Label(
            footer, text="Score: 0", bg=BG, fg=TEXT_MUTED,
            font=("Helvetica", 11)
        )
        self.score_label.pack(side="left")

        self.next_btn = tk.Button(
            footer, text="Next  ➜", command=self._on_next,
            bg=ACCENT, fg=WHITE_TEXT, activebackground=ACCENT_DARK,
            activeforeground=WHITE_TEXT, font=("Helvetica", 12, "bold"),
            relief="flat", padx=22, pady=8, cursor="hand2",
            state="disabled", disabledforeground=WHITE_TEXT
        )
        self.next_btn.pack(side="right")
        self._style_button_hover(self.next_btn)

    # ------------------------------------------------------------
    def _style_button_hover(self, btn):
        def on_enter(e):
            if btn["state"] != "disabled":
                btn.configure(bg=ACCENT_DARK)

        def on_leave(e):
            if btn["state"] != "disabled":
                btn.configure(bg=ACCENT)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # ------------------------------------------------------------
    def _load_question(self):
        self.answer_locked = False
        self.selected.set("")
        self.feedback_label.configure(text="")
        self.next_btn.configure(state="disabled", bg=ACCENT)

        idx = self.current_q
        self.progress["value"] = idx
        self.progress_label.configure(
            text=f"Question {idx + 1} of {len(QUESTIONS)}"
        )
        self.score_label.configure(text=f"Score: {self.score}")

        self.question_label.configure(text=f"{idx + 1}. {QUESTIONS[idx]}")

        # Clear old option widgets
        for child in self.options_container.winfo_children():
            child.destroy()
        self.option_frames.clear()

        for letter, text in OPTIONS[idx]:
            self._make_option_row(letter, text)

    # ------------------------------------------------------------
    def _make_option_row(self, letter, text):
        row = tk.Frame(
            self.options_container, bg=OPTION_BG, cursor="hand2",
            highlightthickness=1, highlightbackground=BORDER
        )
        row.pack(fill="x", pady=6)

        badge = tk.Label(
            row, text=letter, bg=ACCENT, fg=WHITE_TEXT,
            font=("Helvetica", 11, "bold"), width=2, padx=6, pady=4
        )
        badge.pack(side="left", padx=(10, 12), pady=10)

        label = tk.Label(
            row, text=text, bg=OPTION_BG, fg=TEXT_DARK,
            font=("Helvetica", 12), anchor="w"
        )
        label.pack(side="left", fill="x", expand=True, pady=10)

        widgets = (row, badge, label)
        self.option_frames[letter] = widgets

        for w in widgets:
            w.bind("<Button-1>", lambda e, l=letter: self._select_option(l))
            w.bind("<Enter>", lambda e, l=letter: self._hover(l, True))
            w.bind("<Leave>", lambda e, l=letter: self._hover(l, False))

    # ------------------------------------------------------------
    def _hover(self, letter, entering):
        if self.answer_locked or self.selected.get() == letter:
            return
        row, badge, label = self.option_frames[letter]
        colour = OPTION_HOVER if entering else OPTION_BG
        row.configure(bg=colour)
        label.configure(bg=colour)

    # ------------------------------------------------------------
    def _select_option(self, letter):
        if self.answer_locked:
            return

        # Reset previous selection styling
        for l, (row, badge, label) in self.option_frames.items():
            row.configure(bg=OPTION_BG)
            label.configure(bg=OPTION_BG, fg=TEXT_DARK)
            badge.configure(bg=ACCENT)

        self.selected.set(letter)
        row, badge, label = self.option_frames[letter]
        row.configure(bg="#E4D4AE")
        label.configure(bg="#E4D4AE")
        badge.configure(bg=ACCENT_DARK)

        self.next_btn.configure(state="normal")

    # ------------------------------------------------------------
    def _lock_and_reveal(self):
        """Lock in the answer, colour correct/incorrect, show feedback."""
        self.answer_locked = True
        guess = self.selected.get()
        correct = ANSWERS[self.current_q]

        for letter, (row, badge, label) in self.option_frames.items():
            if letter == correct:
                row.configure(bg="#DCE8CB")
                label.configure(bg="#DCE8CB", fg=CORRECT)
                badge.configure(bg=CORRECT)
            elif letter == guess and guess != correct:
                row.configure(bg="#F1D6D3")
                label.configure(bg="#F1D6D3", fg=INCORRECT)
                badge.configure(bg=INCORRECT)
            # unbind further clicks
            for w in (row, badge, label):
                w.unbind("<Button-1>")

        if guess == correct:
            self.score += 1
            self.feedback_label.configure(text="✔  Correct!", fg=CORRECT)
        else:
            self.feedback_label.configure(
                text=f"✘  Incorrect — correct answer: {correct}",
                fg=INCORRECT
            )

        self.guesses.append(guess)
        self.score_label.configure(text=f"Score: {self.score}")

        is_last = self.current_q == len(QUESTIONS) - 1
        self.next_btn.configure(text="See Results  🏁" if is_last else "Next  ➜")

    # ------------------------------------------------------------
    def _on_next(self):
        if not self.answer_locked:
            # First click on Next = lock in / reveal the answer
            self._lock_and_reveal()
            return

        # Second click = advance
        if self.current_q < len(QUESTIONS) - 1:
            self.current_q += 1
            self._load_question()
        else:
            self.progress["value"] = len(QUESTIONS)
            self._show_results()

    # ------------------------------------------------------------
    def _show_results(self):
        for widget in self.winfo_children():
            widget.destroy()

        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(
            outer, text="🏁 Quiz Complete!", bg=BG, fg=TEXT_DARK,
            font=("Georgia", 22, "bold")
        ).pack(pady=(6, 4))

        pct = round(100 * self.score / len(QUESTIONS))
        tk.Label(
            outer, text=f"You scored {self.score} out of {len(QUESTIONS)}  ({pct}%)",
            bg=BG, fg=TEXT_MUTED, font=("Helvetica", 13)
        ).pack(pady=(0, 18))

        card = tk.Frame(outer, bg=CARD_BG, highlightbackground=BORDER,
                         highlightthickness=1)
        card.pack(fill="both", expand=True)
        inner = tk.Frame(card, bg=CARD_BG)
        inner.pack(fill="both", expand=True, padx=22, pady=18)

        # Scrollable review list
        canvas = tk.Canvas(inner, bg=CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(inner, orient="vertical", command=canvas.yview)
        review_frame = tk.Frame(canvas, bg=CARD_BG)

        review_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=review_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, q in enumerate(QUESTIONS):
            correct_letter = ANSWERS[i]
            guess = self.guesses[i] if i < len(self.guesses) else "—"
            is_correct = guess == correct_letter
            colour = CORRECT if is_correct else INCORRECT
            icon = "✔" if is_correct else "✘"

            row = tk.Frame(review_frame, bg=CARD_BG)
            row.pack(fill="x", pady=8, anchor="w")

            tk.Label(
                row, text=icon, fg=colour, bg=CARD_BG,
                font=("Helvetica", 13, "bold")
            ).pack(side="left", padx=(0, 10))

            text_frame = tk.Frame(row, bg=CARD_BG)
            text_frame.pack(side="left", fill="x", expand=True)

            tk.Label(
                text_frame, text=f"{i + 1}. {q}", bg=CARD_BG, fg=TEXT_DARK,
                font=("Helvetica", 11, "bold"), wraplength=440, justify="left",
                anchor="w"
            ).pack(fill="x")

            detail = f"Your answer: {guess}   •   Correct answer: {correct_letter}"
            tk.Label(
                text_frame, text=detail, bg=CARD_BG, fg=TEXT_MUTED,
                font=("Helvetica", 10), anchor="w"
            ).pack(fill="x")

        # Footer buttons
        footer = tk.Frame(outer, bg=BG)
        footer.pack(fill="x", pady=(16, 0))

        restart_btn = tk.Button(
            footer, text="🔄 Restart Quiz", command=self._restart,
            bg=ACCENT, fg=WHITE_TEXT, activebackground=ACCENT_DARK,
            activeforeground=WHITE_TEXT, font=("Helvetica", 12, "bold"),
            relief="flat", padx=20, pady=8, cursor="hand2"
        )
        restart_btn.pack(side="right")
        self._style_button_hover(restart_btn)

        quit_btn = tk.Button(
            footer, text="Quit", command=self.destroy,
            bg=CARD_BG, fg=TEXT_DARK, activebackground=OPTION_HOVER,
            activeforeground=TEXT_DARK, font=("Helvetica", 12),
            relief="flat", padx=20, pady=8, cursor="hand2",
            highlightbackground=BORDER, highlightthickness=1
        )
        quit_btn.pack(side="right", padx=10)

    # ------------------------------------------------------------
    def _restart(self):
        self.current_q = 0
        self.score = 0
        self.guesses = []
        for widget in self.winfo_children():
            widget.destroy()
        self._build_layout()
        self._load_question()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
