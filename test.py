def simple_decorator(func):
    def lines(*args):
        print('=' * 40)
        func(*args)
        print('=' * 40)
    return lines

@simple_decorator
def printer(str):
    print(str)

printer('Hello, World!')