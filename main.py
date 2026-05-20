def show_result_popup(self, result):
    """Показывает результат в всплывающем окне."""
    # ВИБРАЦИЯ
    self.vibrate_short()

    tr = self.tr

    # === ИСПРАВЛЕНИЕ: очистка текста от проблемных символов ===
    if isinstance(result, str):
        import re
        # Удаляем все управляющие символы (кроме \n и \t)
        result = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', result)
        # Дополнительно чистим от нулевых и специальных символов
        result = result.replace('\x00', '').strip()

    if len(result) > 50000:
        result = result[:50000] + "\n\n... " + \
                 tr.get('output_truncated', '(truncated)')

    theme = ThemeManager.get_theme()
    content = BoxLayout(orientation='vertical', padding=dp(5), spacing=dp(3))

    scroll = ScrollView(size_hint=(1, 0.85),
                        do_scroll_x=False, do_scroll_y=True)
    
    output_view = TextInput(
        text=str(result),
        readonly=True,
        font_size=dp(16),
        font_name='SourceBold',          # ← можно попробовать 'DejaVuSans' если квадратики останутся
        background_color=theme['result_bg'],
        foreground_color=theme['result_text'],
        do_wrap=True,
        multiline=True,
        size_hint_y=None,
        height=dp(33),
        padding=(dp(5), dp(5), dp(5), dp(5))
    )
    
    output_view.bind(minimum_height=output_view.setter('height'))
    scroll.add_widget(output_view)
    content.add_widget(scroll)

    btn_layout = BoxLayout(size_hint_y=None, height=dp(18), spacing=dp(3))

    btn_copy = Button(
        text=tr.get('copy_btn', 'Copy'),
        font_name='SourceBold',
        background_color=theme['widget_bg'],
        background_normal='',
        background_down='',
        color=theme['text_color'],
        font_size=dp(15),
        size_hint_y=None,
        height=dp(33),
        on_release=lambda x: self._copy_result(result)
    )

    btn_copy.bind(on_press=lambda x: self.vibrate_short())

    btn_close = Button(
        text=tr.get('close', 'Close'),
        font_name='SourceBold',
        background_color=theme['widget_bg'],
        background_normal='',
        background_down='',
        color=theme['text_color'],
        font_size=dp(15),
        size_hint_y=None,
        height=dp(33)
    )

    btn_close.bind(on_press=lambda x: self.vibrate_short())

    btn_layout.add_widget(btn_copy)
    btn_layout.add_widget(btn_close)
    content.add_widget(btn_layout)

    # Адаптивный размер
    category = get_screen_category()
    if category == 'tablet':
        size_hint = (0.75, 0.70)
    elif category == 'large_phone':
        size_hint = (0.85, 0.76)
    else:
        size_hint = (0.90, 0.82)

    popup = ThemedPopup(
        title=tr.get('result_title', 'Result'),
        popup_bg=theme.get('popup_bg', (0.188, 0.204, 0.251, 1)),
        title_bg=theme.get('popup_title_bg', (0.188, 0.204, 0.251, 1)),
        title_color=theme['popup_title'],
        content=content,
        size_hint=size_hint,
        auto_dismiss=False,
        separator_color=theme.get('popup_separator', (0.25, 0.25, 0.25, 1))
    )
    
    btn_close.bind(on_release=popup.dismiss)
    popup.open()
    
    self._popup = popup
    self._current_popup_type = 'result'
