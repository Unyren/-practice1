from pathlib import Path
from src.classifier import _sanitize_component
from src.file_ops import ensure_directory

p = Path('test_output/한글테스트')
ensure_directory(p)
print('created', p, p.exists())
with open(p / '파일이름테스트.txt', 'w', encoding='utf-8') as f:
    f.write('테스트')
print('wrote file', (p / '파일이름테스트.txt').exists())
print('sanitize:', _sanitize_component('한글/테스트:<>'))
