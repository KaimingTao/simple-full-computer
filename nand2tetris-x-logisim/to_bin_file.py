import sys
from pathlib import Path
import struct


def to_bin_file(file_path):
    file_path = Path(file_path)
    bin_file = file_path.parent / f'{file_path.name}.bin'

    content = []
    with open(file_path) as fd:
        content = fd.readlines()

    content = [
        i.strip()
        for i in content
    ]

    with open(bin_file, 'wb') as fd:
        for i in content:
            fd.write(struct.pack('>H', int(i, 2)))


if __name__ == '__main__':
    to_bin_file(sys.argv[1])
