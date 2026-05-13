"""
Вторая заставка - показывает presplash.png после системной заставки
"""
import os
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp


class PresplashScreen(Screen):
    """Вторая заставка - показывает вашу presplash.png на весь экран"""
    
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.name = 'presplash'
        
        # Чёрный фон
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Контейнер на весь экран
        layout = BoxLayout(orientation='vertical', padding=[0, 0])
        
        # Проверяем наличие файла
        presplash_path = os.path.join(os.path.dirname(__file__), 'presplash.png')
        
        if os.path.exists(presplash_path):
            try:
                self.image = Image(
                    source='presplash.png',
                    size_hint=(1, 1)
                )
                layout.add_widget(self.image)
                print(f"✅ Loaded presplash.png from: {presplash_path}")
            except Exception as e:
                print(f"❌ Error loading presplash.png: {e}")
                self._add_text_fallback(layout)
        else:
            print(f"⚠️ presplash.png not found at: {presplash_path}")
            self._add_text_fallback(layout)
        
        self.add_widget(layout)
        
        # Показываем 1.5 секунды, затем переходим к анимированной заставке
        Clock.schedule_once(self._go_to_animated_splash, 1.5)
    
    def _add_text_fallback(self, layout):
        """Добавляет текстовую заглушку вместо картинки"""
        from kivy.uix.label import Label
        layout.add_widget(Label(
            text='Python Learning IDE',
            font_size='40sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        ))
    
    def _update_bg(self, instance, value):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size
    
    def _go_to_animated_splash(self, dt):
        """Переход к анимированной заставке"""
        self.manager.transition = SlideTransition(direction='left', duration=0.5)
        self.manager.current = 'splash'


