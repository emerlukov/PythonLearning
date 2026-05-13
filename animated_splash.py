"""
Анимированная заставка с прогресс-баром - Чёрно-белая версия
"""
import os
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.core.text import LabelBase
import threading
import time

# ========== РЕГИСТРАЦИЯ ШРИФТОВ ==========
# Получаем путь к папке fonts относительно текущего файла
current_dir = os.path.dirname(os.path.abspath(__file__))
fonts_dir = os.path.join(current_dir, 'fonts')

print(f"Looking for fonts in: {fonts_dir}")

# Регистрируем жирный шрифт (SourceSansPro-Bold.ttf)
bold_font_path = os.path.join(fonts_dir, 'SourceSansPro-Bold.ttf')
if os.path.exists(bold_font_path):
    LabelBase.register(name='SplashTitle', fn_regular=bold_font_path)
    print(f"✅ Registered SplashTitle from: {bold_font_path}")
else:
    print(f"❌ Font not found: {bold_font_path}")
    # Вместо Roboto используем стандартный шрифт Kivy
    # Не регистрируем ничего, будем использовать 'Roboto' который уже есть в Kivy
    pass

# Регистрируем обычный шрифт (NotoSans-Regular.ttf)
regular_font_path = os.path.join(fonts_dir, 'NotoSans-Regular.ttf')
if os.path.exists(regular_font_path):
    LabelBase.register(name='SplashRegular', fn_regular=regular_font_path)
    print(f"✅ Registered SplashRegular from: {regular_font_path}")
else:
    print(f"❌ Font not found: {regular_font_path}")
    # Не регистрируем ничего

# Также пробуем DejaVuSans как запасной
dejavu_font_path = os.path.join(fonts_dir, 'DejaVuSans.ttf')
if os.path.exists(dejavu_font_path):
    LabelBase.register(name='DejaVuSans', fn_regular=dejavu_font_path)
    print(f"✅ Registered DejaVuSans from: {dejavu_font_path}")


class AnimatedSplashScreen(Screen):
    """Третья заставка - анимированная с прогресс-баром"""
    
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.name = 'splash'
        self.loading_complete = False
        
        # Чёрно-белая гамма
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Чёрный фон
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
            # Едва заметный декоративный круг
            Color(0.12, 0.12, 0.12, 0.3)
            self.circle_bg = RoundedRectangle(
                pos=(self.center_x - dp(150), self.y - dp(50)),
                size=(dp(300), dp(300)),
                radius=[dp(150)]
            )
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
        
        # Основной layout
        layout = BoxLayout(
            orientation='vertical',
            padding=[dp(30), dp(60), dp(30), dp(60)],
            spacing=dp(20)
        )
        
        top_spacer = BoxLayout(size_hint_y=0.15)
        layout.add_widget(top_spacer)
        
        # ===== НАЗВАНИЕ =====
        # Определяем какой шрифт использовать
        title_font = 'SplashTitle' if os.path.exists(bold_font_path) else 'Roboto'
        
        self.title_label = Label(
            text='[b]Python[/b]\nLearning IDE',
            markup=True,
            font_name=title_font,
            font_size=sp(30),
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            size_hint=(1, 0.35)
        )
        self.title_label.bind(
            width=lambda inst, val: setattr(inst, 'text_size', (val, None))
        )
        layout.add_widget(self.title_label)
        
        # ===== ПОДЗАГОЛОВОК =====
        subtitle_font = 'SplashRegular' if os.path.exists(regular_font_path) else 'Roboto'
        
        self.subtitle_label = Label(
            text='Learn Python on Android',
            font_name=subtitle_font,
            font_size=sp(12),
            color=(0.75, 0.75, 0.75, 0.9),
            halign='center',
            valign='top',
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.subtitle_label)
        
        # ===== ПРОГРЕСС-БАР =====
        progress_container = BoxLayout(
            size_hint=(0.7, 0.06),
            pos_hint={'center_x': 0.5}
        )
        
        self.progress_bar = ProgressBar(max=100, value=0, size_hint=(1, 1))
        
        # Стилизация прогресс-бара
        self.progress_bar.canvas.before.clear()
        with self.progress_bar.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.progress_bg = RoundedRectangle(
                pos=self.progress_bar.pos,
                size=self.progress_bar.size,
                radius=[dp(4)]
            )
        
        self.progress_bar.canvas.after.clear()
        with self.progress_bar.canvas.after:
            Color(1, 1, 1, 1)
            self.progress_rect = RoundedRectangle(
                pos=self.progress_bar.pos,
                size=(self.progress_bar.width * (self.progress_bar.value / 100), self.progress_bar.height),
                radius=[dp(4)]
            )
        
        self.progress_bar.bind(pos=self._update_progress_rect, size=self._update_progress_rect)
        self.progress_bar.bind(value=self._update_progress_value)
        
        progress_container.add_widget(self.progress_bar)
        layout.add_widget(progress_container)
        
        # ===== СТАТУС =====
        self.status_label = Label(
            text='Загрузка...',
            font_name='Roboto',
            font_size=sp(11),
            color=(0.75, 0.75, 0.75, 0.9),
            halign='center',
            valign='middle',
            size_hint=(1, 0.08)
        )
        layout.add_widget(self.status_label)
        
        # ===== АНИМИРОВАННЫЕ ТОЧКИ =====
        self.dots_label = Label(
            text='',
            font_name='Roboto',
            font_size=sp(16),
            color=(0.7, 0.7, 0.7, 0.6),
            halign='center',
            valign='middle',
            size_hint=(1, 0.08)
        )
        layout.add_widget(self.dots_label)
        
        bottom_spacer = BoxLayout(size_hint_y=0.15)
        layout.add_widget(bottom_spacer)
        
        self.add_widget(layout)
        
        # Запуск
        Clock.schedule_once(self._start, 0.1)
    
    def on_enter(self):
        """При входе на экран - скрываем клавиатуру"""
        self._hide_keyboard()
    
    def _hide_keyboard(self):
        """Скрываем клавиатуру"""
        try:
            Window.softinput_mode = 'below_target'
            if hasattr(self.main_app, 'code_input') and self.main_app.code_input:
                self.main_app.code_input.focus = False
        except:
            pass
    
    def _start(self, dt):
        """Запуск анимации"""
        self._hide_keyboard()
        self._start_animations()
    
    def _start_animations(self):
        """Анимации"""
        # Анимация появления
        anim = Animation(opacity=1, duration=0.5)
        self.title_label.opacity = 0
        anim.start(self.title_label)
        
        pulse = Animation(opacity=0.4, duration=1) + Animation(opacity=0.7, duration=1)
        pulse.repeat = True
        pulse.start(self.subtitle_label)
        
        self._animate_dots()
        Clock.schedule_once(self._start_loading, 0.8)
    
    def _animate_dots(self, count=0):
        dots = ['.', '..', '...', '']
        self.dots_label.text = dots[count % len(dots)]
        Clock.schedule_once(lambda dt: self._animate_dots(count + 1), 0.6)
    
    def _start_loading(self, dt):
        threading.Thread(target=self._load_resources, daemon=True).start()
    
    def _load_resources(self):
        steps = [
            (10, "Загрузка шрифтов..."),
            (10, "Инициализация..."),
            (15, "Настройка редактора..."),
            (20, "Загрузка тем..."),
            (20, "Подготовка примеров..."),
            (15, "Финальная подготовка..."),
            (10, "Запуск!"),
        ]
        
        current = 0
        for step_val, step_text in steps:
            Clock.schedule_once(lambda dt, t=step_text: self._set_status(t), 0)
            for _ in range(step_val):
                current += 1
                if current <= 100:
                    Clock.schedule_once(lambda dt, v=current: self._set_progress(v), 0)
                    time.sleep(0.02)
        
        Clock.schedule_once(lambda dt: self._set_progress(100), 0)
        Clock.schedule_once(self._finish, 0.5)
    
    def _set_status(self, text):
        self.status_label.text = text
    
    def _set_progress(self, value):
        self.progress_bar.value = value
    
    def _finish(self, dt):
        if not self.loading_complete:
            self.loading_complete = True
            self.status_label.text = "Готово!"
            fade = Animation(opacity=0, duration=0.4)
            fade.start(self)
            Clock.schedule_once(self._go_to_main, 0.5)
    
    def _go_to_main(self, dt):
        # Восстанавливаем клавиатуру
        Window.softinput_mode = ''
        
        self.manager.transition = SlideTransition(direction='left', duration=0.4)
        self.manager.current = 'main'
        
        if hasattr(self.main_app, 'on_splash_finished'):
            self.main_app.on_splash_finished()
    
    def _update_graphics(self, instance, value):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size
        if hasattr(self, 'circle_bg'):
            self.circle_bg.pos = (self.center_x - dp(150), self.y - dp(50))
    
    def _update_progress_rect(self, instance, value):
        if hasattr(self, 'progress_rect'):
            self.progress_rect.pos = instance.pos
            self.progress_rect.size = (
                instance.width * (instance.value / 100),
                instance.height
            )
    
    def _update_progress_value(self, instance, value):
        if hasattr(self, 'progress_rect'):
            self.progress_rect.size = (
                instance.width * (value / 100),
                instance.height
            )





