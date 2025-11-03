import pathlib
paths = sorted(path.as_posix() for path in pathlib.Path('contracts').rglob('*.schema.json'))
for item in paths:
    print(item)
