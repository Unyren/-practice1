from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from .config import OrganizeConfig
from .runner import run_organizer


class OrganizerGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("MP3 자동 분류 프로그램")
        self.geometry("900x700")
        self.resizable(True, True)
        self._create_widgets()

    def _create_widgets(self) -> None:
        # 상단 제목
        title_frame = tk.Frame(self)
        title_frame.pack(fill="x", padx=10, pady=8)
        tk.Label(title_frame, text="MP3 자동 분류 프로그램", font=("Arial", 16, "bold")).pack()

        # 메인 설정 프레임
        frame = ttk.LabelFrame(self, text="기본 설정", padding=10)
        frame.pack(fill="x", padx=10, pady=8)

        tk.Label(frame, text="원본 폴더:").grid(row=0, column=0, sticky="w", pady=8)
        self.source_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.source_var, width=70).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(frame, text="찾기", command=self._browse_source, width=10).grid(row=0, column=2, padx=5)

        tk.Label(frame, text="저장 폴더:").grid(row=1, column=0, sticky="w", pady=8)
        self.dest_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.dest_var, width=70).grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(frame, text="찾기", command=self._browse_destination, width=10).grid(row=1, column=2, padx=5)

        # 분류 설정 프레임
        classify_frame = ttk.LabelFrame(self, text="분류 설정", padding=10)
        classify_frame.pack(fill="x", padx=10, pady=8)

        tk.Label(classify_frame, text="분류 방식:").grid(row=0, column=0, sticky="w", pady=8)
        self.mode_var = tk.StringVar(value="copy")
        ttk.Combobox(
            classify_frame,
            textvariable=self.mode_var,
            values=["복사 (copy)", "이동 (move)"],
            state="readonly",
            width=25
        ).grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(classify_frame, text="중복 파일 처리:").grid(row=1, column=0, sticky="w", pady=8)
        self.duplicate_var = tk.StringVar(value="rename")
        ttk.Combobox(
            classify_frame,
            textvariable=self.duplicate_var,
            values=["이름 변경 (rename)", "건너뛰기 (skip)", "덮어쓰기 (overwrite)"],
            state="readonly",
            width=25
        ).grid(row=1, column=1, sticky="w", padx=5)

        tk.Label(classify_frame, text="폴더 구조:").grid(row=2, column=0, sticky="w", pady=8)
        self.template_var = tk.StringVar(value="genre/{genre}/{artist}")
        ttk.Entry(classify_frame, textvariable=self.template_var, width=70).grid(row=2, column=1, columnspan=2, sticky="ew", padx=5)
        tk.Label(classify_frame, text="예: genre/{genre}/{artist}, artist/{artist}/{album}", font=("Arial", 8), foreground="gray").grid(row=3, column=1, columnspan=2, sticky="w", padx=5)

        tk.Label(classify_frame, text="태그 없는 파일:").grid(row=4, column=0, sticky="w", pady=8)
        self.fallback_var = tk.StringVar(value="분류안됨")
        ttk.Entry(classify_frame, textvariable=self.fallback_var, width=30).grid(row=4, column=1, sticky="w", padx=5)

        tk.Label(classify_frame, text="제외 패턴:").grid(row=5, column=0, sticky="w", pady=8)
        self.exclude_var = tk.StringVar()
        ttk.Entry(classify_frame, textvariable=self.exclude_var, width=70).grid(row=5, column=1, columnspan=2, sticky="ew", padx=5)
        tk.Label(classify_frame, text="쉼표로 구분 (예: temp, backup)", font=("Arial", 8), foreground="gray").grid(row=6, column=1, columnspan=2, sticky="w", padx=5)

        # 옵션 프레임
        option_frame = ttk.LabelFrame(self, text="옵션", padding=10)
        option_frame.pack(fill="x", padx=10, pady=8)

        self.dry_run_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(option_frame, text="시뮬레이션만 실행 (파일 이동/복사 없음)", variable=self.dry_run_var).pack(anchor="w", pady=5)

        self.verbose_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(option_frame, text="상세 로그 출력", variable=self.verbose_var).pack(anchor="w", pady=5)

        # 시작 버튼 및 상태
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=8)
        ttk.Button(button_frame, text="시작", command=self._start_organizer, width=20).pack(side="left", padx=5)
        ttk.Button(button_frame, text="초기화", command=self._reset_form, width=20).pack(side="left", padx=5)

        self.status_var = tk.StringVar(value="준비 완료")
        tk.Label(self, textvariable=self.status_var).pack(fill="x", padx=10, pady=5)

        # 로그 영역
        tk.Label(self, text="처리 로그", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        
        self.log_text = tk.Text(self, wrap="word", height=15, state="disabled", font=("Courier", 9))
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))


    def _browse_source(self) -> None:
        selected = filedialog.askdirectory(title="원본 폴더 선택")
        if selected:
            self.source_var.set(selected)

    def _browse_destination(self) -> None:
        selected = filedialog.askdirectory(title="저장 폴더 선택")
        if selected:
            self.dest_var.set(selected)

    def _reset_form(self) -> None:
        self.source_var.set("")
        self.dest_var.set("")
        self.mode_var.set("copy")
        self.duplicate_var.set("rename")
        self.template_var.set("genre/{genre}/{artist}")
        self.fallback_var.set("분류안됨")
        self.exclude_var.set("")
        self.dry_run_var.set(False)
        self.verbose_var.set(False)
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self._set_status("준비 완료")

    def _append_log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _start_organizer(self) -> None:
        source = self.source_var.get().strip()
        destination = self.dest_var.get().strip()
        if not source or not destination:
            self._append_log("원본 폴더와 저장 폴더를 반드시 선택해주세요.")
            return

        mode = self.mode_var.get().split("(")[1].rstrip(")")
        duplicate = self.duplicate_var.get().split("(")[1].rstrip(")")
        
        config = OrganizeConfig(
            source=Path(source),
            destination=Path(destination),
            mode=mode,
            template=self.template_var.get(),
            fallback_dir=self.fallback_var.get() or "분류안됨",
            duplicate_strategy=duplicate,
            dry_run=self.dry_run_var.get(),
            exclude_patterns=[pattern.strip() for pattern in self.exclude_var.get().split(",") if pattern.strip()],
            workers=1,
            verbose=self.verbose_var.get(),
        )

        self._append_log("=" * 60)
        self._append_log(f"시작: {source}")
        self._append_log(f"저장: {destination}")
        if self.dry_run_var.get():
            self._append_log("⚠ 시뮬레이션 모드 (파일 이동/복사 없음)")
        self._append_log("=" * 60)
        
        self._set_status("실행 중...")
        self._set_controls_state("disabled")

        thread = threading.Thread(target=self._run_worker, args=(config,), daemon=True)
        thread.start()

    def _run_worker(self, config: OrganizeConfig) -> None:
        try:
            run_organizer(config, progress_callback=self._gui_callback)
        except Exception as exc:
            self.after(0, lambda: self._append_log(f"❌ 오류 발생: {exc}"))
        finally:
            self.after(0, lambda: self._set_status("완료"))
            self.after(0, lambda: self._set_controls_state("normal"))

    def _gui_callback(self, message: str) -> None:
        self.after(0, lambda: self._append_log(message))

    def _set_controls_state(self, state: str) -> None:
        for child in self.winfo_children():
            if isinstance(child, (ttk.Frame, ttk.LabelFrame)):
                for grandchild in child.winfo_children():
                    try:
                        grandchild.configure(state=state)
                    except tk.TclError:
                        pass
        try:
            self.log_text.configure(state=state if state == "normal" else "disabled")
        except tk.TclError:
            pass
