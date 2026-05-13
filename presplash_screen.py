"""
Вторая заставка - presplash.png показывается после системной
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp


class PresplashScreen(Screen):
    """Вторая заставка - показывает presplash.png"""
    
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.name = 'presplash'
        
        # Чёрный фон
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Контейнер
        layout = BoxLayout(orientation='vertical', padding=[dp(0), dp(0)])
        
        # Ваша картинка presplash.png
        try:
            self.image = Image(
                source='presplash.png',
                allow_stretch=True,
                keep_ratio=True,
                size_hint=(1, 1)
            )
            layout.add_widget(self.image)
        except:
            # Если картинки нет - показываем текст
            from kivy.uix.label import Label
            layout.add_widget(Label(
                text='Python Learning IDE',
                font_size='30sp',
                color=(1, 1, 1, 1),
                halign='center',
                valign='middle'
            ))
        
        self.add_widget(layout)
        
        # Показываем 1.5 секунды и переходим к анимированной заставке
        Clock.schedule_once(self._next, 1.5)
    
    def _update_bg(self, instance, value):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size
    
    def _next(self, dt):
        """Переход к анимированной заставке"""
        from kivy.uix.screenmanager import SlideTransition
        self.manager.transition = SlideTransition(direction='left', duration=0.5)
        self.manager.current = 'animated_splash'