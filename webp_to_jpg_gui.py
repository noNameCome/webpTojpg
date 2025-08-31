#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebP to JPG Converter GUI
GUI 버전의 WebP to JPG 변환기 - 드래그 앤 드롭 및 파일 선택 지원
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
from pathlib import Path
import tempfile
import zipfile
from PIL import Image

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
    print("✅ tkinterdnd2 라이브러리가 로드되었습니다.")
except ImportError:
    DND_AVAILABLE = False
    print("⚠️ 경고: tkinterdnd2가 설치되지 않아 드래그 앤 드롭 기능을 사용할 수 없습니다.")
    print("설치하려면: pip install tkinterdnd2")
except Exception as e:
    DND_AVAILABLE = False
    print(f"⚠️ 드래그 앤 드롭 라이브러리 로딩 오류: {e}")
    print("대신 '파일 선택' 버튼을 사용해주세요.")


class WebPConverterGUI:
    def __init__(self):
        # 해커 스타일 색상 정의
        self.colors = {
            'bg': '#000000',        # 검정 배경
            'fg': '#00FF00',        # 초록 글씨
            'accent': '#00AA00',    # 진한 초록 (버튼 등)
            'warning': '#FFFF00',   # 노랑 (경고)
            'error': '#FF0000',     # 빨강 (오류)
            'success': '#00FFAA',   # 밝은 초록 (성공)
            'border': '#00AA00',    # 테두리 초록
            'button_bg': '#003300', # 버튼 배경
            'entry_bg': '#001100',  # 입력창 배경
        }
        
        # 메인 윈도우 설정
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
        
        self.root.title("🔥 WebP >> JPG Converter [ By noName_Come] 🔥")
        self.root.geometry("850x800")
        self.root.minsize(700, 750)
        self.root.configure(bg=self.colors['bg'])
        
        # 아이콘 설정
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass  # 아이콘이 없어도 계속 실행
        
        # 해커 스타일 설정
        self.setup_hacker_style()
        
        # 변수 초기화
        self.selected_files = []
        self.output_directory = tk.StringVar()
        self.is_processing = False
        self.message_queue = queue.Queue()
        
        # GUI 구성 요소 생성
        self.create_widgets()
        self.setup_drag_drop()
        
        # 메시지 큐 처리를 위한 타이머 설정
        self.root.after(100, self.process_queue)
    
    def setup_hacker_style(self):
        """해커 스타일 테마 설정"""
        style = ttk.Style()
        
        # 다크 테마 설정
        style.theme_use('clam')
        
        # 프레임 스타일
        style.configure('Hacker.TLabelframe', 
                       background=self.colors['bg'],
                       foreground=self.colors['fg'],
                       borderwidth=2,
                       relief='solid')
        style.configure('Hacker.TLabelframe.Label',
                       background=self.colors['bg'],
                       foreground=self.colors['success'],
                       font=('Consolas', 10, 'bold'))
        
        # 버튼 스타일
        style.configure('Hacker.TButton',
                       background=self.colors['button_bg'],
                       foreground=self.colors['fg'],
                       borderwidth=1,
                       focuscolor='none',
                       font=('Consolas', 9, 'bold'))
        style.map('Hacker.TButton',
                 background=[('active', self.colors['accent']),
                           ('pressed', self.colors['border'])])
        
        # 라벨 스타일
        style.configure('Hacker.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['fg'],
                       font=('Consolas', 9))
        
        # 엔트리 스타일
        style.configure('Hacker.TEntry',
                       fieldbackground=self.colors['entry_bg'],
                       background=self.colors['entry_bg'],
                       foreground=self.colors['fg'],
                       borderwidth=1,
                       insertcolor=self.colors['fg'],
                       font=('Consolas', 9))
        
        # 진행바 스타일
        style.configure('Hacker.Horizontal.TProgressbar',
                       background=self.colors['success'],
                       troughcolor=self.colors['button_bg'],
                       borderwidth=1,
                       lightcolor=self.colors['success'],
                       darkcolor=self.colors['success'])
    
    def create_widgets(self):
        """GUI 위젯들을 생성"""
        # 메인 프레임
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=15, pady=15)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 해커 스타일 제목
        title_label = tk.Label(main_frame, 
                              text="🔥 >>> WebP >> JPG CONVERTER <<< 🔥\n[ By noName_Come]", 
                              font=("Consolas", 14, "bold"),
                              bg=self.colors['bg'],
                              fg=self.colors['success'])
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 파일 선택 영역
        file_frame = ttk.LabelFrame(main_frame, text=">>> FILE INPUT <<<", 
                                   padding="15", style="Hacker.TLabelframe")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
        # 드래그 앤 드롭 영역
        if DND_AVAILABLE:
            drop_text = ">>> DRAG & DROP ZIP FILES HERE <<<\n[MULTIPLE FILES SUPPORTED]\n🎯 OR USE BUTTONS BELOW 🎯"
        else:
            drop_text = ">>> CLICK 'ADD FILES' BUTTON <<<\n[MULTIPLE FILES SUPPORTED]\n🎯 DRAG & DROP NOT AVAILABLE 🎯"
        
        self.drop_label = tk.Label(file_frame, 
                                  text=drop_text,
                                  relief="solid", 
                                  borderwidth=2,
                                  bg=self.colors['entry_bg'],
                                  fg=self.colors['fg'],
                                  bd=2,
                                  highlightbackground=self.colors['border'],
                                  anchor="center",
                                  font=("Consolas", 10, "bold"))
        self.drop_label.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                            pady=(0, 15), ipady=25)
        
        # 버튼 프레임
        button_frame = tk.Frame(file_frame, bg=self.colors['bg'])
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        button_frame.columnconfigure(1, weight=1)
        
        # 파일 선택 버튼
        select_button = ttk.Button(button_frame, text="[+] ADD FILES", 
                                  command=self.select_files, style="Hacker.TButton")
        select_button.grid(row=0, column=0, padx=(0, 10))
        
        # 전체 삭제 버튼
        clear_button = ttk.Button(button_frame, text="[X] CLEAR ALL", 
                                 command=self.clear_files, style="Hacker.TButton")
        clear_button.grid(row=0, column=1, padx=(10, 0))
        
        # 선택된 파일 표시
        self.files_label = tk.Label(file_frame, text=">>> FILES: NONE SELECTED <<<", 
                                   bg=self.colors['bg'],
                                   fg=self.colors['accent'],
                                   font=("Consolas", 9))
        self.files_label.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 출력 설정 영역
        output_frame = ttk.LabelFrame(main_frame, text=">>> OUTPUT CONFIG <<<", 
                                     padding="15", style="Hacker.TLabelframe")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        output_frame.columnconfigure(1, weight=1)
        
        output_label = tk.Label(output_frame, text="TARGET DIR:", 
                               bg=self.colors['bg'], fg=self.colors['fg'],
                               font=("Consolas", 9, "bold"))
        output_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_directory,
                                     style="Hacker.TEntry", font=("Consolas", 9))
        self.output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        output_button = ttk.Button(output_frame, text="[📁] BROWSE", 
                                  command=self.select_output_directory,
                                  style="Hacker.TButton")
        output_button.grid(row=0, column=2)
        
        # 기본 출력 폴더 설정 (현재 폴더)
        self.output_directory.set(str(Path.cwd()))
        
        # 변환 버튼 (특별한 스타일)
        self.convert_button = tk.Button(main_frame, 
                                       text="🚀 [EXECUTE] START CONVERSION 🚀", 
                                       command=self.start_conversion,
                                       bg=self.colors['button_bg'],
                                       fg=self.colors['success'],
                                       font=("Consolas", 12, "bold"),
                                       bd=2,
                                       relief="solid",
                                       activebackground=self.colors['accent'],
                                       activeforeground=self.colors['bg'])
        self.convert_button.grid(row=3, column=0, columnspan=3, pady=(0, 15), ipadx=20, ipady=10)
        
        # 진행상황 및 로그 영역
        progress_frame = ttk.LabelFrame(main_frame, text=">>> SYSTEM LOG <<<", 
                                       padding="15", style="Hacker.TLabelframe")
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        
        # 진행 바
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           maximum=100, style="Hacker.Horizontal.TProgressbar")
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 로그 출력 영역
        log_frame = tk.Frame(progress_frame, bg=self.colors['bg'])
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=16, wrap=tk.WORD,
                               bg=self.colors['bg'],
                               fg=self.colors['fg'],
                               font=("Consolas", 9),
                               insertbackground=self.colors['fg'],
                               selectbackground=self.colors['accent'],
                               selectforeground=self.colors['bg'],
                               bd=1,
                               relief="solid")
        
        log_scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview,
                                    bg=self.colors['button_bg'],
                                    troughcolor=self.colors['bg'],
                                    activebackground=self.colors['accent'])
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 하단 상태바
        self.status_var = tk.StringVar()
        self.status_var.set(">>> STATUS: READY FOR OPERATION <<<")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, 
                             bg=self.colors['button_bg'],
                             fg=self.colors['fg'],
                             font=("Consolas", 9, "bold"),
                             relief="solid", 
                             anchor="w",
                             bd=1)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 0), ipady=5)
    
    def setup_drag_drop(self):
        """드래그 앤 드롭 기능 설정"""
        if DND_AVAILABLE:
            try:
                self.drop_label.drop_target_register(DND_FILES)
                self.drop_label.dnd_bind('<<Drop>>', self.on_drop)
                self.log_message("✅ 드래그 앤 드롭 기능이 활성화되었습니다.")
            except Exception as e:
                print(f"❌ 드래그 앤 드롭 설정 실패: {e}")
                self.log_message("⚠️ 드래그 앤 드롭 설정에 실패했습니다. '파일 선택' 버튼을 사용해주세요.")
        else:
            self.log_message("📌 참고: 드래그 앤 드롭을 사용하려면 'pip install tkinterdnd2'를 실행하세요.")
    
    def on_drop(self, event):
        """드래그 앤 드롭 이벤트 처리"""
        try:
            # 여러 방법으로 파일 목록 파싱 시도
            files = []
            
            # 방법 1: splitlist 사용
            try:
                files = self.root.tk.splitlist(event.data)
            except:
                pass
            
            # 방법 2: 공백으로 분리 (경로에 공백이 있을 경우 대비)
            if not files:
                try:
                    # Windows 스타일 파일 경로 처리
                    data = event.data.strip()
                    if data.startswith('{') and data.endswith('}'):
                        # 중괄호로 감싸진 경우
                        files = [data[1:-1]]
                    else:
                        # 여러 파일이 공백으로 구분된 경우
                        files = [f.strip('{}') for f in data.split()] if '}' in data else [data]
                except:
                    pass
            
            # 방법 3: 단일 파일로 처리
            if not files and event.data:
                files = [event.data.strip().strip('{}')]
            
            # ZIP 파일만 필터링
            zip_files = []
            for file_path in files:
                if file_path and file_path.lower().endswith('.zip'):
                    # 경로 정리
                    clean_path = file_path.strip().strip('"').strip("'")
                    if Path(clean_path).exists():
                        zip_files.append(clean_path)
            
            if zip_files:
                # 기존 파일 목록에 새 파일들 추가 (중복 제거)
                existing_files = set(self.selected_files)
                new_files = []
                
                for file_path in zip_files:
                    if file_path not in existing_files:
                        self.selected_files.append(file_path)
                        new_files.append(file_path)
                
                self.update_files_display()
                
                if new_files:
                    self.log_message(f"드래그 앤 드롭으로 {len(new_files)}개 파일이 추가되었습니다:")
                    for i, file_path in enumerate(new_files, 1):
                        self.log_message(f"  {i}. {Path(file_path).name}")
                    self.log_message(f"총 선택된 파일: {len(self.selected_files)}개")
                else:
                    self.log_message("⚠️ 선택한 파일들이 이미 목록에 있습니다.")
            else:
                if files:
                    self.log_message("⚠️ ZIP 파일만 선택할 수 있습니다.")
                    self.log_message(f"감지된 파일들: {files}")
                else:
                    self.log_message("⚠️ 드래그한 파일을 인식할 수 없습니다.")
                    
        except Exception as e:
            self.log_message(f"❌ 드래그 앤 드롭 처리 오류: {e}")
            self.log_message("💡 '파일 선택' 버튼을 사용해보세요.")
    
    def select_files(self):
        """파일 선택 대화상자"""
        files = filedialog.askopenfilenames(
            title="ZIP 파일 선택",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        
        if files:
            # 기존 파일 목록에 새 파일들 추가 (중복 제거)
            existing_files = set(self.selected_files)
            new_files = []
            
            for file_path in files:
                if file_path not in existing_files:
                    self.selected_files.append(file_path)
                    new_files.append(file_path)
            
            self.update_files_display()
            
            if new_files:
                self.log_message(f"{len(new_files)}개 파일이 추가되었습니다:")
                for i, file_path in enumerate(new_files, 1):
                    self.log_message(f"  {i}. {Path(file_path).name}")
                self.log_message(f"총 선택된 파일: {len(self.selected_files)}개")
            else:
                self.log_message("⚠️ 선택한 파일들이 이미 목록에 있습니다.")
    
    def clear_files(self):
        """선택된 파일 목록 전체 삭제"""
        if self.selected_files:
            self.selected_files.clear()
            self.update_files_display()
            self.log_message("모든 파일이 목록에서 제거되었습니다.")
        else:
            self.log_message("제거할 파일이 없습니다.")
    
    def select_output_directory(self):
        """출력 폴더 선택 대화상자"""
        directory = filedialog.askdirectory(title="출력 폴더 선택")
        if directory:
            self.output_directory.set(directory)
    
    def update_files_display(self):
        """선택된 파일 목록 표시 업데이트"""
        if not self.selected_files:
            self.files_label.config(text=">>> FILES: NONE SELECTED <<<", fg=self.colors['accent'])
        else:
            file_count = len(self.selected_files)
            if file_count == 1:
                display_text = f">>> LOADED: {Path(self.selected_files[0]).name} <<<"
            elif file_count <= 3:
                file_names = [Path(f).name for f in self.selected_files]
                display_text = f">>> LOADED ({file_count}): {' | '.join(file_names)} <<<"
            else:
                first_files = [Path(f).name for f in self.selected_files[:2]]
                display_text = f">>> LOADED ({file_count}): {' | '.join(first_files)} + {file_count-2} MORE <<<"
            
            self.files_label.config(text=display_text, fg=self.colors['success'])
    
    def log_message(self, message):
        """로그 메시지 출력"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_conversion(self):
        """변환 시작"""
        if not self.selected_files:
            messagebox.showwarning("경고", "변환할 파일을 선택해주세요.")
            return
        
        if self.is_processing:
            messagebox.showinfo("알림", "이미 변환 작업이 진행 중입니다.")
            return
        
        # 출력 폴더 확인
        output_dir = Path(self.output_directory.get())
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                messagebox.showerror("오류", f"출력 폴더를 생성할 수 없습니다: {e}")
                return
        
        # 변환 시작
        self.is_processing = True
        self.convert_button.config(state="disabled", text="🔄 [PROCESSING] CONVERSION IN PROGRESS 🔄")
        self.status_var.set(">>> STATUS: CONVERSION IN PROGRESS <<<")
        self.progress_var.set(0)
        
        # 로그 초기화
        self.log_text.delete(1.0, tk.END)
        self.log_message(">>> OPERATION INITIATED <<<")
        self.log_message(">>> LOADING CONVERSION PROTOCOLS <<<")
        self.log_message(">>> SCANNING TARGET FILES <<<")
        
        # 백그라운드 스레드에서 변환 실행
        thread = threading.Thread(target=self.conversion_worker, daemon=True)
        thread.start()
    
    def conversion_worker(self):
        """백그라운드에서 변환 작업 수행"""
        try:
            total_files = len(self.selected_files)
            successful_count = 0
            failed_files = []
            
            for i, file_path in enumerate(self.selected_files):
                # 메시지 큐를 통한 UI 업데이트
                self.message_queue.put(("progress", (i / total_files) * 100))
                self.message_queue.put(("log", f"\n[{i+1}/{total_files}] 처리 중: {Path(file_path).name}"))
                
                try:
                    success = self.process_single_file(file_path)
                    if success:
                        successful_count += 1
                        self.message_queue.put(("log", f"✅ 완료: {Path(file_path).name}"))
                    else:
                        failed_files.append(file_path)
                        self.message_queue.put(("log", f"❌ 실패: {Path(file_path).name}"))
                        
                except Exception as e:
                    failed_files.append(file_path)
                    self.message_queue.put(("log", f"❌ 오류: {Path(file_path).name} - {str(e)}"))
            
            # 결과 요약
            self.message_queue.put(("progress", 100))
            self.message_queue.put(("log", f"\n=== 변환 완료 ==="))
            self.message_queue.put(("log", f"✅ 성공: {successful_count}개"))
            self.message_queue.put(("log", f"❌ 실패: {len(failed_files)}개"))
            self.message_queue.put(("log", f"📁 총 파일: {total_files}개"))
            
            if failed_files:
                self.message_queue.put(("log", f"\n실패한 파일들:"))
                for failed_file in failed_files:
                    self.message_queue.put(("log", f"  - {Path(failed_file).name}"))
            
            # 완료 상태 업데이트
            if successful_count > 0:
                self.message_queue.put(("status", f"완료: {successful_count}개 파일 변환됨"))
                if failed_files:
                    self.message_queue.put(("show_warning", f"{successful_count}개 파일이 변환되었지만, {len(failed_files)}개 파일에서 오류가 발생했습니다."))
                else:
                    self.message_queue.put(("show_info", f"모든 파일({successful_count}개)이 성공적으로 변환되었습니다!"))
            else:
                self.message_queue.put(("status", "실패: 변환된 파일 없음"))
                self.message_queue.put(("show_error", "모든 파일 변환에 실패했습니다."))
            
        except Exception as e:
            self.message_queue.put(("log", f"💥 예상하지 못한 오류: {str(e)}"))
            self.message_queue.put(("status", "오류 발생"))
            self.message_queue.put(("show_error", f"예상하지 못한 오류가 발생했습니다: {str(e)}"))
        
        finally:
            # UI 상태 복원
            self.message_queue.put(("finish", None))
    
    def process_single_file(self, input_zip_path):
        """단일 ZIP 파일 처리"""
        input_path = Path(input_zip_path)
        output_path = Path(self.output_directory.get()) / input_path.name
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                extract_dir = Path(temp_dir) / "extracted"
                extract_dir.mkdir()
                
                # 1. ZIP 파일 압축 해제
                self.message_queue.put(("log", "  📦 압축 해제 중..."))
                with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # 2. WebP 파일 찾기 및 변환
                webp_files = list(extract_dir.rglob("*.webp"))
                
                if not webp_files:
                    self.message_queue.put(("log", "  ⚠️ WebP 파일을 찾을 수 없습니다"))
                    return False
                
                self.message_queue.put(("log", f"  📁 {len(webp_files)}개의 WebP 파일 발견"))
                
                converted_count = 0
                for webp_file in webp_files:
                    try:
                        # WebP를 JPG로 변환
                        with Image.open(webp_file) as img:
                            if img.mode in ('RGBA', 'LA'):
                                background = Image.new('RGB', img.size, (255, 255, 255))
                                if img.mode == 'RGBA':
                                    background.paste(img, mask=img.split()[-1])
                                else:
                                    background.paste(img)
                                img = background
                            elif img.mode != 'RGB':
                                img = img.convert('RGB')
                            
                            jpg_path = webp_file.with_suffix('.jpg')
                            img.save(jpg_path, 'JPEG', quality=95)
                        
                        webp_file.unlink()
                        converted_count += 1
                        
                    except Exception as e:
                        self.message_queue.put(("log", f"    ❌ {webp_file.name} 변환 실패: {str(e)}"))
                
                if converted_count == 0:
                    return False
                
                self.message_queue.put(("log", f"  ✨ {converted_count}개 파일 변환 완료"))
                
                # 3. 재압축
                self.message_queue.put(("log", "  📦 재압축 중..."))
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in extract_dir.rglob("*"):
                        if file_path.is_file():
                            arcname = file_path.relative_to(extract_dir)
                            zipf.write(file_path, arcname)
                
                return True
                
        except Exception as e:
            self.message_queue.put(("log", f"  💥 처리 중 오류: {str(e)}"))
            return False
    
    def process_queue(self):
        """메시지 큐 처리"""
        try:
            while True:
                message_type, data = self.message_queue.get_nowait()
                
                if message_type == "log":
                    self.log_message(data)
                elif message_type == "progress":
                    self.progress_var.set(data)
                elif message_type == "status":
                    self.status_var.set(data)
                elif message_type == "show_info":
                    messagebox.showinfo("완료", data)
                elif message_type == "show_warning":
                    messagebox.showwarning("주의", data)
                elif message_type == "show_error":
                    messagebox.showerror("오류", data)
                elif message_type == "finish":
                    self.is_processing = False
                    self.convert_button.config(state="normal", text="🚀 [EXECUTE] START CONVERSION 🚀")
                    
        except queue.Empty:
            pass
        
        # 다음 처리를 위해 타이머 재설정
        self.root.after(100, self.process_queue)
    
    def run(self):
        """GUI 실행"""
        # 창 아이콘 설정 (선택사항)
        try:
            # 아이콘이 있다면 설정
            pass
        except:
            pass
        
        # 창 닫기 이벤트 처리
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 해커 스타일 환영 메시지
        welcome_msg = """>>> By noName_Come <<<
================================
🔥 WebP >> JPG CONVERTER v2.0 🔥
================================

>>> OPERATION MANUAL <<<
[1] DRAG & DROP: Target ZIP files into input zone
[2] ADD FILES: Use [+] ADD FILES button for multiple selection
[3] CONFIG: Set target directory for output
[4] EXECUTE: Hit the conversion button to begin operation

>>> SYSTEM CAPABILITIES <<<
✅ MULTI-FILE PROCESSING
✅ DRAG & DROP INTERFACE  
✅ REAL-TIME PROGRESS MONITORING
✅ HIGH-QUALITY JPG OUTPUT (95%)
✅ STEALTH MODE (NO CMD WINDOW)

>>> STATUS: SYSTEM READY <<<
Awaiting user input..."""

        self.log_message(welcome_msg)
        
        # GUI 시작
        self.root.mainloop()
    
    def on_closing(self):
        """창 닫기 이벤트"""
        if self.is_processing:
            if messagebox.askokcancel("종료", "변환 작업이 진행 중입니다. 정말 종료하시겠습니까?"):
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """메인 함수"""
    # DnD 라이브러리 확인
    if not DND_AVAILABLE:
        print("\n📌 참고: 더 나은 사용자 경험을 위해 다음 명령으로 드래그 앤 드롭 라이브러리를 설치하세요:")
        print("pip install tkinterdnd2\n")
    
    # GUI 실행
    app = WebPConverterGUI()
    app.run()


if __name__ == "__main__":
    main()
