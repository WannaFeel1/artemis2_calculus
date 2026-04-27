books = {'d':'f','g':'h'}
def add_book(b,a,c):
    b[a] = c
def remove_book(b,a):
    b.pop(a)
def find_book(b,a):
    res = b[a]
    return res
def list_books(b):
    a = list(b)
    return a

add_book(books,'k','j')
remove_book(books,'k')
res = find_book(books,'d')
a = list_books(books)
print(a)
print(res)
print(books)

