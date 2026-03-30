# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import vlc
import platform
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# 📁 ОПРЕДЕЛЕНИЕ ДИРЕКТОРИЙ
# ─────────────────────────────────────────────────────────────
def get_downloads_folder():
    """Получение пути к папке Загрузки"""
    if platform.system() == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            downloads = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
            winreg.CloseKey(key)
            if os.path.exists(downloads):
                return downloads
        except:
            pass
        
        profile = os.environ.get('USERPROFILE', '')
        downloads = os.path.join(profile, 'Downloads')
        if os.path.exists(downloads):
            return downloads
    
    downloads = os.path.expanduser('~/Downloads')
    if os.path.exists(downloads):
        return downloads
    
    return os.path.expanduser('~')

class SettingsManager:
    """Управление сохранением и загрузкой настроек"""
    
    def __init__(self):
        downloads_folder = get_downloads_folder()
        self.settings_dir = Path(downloads_folder) / "PythonVLCPlayer"
        self.settings_file = self.settings_dir / "settings.json"
        self.screenshots_dir = self.settings_dir / "screenshots"
        self.playlists_dir = self.settings_dir / "playlists"
        
        self.create_folders()
        
        self.default_settings = {
            "theme": "Modrinth Dark",
            "volume": 50,
            "font_size": 10,
            "border_radius": 10,
            "last_video": None,
            "last_directory": None,
            "window_width": 1000,
            "window_height": 700,
            "window_x": None,
            "window_y": None,
            "remember_last_video": True,
            "auto_play": True,
            "show_hotkeys": True,
            "animation_enabled": True,
            "border_enabled": True,
            "custom_colors": {},
            "playback_speed": 1.0,
            "last_opened_files": [],
            "max_history": 15,
            "screenshots_folder": str(self.screenshots_dir),
            "auto_save_playlist": True,
            "control_panel_opacity": 0.95,
            "hide_controls_delay": 10,
            "seek_step": 10,
            "volume_step": 5,
            "last_playlist": None,
            "recent_files": []
        }
        
        self.settings = self.load_settings()
        self.save_settings()
    
    def create_folders(self):
        try:
            self.settings_dir.mkdir(parents=True, exist_ok=True)
            self.screenshots_dir.mkdir(parents=True, exist_ok=True)
            self.playlists_dir.mkdir(parents=True, exist_ok=True)
            
            readme_file = self.settings_dir / "README.txt"
            if not readme_file.exists():
                with open(readme_file, 'w', encoding='utf-8') as f:
                    f.write("""Python VLC Player - Папка настроек
=====================================

Эта папка содержит настройки вашего плеера:

📁 screenshots/ - скриншоты видео
📁 playlists/ - сохраненные плейлисты
📄 settings.json - файл настроек

Не удаляйте эту папку, если хотите сохранить свои настройки!

Дата создания: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return True
        except Exception as e:
            print(f"Ошибка создания папок: {e}")
            return False
    
    def load_settings(self):
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    settings = self.default_settings.copy()
                    settings.update(loaded)
                    return settings
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
        return self.default_settings.copy()
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
            return False
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
    
    def add_to_history(self, filepath):
        if not filepath or not os.path.isfile(filepath):
            return
        
        if filepath in self.settings["last_opened_files"]:
            self.settings["last_opened_files"].remove(filepath)
        
        self.settings["last_opened_files"].insert(0, filepath)
        max_history = self.settings.get("max_history", 15)
        self.settings["last_opened_files"] = self.settings["last_opened_files"][:max_history]
        
        if filepath not in self.settings.get("recent_files", []):
            recent = self.settings.get("recent_files", [])
            recent.insert(0, filepath)
            self.settings["recent_files"] = recent[:15]
        
        self.save_settings()
    
    def get_last_video(self):
        last_video = self.settings.get("last_video")
        if last_video and os.path.isfile(last_video):
            return last_video
        return None
    
    def get_history(self):
        return [f for f in self.settings.get("last_opened_files", []) if os.path.isfile(f)]
    
    def take_screenshot(self, video_player):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.screenshots_dir / f"screenshot_{timestamp}.png"
            video_player.player.video_take_snapshot(0, str(filename), 0, 0)
            return str(filename)
        except Exception as e:
            print(f"Ошибка создания скриншота: {e}")
        return None

# ─────────────────────────────────────────────────────────────
# 🎨 РАСШИРЕННЫЕ ТЕМЫ MODRINTH С ГРАДИЕНТАМИ
# ─────────────────────────────────────────────────────────────
MODRINTH_THEMES = {
    # Базовые темы с градиентами
    "Modrinth Dark": {
        "bg_primary": "#0a0a0a", "bg_secondary": "#141414", "bg_tertiary": "#1e1e1e",
        "gradient_start": "#0a0a0a", "gradient_end": "#1a1a2e",
        "accent": "#00ff88", "accent_hover": "#33ffaa",
        "text_primary": "#ffffff", "text_secondary": "#b0b0b0",
        "video_bg": "#000000", "border": "#2a2a3a", "font": "Segoe UI",
    },
    "Modrinth Light": {
        "bg_primary": "#ffffff", "bg_secondary": "#f8f8f8", "bg_tertiary": "#f0f0f0",
        "gradient_start": "#ffffff", "gradient_end": "#e8eef4",
        "accent": "#00cc66", "accent_hover": "#00dd77",
        "text_primary": "#1a1a1a", "text_secondary": "#666666",
        "video_bg": "#000000", "border": "#e0e0e0", "font": "Segoe UI",
    },
    "Modrinth OLED": {
        "bg_primary": "#000000", "bg_secondary": "#050505", "bg_tertiary": "#0a0a0a",
        "gradient_start": "#000000", "gradient_end": "#0a0a1a",
        "accent": "#00ff6b", "accent_hover": "#6bff9e",
        "text_primary": "#ffffff", "text_secondary": "#888888",
        "video_bg": "#000000", "border": "#1a1a2a", "font": "Segoe UI",
    },
    
    # Природные темы с градиентами
    "Modrinth Forest": {
        "bg_primary": "#0a1a0f", "bg_secondary": "#0f2a14", "bg_tertiary": "#143a19",
        "gradient_start": "#0a1a0f", "gradient_end": "#1a3a2a",
        "accent": "#6eff8e", "accent_hover": "#8effaa",
        "text_primary": "#e8ffe8", "text_secondary": "#b8ffb8",
        "video_bg": "#051005", "border": "#2a6a3a", "font": "Segoe UI",
    },
    "Modrinth Ocean": {
        "bg_primary": "#0a1525", "bg_secondary": "#0f2035", "bg_tertiary": "#142b45",
        "gradient_start": "#0a1525", "gradient_end": "#1a3555",
        "accent": "#4acdff", "accent_hover": "#7addff",
        "text_primary": "#e6f3ff", "text_secondary": "#b8d6ff",
        "video_bg": "#05101a", "border": "#2a5a8a", "font": "Segoe UI",
    },
    "Modrinth Jungle": {
        "bg_primary": "#0a1f0a", "bg_secondary": "#0f2f0f", "bg_tertiary": "#143f14",
        "gradient_start": "#0a1f0a", "gradient_end": "#1a4f1a",
        "accent": "#4aff4a", "accent_hover": "#7aff7a",
        "text_primary": "#e0ffe0", "text_secondary": "#b0ffb0",
        "video_bg": "#051005", "border": "#2a8a2a", "font": "Segoe UI",
    },
    "Modrinth Sunset": {
        "bg_primary": "#2a0a1a", "bg_secondary": "#3a1425", "bg_tertiary": "#4a1e30",
        "gradient_start": "#2a0a1a", "gradient_end": "#5a2a3a",
        "accent": "#ff66aa", "accent_hover": "#ff88bb",
        "text_primary": "#ffe6f0", "text_secondary": "#ffccdd",
        "video_bg": "#1a0510", "border": "#aa4a6a", "font": "Segoe UI",
    },
    "Modrinth Aurora": {
        "bg_primary": "#0a0a2a", "bg_secondary": "#0f0f3a", "bg_tertiary": "#14144a",
        "gradient_start": "#0a0a2a", "gradient_end": "#2a2a6a",
        "accent": "#ff66cc", "accent_hover": "#ff88dd",
        "text_primary": "#f0e6ff", "text_secondary": "#c0b0ff",
        "video_bg": "#050518", "border": "#6a4aff", "font": "Segoe UI",
    },
    "Modrinth Cyberpunk": {
        "bg_primary": "#0a0a1a", "bg_secondary": "#12122a", "bg_tertiary": "#1a1a3a",
        "gradient_start": "#0a0a1a", "gradient_end": "#3a0a5a",
        "accent": "#ff00ff", "accent_hover": "#ff44ff",
        "text_primary": "#00ffff", "text_secondary": "#88aaff",
        "video_bg": "#000000", "border": "#ff00ff", "font": "Segoe UI",
    },
    "Modrinth Matrix": {
        "bg_primary": "#0a1a0a", "bg_secondary": "#0f2a0f", "bg_tertiary": "#143a14",
        "gradient_start": "#0a1a0a", "gradient_end": "#1a4a1a",
        "accent": "#33ff33", "accent_hover": "#66ff66",
        "text_primary": "#33ff33", "text_secondary": "#88ff88",
        "video_bg": "#000000", "border": "#33cc33", "font": "Consolas",
    },
    "Modrinth Sakura": {
        "bg_primary": "#2a1a2a", "bg_secondary": "#3a2540", "bg_tertiary": "#4a3055",
        "gradient_start": "#2a1a2a", "gradient_end": "#5a3a6a",
        "accent": "#ff99cc", "accent_hover": "#ffbbdd",
        "text_primary": "#ffe6f0", "text_secondary": "#ffccdd",
        "video_bg": "#1a0f1a", "border": "#ff99cc", "font": "Segoe UI",
    },
    "Modrinth Midnight": {
        "bg_primary": "#0a0a2a", "bg_secondary": "#0f0f3a", "bg_tertiary": "#14144a",
        "gradient_start": "#0a0a2a", "gradient_end": "#1a1a5a",
        "accent": "#4a6eff", "accent_hover": "#6c8aff",
        "text_primary": "#e6e6ff", "text_secondary": "#b8b8e6",
        "video_bg": "#050518", "border": "#2a2a6e", "font": "Segoe UI",
    },
    "Modrinth Arctic": {
        "bg_primary": "#0a202f", "bg_secondary": "#0f2a3f", "bg_tertiary": "#14354f",
        "gradient_start": "#0a202f", "gradient_end": "#2a5070",
        "accent": "#7cb9e8", "accent_hover": "#9bcaf0",
        "text_primary": "#e0f0ff", "text_secondary": "#b0d0ff",
        "video_bg": "#0a1a2a", "border": "#4a6a8a", "font": "Segoe UI",
    },
    "Modrinth Lavender": {
        "bg_primary": "#251a35", "bg_secondary": "#352545", "bg_tertiary": "#453055",
        "gradient_start": "#251a35", "gradient_end": "#553a75",
        "accent": "#b87cff", "accent_hover": "#ca9bff",
        "text_primary": "#f2e6ff", "text_secondary": "#c9b3e6",
        "video_bg": "#1a0f25", "border": "#6b4e7c", "font": "Segoe UI",
    },
    "Modrinth Neon": {
        "bg_primary": "#1a0a2a", "bg_secondary": "#2a1440", "bg_tertiary": "#3a1e55",
        "gradient_start": "#1a0a2a", "gradient_end": "#5a2a8a",
        "accent": "#ff44ff", "accent_hover": "#ff77ff",
        "text_primary": "#ff44ff", "text_secondary": "#ff88ff",
        "video_bg": "#0a0515", "border": "#aa44aa", "font": "Segoe UI",
    },
    "Modrinth Blood": {
        "bg_primary": "#2a0a0a", "bg_secondary": "#3a1414", "bg_tertiary": "#4a1e1e",
        "gradient_start": "#2a0a0a", "gradient_end": "#6a2a2a",
        "accent": "#ff4444", "accent_hover": "#ff6666",
        "text_primary": "#ffdddd", "text_secondary": "#ffaaaa",
        "video_bg": "#1a0505", "border": "#aa4444", "font": "Segoe UI",
    },
    "Modrinth Gold": {
        "bg_primary": "#2a2410", "bg_secondary": "#3a301a", "bg_tertiary": "#4a3c24",
        "gradient_start": "#2a2410", "gradient_end": "#6a542a",
        "accent": "#ffd700", "accent_hover": "#ffe44d",
        "text_primary": "#fff4e0", "text_secondary": "#ffe4b0",
        "video_bg": "#1a1408", "border": "#d4af37", "font": "Segoe UI",
    },
    "Modrinth Emerald": {
        "bg_primary": "#0a2a1a", "bg_secondary": "#103a20", "bg_tertiary": "#164a26",
        "gradient_start": "#0a2a1a", "gradient_end": "#2a6a3a",
        "accent": "#50c878", "accent_hover": "#72d48e",
        "text_primary": "#e0ffe0", "text_secondary": "#b0ffb0",
        "video_bg": "#051a0a", "border": "#2e8b57", "font": "Segoe UI",
    },
    "Modrinth Galaxy": {
        "bg_primary": "#0a0a2a", "bg_secondary": "#101038", "bg_tertiary": "#161646",
        "gradient_start": "#0a0a2a", "gradient_end": "#4a2a8a",
        "accent": "#bc13fe", "accent_hover": "#cc34ff",
        "text_primary": "#f0e0ff", "text_secondary": "#c0a0ff",
        "video_bg": "#050518", "border": "#8a2be2", "font": "Segoe UI",
    },
    "Modrinth Vaporwave": {
        "bg_primary": "#1a0a2a", "bg_secondary": "#2a1a3a", "bg_tertiary": "#3a2a4a",
        "gradient_start": "#1a0a2a", "gradient_end": "#6a4a8a",
        "accent": "#ff71ce", "accent_hover": "#ff91de",
        "text_primary": "#e0b0ff", "text_secondary": "#c090ff",
        "video_bg": "#0f051a", "border": "#ff71ce", "font": "Segoe UI",
    },
    "Modrinth Fire": {
        "bg_primary": "#2a1a0a", "bg_secondary": "#3a2a14", "bg_tertiary": "#4a3a1e",
        "gradient_start": "#2a1a0a", "gradient_end": "#8a4a1a",
        "accent": "#ff5500", "accent_hover": "#ff7733",
        "text_primary": "#ffe0d0", "text_secondary": "#ffb090",
        "video_bg": "#1a0f05", "border": "#cc5500", "font": "Segoe UI",
    },
    "Modrinth Ice": {
        "bg_primary": "#1a2a3a", "bg_secondary": "#203a4a", "bg_tertiary": "#264a5a",
        "gradient_start": "#1a2a3a", "gradient_end": "#4a6a8a",
        "accent": "#9ed9ff", "accent_hover": "#bee9ff",
        "text_primary": "#ffffff", "text_secondary": "#e0f0ff",
        "video_bg": "#0f1a2a", "border": "#7cb9e8", "font": "Segoe UI",
    },
    "Modrinth Royal": {
        "bg_primary": "#1a0a2a", "bg_secondary": "#2a1a3a", "bg_tertiary": "#3a2a4a",
        "gradient_start": "#1a0a2a", "gradient_end": "#6a2a8a",
        "accent": "#da70d6", "accent_hover": "#ea90e6",
        "text_primary": "#f0e6ff", "text_secondary": "#d0b0ff",
        "video_bg": "#0f051a", "border": "#ba55d3", "font": "Segoe UI",
    },
    "Modrinth Aqua": {
        "bg_primary": "#0a2a2a", "bg_secondary": "#103a3a", "bg_tertiary": "#164a4a",
        "gradient_start": "#0a2a2a", "gradient_end": "#2a6a6a",
        "accent": "#33ffff", "accent_hover": "#66ffff",
        "text_primary": "#e0ffff", "text_secondary": "#b0ffff",
        "video_bg": "#051a1a", "border": "#00cccc", "font": "Segoe UI",
    },
    "Modrinth Halloween": {
        "bg_primary": "#2a1a0a", "bg_secondary": "#3a2a14", "bg_tertiary": "#4a3a1e",
        "gradient_start": "#2a1a0a", "gradient_end": "#6a3a1a",
        "accent": "#ff6600", "accent_hover": "#ff8833",
        "text_primary": "#ffcc88", "text_secondary": "#ffaa66",
        "video_bg": "#1a0f05", "border": "#ff4400", "font": "Segoe UI",
    },
    "Modrinth Christmas": {
        "bg_primary": "#1a2a1a", "bg_secondary": "#2a3a2a", "bg_tertiary": "#3a4a3a",
        "gradient_start": "#1a2a1a", "gradient_end": "#4a6a4a",
        "accent": "#ff4d4d", "accent_hover": "#ff6b6b",
        "text_primary": "#e0ffe0", "text_secondary": "#c0ffc0",
        "video_bg": "#0f1a0f", "border": "#228b22", "font": "Segoe UI",
    },
}

# ─────────────────────────────────────────────────────────────
# 🎨 КЛАСС ДЛЯ СОЗДАНИЯ ГРАДИЕНТОВ
# ─────────────────────────────────────────────────────────────
class GradientFrame(tk.Canvas):
    """Кастомный фрейм с градиентным фоном"""
    def __init__(self, parent, color_start, color_end, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.color_start = color_start
        self.color_end = color_end
        self.bind('<Configure>', self._draw_gradient)
    
    def _draw_gradient(self, event=None):
        self.delete('gradient')
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1:
            return
        
        # Вертикальный градиент
        steps = 50
        for i in range(steps):
            ratio = i / steps
            r = int(int(self.color_start[1:3], 16) * (1 - ratio) + 
                    int(self.color_end[1:3], 16) * ratio)
            g = int(int(self.color_start[3:5], 16) * (1 - ratio) + 
                    int(self.color_end[3:5], 16) * ratio)
            b = int(int(self.color_start[5:7], 16) * (1 - ratio) + 
                    int(self.color_end[5:7], 16) * ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'
            y1 = (i * height) // steps
            y2 = ((i + 1) * height) // steps
            self.create_rectangle(0, y1, width, y2, fill=color, outline='', tags='gradient')
        self.lower('gradient')

class RoundedButton(tk.Canvas):
    """Кастомная кнопка со скругленными углами"""
    def __init__(self, parent, text, command, bg_color, hover_color, text_color="#ffffff", 
                 radius=10, width=100, height=30, font=("Segoe UI", 10, "bold")):
        super().__init__(parent, highlightthickness=0, width=width, height=height, bg=parent.cget('bg'))
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.radius = radius
        self.text = text
        self.font = font
        self.is_hovered = False
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        
        self._draw_button(self.bg_color)
    
    def _draw_button(self, color):
        self.delete('all')
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1 or h <= 1:
            w, h = 100, 30
        
        # Рисуем скругленный прямоугольник
        self.create_round_rect(0, 0, w, h, self.radius, fill=color, outline='')
        # Рисуем текст
        self.create_text(w//2, h//2, text=self.text, fill=self.text_color, font=self.font)
    
    def create_round_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = []
        points.append((x1 + radius, y1))
        points.append((x2 - radius, y1))
        points.append((x2, y1))
        points.append((x2, y1 + radius))
        points.append((x2, y2 - radius))
        points.append((x2, y2))
        points.append((x2 - radius, y2))
        points.append((x1 + radius, y2))
        points.append((x1, y2))
        points.append((x1, y2 - radius))
        points.append((x1, y1 + radius))
        points.append((x1, y1))
        
        coords = []
        for p in points:
            coords.extend(p)
        
        return self.create_polygon(coords, smooth=True, **kwargs)
    
    def on_enter(self, event):
        if not self.is_hovered:
            self.is_hovered = True
            self._draw_button(self.hover_color)
    
    def on_leave(self, event):
        if self.is_hovered:
            self.is_hovered = False
            self._draw_button(self.bg_color)
    
    def on_click(self, event):
        if self.command:
            self.command()

class FullscreenPlayer:
    """Класс для управления полноэкранным режимом"""
    def __init__(self, video_player):
        self.video_player = video_player
        self.is_fullscreen = False
        self.original_geometry = None
        self.controls_visible = True
        self.hide_timer = None
        self.mouse_timer = None
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.control_panel = None
        self.progress_update_id = None
        
    def toggle(self):
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()
    
    def enter_fullscreen(self):
        if not self.is_fullscreen:
            self.original_geometry = self.video_player.root.geometry()
            self.video_player.root.attributes('-fullscreen', True)
            self.is_fullscreen = True
            self.controls_visible = True
            
            self.video_player.control_frame.pack_forget()
            self.create_floating_controls()
            
            # Привязываем события
            self.video_player.root.bind('<Motion>', self.on_mouse_move)
            self.video_player.root.bind('<KeyPress-Escape>', lambda e: self.toggle())
            
            # Показываем панель
            self.show_controls()
            
            # Запускаем таймер скрытия
            self.start_hide_timer()
    
    def exit_fullscreen(self):
        if self.is_fullscreen:
            # Останавливаем все таймеры
            if self.hide_timer:
                self.video_player.root.after_cancel(self.hide_timer)
                self.hide_timer = None
            
            # Удаляем привязки событий
            self.video_player.root.unbind('<Motion>')
            self.video_player.root.unbind('<KeyPress-Escape>')
            
            # Выходим из полноэкранного режима
            self.video_player.root.attributes('-fullscreen', False)
            if self.original_geometry:
                self.video_player.root.geometry(self.original_geometry)
            
            # Уничтожаем плавающую панель
            if self.control_panel:
                self.control_panel.destroy()
                self.control_panel = None
            
            # Восстанавливаем основную панель управления
            self.video_player.control_frame.pack(fill=tk.X, side=tk.BOTTOM)
            
            self.is_fullscreen = False
            self.controls_visible = False
    
    def create_floating_controls(self):
        """Создание плавающей панели управления с градиентами и скругленными углами"""
        theme_name = self.video_player.settings.get("theme", "Modrinth Dark")
        theme = MODRINTH_THEMES.get(theme_name, MODRINTH_THEMES["Modrinth Dark"])
        
        self.control_panel = tk.Toplevel(self.video_player.root)
        self.control_panel.overrideredirect(True)
        self.control_panel.attributes('-topmost', True)
        self.control_panel.attributes('-alpha', self.video_player.settings.get("control_panel_opacity", 0.95))
        self.control_panel.configure(bg=theme["bg_secondary"])
        
        # Создаем градиентный фон для панели
        panel_bg = GradientFrame(self.control_panel, theme["gradient_start"], theme["gradient_end"])
        panel_bg.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Основной фрейм с закругленными углами
        panel_frame = tk.Frame(panel_bg, bg=theme["bg_secondary"], bd=0)
        panel_frame.pack(padx=12, pady=10, fill=tk.BOTH, expand=True)
        
        # Прогресс бар
        progress_frame = tk.Frame(panel_frame, bg=theme["bg_secondary"])
        progress_frame.pack(fill=tk.X, padx=8, pady=(5, 8))
        
        self.float_time_label = tk.Label(progress_frame, text="00:00 / 00:00",
                                         font=("Segoe UI", 11, "bold"), 
                                         bg=theme["bg_secondary"], 
                                         fg=theme["text_secondary"])
        self.float_time_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.float_scale = tk.Scale(progress_frame, from_=0, to=100, 
                                    orient=tk.HORIZONTAL,
                                    bg=theme["bg_secondary"], 
                                    fg=theme["accent"], 
                                    highlightthickness=0,
                                    troughcolor=theme["bg_tertiary"], 
                                    sliderrelief=tk.FLAT,
                                    length=550,
                                    sliderlength=18)
        self.float_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.float_scale.bind("<ButtonRelease-1>", self.float_set_time)
        
        # Кнопки управления
        buttons_frame = tk.Frame(panel_frame, bg=theme["bg_secondary"])
        buttons_frame.pack(pady=(5, 8))
        
        # Кнопка перемотки назад
        self.float_btn_back = RoundedButton(
            buttons_frame, text="◀◀ 10", command=self.float_seek_back,
            bg_color=theme["bg_tertiary"], hover_color=theme["accent"],
            text_color=theme["text_primary"], radius=8, width=70, height=34,
            font=("Segoe UI", 10, "bold")
        )
        self.float_btn_back.pack(side=tk.LEFT, padx=4)
        
        # Кнопка Play/Pause
        self.float_btn_play = RoundedButton(
            buttons_frame, text="▶ Воспр.", command=self.float_play_pause,
            bg_color=theme["accent"], hover_color=theme["accent_hover"],
            text_color="#ffffff", radius=8, width=85, height=34,
            font=("Segoe UI", 10, "bold")
        )
        self.float_btn_play.pack(side=tk.LEFT, padx=4)
        
        # Кнопка Stop
        self.float_btn_stop = RoundedButton(
            buttons_frame, text="⏹ Стоп", command=self.float_stop,
            bg_color=theme["bg_tertiary"], hover_color=theme["accent"],
            text_color=theme["text_primary"], radius=8, width=70, height=34,
            font=("Segoe UI", 10, "bold")
        )
        self.float_btn_stop.pack(side=tk.LEFT, padx=4)
        
        # Кнопка перемотки вперед
        self.float_btn_forward = RoundedButton(
            buttons_frame, text="10 ▶▶", command=self.float_seek_forward,
            bg_color=theme["bg_tertiary"], hover_color=theme["accent"],
            text_color=theme["text_primary"], radius=8, width=70, height=34,
            font=("Segoe UI", 10, "bold")
        )
        self.float_btn_forward.pack(side=tk.LEFT, padx=4)
        
        # Разделитель
        sep = tk.Frame(buttons_frame, width=2, bg=theme["border"], height=30)
        sep.pack(side=tk.LEFT, padx=8, fill=tk.Y)
        
        # Громкость
        vol_frame = tk.Frame(buttons_frame, bg=theme["bg_secondary"])
        vol_frame.pack(side=tk.LEFT, padx=5)
        
        vol_label = tk.Label(vol_frame, text="🔊", font=("Segoe UI", 12), 
                            bg=theme["bg_secondary"], fg=theme["text_secondary"])
        vol_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.float_vol_scale = tk.Scale(vol_frame, from_=0, to=100, 
                                        orient=tk.HORIZONTAL, length=110,
                                        bg=theme["bg_secondary"], 
                                        fg=theme["accent"], 
                                        highlightthickness=0,
                                        troughcolor=theme["bg_tertiary"], 
                                        sliderrelief=tk.FLAT,
                                        command=self.float_set_volume)
        self.float_vol_scale.pack(side=tk.LEFT)
        
        self.float_vol_label = tk.Label(vol_frame, text="50%", 
                                        font=("Segoe UI", 10, "bold"),
                                        bg=theme["bg_secondary"], 
                                        fg=theme["text_secondary"],
                                        width=4)
        self.float_vol_label.pack(side=tk.LEFT, padx=5)
        
        # Кнопка выхода
        self.float_btn_exit = RoundedButton(
            buttons_frame, text="✖ Выход", command=self.toggle,
            bg_color=theme["bg_tertiary"], hover_color="#ff4444",
            text_color=theme["text_primary"], radius=8, width=75, height=34,
            font=("Segoe UI", 10, "bold")
        )
        self.float_btn_exit.pack(side=tk.LEFT, padx=5)
        
        # Информационная строка
        info_frame = tk.Frame(panel_frame, bg=theme["bg_secondary"])
        info_frame.pack(fill=tk.X, padx=8, pady=(0, 5))
        
        info_label = tk.Label(info_frame, 
                              text="🎮 Пробел: Play/Pause | ←/→: -/+10 сек | ↑/↓: Громкость | Esc: Выход",
                              font=("Segoe UI", 8),
                              bg=theme["bg_secondary"], 
                              fg=theme["text_secondary"])
        info_label.pack()
        
        # Устанавливаем текущие значения
        current_vol = self.video_player.player.audio_get_volume()
        self.float_vol_scale.set(current_vol)
        self.float_vol_label.config(text=f"{current_vol}%")
        
        self.video_player.float_scale = self.float_scale
        self.video_player.float_time_label = self.float_time_label
        self.video_player.float_btn_play = self.float_btn_play
        
        self.update_panel_position()
        self.start_progress_update()
    
    def update_panel_position(self):
        if self.control_panel and self.is_fullscreen:
            try:
                screen_width = self.video_player.root.winfo_screenwidth()
                screen_height = self.video_player.root.winfo_screenheight()
                
                self.control_panel.update_idletasks()
                panel_width = self.control_panel.winfo_width()
                panel_height = self.control_panel.winfo_height()
                
                if panel_width < 100:
                    self.control_panel.after(50, self.update_panel_position)
                    return
                
                x = (screen_width - panel_width) // 2
                y = screen_height - panel_height - 40
                
                self.control_panel.geometry(f"+{x}+{y}")
            except:
                pass
    
    def show_controls(self):
        if self.control_panel and self.is_fullscreen:
            try:
                self.control_panel.deiconify()
                self.controls_visible = True
                self.update_panel_position()
                # Обновляем позицию при показе
                self.video_player.root.after(10, self.update_panel_position)
            except:
                pass
    
    def hide_controls(self):
        if self.control_panel and self.is_fullscreen and self.controls_visible:
            try:
                # Проверяем позицию курсора
                pointer_x = self.video_player.root.winfo_pointerx()
                pointer_y = self.video_player.root.winfo_pointery()
                
                panel_x = self.control_panel.winfo_x()
                panel_y = self.control_panel.winfo_y()
                panel_width = self.control_panel.winfo_width()
                panel_height = self.control_panel.winfo_height()
                
                # Если курсор на панели - не скрываем
                if (panel_x <= pointer_x <= panel_x + panel_width and
                    panel_y <= pointer_y <= panel_y + panel_height):
                    self.start_hide_timer()
                    return
                    
                # Скрываем панель
                self.control_panel.withdraw()
                self.controls_visible = False
            except:
                pass
    
    def start_hide_timer(self):
        if self.hide_timer:
            self.video_player.root.after_cancel(self.hide_timer)
        
        delay = self.video_player.settings.get("hide_controls_delay", 10) * 1000
        self.hide_timer = self.video_player.root.after(delay, self.hide_controls)
    
    def on_mouse_move(self, event):
        # Проверяем, что курсор действительно двигается
        if (abs(event.x - self.last_mouse_x) > 2 or 
            abs(event.y - self.last_mouse_y) > 2):
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            
            # Показываем панель если она скрыта
            if not self.controls_visible:
                self.show_controls()
            # Перезапускаем таймер
            self.start_hide_timer()
    
    def start_progress_update(self):
        def update_progress():
            if self.is_fullscreen and self.control_panel:
                try:
                    if self.video_player.player.is_playing():
                        current_time = self.video_player.player.get_time()
                        total_time = self.video_player.player.get_length()
                        if total_time > 0 and total_time != -1:
                            percent = (current_time / total_time) * 100
                            self.float_scale.set(percent)
                            curr_min, curr_sec = divmod(current_time // 1000, 60)
                            tot_min, tot_sec = divmod(total_time // 1000, 60)
                            self.float_time_label.config(
                                text=f"{curr_min:02d}:{curr_sec:02d} / {tot_min:02d}:{tot_sec:02d}"
                            )
                    
                    # Обновляем состояние кнопки Play/Pause
                    if self.video_player.is_playing and not self.video_player.is_paused:
                        if hasattr(self.float_btn_play, 'text') and self.float_btn_play.text != "⏸ Пауза":
                            self.float_btn_play.text = "⏸ Пауза"
                            self.float_btn_play._draw_button(self.float_btn_play.bg_color)
                    else:
                        if hasattr(self.float_btn_play, 'text') and self.float_btn_play.text != "▶ Воспр.":
                            self.float_btn_play.text = "▶ Воспр."
                            self.float_btn_play._draw_button(self.float_btn_play.bg_color)
                    
                    current_vol = self.video_player.player.audio_get_volume()
                    if int(self.float_vol_scale.get()) != current_vol:
                        self.float_vol_scale.set(current_vol)
                        self.float_vol_label.config(text=f"{current_vol}%")
                except:
                    pass
                
                self.progress_update_id = self.video_player.root.after(100, update_progress)
        
        update_progress()
    
    def float_play_pause(self):
        if self.video_player.is_playing:
            if self.video_player.is_paused:
                self.video_player.play_video()
            else:
                self.video_player.pause_video()
        else:
            if self.video_player.current_media_path:
                self.video_player.play_video()
        self.start_hide_timer()
    
    def float_stop(self):
        self.video_player.stop_video()
        self.start_hide_timer()
    
    def float_seek_back(self):
        if self.video_player.player.is_playing():
            current_time = self.video_player.player.get_time()
            new_time = max(0, current_time - 10000)
            self.video_player.player.set_time(new_time)
        self.start_hide_timer()
    
    def float_seek_forward(self):
        if self.video_player.player.is_playing():
            current_time = self.video_player.player.get_time()
            total_time = self.video_player.player.get_length()
            if total_time > 0:
                new_time = min(total_time, current_time + 10000)
                self.video_player.player.set_time(new_time)
        self.start_hide_timer()
    
    def float_set_time(self, event):
        total_time = self.video_player.player.get_length()
        if total_time > 0:
            seek_time = (float(self.float_scale.get()) / 100) * total_time
            self.video_player.player.set_time(int(seek_time))
        self.start_hide_timer()
    
    def float_set_volume(self, val):
        volume = int(float(val))
        self.video_player.player.audio_set_volume(volume)
        self.float_vol_label.config(text=f"{volume}%")
        if hasattr(self.video_player, 'scale_vol'):
            self.video_player.scale_vol.set(volume)
            self.video_player.vol_label.config(text=f"{volume}%")
        self.start_hide_timer()
    
    def update_theme(self):
        if self.control_panel and self.is_fullscreen:
            was_visible = self.controls_visible
            self.control_panel.destroy()
            self.create_floating_controls()
            if was_visible:
                self.show_controls()
            else:
                self.control_panel.withdraw()

class ModrinthStyleWindow(tk.Toplevel):
    def __init__(self, parent, video_player):
        super().__init__(parent)
        self.video_player = video_player
        self.settings = video_player.settings
        self.title("🎨 Темы и настройки")
        self.geometry("800x850")
        self.resizable(True, True)
        self.minsize(700, 750)
        self.transient(parent)
        self.grab_set()
        self.current_theme = self.settings.get("theme", "Modrinth Dark")
        
        self.create_widgets()
    
    def create_widgets(self):
        theme = MODRINTH_THEMES.get(self.current_theme, MODRINTH_THEMES["Modrinth Dark"])
        
        # Градиентный фон
        main_bg = GradientFrame(self, theme["gradient_start"], theme["gradient_end"])
        main_bg.pack(fill=tk.BOTH, expand=True)
        
        main_container = tk.Frame(main_bg, bg=theme["bg_secondary"], bd=0)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(main_container, bg=theme["bg_secondary"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=theme["bg_secondary"])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Заголовок
        header = tk.Frame(scrollable_frame, bg=theme["bg_secondary"])
        header.pack(fill=tk.X, pady=(15, 5))
        title = tk.Label(header, text="🎨 Настройка внешнего вида", font=("Segoe UI", 20, "bold"),
                         bg=theme["bg_secondary"], fg=theme["accent"])
        title.pack()
        subtitle = tk.Label(header, text=f"Доступно {len(MODRINTH_THEMES)} уникальных тем", font=("Segoe UI", 11),
                            bg=theme["bg_secondary"], fg=theme["text_secondary"])
        subtitle.pack()
        
        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill=tk.X, pady=12, padx=20)
        
        # Настройка задержки скрытия панели
        delay_frame = tk.Frame(scrollable_frame, bg=theme["bg_secondary"])
        delay_frame.pack(fill=tk.X, padx=25, pady=10)
        
        delay_label = tk.Label(delay_frame, text="⏱️ Задержка скрытия панели в fullscreen (сек):", 
                               font=("Segoe UI", 11), bg=theme["bg_secondary"], fg=theme["text_primary"])
        delay_label.pack(anchor=tk.W)
        
        delay_control = tk.Frame(delay_frame, bg=theme["bg_secondary"])
        delay_control.pack(fill=tk.X, pady=5)
        
        self.delay_scale = tk.Scale(delay_control, from_=3, to=20, orient=tk.HORIZONTAL,
                                    bg=theme["bg_secondary"], fg=theme["accent"], highlightthickness=0,
                                    troughcolor=theme["bg_tertiary"], sliderrelief=tk.FLAT,
                                    command=self._change_delay)
        self.delay_scale.set(self.settings.get("hide_controls_delay", 10))
        self.delay_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        self.delay_value = tk.Label(delay_control, text=f"{self.settings.get('hide_controls_delay', 10)} сек",
                                    font=("Segoe UI", 11, "bold"), bg=theme["bg_secondary"], 
                                    fg=theme["accent"], width=8)
        self.delay_value.pack(side=tk.RIGHT)
        
        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill=tk.X, pady=12, padx=20)
        
        # Сетка тем
        themes_label = tk.Label(scrollable_frame, text="🎨 Выберите тему:", 
                                font=("Segoe UI", 13, "bold"), bg=theme["bg_secondary"], fg=theme["text_primary"])
        themes_label.pack(anchor=tk.W, padx=25, pady=(5, 10))
        
        themes_frame = tk.Frame(scrollable_frame, bg=theme["bg_secondary"])
        themes_frame.pack(fill=tk.X, padx=15, pady=5)
        
        row = 0
        col = 0
        for theme_name in MODRINTH_THEMES.keys():
            btn = self._create_theme_button(themes_frame, theme_name)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        for i in range(3):
            themes_frame.grid_columnconfigure(i, weight=1)
        
        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill=tk.X, pady=15, padx=20)
        
        # Кнопки действий
        actions_frame = tk.Frame(scrollable_frame, bg=theme["bg_secondary"])
        actions_frame.pack(fill=tk.X, padx=20, pady=15)
        
        self.btn_apply = RoundedButton(actions_frame, text="✅ Применить", command=self._apply_and_close,
                                        bg_color=theme["accent"], hover_color=theme["accent_hover"],
                                        text_color="#ffffff", radius=10, width=120, height=38,
                                        font=("Segoe UI", 11, "bold"))
        self.btn_apply.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)
        
        self.btn_reset = RoundedButton(actions_frame, text="🔄 Сбросить", command=self._reset_styles,
                                        bg_color="#ff4444", hover_color="#ff6666",
                                        text_color="#ffffff", radius=10, width=120, height=38,
                                        font=("Segoe UI", 11, "bold"))
        self.btn_reset.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)
        
        self.btn_cancel = RoundedButton(actions_frame, text="❌ Отмена", command=self.destroy,
                                         bg_color="#666666", hover_color="#888888",
                                         text_color="#ffffff", radius=10, width=120, height=38,
                                         font=("Segoe UI", 11, "bold"))
        self.btn_cancel.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)
    
    def _change_delay(self, val):
        delay = int(float(val))
        self.delay_value.config(text=f"{delay} сек")
    
    def _create_theme_button(self, parent, theme_name):
        theme_data = MODRINTH_THEMES[theme_name]
        btn_frame = tk.Frame(parent, bg=theme_data["bg_secondary"], cursor="hand2",
                            highlightthickness=2, relief=tk.FLAT, bd=0,
                            highlightbackground=theme_data["accent"] if theme_name == self.current_theme else "#404040")
        
        # Превью с градиентом
        preview = GradientFrame(btn_frame, theme_data["gradient_start"], theme_data["gradient_end"], height=60)
        preview.pack(fill=tk.X, padx=5, pady=(5, 2))
        
        accent_bar = tk.Frame(preview, height=30, width=50, bg=theme_data["accent"])
        accent_bar.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=5)
        
        preview_text = tk.Label(preview, text="Aa", font=("Segoe UI", 12, "bold"),
                                bg=theme_data["bg_primary"], fg=theme_data["text_primary"])
        preview_text.place(relx=0.1, rely=0.5, anchor=tk.W)
        
        text_color = theme_data["text_primary"]
        label = tk.Label(btn_frame, text=theme_name.replace("Modrinth ", ""), 
                         font=("Segoe UI", 9, "bold" if theme_name == self.current_theme else "normal"),
                         bg=theme_data["bg_secondary"], fg=text_color)
        label.pack(pady=(0, 8))
        
        for widget in [btn_frame, preview, accent_bar, preview_text, label]:
            widget.bind("<Button-1>", lambda e, t=theme_name: self._select_theme(t))
        
        return btn_frame
    
    def _select_theme(self, theme_name):
        self.current_theme = theme_name
        self._apply_theme(MODRINTH_THEMES[theme_name])
        
        # Обновляем стиль кнопок в окне
        for widget in self.winfo_children():
            self._update_theme_buttons(widget, theme_name)
        
        # Обновляем цвет кнопок в окне настроек
        new_theme = MODRINTH_THEMES[theme_name]
        self.btn_apply.bg_color = new_theme["accent"]
        self.btn_apply.hover_color = new_theme["accent_hover"]
        self.btn_apply._draw_button(self.btn_apply.bg_color)
    
    def _update_theme_buttons(self, widget, selected_theme):
        if isinstance(widget, tk.Frame) and widget.cget("cursor") == "hand2":
            for child in widget.winfo_children():
                if isinstance(child, tk.Label):
                    theme_name = "Modrinth " + child.cget("text")
                    if theme_name in MODRINTH_THEMES:
                        theme_data = MODRINTH_THEMES[theme_name]
                        highlight = theme_data["accent"] if theme_name == selected_theme else "#404040"
                        widget.config(highlightbackground=highlight)
                        child.config(font=("Segoe UI", 9, "bold" if theme_name == selected_theme else "normal"))
                        break
        for child in widget.winfo_children():
            self._update_theme_buttons(child, selected_theme)
    
    def _apply_theme(self, theme):
        vp = self.video_player
        vp.root.config(bg=theme["bg_primary"])
        vp.video_frame.config(bg=theme["video_bg"])
        vp.control_frame.config(bg=theme["bg_secondary"])
        vp._apply_theme_recursive(vp.root, theme)
        
        if hasattr(vp, 'fullscreen_manager') and vp.fullscreen_manager.is_fullscreen:
            vp.fullscreen_manager.update_theme()
        
        # Обновляем фон окна настроек
        if hasattr(self, 'winfo_exists') and self.winfo_exists():
            for child in self.winfo_children():
                if isinstance(child, GradientFrame):
                    child.color_start = theme["gradient_start"]
                    child.color_end = theme["gradient_end"]
                    child._draw_gradient()
    
    def _apply_and_close(self):
        self.settings.set("theme", self.current_theme)
        self.settings.set("hide_controls_delay", int(self.delay_scale.get()))
        self._apply_theme(MODRINTH_THEMES[self.current_theme])
        self.destroy()
    
    def _reset_styles(self):
        self.current_theme = "Modrinth Dark"
        self.delay_scale.set(10)
        self.delay_value.config(text="10 сек")
        self._apply_theme(MODRINTH_THEMES["Modrinth Dark"])
        self._update_theme_buttons(self, "Modrinth Dark")
        self.btn_apply.bg_color = MODRINTH_THEMES["Modrinth Dark"]["accent"]
        self.btn_apply.hover_color = MODRINTH_THEMES["Modrinth Dark"]["accent_hover"]
        self.btn_apply._draw_button(self.btn_apply.bg_color)

class VideoPlayer:
    def __init__(self, root):
        self.root = root
        self.settings = SettingsManager()
        
        window_width = self.settings.get("window_width", 1000)
        window_height = self.settings.get("window_height", 700)
        window_x = self.settings.get("window_x")
        window_y = self.settings.get("window_y")
        
        self.root.title("🎬 Python VLC Player")
        self.root.geometry(f"{window_width}x{window_height}")
        if window_x and window_y:
            self.root.geometry(f"+{window_x}+{window_y}")
        self.root.minsize(800, 600)
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        try:
            self.instance = vlc.Instance("--quiet", "--no-xlib")
            self.player = self.instance.media_player_new()
        except Exception as e:
            messagebox.showerror("Ошибка VLC", f"Не удалось инициализировать VLC:\n{str(e)}")
            root.destroy()
            return
        
        self.current_media_path = None
        self.is_playing = False
        self.is_paused = False
        self.auto_play_on_open = self.settings.get("auto_play", True)
        
        self.create_widgets()
        self.setup_hotkeys()
        
        self.fullscreen_manager = FullscreenPlayer(self)
        
        self.update_timer()
        
        saved_volume = self.settings.get("volume", 50)
        self.player.audio_set_volume(saved_volume)
        if hasattr(self, 'scale_vol'):
            self.scale_vol.set(saved_volume)
            self.vol_label.config(text=f"{saved_volume}%")
        
        saved_theme = self.settings.get("theme", "Modrinth Dark")
        self._apply_theme_recursive(self.root, MODRINTH_THEMES[saved_theme])
        
        # Загружаем последнее видео только если не было аргументов командной строки
        if len(sys.argv) <= 1:
            self.load_last_video()
        else:
            self.load_video_from_args()
            
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        print(f"📁 Папка настроек: {self.settings.settings_dir}")
        print(f"🎨 Доступно тем: {len(MODRINTH_THEMES)}")
    
    def create_widgets(self):
        theme = MODRINTH_THEMES.get(self.settings.get("theme", "Modrinth Dark"), MODRINTH_THEMES["Modrinth Dark"])
        
        self.video_frame = tk.Frame(self.root, bg=theme["video_bg"], relief=tk.FLAT)
        self.video_frame.pack(fill=tk.BOTH, expand=True)
        
        # Градиентный фон для панели управления
        self.control_frame = GradientFrame(self.root, theme["gradient_start"], theme["gradient_end"])
        self.control_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Внутренний фрейм для содержимого
        content_frame = tk.Frame(self.control_frame, bg=theme["bg_secondary"], bd=0)
        content_frame.pack(fill=tk.X, padx=5, pady=5)
        
        progress_frame = tk.Frame(content_frame, bg=theme["bg_secondary"], height=30)
        progress_frame.pack(fill=tk.X, padx=12, pady=(8, 5))
        progress_frame.pack_propagate(False)
        
        self.time_label = tk.Label(progress_frame, text="00:00 / 00:00",
                                   font=("Segoe UI", 10), bg=theme["bg_secondary"], fg=theme["text_secondary"])
        self.time_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.scale_time = tk.Scale(progress_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                   bg=theme["bg_secondary"], fg=theme["accent"], highlightthickness=0,
                                   troughcolor=theme["bg_tertiary"], sliderrelief=tk.FLAT,
                                   sliderlength=18)
        self.scale_time.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.scale_time.bind("<ButtonRelease-1>", self.set_time)
        
        buttons_frame = tk.Frame(content_frame, bg=theme["bg_secondary"], height=50)
        buttons_frame.pack(fill=tk.X, padx=12, pady=(0, 8))
        buttons_frame.pack_propagate(False)
        
        left_buttons = tk.Frame(buttons_frame, bg=theme["bg_secondary"])
        left_buttons.pack(side=tk.LEFT)
        
        # Создаем кнопки с закругленными углами
        self.btn_open = RoundedButton(left_buttons, text="📂 Открыть", command=self.open_file,
                                       bg_color=theme["bg_tertiary"], hover_color=theme["accent"],
                                       text_color=theme["text_primary"], radius=8, width=90, height=32,
                                       font=("Segoe UI", 9, "bold"))
        self.btn_open.pack(side=tk.LEFT, padx=3)
        
        self.btn_play = RoundedButton(left_buttons, text="▶ Воспр.", command=self.play_video,
                                       bg_color=theme["accent"], hover_color=theme["accent_hover"],
                                       text_color="#ffffff", radius=8, width=90, height=32,
                                       font=("Segoe UI", 9, "bold"))
        self.btn_play.pack(side=tk.LEFT, padx=3)
        
        self.btn_pause = RoundedButton(left_buttons, text="⏸ Пауза", command=self.pause_video,
                                        bg_color=theme["bg_tertiary"], hover_color=theme["accent"],
                                        text_color=theme["text_primary"], radius=8, width=90, height=32,
                                        font=("Segoe UI", 9, "bold"))
        self.btn_pause.pack(side=tk.LEFT, padx=3)
        
        self.btn_stop = RoundedButton(left_buttons, text="⏹ Стоп", command=self.stop_video,
                                       bg_color=theme["bg_tertiary"], hover_color=theme["accent"],
                                       text_color=theme["text_primary"], radius=8, width=90, height=32,
                                       font=("Segoe UI", 9, "bold"))
        self.btn_stop.pack(side=tk.LEFT, padx=3)
        
        self.btn_fullscreen = RoundedButton(left_buttons, text="⛶ Fullscreen", command=self.toggle_fullscreen,
                                             bg_color=theme["bg_tertiary"], hover_color=theme["accent"],
                                             text_color=theme["text_primary"], radius=8, width=100, height=32,
                                             font=("Segoe UI", 9, "bold"))
        self.btn_fullscreen.pack(side=tk.LEFT, padx=3)
        
        self.btn_style = RoundedButton(left_buttons, text="🎨 Темы", command=self.open_style_window,
                                        bg_color=theme["accent"], hover_color=theme["accent_hover"],
                                        text_color="#ffffff", radius=8, width=80, height=32,
                                        font=("Segoe UI", 9, "bold"))
        self.btn_style.pack(side=tk.LEFT, padx=5)
        
        right_buttons = tk.Frame(buttons_frame, bg=theme["bg_secondary"])
        right_buttons.pack(side=tk.RIGHT)
        
        vol_label = tk.Label(right_buttons, text="🔊", font=("Segoe UI", 12), 
                            bg=theme["bg_secondary"], fg=theme["text_secondary"])
        vol_label.pack(side=tk.LEFT)
        
        self.scale_vol = tk.Scale(right_buttons, from_=0, to=100, orient=tk.HORIZONTAL, length=120,
                                 bg=theme["bg_secondary"], fg=theme["accent"], highlightthickness=0,
                                 troughcolor=theme["bg_tertiary"], sliderrelief=tk.FLAT,
                                 command=self.set_volume, sliderlength=16)
        self.scale_vol.pack(side=tk.LEFT, padx=8)
        
        self.vol_label = tk.Label(right_buttons, text="50%", font=("Segoe UI", 10, "bold"),
                                 bg=theme["bg_secondary"], fg=theme["text_secondary"], width=4)
        self.vol_label.pack(side=tk.LEFT, padx=3)
        
        self.info_label = tk.Label(right_buttons, text="", font=("Segoe UI", 8),
                                   bg=theme["bg_secondary"], fg=theme["text_secondary"])
        self.info_label.pack(side=tk.LEFT, padx=12)
        
        self._attach_video()
        self.create_menu()
        self.update_info_label()
    
    def toggle_fullscreen(self):
        if hasattr(self, 'fullscreen_manager'):
            self.fullscreen_manager.toggle()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="📂 Открыть видео...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        
        self.history_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="📜 Недавние файлы", menu=self.history_menu)
        self.update_history_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="📁 Открыть папку с настройками", command=self.open_settings_folder)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Выход", command=self.on_closing)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label="⛶ Полноэкранный режим", command=self.toggle_fullscreen, accelerator="Enter/F")
        view_menu.add_command(label="🎨 Темы оформления", command=self.open_style_window)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="📸 Сделать скриншот", command=self.take_screenshot, accelerator="Shift+S")
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="📖 Горячие клавиши", command=self.show_hotkeys)
        help_menu.add_command(label="ℹ️ О программе", command=self.show_about)
    
    def update_history_menu(self):
        self.history_menu.delete(0, tk.END)
        history = self.settings.get_history()
        if history:
            for filepath in history[:10]:
                filename = os.path.basename(filepath)
                self.history_menu.add_command(
                    label=filename,
                    command=lambda p=filepath: self.load_file(p)
                )
        else:
            self.history_menu.add_command(label="(нет недавних файлов)", state=tk.DISABLED)
    
    def update_info_label(self):
        if self.settings.get("show_hotkeys", True):
            hotkeys = "Пробел: Play/Pause | Enter/F: Fullscreen | ←/→: -/+10 сек | Shift+S: Скриншот"
            self.info_label.config(text=hotkeys)
    
    def setup_hotkeys(self):
        self.root.bind('<space>', lambda e: self.play_pause_toggle())
        self.root.bind('<Return>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self.fullscreen_manager.exit_fullscreen() if hasattr(self, 'fullscreen_manager') and self.fullscreen_manager.is_fullscreen else None)
        self.root.bind('<Left>', lambda e: self.seek_backward())
        self.root.bind('<Right>', lambda e: self.seek_forward())
        self.root.bind('<Up>', lambda e: self.volume_up())
        self.root.bind('<Down>', lambda e: self.volume_down())
        self.root.bind('<f>', lambda e: self.toggle_fullscreen())
        self.root.bind('<F>', lambda e: self.toggle_fullscreen())
        self.root.bind('<KeyPress-o>', lambda e: self.open_file())
        self.root.bind('<KeyPress-O>', lambda e: self.open_file())
        self.root.bind('<Shift-S>', lambda e: self.take_screenshot())
        self.root.bind('<Shift-s>', lambda e: self.take_screenshot())
    
    def take_screenshot(self):
        screenshot_path = self.settings.take_screenshot(self)
        if screenshot_path:
            messagebox.showinfo("Скриншот", f"Скриншот сохранен:\n{screenshot_path}")
        else:
            messagebox.showerror("Ошибка", "Не удалось создать скриншот")
    
    def open_settings_folder(self):
        try:
            if platform.system() == "Windows":
                os.startfile(str(self.settings.settings_dir))
            elif platform.system() == "Darwin":
                os.system(f"open {self.settings.settings_dir}")
            else:
                os.system(f"xdg-open {self.settings.settings_dir}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку:\n{str(e)}")
    
    def show_hotkeys(self):
        hotkeys_text = """
        🎮 ГОРЯЧИЕ КЛАВИШИ:
        
        Пробел     - Play / Pause
        Enter / F  - Полноэкранный режим
        Esc        - Выход из полноэкранного
        ← / →      - Перемотка -10/+10 сек
        ↑ / ↓      - Увеличить/Уменьшить громкость
        O          - Открыть файл
        Shift+S    - Сделать скриншот
        
        🎨 Управление:
        Кнопки мыши - Управление плеером
        """
        messagebox.showinfo("Горячие клавиши", hotkeys_text)
    
    def show_about(self):
        about_text = f"""
        🎬 Python VLC Player
        
        Версия: 5.0
        Движок: VLC Media Player
        Количество тем: {len(MODRINTH_THEMES)}
        
        📁 Папка настроек:
        {self.settings.settings_dir}
        
        ✨ Особенности:
        • {len(MODRINTH_THEMES)} стильных тем с градиентами
        • Полноэкранный режим с плавающей панелью
        • Скругленные углы (border-radius)
        • Автоматическое появление панели при движении мыши
        • Сохранение настроек
        • История файлов
        • Создание скриншотов
        • Горячие клавиши
        
        Разработано с ❤️ на Python
        """
        messagebox.showinfo("О программе", about_text)
    
    def load_file(self, filename):
        try:
            if filename and os.path.isfile(filename):
                self.current_media_path = filename
                self.media = self.instance.media_new(filename)
                self.player.set_media(self.media)
                self.root.title(f"🎬 {os.path.basename(filename)}")
                self.settings.add_to_history(filename)
                if self.settings.get("remember_last_video", True):
                    self.settings.set("last_video", filename)
                self.settings.set("last_directory", os.path.dirname(filename))
                
                # Автовоспроизведение только если включено в настройках
                if self.settings.get("auto_play", True):
                    self.play_video()
                else:
                    self.is_playing = False
                    self.is_paused = False
                    
                self.update_history_menu()
                return True
            return False
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить видео:\n{str(e)}")
            return False
    
    def load_last_video(self):
        """Загрузка последнего видео"""
        if self.settings.get("remember_last_video", True):
            last_video = self.settings.get_last_video()
            if last_video:
                self.root.after(500, lambda: self.load_file(last_video))
    
    def load_video_from_args(self):
        """Загрузка видео из аргументов командной строки"""
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                if os.path.isfile(arg):
                    self.load_file(arg)
                    break
    
    def save_window_settings(self):
        self.settings.set("window_width", self.root.winfo_width())
        self.settings.set("window_height", self.root.winfo_height())
        self.settings.set("window_x", self.root.winfo_x())
        self.settings.set("window_y", self.root.winfo_y())
    
    def play_pause_toggle(self):
        if self.is_playing:
            if self.is_paused:
                self.play_video()
            else:
                self.pause_video()
        else:
            if self.current_media_path:
                self.play_video()
    
    def play_video(self):
        if not self.current_media_path:
            self.open_file()
            return
        if self.player.play() == -1:
            messagebox.showwarning("Предупреждение", "Не удалось воспроизвести видео")
            return
        self.is_playing = True
        self.is_paused = False
        
        theme = MODRINTH_THEMES.get(self.settings.get("theme", "Modrinth Dark"), MODRINTH_THEMES["Modrinth Dark"])
        self.btn_play.bg_color = theme["accent"]
        self.btn_play.hover_color = theme["accent_hover"]
        self.btn_play._draw_button(self.btn_play.bg_color)
        self.btn_pause.bg_color = theme["bg_tertiary"]
        self.btn_pause._draw_button(self.btn_pause.bg_color)
    
    def pause_video(self):
        self.player.pause()
        self.is_paused = True
        
        theme = MODRINTH_THEMES.get(self.settings.get("theme", "Modrinth Dark"), MODRINTH_THEMES["Modrinth Dark"])
        self.btn_play.bg_color = theme["bg_tertiary"]
        self.btn_play._draw_button(self.btn_play.bg_color)
        self.btn_pause.bg_color = theme["accent"]
        self.btn_pause._draw_button(self.btn_pause.bg_color)
    
    def stop_video(self):
        self.player.stop()
        self.is_playing = False
        self.is_paused = False
        
        theme = MODRINTH_THEMES.get(self.settings.get("theme", "Modrinth Dark"), MODRINTH_THEMES["Modrinth Dark"])
        self.btn_play.bg_color = theme["bg_tertiary"]
        self.btn_play._draw_button(self.btn_play.bg_color)
        self.btn_pause.bg_color = theme["bg_tertiary"]
        self.btn_pause._draw_button(self.btn_pause.bg_color)
        self.scale_time.set(0)
        self.time_label.config(text="00:00 / 00:00")
    
    def seek_backward(self):
        if self.player.is_playing():
            current_time = self.player.get_time()
            new_time = max(0, current_time - 10000)
            self.player.set_time(new_time)
    
    def seek_forward(self):
        if self.player.is_playing():
            current_time = self.player.get_time()
            total_time = self.player.get_length()
            if total_time > 0:
                new_time = min(total_time, current_time + 10000)
                self.player.set_time(new_time)
    
    def volume_up(self):
        current_vol = self.player.audio_get_volume()
        new_vol = min(100, current_vol + 5)
        self.player.audio_set_volume(new_vol)
        self.scale_vol.set(new_vol)
        self.vol_label.config(text=f"{new_vol}%")
        self.settings.set("volume", new_vol)
    
    def volume_down(self):
        current_vol = self.player.audio_get_volume()
        new_vol = max(0, current_vol - 5)
        self.player.audio_set_volume(new_vol)
        self.scale_vol.set(new_vol)
        self.vol_label.config(text=f"{new_vol}%")
        self.settings.set("volume", new_vol)
    
    def set_volume(self, val):
        volume = int(float(val))
        self.player.audio_set_volume(volume)
        self.vol_label.config(text=f"{volume}%")
        self.settings.set("volume", volume)
    
    def set_time(self, event):
        total_time = self.player.get_length()
        if total_time > 0:
            seek_time = (float(self.scale_time.get()) / 100) * total_time
            self.player.set_time(int(seek_time))
    
    def update_timer(self):
        try:
            if self.player.is_playing():
                current_time = self.player.get_time()
                total_time = self.player.get_length()
                if total_time > 0 and total_time != -1:
                    percent = (current_time / total_time) * 100
                    self.scale_time.set(percent)
                    curr_min, curr_sec = divmod(current_time // 1000, 60)
                    tot_min, tot_sec = divmod(total_time // 1000, 60)
                    self.time_label.config(text=f"{curr_min:02d}:{curr_sec:02d} / {tot_min:02d}:{tot_sec:02d}")
                
                if current_time > 0 and total_time > 0 and current_time >= total_time - 100:
                    self.is_playing = False
                    theme = MODRINTH_THEMES.get(self.settings.get("theme", "Modrinth Dark"), MODRINTH_THEMES["Modrinth Dark"])
                    self.btn_play.bg_color = theme["bg_tertiary"]
                    self.btn_play._draw_button(self.btn_play.bg_color)
                    self.btn_pause.bg_color = theme["bg_tertiary"]
                    self.btn_pause._draw_button(self.btn_pause.bg_color)
        except Exception:
            pass
        self.root.after(16, self.update_timer)
    
    def open_file(self):
        last_dir = self.settings.get("last_directory", os.path.expanduser("~"))
        filename = filedialog.askopenfilename(
            title="🎬 Выберите видео",
            initialdir=last_dir,
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.webm *.flv *.wmv *.m4v *.mpg *.mpeg"), 
                      ("All Files", "*.*")]
        )
        if filename:
            self.load_file(filename)
    
    def open_style_window(self):
        if hasattr(self, 'style_window') and self.style_window.winfo_exists():
            self.style_window.focus_force()
            self.style_window.lift()
        else:
            self.style_window = ModrinthStyleWindow(self.root, self)
    
    def _attach_video(self):
        self.root.update()
        if platform.system() == "Windows":
            self.player.set_hwnd(self.video_frame.winfo_id())
        elif platform.system() == "Darwin":
            self.player.set_nsobject(int(self.video_frame.winfo_id()))
        else:
            self.player.set_xid(self.video_frame.winfo_id())
    
    def _apply_theme_recursive(self, widget, theme):
        try:
            if isinstance(widget, tk.Frame):
                if widget == self.control_frame:
                    if hasattr(widget, 'color_start'):
                        widget.color_start = theme["gradient_start"]
                        widget.color_end = theme["gradient_end"]
                        widget._draw_gradient()
                elif widget != self.video_frame:
                    widget.config(bg=theme["bg_secondary"])
            elif isinstance(widget, tk.Label):
                if widget in [self.time_label, self.vol_label, self.info_label]:
                    widget.config(bg=theme["bg_secondary"], fg=theme["text_secondary"])
                else:
                    widget.config(bg=theme["bg_secondary"], fg=theme["text_primary"])
            elif isinstance(widget, tk.Scale):
                widget.config(bg=theme["bg_secondary"], troughcolor=theme["bg_tertiary"],
                            fg=theme["accent"], activebackground=theme["accent_hover"])
        except Exception:
            pass
        for child in widget.winfo_children():
            self._apply_theme_recursive(child, theme)
        
        # Обновляем цвета кнопок
        if hasattr(self, 'btn_open'):
            self.btn_open.bg_color = theme["bg_tertiary"]
            self.btn_open.hover_color = theme["accent"]
            self.btn_open._draw_button(self.btn_open.bg_color)
        
        if hasattr(self, 'btn_play'):
            if self.is_playing and not self.is_paused:
                self.btn_play.bg_color = theme["accent"]
            else:
                self.btn_play.bg_color = theme["bg_tertiary"]
            self.btn_play.hover_color = theme["accent_hover"]
            self.btn_play._draw_button(self.btn_play.bg_color)
        
        if hasattr(self, 'btn_pause'):
            if self.is_paused:
                self.btn_pause.bg_color = theme["accent"]
            else:
                self.btn_pause.bg_color = theme["bg_tertiary"]
            self.btn_pause.hover_color = theme["accent"]
            self.btn_pause._draw_button(self.btn_pause.bg_color)
        
        if hasattr(self, 'btn_stop'):
            self.btn_stop.bg_color = theme["bg_tertiary"]
            self.btn_stop.hover_color = theme["accent"]
            self.btn_stop._draw_button(self.btn_stop.bg_color)
        
        if hasattr(self, 'btn_fullscreen'):
            self.btn_fullscreen.bg_color = theme["bg_tertiary"]
            self.btn_fullscreen.hover_color = theme["accent"]
            self.btn_fullscreen._draw_button(self.btn_fullscreen.bg_color)
        
        if hasattr(self, 'btn_style'):
            self.btn_style.bg_color = theme["accent"]
            self.btn_style.hover_color = theme["accent_hover"]
            self.btn_style._draw_button(self.btn_style.bg_color)
    
    def on_closing(self):
        self.save_window_settings()
        self.settings.set("volume", self.player.audio_get_volume())
        if self.current_media_path and self.settings.get("remember_last_video", True):
            self.settings.set("last_video", self.current_media_path)
        try:
            self.player.stop()
            self.instance.release()
        except Exception:
            pass
        self.root.destroy()


# ─────────────────────────────────────────────────────────────
# 🚀 ТОЧКА ВХОДА
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        root = tk.Tk()
        
        if platform.system() == "Windows":
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass
        
        app = VideoPlayer(root)
        root.mainloop()
    except Exception as e:
        import traceback
        error_msg = f"КРИТИЧЕСКАЯ ОШИБКА:\n\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        messagebox.showerror("Ошибка", error_msg)
        sys.exit(1)