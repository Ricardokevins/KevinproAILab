import copy
class test1:
    def __init__(self):
        self.data = [[1,2],[2,3]]

t = test1()
print(t.data)

t2 = test1()
t2.data = copy.deepcopy(t.data)

print(t2.data)

t2.data[0][0]= 10000

print(t.data)
print(t2.data)