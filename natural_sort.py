import re

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

if __name__ == '__main__':
    l=['2', '5', '1', '10']
    l=natural_sort(l)
    print(l)
