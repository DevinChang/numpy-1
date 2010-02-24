import numpy as np
import time

#x = np.random.randn(10)
#print "DUMMY 98765"
a = (np.float128(1234567890) * 10**10 + 1234567890)
print repr(a)
now = time.time()
a = np.longdouble(1234765876587)
for i in range(100000):
    b = long(a)
print time.time() - now
print b
print repr(np.float128(b))
#print a - np.float128(b)
#print a.__long__()
