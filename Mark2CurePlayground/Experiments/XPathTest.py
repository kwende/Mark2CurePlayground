import lxml.etree

tree = lxml.etree.parse('C:/Users/Ben/Desktop/test.xml')

ret = tree.xpath("/bookstore/book/title[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='learning']")
#ret = t.xpath(".//start/test[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'hello']")
print()