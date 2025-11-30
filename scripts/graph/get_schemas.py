import pathlib
paths = sorted(p.as_posix() for p in pathlib.Path('contracts').rglob('*.schema.json'))
for item in paths:
    print(item)
