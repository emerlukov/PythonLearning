import sys
print("Пути поиска модулей:")
for p in sys.path:
    print(f"  {p}")

try:
    import pygments
    print("✅ Pygments импортирован!")
except ImportError as e:
    print(f"❌ Ошибка: {e}")