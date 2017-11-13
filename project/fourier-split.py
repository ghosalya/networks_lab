# fft split tryout

from numpy.fft import fft, ifft

f = open('test.txt', 'r')
fr = f.read()
print(fr)
fb = bytearray()
fb.extend(map(ord,fr))
print(fb)
ft = fft(fb)
print(ft)
print(len(fr), len(fb), len(ft))
ift = ifft(ft[0:])
ifts = bytearray()
ifts.extend(map(ord,ift))
print(ifts)
