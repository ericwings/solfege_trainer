#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solfege & Degrees Trainer — Simple (no CSV)
- 不写入任何CSV/文件；只在界面显示统计
- 窗口启动居中
- 答对后可自动切换到下一题（可开关）
- 组合键快捷方式，避免与输入冲突
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random

ORDER_SHARPS = ['F','C','G','D','A','E','B']
ORDER_FLATS  = ['B','E','A','D','G','C','F']

MAJOR_KEY_SIG = {
    'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'F#': 6, 'C#': 7,
    'F': -1, 'Bb': -2, 'Eb': -3, 'Ab': -4, 'Db': -5, 'Gb': -6, 'Cb': -7,
}
MINOR_KEY_SIG = {
    'A': 0, 'E': 1, 'B': 2, 'F#': 3, 'C#': 4, 'G#': 5, 'D#': 6, 'A#': 7,
    'D': -1, 'G': -2, 'C': -3, 'F': -4, 'Bb': -5, 'Eb': -6, 'Ab': -7,
}

LETTER_SEQ = ['A','B','C','D','E','F','G']

SOLFEGE_BASE = ['do','re','mi','fa','sol','la','ti']
SOLFEGE_SYNONYMS = {
    'do':'do','dou':'do',
    're':'re','ray':'re',
    'mi':'mi','me':'mi',
    'fa':'fa',
    'sol':'sol','so':'sol','sou':'sol',
    'la':'la',
    'ti':'ti','si':'ti',
    'ra':'ra','ri':'ri','me':'me','fi':'fi','se':'se','le':'le','te':'te','li':'li','si#':'li',
}
ROMAN_TO_DEGREE = {'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6,'VII':7}

PC_MAP = {
    'C':0, 'B#':0,
    'C#':1, 'Db':1,
    'D':2,
    'D#':3, 'Eb':3,
    'E':4, 'Fb':4,
    'F':5, 'E#':5,
    'F#':6, 'Gb':6,
    'G':7,
    'G#':8, 'Ab':8,
    'A':9,
    'A#':10, 'Bb':10,
    'B':11, 'Cb':11,
}

PROMPT_TYPES = ['Note → Solfege + Degree','Degree → Note + Solfege','Solfege → Note + Degree','Mixed']
SCALE_MODES  = ['Major 大调', 'Minor 自然小调', 'Minor 和声小调', 'Minor 旋律小调(上行)']

def sanitize_note_name(s: str) -> str:
    s = s.strip().replace('♯','#').replace('♭','b')
    if not s:
        return s
    return s[0].upper() + s[1:]

def degree_from_input(s: str):
    s = s.strip()
    if not s: return None
    if s.isdigit():
        n = int(s);  return n if 1 <= n <= 7 else None
    if len(s) >= 2 and s[:-2].isdigit():
        try:
            n = int(s[:-2]);
            if 1 <= n <= 7: return n
        except: pass
    return ROMAN_TO_DEGREE.get(s.upper(), None)

def solfege_from_input(s: str):
    return SOLFEGE_SYNONYMS.get(s.strip().lower(), None)

def key_accidental_map_from_count(n_accidentals: int):
    acc = {}
    if n_accidentals > 0:
        for L in ORDER_SHARPS[:n_accidentals]: acc[L] = '#'
    elif n_accidentals < 0:
        for L in ORDER_FLATS[:(-n_accidentals)]: acc[L] = 'b'
    return acc

def build_scale_letters(tonic_letter: str):
    tonic_letter = tonic_letter.upper()
    letters, idx = [], LETTER_SEQ.index(tonic_letter)
    for i in range(7): letters.append(LETTER_SEQ[(idx+i)%7])
    return letters

def apply_key_signature(letters, n_accidentals: int):
    accmap = key_accidental_map_from_count(n_accidentals)
    return [L + accmap.get(L, '') for L in letters]

def note_to_pc(note: str):
    return PC_MAP.get(sanitize_note_name(note), None)

def adjust_letter_by_semitone(note_str: str, semitone_delta: int):
    if semitone_delta == 0: return note_str
    base = note_str[0].upper()
    has_sharp = '#' in note_str
    has_flat  = 'b' in note_str
    if semitone_delta == +1:
        if has_flat: return base
        else: return base + '#'
    else:
        if has_sharp: return base
        else: return base + 'b'

def build_major_scale(key_name: str):
    return apply_key_signature(build_scale_letters(key_name[0]), MAJOR_KEY_SIG[key_name])

def build_minor_natural_scale(key_name: str):
    return apply_key_signature(build_scale_letters(key_name[0]), MINOR_KEY_SIG[key_name])

def build_minor_harmonic_scale(key_name: str):
    sc = build_minor_natural_scale(key_name); sc[6] = adjust_letter_by_semitone(sc[6], +1); return sc

def build_minor_melodic_scale(key_name: str):
    sc = build_minor_natural_scale(key_name); sc[5] = adjust_letter_by_semitone(sc[5], +1); sc[6] = adjust_letter_by_semitone(sc[6], +1); return sc

ALL_MAJOR_KEYS = sorted(MAJOR_KEY_SIG.keys(), key=lambda k: MAJOR_KEY_SIG[k])
ALL_MINOR_KEYS = sorted(MINOR_KEY_SIG.keys(), key=lambda k: MINOR_KEY_SIG[k])

def random_key(selected: str, scale_mode: str):
    if selected == 'Random 随机':
        return random.choice(ALL_MAJOR_KEYS if scale_mode.startswith('Major') else ALL_MINOR_KEYS)
    return selected

def build_scale(key_name: str, scale_mode: str):
    if scale_mode.startswith('Major'): return build_major_scale(key_name)
    if '自然' in scale_mode: return build_minor_natural_scale(key_name)
    if '和声' in scale_mode: return build_minor_harmonic_scale(key_name)
    if '旋律' in scale_mode: return build_minor_melodic_scale(key_name)
    return build_major_scale(key_name)

def solfege_for_degree(deg: int, scale_mode: str, accidental_aware: bool):
    if not (1 <= deg <= 7): return None
    if not accidental_aware: return SOLFEGE_BASE[deg-1]
    if scale_mode.startswith('Major'): mapping = ['do','re','mi','fa','sol','la','ti']
    elif '自然' in scale_mode:          mapping = ['do','re','me','fa','sol','le','te']
    elif '和声' in scale_mode:          mapping = ['do','re','me','fa','sol','le','ti']
    elif '旋律' in scale_mode:          mapping = ['do','re','me','fa','sol','la','ti']
    else:                               mapping = SOLFEGE_BASE
    return mapping[deg-1]

class QuizItem:
    def __init__(self, key_name: str, scale_mode: str, prompt_type: str, accidental_aware: bool):
        self.key_name = key_name
        self.scale_mode = scale_mode
        self.scale = build_scale(key_name, scale_mode)
        self.degree = random.randint(1,7)
        self.note = self.scale[self.degree - 1]
        self.solfege = solfege_for_degree(self.degree, scale_mode, accidental_aware)
        self.prompt_type = prompt_type if prompt_type != 'Mixed' else random.choice(PROMPT_TYPES[:-1])

class TrainerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Solfege & Degrees Trainer (Simple)')
        self.initial_w, self.initial_h = 860, 580
        self.geometry(f'{self.initial_w}x{self.initial_h}')
        self.minsize(820, 540)

        self.scale_mode = tk.StringVar(value=SCALE_MODES[0])
        self.selected_key = tk.StringVar(value='C')
        self.prompt_type = tk.StringVar(value=PROMPT_TYPES[0])
        self.enharmonic_ok = tk.BooleanVar(value=False)
        self.accidental_solfege = tk.BooleanVar(value=True)
        self.autonext = tk.BooleanVar(value=True)
        self.autonext_delay_ms = 700

        self.session_seconds = 60*60
        self.remaining = self.session_seconds
        self.timer_running = False
        self.correct = 0
        self.attempts = 0
        self.streak = 0

        self.current_item = None
        self.need_note = False
        self.need_solfege = False
        self.need_degree = False
        self.tries_current = 0

        self._build_ui()
        self._bind_shortcuts()
        self._refresh_key_options()
        self.center_on_screen(self.initial_w, self.initial_h)
        self._next_question()

    def center_on_screen(self, w, h):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 3
        self.geometry(f'{w}x{h}+{x}+{y}')

    def _bind_shortcuts(self):
        self.bind_all('<Return>', lambda e: (self.check_answer(), 'break'))
        self.bind_all('<Control-n>', lambda e: (self._next_question(), 'break'))
        self.bind_all('<Command-n>', lambda e: (self._next_question(), 'break'))
        self.bind_all('<Control-Shift-H>', lambda e: (self.show_hint(), 'break'))
        self.bind_all('<Command-Shift-H>', lambda e: (self.show_hint(), 'break'))
        self.bind_all('<Control-Shift-R>', lambda e: (self.reveal_answer(), 'break'))
        self.bind_all('<Command-Shift-R>', lambda e: (self.reveal_answer(), 'break'))

    def _build_ui(self):
        top = ttk.Frame(self, padding=10); top.pack(fill='x')
        ttk.Label(top, text='Scale 调式:').pack(side='left')
        cmb_mode = ttk.Combobox(top, textvariable=self.scale_mode, values=SCALE_MODES, width=22, state='readonly')
        cmb_mode.pack(side='left', padx=(6,18))
        try:
            self.scale_mode.trace_add('write', lambda *_: self._refresh_key_options())
        except Exception:
            self.scale_mode.trace('w', lambda *args: self._refresh_key_options())

        ttk.Label(top, text='Key 调:').pack(side='left')
        self.key_combo = ttk.Combobox(top, textvariable=self.selected_key, width=12, state='readonly')
        self.key_combo.pack(side='left', padx=(6,18))

        ttk.Label(top, text='Mode 题型:').pack(side='left')
        ttk.Combobox(top, textvariable=self.prompt_type, values=PROMPT_TYPES, width=26, state='readonly').pack(side='left', padx=(6,18))

        ttk.Checkbutton(top, text='允许等音(Enharmonic)', variable=self.enharmonic_ok).pack(side='left', padx=(0,12))
        ttk.Checkbutton(top, text='按变音显示唱名（me/le/te/fi等）', variable=self.accidental_solfege).pack(side='left')
        ttk.Checkbutton(top, text='答对自动下一题', variable=self.autonext).pack(side='left', padx=(12,0))

        right_top = ttk.Frame(self, padding=(10,0,10,10)); right_top.pack(fill='x')
        self.timer_lbl = ttk.Label(right_top, text='剩余 60:00', font=('Helvetica', 12, 'bold')); self.timer_lbl.pack(side='left')
        ttk.Button(right_top, text='开始 60分钟', command=self.start_timer).pack(side='left', padx=8)
        ttk.Button(right_top, text='暂停', command=self.pause_timer).pack(side='left')
        ttk.Button(right_top, text='重置', command=self.reset_timer).pack(side='left', padx=(8,0))

        qf = ttk.LabelFrame(self, text='题目 / Question', padding=12); qf.pack(fill='both', expand=True, padx=10, pady=(0,10))
        self.question_lbl = ttk.Label(qf, text='——', font=('Helvetica', 16, 'bold')); self.question_lbl.pack(anchor='w', pady=(0,8))
        inpf = ttk.Frame(qf); inpf.pack(fill='x', pady=6)
        self.entry_note = self._labeled_entry(inpf, '音名 Note:', 0)
        self.entry_solfege = self._labeled_entry(inpf, '唱名 Solfege:', 1)
        self.entry_degree = self._labeled_entry(inpf, '级数 Degree:', 2)

        btnf = ttk.Frame(qf); btnf.pack(fill='x', pady=(10,0))
        ttk.Button(btnf, text='检查 Check (Enter)', command=self.check_answer).pack(side='left')
        ttk.Button(btnf, text='换一题 Next (Ctrl/Cmd+N)', command=self._next_question).pack(side='left', padx=8)
        ttk.Button(btnf, text='重置本题 Retry', command=self.retry_same_question).pack(side='left')
        ttk.Button(btnf, text='提示 Hint (Ctrl/Cmd+Shift+H)', command=self.show_hint).pack(side='left', padx=8)
        ttk.Button(btnf, text='显示答案 Reveal (Ctrl/Cmd+Shift+R)', command=self.reveal_answer).pack(side='left')

        self.feedback_lbl = ttk.Label(qf, text='', font=('Helvetica', 12)); self.feedback_lbl.pack(anchor='w', pady=(8,0))

        sf = ttk.Frame(self, padding=(10,0,10,10)); sf.pack(fill='x')
        self.stat_correct = ttk.Label(sf, text='正确 0')
        self.stat_attempts = ttk.Label(sf, text='尝试 0')
        self.stat_acc = ttk.Label(sf, text='命中率 0.0%')
        self.stat_streak = ttk.Label(sf, text='连对 0')
        for w in (self.stat_correct, self.stat_attempts, self.stat_acc, self.stat_streak):
            w.pack(side='left', padx=(0,12))

    def _labeled_entry(self, parent, label_text, row):
        frame = ttk.Frame(parent); frame.grid(row=row, column=0, sticky='w', pady=4)
        ttk.Label(frame, text=label_text, width=20, anchor='e').pack(side='left')
        entry = ttk.Entry(frame, width=28); entry.pack(side='left', padx=6)
        return entry

    def _refresh_key_options(self):
        mode = self.scale_mode.get()
        keys = ['Random 随机'] + (ALL_MAJOR_KEYS if mode.startswith('Major') else ALL_MINOR_KEYS)
        self.key_combo.config(values=keys)
        if self.selected_key.get() not in keys:
            self.selected_key.set('Random 随机')

    # Timer
    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True; self._tick()
    def pause_timer(self): self.timer_running = False
    def reset_timer(self):
        self.timer_running = False; self.remaining = self.session_seconds; self._update_timer_label()
    def _tick(self):
        if self.timer_running:
            if self.remaining > 0:
                self.remaining -= 1; self._update_timer_label(); self.after(1000, self._tick)
            else:
                self.timer_running = False; messagebox.showinfo('时间到', '60分钟到！辛苦啦～'); self._update_timer_label()
    def _update_timer_label(self):
        m, s = divmod(self.remaining, 60); self.timer_lbl.config(text=f'剩余 {m:02d}:{s:02d}')

    # Quiz
    def _next_question(self):
        key = random_key(self.selected_key.get(), self.scale_mode.get())
        ptype = self.prompt_type.get()
        accidental = self.accidental_solfege.get()
        self.current_item = QuizItem(key, self.scale_mode.get(), ptype, accidental)
        self.tries_current = 0
        self.need_note = True; self.need_solfege = True; self.need_degree = True
        for e in (self.entry_note, self.entry_solfege, self.entry_degree):
            e.config(state='normal'); e.delete(0, tk.END)
        self.feedback_lbl.config(text='')
        it = self.current_item
        if it.prompt_type == 'Note → Solfege + Degree':
            self.question_lbl.config(text=f'[{it.scale_mode}]  Key: {it.key_name} | 给定音名 Note = {it.note}，请输入 唱名 + 级数')
            self.entry_note.insert(0, it.note); self.entry_note.config(state='disabled'); self.need_note = False; self.entry_solfege.focus_set()
        elif it.prompt_type == 'Degree → Note + Solfege':
            self.question_lbl.config(text=f'[{it.scale_mode}]  Key: {it.key_name} | 给定级数 Degree = {it.degree}，请输入 音名 + 唱名')
            self.entry_degree.insert(0, str(it.degree)); self.entry_degree.config(state='disabled'); self.need_degree = False; self.entry_note.focus_set()
        elif it.prompt_type == 'Solfege → Note + Degree':
            self.question_lbl.config(text=f'[{it.scale_mode}]  Key: {it.key_name} | 给定唱名 Solfege = {it.solfege}，请输入 音名 + 级数')
            self.entry_solfege.insert(0, it.solfege); self.entry_solfege.config(state='disabled'); self.need_solfege = False; self.entry_note.focus_set()
        else:
            self.question_lbl.config(text='(未知题型)')

    def retry_same_question(self):
        if self.need_note:
            self.entry_note.config(state='normal'); self.entry_note.delete(0, tk.END)
        if self.need_solfege:
            self.entry_solfege.config(state='normal'); self.entry_solfege.delete(0, tk.END)
        if self.need_degree:
            self.entry_degree.config(state='normal'); self.entry_degree.delete(0, tk.END)
        self.feedback_lbl.config(text='(已重置本题输入)')

    def show_hint(self):
        if not self.current_item: return
        it = self.current_item
        if it.prompt_type == 'Note → Solfege + Degree':
            hint = f"提示: 该音在 {it.key_name} {it.scale_mode} 是 {it.solfege.upper()}（第 {it.degree} 级）"
        elif it.prompt_type == 'Degree → Note + Solfege':
            hint = f"提示: 对应音名以字母 {it.note[0]} 开头"
        elif it.prompt_type == 'Solfege → Note + Degree':
            hint = f"提示: {it.solfege} = 第 {it.degree} 级"
        else:
            hint = '——'
        self.feedback_lbl.config(text=hint)

    def reveal_answer(self):
        if not self.current_item: return
        it = self.current_item
        ans = f"答案 / Answer → Note: {it.note} | Solfege: {it.solfege} | Degree: {it.degree}   （Key: {it.key_name}, {it.scale_mode}）"
        self.feedback_lbl.config(text=ans)
        for e, need in ((self.entry_note, self.need_note),(self.entry_solfege, self.need_solfege),(self.entry_degree, self.need_degree)):
            if need: e.config(state='disabled')

    def check_answer(self):
        if not self.current_item: return
        it = self.current_item
        enh_ok = self.enharmonic_ok.get()

        note_in = sanitize_note_name(self.entry_note.get()) if self.need_note else it.note
        solf_in = solfege_from_input(self.entry_solfege.get()) if self.need_solfege else it.solfege
        deg_in  = degree_from_input(self.entry_degree.get()) if self.need_degree else it.degree

        note_ok = self._check_note(note_in, it.note, enh_ok) if self.need_note else True
        solf_ok = (solf_in == it.solfege) if self.need_solfege else True
        deg_ok  = (deg_in == it.degree)  if self.need_degree else True
        all_ok = note_ok and solf_ok and deg_ok

        self.attempts += 1
        if all_ok:
            self.correct += 1; self.streak += 1; msg = "✅ 正确！"
            for e, need in ((self.entry_note, self.need_note),(self.entry_solfege, self.need_solfege),(self.entry_degree, self.need_degree)):
                if need: e.config(state='disabled')
            if self.autonext.get():
                self.after(self.autonext_delay_ms, self._next_question)
        else:
            self.streak = 0
            pieces = []
            if self.need_note and not note_ok: pieces.append(f"Note 应为 {it.note}")
            if self.need_solfege and not solf_ok: pieces.append(f"Solfege 应为 {it.solfege}")
            if self.need_degree and not deg_ok: pieces.append(f"Degree 应为 {it.degree}")
            msg = "❌ 再试试： " + "；".join(pieces)

        acc = (self.correct / self.attempts * 100.0) if self.attempts else 0.0
        self.stat_correct.config(text=f'正确 {self.correct}')
        self.stat_attempts.config(text=f'尝试 {self.attempts}')
        self.stat_acc.config(text=f'命中率 {acc:.1f}%')
        self.stat_streak.config(text=f'连对 {self.streak}')
        self.feedback_lbl.config(text=msg + f"   (Key {it.key_name} | {it.scale_mode})")

    def _check_note(self, user_note: str, correct_note: str, enh_ok: bool) -> bool:
        if not user_note: return False
        if user_note == correct_note: return True
        if enh_ok:
            pc_u = note_to_pc(user_note); pc_c = note_to_pc(correct_note)
            if pc_u is not None and pc_c is not None and pc_u == pc_c: return True
        return False

if __name__ == '__main__':
    app = TrainerApp()
    app.mainloop()
