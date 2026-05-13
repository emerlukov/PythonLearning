"""
Анимированная заставка с прогресс-баром
Использует шрифты из папки fonts
"""
import os
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.core.text import LabelBase
import threading
import time

# Регистрируем шрифты из папки fonts
fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')

# Регистрируем жирный шрифт для заголовка (SourceSansPro-Bold.ttf)
bold_font_path = os.path.join(fonts_dir, 'SourceSansPro-Bold.ttf')
if os.path.exists(bold_font_path):
    LabelBase.register(name='SplashTitle', fn_regular=bold_font_path)
else:
    # Запасной вариант - используем любой доступный жирный шрифт
    fallback_fonts = [
        os.path.join(fonts_dir, 'JetBrainsMono.ttf'),
        os.path.join(fonts_dir, 'FiraCode-Regular.ttf'),
    ]
    for font in fallback_fonts:
        if os.path.exists(font):
            LabelBase.register(name='SplashTitle', fn_regular=font)
            break

# Регистрируем обычный шрифт для текста (NotoSans-Regular.ttf)
regular_font_path = os.path.join(fonts_dir, 'NotoSans-Regular.ttf')
if os.path.exists(regular_font_path):
    LabelBase.register(name='SplashRegular', fn_regular=regular_font_path)
else:
    # Запасной вариант
    fallback_fonts = [
        os.path.join(fonts_dir, 'DejaVuSans.ttf'),
        os.path.join(fonts_dir, 'NotoSansMono.ttf'),
    ]
    for font in fallback_fonts:
        if os.path.exists(font):
            LabelBase.register(name='SplashRegular', fn_regular=font)
            break


class AnimatedSplashScreen(Screen):
    """
    Экран заставки с анимацией и прогресс-баром
    Показывает процесс загрузки приложения
    """
    
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.name = 'splash'
        self.loading_complete = False
        
        # Создаём красивый градиентный фон
        with self.canvas.before:
            # Основной цвет фона (фиолетовый градиент)
            Color(0.361, 0.255, 0.878, 1)  # #5C41E0
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
            # Декоративный круг внизу
            Color(0.459, 0.365, 0.918, 0.3)  # #755DEA с прозрачностью
            self.circle_bg = RoundedRectangle(
                pos=(self.center_x - dp(150), self.y - dp(50)),
                size=(dp(300), dp(300)),
                radius=[dp(150)]
            )
        
        # Обновляем позиции при изменении размера окна
        self.bind(pos=self._update_graphics, size=self._update_graphics)
        
        # Создаём основной layout
        layout = BoxLayout(
            orientation='vertical',
            padding=[dp(30), dp(60), dp(30), dp(60)],
            spacing=dp(25)
        )
        
        # Верхний отступ для красоты
        top_spacer = BoxLayout(size_hint_y=0.15)
        layout.add_widget(top_spacer)
        
        # ===== Анимированное название приложения =====
        self.title_label = Label(
            text='[b]Python[/b] Learning IDE',
            markup=True,
            font_name='SplashTitle',
            font_size=sp(42),
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            size_hint=(1, 0.25)
        )
        layout.add_widget(self.title_label)
        
        # Подзаголовок
        self.subtitle_label = Label(
            text='Learn Python on Android',
            font_name='SplashRegular',
            font_size=sp(14),
            color=(0.9, 0.9, 0.9, 0.8),
            halign='center',
            valign='top',
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.subtitle_label)
        
        # ===== Прогресс-бар с кастомным стилем =====
        progress_container = BoxLayout(
            size_hint=(0.8, 0.08),
            pos_hint={'center_x': 0.5}
        )
        
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint=(1, 1)
        )
        
        # Кастомизируем цвет прогресс-бара
        self.progress_bar.canvas.before.clear()
        with self.progress_bar.canvas.before:
            # Фон прогресс-бара
            Color(0.2, 0.2, 0.3, 0.5)
            RoundedRectangle(pos=self.progress_bar.pos, size=self.progress_bar.size, radius=[dp(5)])
        
        self.progress_bar.canvas.after.clear()
        with self.progress_bar.canvas.after:
            # Заливка прогресса (будет обновляться)
            Color(1, 1, 1, 1)  # Белый цвет
            self.progress_rect = RoundedRectangle(
                pos=self.progress_bar.pos,
                size=(self.progress_bar.width * (self.progress_bar.value / 100), self.progress_bar.height),
                radius=[dp(5)]
            )
        
        # Привязываем обновление прогресс-бара
        self.progress_bar.bind(pos=self._update_progress_rect, size=self._update_progress_rect)
        self.progress_bar.bind(value=self._update_progress_value)
        
        progress_container.add_widget(self.progress_bar)
        layout.add_widget(progress_container)
        
        # ===== Текст статуса загрузки =====
        self.status_label = Label(
            text='Инициализация...',
            font_name='SplashRegular',
            font_size=sp(12),
            color=(0.9, 0.9, 0.9, 0.9),
            halign='center',
            valign='middle',
            size_hint=(1, 0.08)
        )
        layout.add_widget(self.status_label)
        
        # ===== Анимированные точки (эффект загрузки) =====
        self.dots_label = Label(
            text='',
            font_name='SplashRegular',
            font_size=sp(18),
            color=(1, 1, 1, 0.7),
            halign='center',
            valign='middle',
            size_hint=(1, 0.08)
        )
        layout.add_widget(self.dots_label)
        
        # Нижний отступ
        bottom_spacer = BoxLayout(size_hint_y=0.15)
        layout.add_widget(bottom_spacer)
        
        self.add_widget(layout)
        
        # Запускаем анимации
        Clock.schedule_once(self._start_animations, 0.1)
    
    def _update_graphics(self, instance, value):
        """Обновляет позиции графических элементов"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size
        
        if hasattr(self, 'circle_bg'):
            self.circle_bg.pos = (self.center_x - dp(150), self.y - dp(50))
    
    def _update_progress_rect(self, instance, value):
        """Обновляет позицию прямоугольника прогресса"""
        if hasattr(self, 'progress_rect'):
            self.progress_rect.pos = instance.pos
            self.progress_rect.size = (
                instance.width * (instance.value / 100),
                instance.height
            )
    
    def _update_progress_value(self, instance, value):
        """Обновляет ширину прямоугольника прогресса при изменении значения"""
        if hasattr(self, 'progress_rect'):
            self.progress_rect.size = (
                instance.width * (instance.value / 100),
                instance.height
            )
    
    def _start_animations(self, dt):
        """Запускает все анимации при старте"""
        # Анимация появления названия
        title_anim = Animation(font_size=sp(48), duration=0.6, t='out_back')
        title_anim.start(self.title_label)
        
        # Анимация пульсации подзаголовка
        pulse = Animation(opacity=0.5, duration=1) + Animation(opacity=0.8, duration=1)
        pulse.repeat = True
        pulse.start(self.subtitle_label)
        
        # Анимация точек загрузки
        self._animate_dots()
        
        # Запускаем процесс загрузки
        Clock.schedule_once(self._start_loading, 0.8)
    
    def _animate_dots(self, count=0):
        """Анимирует точки загрузки"""
        dots = ['.', '..', '...', '']
        self.dots_label.text = dots[count % len(dots)]
        Clock.schedule_once(lambda dt: self._animate_dots(count + 1), 0.5)
    
    def _start_loading(self, dt):
        """Начинает процесс загрузки ресурсов"""
        # Запускаем загрузку в отдельном потоке
        loading_thread = threading.Thread(target=self._load_resources, daemon=True)
        loading_thread.start()
    
    def _load_resources(self):
        """Симулирует загрузку ресурсов (реально загружает то, что нужно)"""
        
        loading_steps = [
            (8, "Загрузка шрифтов..."),
            (7, "Инициализация настроек..."),
            (10, "Проверка разрешений..."),
            (15, "Загрузка тем оформления..."),
            (12, "Настройка редактора кода..."),
            (15, "Загрузка примеров кода..."),
            (10, "Подготовка AI помощника..."),
            (8, "Проверка обновлений..."),
            (10, "Оптимизация интерфейса..."),
            (5, "Финальная подготовка..."),
        ]
        
        current_value = 0
        
        for step_value, step_text in loading_steps:
            # Обновляем статус
            Clock.schedule_once(lambda dt, text=step_text: self._update_status(text), 0)
            
            # Плавно увеличиваем прогресс
            for _ in range(step_value):
                current_value += 1
                if current_value <= 100:
                    Clock.schedule_once(lambda dt, v=current_value: self._set_progress(v), 0)
                    time.sleep(0.02)  # Небольшая задержка для красивого эффекта
        
        # Убеждаемся, что прогресс достиг 100%
        Clock.schedule_once(lambda dt: self._set_progress(100), 0)
        
        # Завершаем
        Clock.schedule_once(self._finish_loading, 0.8)
    
    def _update_status(self, text):
        """Обновляет текст статуса"""
        self.status_label.text = text
    
    def _set_progress(self, value):
        """Устанавливает значение прогресс-бара"""
        self.progress_bar.value = min(value, 100)
    
    def _finish_loading(self, dt):
        """Завершает загрузку и переходит в главное приложение"""
        if not self.loading_complete:
            self.loading_complete = True
            self.status_label.text = "Готово! Запуск..."
            
            # Финальная анимация
            fade_out = Animation(opacity=0, duration=0.4)
            fade_out.start(self)
            
            # Переход на главный экран
            Clock.schedule_once(self._go_to_main, 0.5)
    
    def _go_to_main(self, dt):
        """Переход на главный экран приложения"""
        # Используем плавный переход
        self.manager.transition = SlideTransition(direction='left', duration=0.4)
        self.manager.current = 'main'
        
        # Уведомляем основное приложение
        if hasattr(self.main_app, 'on_splash_finished'):
            self.main_app.on_splash_finished()
















































