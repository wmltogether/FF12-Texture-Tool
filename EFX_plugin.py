import struct,os
from cStringIO import StringIO
def efx2tim(width , height , data ,opt):
    
    ndata_buffer = ['\x00' for i in range(width * height)]
    data_buffer = StringIO()
    data_buffer.write(data)
    data_buffer.seek(0)
    Rom = {}
    for i in xrange(width * height):
        y = ((i / (2 * width)) & 1) + (( i / (4 * width )) & 1) * 4 + (i & 1) * 2 + ( i / (8 * width)) * 8
        if ((y & 7) <2 or (y & 7 ) > 5):
            x = ((i >> 2) & 7) + 4 * (i & 2)
        else:    
            x = 4 + ((i >> 2) & 3) + 4 * (i & 2)-(i & 0x10) / 4
        x += ((i >> 5) << 4) & (width - 1)
        if opt == 'EFX2TIM':
            Rom[i] = (y * width + x)
        if opt == 'TIM2EFX':
            Rom[y * width + x] = i
    if opt == 'EFX2TIM':
        for i in xrange(len(data)):
            ndata_buffer[Rom[i]] = data_buffer.read(1)
    if opt == 'TIM2EFX':
        for i in xrange(len(data)):
            ndata_buffer[Rom[i]] = data_buffer.read(1)
    ndata = ''.join(ndata_buffer)
    return ndata
def test():
    fp = open('C_28B' , 'rb')
    fp.seek(0x30)
    pal = fp.read(0x400)
    width, height = 512 , 512
    data =fp.read(width * height)
    data = efx2tim(width , height , data ,'EFX2TIM')
    dest =open('C_28B.0.dat' , 'wb')
    dest.write(pal)
    dest.write(data)
    dest.close()
    fp.close()


