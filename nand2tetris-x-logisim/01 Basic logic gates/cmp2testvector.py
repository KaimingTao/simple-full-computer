from pathlib import Path
import sys


def work(cmp_file_path):
    cmp_file_path = Path(cmp_file_path).resolve()
    test_vector_path = cmp_file_path.parent / f"{cmp_file_path.stem}.testvector.txt"

    content = []

    with open(cmp_file_path) as fd:
        for idx, line in enumerate(fd.readlines()):
            values = line.split('|')
            values = [
                v.strip()
                for v in values
                if v.strip()
            ]
            values = [
                v if v != 'out' else 'o'
                for v in values
            ]
            values = [
                v if v != 'in' else 'i'
                for v in values
            ]
            content.append(' '.join(values))

    with open(test_vector_path, 'w') as fd:
        for row in content:
            fd.write(row)
            fd.write('\n')


if __name__ == '__main__':
    work(sys.argv[1])
