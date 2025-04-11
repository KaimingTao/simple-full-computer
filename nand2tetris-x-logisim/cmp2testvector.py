from pathlib import Path
import sys


def work(cmp_folder_path):
    cmp_folder_path = Path(cmp_folder_path).resolve()

    for f in cmp_folder_path.iterdir():
        if f.suffix == '.cmp':
            convert(f)


def convert(cmp_file_path):

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
            content.append(values)

    content = fix_n_bit(content)

    with open(test_vector_path, 'w') as fd:
        for row in content:
            fd.write(' '.join(row))
            fd.write('\n')


def fix_n_bit(content):
    headers = content[0]
    column_number_of_bits = [
        len(c)
        for c in content[1]
    ]
    headers = [
        h if nbits == 1 else f"{h}[{nbits}]"
        for nbits, h in zip(column_number_of_bits, headers)
    ]
    content[0] = headers
    return content


if __name__ == '__main__':
    work(sys.argv[1])
