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
        self.root.geometry("850x900")  # 높이를 800에서 900으로 증가
        self.root.minsize(700, 850)   # 최소 높이도 750에서 850으로 증가
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
            drop_text = ">>> DRAG & DROP HERE <<<\n[ZIP, WEBP FILES + FOLDERS SUPPORTED]\n🎯 OR USE BUTTONS BELOW 🎯"
        else:
            drop_text = ">>> CLICK BUTTONS BELOW <<<\n[ZIP, WEBP FILES + FOLDERS SUPPORTED]\n🎯 DRAG & DROP NOT AVAILABLE 🎯"
        
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
        select_button.grid(row=0, column=0, padx=(0, 5))
        
        # 폴더 선택 버튼
        folder_button = ttk.Button(button_frame, text="[📁] ADD FOLDER", 
                                  command=self.select_folder, style="Hacker.TButton")
        folder_button.grid(row=0, column=1, padx=(5, 5))
        
        # 전체 삭제 버튼
        clear_button = ttk.Button(button_frame, text="[X] CLEAR ALL", 
                                 command=self.clear_files, style="Hacker.TButton")
        clear_button.grid(row=0, column=2, padx=(5, 0))
        
        # 선택된 파일 목록 표시 (스크롤 가능한 리스트박스로 변경)
        files_list_frame = tk.Frame(file_frame, bg=self.colors['bg'])
        files_list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        files_list_frame.columnconfigure(0, weight=1)
        files_list_frame.rowconfigure(0, weight=1)
        
        # 파일 목록 리스트박스 (다중 선택 지원)
        self.files_listbox = tk.Listbox(files_list_frame, 
                                       height=5,
                                       bg=self.colors['entry_bg'],
                                       fg=self.colors['fg'],
                                       font=("Consolas", 9),
                                       selectbackground=self.colors['accent'],
                                       selectforeground=self.colors['bg'],
                                       bd=1,
                                       relief="solid",
                                       activestyle='none',
                                       selectmode=tk.EXTENDED)  # 다중 선택 모드 활성화
        
        files_scrollbar = tk.Scrollbar(files_list_frame, orient="vertical", 
                                      command=self.files_listbox.yview,
                                      bg=self.colors['button_bg'],
                                      troughcolor=self.colors['bg'],
                                      activebackground=self.colors['accent'])
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        
        self.files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        files_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 개별 삭제 버튼
        remove_button_frame = tk.Frame(file_frame, bg=self.colors['bg'])
        remove_button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        remove_selected_button = ttk.Button(remove_button_frame, text="[-] REMOVE SELECTED", 
                                           command=self.remove_selected_files, style="Hacker.TButton")
        remove_selected_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 다중 선택 안내 라벨
        multi_select_info = tk.Label(remove_button_frame, 
                                    text="💡 Ctrl+클릭 또는 Shift+클릭으로 다중 선택 가능", 
                                    bg=self.colors['bg'],
                                    fg=self.colors['warning'],
                                    font=("Consolas", 8))
        multi_select_info.pack(side=tk.LEFT)
        
        # 상태 표시 라벨
        self.files_status_label = tk.Label(file_frame, text=">>> FILES: NONE SELECTED <<<", 
                                          bg=self.colors['bg'],
                                          fg=self.colors['accent'],
                                          font=("Consolas", 9, "bold"))
        self.files_status_label.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
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
        
        self.log_text = tk.Text(log_frame, height=20, wrap=tk.WORD,  # 높이를 16에서 20으로 증가
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
            
            # ZIP, WebP 파일 및 폴더 필터링 (개선된 파일 타입 검증)
            valid_items = []
            skipped_items = []
            
            for item_path in files:
                if item_path:
                    # 경로 정리
                    clean_path = item_path.strip().strip('"').strip("'")
                    if Path(clean_path).exists():
                        path_obj = Path(clean_path)
                        
                        # 폴더이거나 지원하는 파일 확장자인 경우
                        if path_obj.is_dir():
                            valid_items.append(clean_path)
                        elif clean_path.lower().endswith(('.zip', '.webp')):
                            valid_items.append(clean_path)
                        elif clean_path.lower().endswith(('.jpg', '.jpeg')):
                            skipped_items.append((clean_path, 'JPG'))
                        elif clean_path.lower().endswith('.png'):
                            skipped_items.append((clean_path, 'PNG'))
                        else:
                            # 기타 지원되지 않는 파일 타입
                            skipped_items.append((clean_path, 'UNSUPPORTED'))
            
            if valid_items:
                # 기존 파일 목록에 새 항목들 추가 (중복 제거)
                existing_items = set(self.selected_files)
                new_items = []
                
                for item_path in valid_items:
                    if item_path not in existing_items:
                        self.selected_files.append(item_path)
                        new_items.append(item_path)
                
                self.update_files_display()
                
                if new_items:
                    self.log_message(f"드래그 앤 드롭으로 {len(new_items)}개 항목이 추가되었습니다:")
                    for i, item_path in enumerate(new_items, 1):
                        item_type = "📁 폴더" if Path(item_path).is_dir() else "📄 파일"
                        self.log_message(f"  {i}. {item_type}: {Path(item_path).name}")
                    self.log_message(f"총 선택된 항목: {len(self.selected_files)}개")
                else:
                    self.log_message("⚠️ 선택한 항목들이 이미 목록에 있습니다.")
            
            # 스킵된 파일들에 대한 메시지 표시
            if skipped_items:
                self.log_message(f"\n📋 변환 패스된 파일들 ({len(skipped_items)}개):")
                for file_path, file_type in skipped_items:
                    file_name = Path(file_path).name
                    if file_type == 'JPG':
                        self.log_message(f"  📸 {file_name} - JPG 파일이라서 변환 패스")
                    elif file_type == 'PNG':
                        self.log_message(f"  🖼️ {file_name} - PNG 파일이라서 변환 패스")
                    else:
                        self.log_message(f"  ❓ {file_name} - 지원되지 않는 파일 형식")
            
            if not valid_items and not skipped_items:
                if files:
                    self.log_message("⚠️ 인식할 수 있는 파일이 없습니다.")
                    self.log_message(f"감지된 항목들: {files}")
                else:
                    self.log_message("⚠️ 드래그한 항목을 인식할 수 없습니다.")
                    
        except Exception as e:
            self.log_message(f"❌ 드래그 앤 드롭 처리 오류: {e}")
            self.log_message("💡 '파일 선택' 버튼을 사용해보세요.")
    
    def select_folder(self):
        """폴더 선택 대화상자"""
        folder_path = filedialog.askdirectory(title="WebP 파일이 있는 폴더 선택")
        
        if folder_path:
            # 기존 파일 목록에 폴더 추가 (중복 제거)
            existing_files = set(self.selected_files)
            
            if folder_path not in existing_files:
                self.selected_files.append(folder_path)
                self.update_files_display()
                self.log_message(f"폴더가 추가되었습니다: {Path(folder_path).name}")
                self.log_message(f"총 선택된 항목: {len(self.selected_files)}개")
            else:
                self.log_message("⚠️ 선택한 폴더가 이미 목록에 있습니다.")

    def select_files(self):
        """파일 선택 대화상자"""
        files = filedialog.askopenfilenames(
            title="ZIP 또는 WebP 파일 선택",
            filetypes=[("Supported files", "*.zip;*.webp"), ("ZIP files", "*.zip"), ("WebP files", "*.webp"), ("All files", "*.*")]
        )
        
        if files:
            # 기존 파일 목록에 새 파일들 추가 (중복 제거) 및 파일 타입 검증
            existing_files = set(self.selected_files)
            new_files = []
            skipped_files = []
            
            for file_path in files:
                if file_path not in existing_files:
                    # 파일 타입 검증
                    if file_path.lower().endswith(('.zip', '.webp')):
                        self.selected_files.append(file_path)
                        new_files.append(file_path)
                    elif file_path.lower().endswith(('.jpg', '.jpeg')):
                        skipped_files.append((file_path, 'JPG'))
                    elif file_path.lower().endswith('.png'):
                        skipped_files.append((file_path, 'PNG'))
                    else:
                        skipped_files.append((file_path, 'UNSUPPORTED'))
            
            self.update_files_display()
            
            if new_files:
                self.log_message(f"{len(new_files)}개 파일이 추가되었습니다:")
                for i, file_path in enumerate(new_files, 1):
                    self.log_message(f"  {i}. {Path(file_path).name}")
                self.log_message(f"총 선택된 파일: {len(self.selected_files)}개")
            elif not skipped_files:
                self.log_message("⚠️ 선택한 파일들이 이미 목록에 있습니다.")
            
            # 스킵된 파일들에 대한 메시지 표시
            if skipped_files:
                self.log_message(f"\n📋 변환 패스된 파일들 ({len(skipped_files)}개):")
                for file_path, file_type in skipped_files:
                    file_name = Path(file_path).name
                    if file_type == 'JPG':
                        self.log_message(f"  📸 {file_name} - JPG 파일이라서 변환 패스")
                    elif file_type == 'PNG':
                        self.log_message(f"  🖼️ {file_name} - PNG 파일이라서 변환 패스")
                    else:
                        self.log_message(f"  ❓ {file_name} - 지원되지 않는 파일 형식")
    
    def clear_files(self):
        """선택된 파일 목록 전체 삭제"""
        if self.selected_files:
            self.selected_files.clear()
            self.update_files_display()
            self.log_message("모든 파일이 목록에서 제거되었습니다.")
        else:
            self.log_message("제거할 파일이 없습니다.")
    
    def remove_selected_files(self):
        """리스트박스에서 선택된 파일들 삭제 (다중 선택 지원)"""
        selected_indices = self.files_listbox.curselection()
        
        if not selected_indices:
            self.log_message("⚠️ 삭제할 파일을 선택해주세요.")
            self.log_message("💡 팁: Ctrl+클릭으로 여러 파일 선택, Shift+클릭으로 범위 선택 가능")
            return
        
        # 선택된 파일들의 이름 가져오기 (뒤에서부터 삭제해야 인덱스가 안 꼬임)
        removed_files = []
        selection_count = len(selected_indices)
        
        for index in reversed(selected_indices):
            if 0 <= index < len(self.selected_files):
                removed_file = self.selected_files.pop(index)
                removed_files.append(Path(removed_file).name)
        
        self.update_files_display()
        
        if removed_files:
            if selection_count == 1:
                self.log_message(f"📝 1개 항목이 목록에서 제거되었습니다:")
            else:
                self.log_message(f"📝 {len(removed_files)}개 항목이 다중 선택으로 제거되었습니다:")
            
            for file_name in reversed(removed_files):  # 원래 순서대로 표시
                self.log_message(f"  - {file_name}")
            self.log_message(f"남은 항목: {len(self.selected_files)}개")
    
    def select_output_directory(self):
        """출력 폴더 선택 대화상자"""
        directory = filedialog.askdirectory(title="출력 폴더 선택")
        if directory:
            self.output_directory.set(directory)
    
    def update_files_display(self):
        """선택된 파일/폴더 목록 표시 업데이트"""
        # 리스트박스 내용 업데이트
        self.files_listbox.delete(0, tk.END)
        
        if not self.selected_files:
            self.files_status_label.config(text=">>> FILES: NONE SELECTED <<<", fg=self.colors['accent'])
            self.files_listbox.insert(0, ">>> 파일을 추가하려면 위의 버튼을 사용하거나 드래그 앤 드롭 하세요 <<<")
            self.files_listbox.config(state='disabled')
        else:
            self.files_listbox.config(state='normal')
            item_count = len(self.selected_files)
            
            # 리스트박스에 모든 파일 표시
            for i, file_path in enumerate(self.selected_files):
                item_path = Path(file_path)
                item_type = "📁" if item_path.is_dir() else "📄"
                # 파일 확장자에 따른 추가 아이콘
                if file_path.lower().endswith('.zip'):
                    item_type = "📦"
                elif file_path.lower().endswith('.webp'):
                    item_type = "🖼️"
                
                display_text = f"{item_type} {item_path.name}"
                self.files_listbox.insert(tk.END, display_text)
            
            # 상태 라벨 업데이트
            self.files_status_label.config(
                text=f">>> LOADED: {item_count} ITEMS | MULTI-SELECT & REMOVE <<<", 
                fg=self.colors['success']
            )
    
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
                    # 파일/폴더 타입에 따라 처리 방법 결정
                    if Path(file_path).is_dir():
                        success = self.process_folder(file_path)
                    elif file_path.lower().endswith('.zip'):
                        success = self.process_zip_file(file_path)
                    elif file_path.lower().endswith('.webp'):
                        success = self.process_webp_file(file_path)
                    else:
                        success = False
                        
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
    
    def process_folder(self, folder_path):
        """폴더 내 WebP 파일들 처리 (폴더 구조 유지)"""
        folder = Path(folder_path)
        output_dir = Path(self.output_directory.get())
        
        # 출력 폴더에 원본 폴더 이름으로 새 폴더 생성
        output_folder = output_dir / folder.name
        
        try:
            self.message_queue.put(("log", "  📁 폴더 스캔 중..."))
            
            # 폴더 내 모든 이미지 파일 찾기 (하위 폴더 포함)
            webp_files = list(folder.rglob("*.webp"))
            jpg_files = list(folder.rglob("*.jpg")) + list(folder.rglob("*.jpeg"))
            png_files = list(folder.rglob("*.png"))
            
            if not webp_files:
                self.message_queue.put(("log", "  ⚠️ 폴더 내에 WebP 파일을 찾을 수 없습니다"))
                return False
            
            self.message_queue.put(("log", f"  📄 {len(webp_files)}개의 WebP 파일 발견"))
            
            # JPG/PNG 파일에 대한 패스 메시지
            if jpg_files:
                self.message_queue.put(("log", f"  📸 {len(jpg_files)}개의 JPG 파일 - 변환 패스"))
            if png_files:
                self.message_queue.put(("log", f"  🖼️ {len(png_files)}개의 PNG 파일 - 변환 패스"))
            
            self.message_queue.put(("log", f"  📂 출력 폴더: {output_folder.name}"))
            
            converted_count = 0
            failed_count = 0
            
            for webp_file in webp_files:
                try:
                    # 원본 폴더 기준 상대 경로 유지해서 출력 경로 생성
                    relative_path = webp_file.relative_to(folder)
                    output_path = output_folder / relative_path.with_suffix('.jpg')
                    
                    # 출력 디렉토리 생성 (하위 폴더 구조 유지)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
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
                        
                        img.save(output_path, 'JPEG', quality=95)
                    
                    converted_count += 1
                    # 상대 경로로 표시해서 폴더 구조 확인 가능
                    self.message_queue.put(("log", f"    ✅ {relative_path} → {relative_path.with_suffix('.jpg')}"))
                    
                except Exception as e:
                    failed_count += 1
                    self.message_queue.put(("log", f"    ❌ {relative_path} 변환 실패: {str(e)}"))
            
            if converted_count == 0:
                return False
            
            self.message_queue.put(("log", f"  ✨ 폴더 처리 완료: {converted_count}개 성공, {failed_count}개 실패"))
            self.message_queue.put(("log", f"  📂 결과 저장됨: {output_folder}"))
            return True
            
        except Exception as e:
            self.message_queue.put(("log", f"  💥 폴더 처리 중 오류: {str(e)}"))
            return False

    def process_webp_file(self, input_webp_path):
        """단일 WebP 파일 처리"""
        input_path = Path(input_webp_path)
        output_dir = Path(self.output_directory.get())
        output_path = output_dir / input_path.with_suffix('.jpg').name
        
        try:
            self.message_queue.put(("log", "  🖼️ WebP 이미지 로딩 중..."))
            
            # WebP를 JPG로 변환
            with Image.open(input_webp_path) as img:
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                self.message_queue.put(("log", "  ✨ JPG로 변환 중..."))
                img.save(output_path, 'JPEG', quality=95)
            
            self.message_queue.put(("log", f"  💾 저장 완료: {output_path.name}"))
            return True
            
        except Exception as e:
            self.message_queue.put(("log", f"  💥 처리 중 오류: {str(e)}"))
            return False
    
    def process_zip_file(self, input_zip_path):
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
                
                # 2. 이미지 파일 찾기 및 변환
                webp_files = list(extract_dir.rglob("*.webp"))
                jpg_files = list(extract_dir.rglob("*.jpg")) + list(extract_dir.rglob("*.jpeg"))
                png_files = list(extract_dir.rglob("*.png"))
                
                if not webp_files:
                    self.message_queue.put(("log", "  ⚠️ WebP 파일을 찾을 수 없습니다"))
                    return False
                
                self.message_queue.put(("log", f"  📁 {len(webp_files)}개의 WebP 파일 발견"))
                
                # JPG/PNG 파일에 대한 패스 메시지
                if jpg_files:
                    self.message_queue.put(("log", f"  📸 {len(jpg_files)}개의 JPG 파일 - 변환 패스"))
                if png_files:
                    self.message_queue.put(("log", f"  🖼️ {len(png_files)}개의 PNG 파일 - 변환 패스"))
                
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

