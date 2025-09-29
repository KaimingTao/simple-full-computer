#!/usr/bin/env python3
from pathlib import Path
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine

def main(source):

    print("Start Compiling...")

    src = Path(source)
    if not src.is_file() and not src.is_dir():
        raise Exception("Source Code not found.")

    if src.is_file():
        if src.suffix != '.jack':
            raise Exception("Source file is not jack")
        
        output_file = src.parent / src.name.replace('.jack', '-Test.xml')
        tokenizer = JackTokenizer(src)
        CompilationEngine(tokenizer, output_file).work()

    else:
        for item in src.iterdir():
            if item.suffix == '.jack':
                output_file = item.parent / item.name.replace('.jack', '-Test.xml')
                tokenizer = JackTokenizer(item)
                CompilationEngine(tokenizer, output_file).work()

    print('Finish Compiling.')


if __name__ == '__main__':
    import sys
    main(sys.argv[1])