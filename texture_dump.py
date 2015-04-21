import struct,os
from cStringIO import StringIO
from GIDecode import *
from PIL import Image
from EFX_plugin import efx2tim
import glob
import shutil
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst
def forceGetEFXpos(fn):
    fp = open(fn , 'rb')
    size = os.path.getsize(fn)
    pos = 0
    efx_pos_list = []
    while pos < ((size / 8) * 0x8) :
        tmp_pos = fp.tell()
        data = fp.read(0x8)
        if data[:5] == 'EFX00':
            fp.seek(4, 1)
            full_tim_size = 0
            tim_size = struct.unpack('I' , fp.read(4))[0]

            full_tim_size += tim_size
            fp.seek(tim_size-0x10 , 1)
            pos += full_tim_size
            efx_pos_list.append((tmp_pos , full_tim_size))
        else:
            pos += 8
    fp.close()
    return efx_pos_list 
def forceGetTIM2pos(fn):

    fp = open(fn , 'rb')
    size = os.path.getsize(fn)
    pos = 0
    tim_pos_list = []
    while pos < ((size / 8) * 0x8) :
        tmp_pos = fp.tell()
        data = fp.read(0x8)
        if data[:4] == '\x54\x49\x4D\x32':
            print('get tim2')
            im_nums, = struct.unpack('H' , data[6:8])
            fp.seek(8,1)
            full_tim_size = 0
            for i in range(im_nums):
                tim_size = struct.unpack('I' , fp.read(4))[0]

                full_tim_size += tim_size
                fp.seek(tim_size-4 , 1)
            pos += full_tim_size
            tim_pos_list.append((tmp_pos , full_tim_size + 0x10))
        else:
            pos += 8
    fp.close()
    return tim_pos_list
def getEFX_extinfo(efx_buffer):
    EFX_MAGIC = efx_buffer.read(4)
    efx_info_list = []
    if EFX_MAGIC == 'EFX0':
        efx_buffer.seek(0xc)
        efx_size ,  = struct.unpack('I' , efx_buffer.read(4))
        pos = 0x10
        while pos < efx_size - 0x40:
            efx_buffer.seek(pos)
            texture_size , unk ,texture_size_b   = struct.unpack('3I' , efx_buffer.read(0xc))
            blank , blank , gid , texture_id  = struct.unpack('4B' , efx_buffer.read(0x4))
            image_type_id , unk = struct.unpack('2H' , efx_buffer.read(0x4))
            rwidth , rheight = struct.unpack('2H' , efx_buffer.read(0x4))
            gwidth , gheight = struct.unpack('2H' , efx_buffer.read(0x4))
            efx_buffer.seek(4 ,1)
            width , height = rwidth*2 , rheight*2
            if image_type_id == 0x81:
                im_type = '8BPP'
                palette_size = 0x400
                palette_color_nums = 256
                if (texture_size > 0) and (texture_size == (0x400 + 0x20 + width * height)) :
                    palette_data = efx_buffer.read(palette_size)
                    data_pos = efx_buffer.tell()
                    image_data = efx_buffer.read(width * height)
                    pos += texture_size
                    efx_info_list.append((im_type , 
                                          palette_color_nums , 
                                          width , 
                                          height , 
                                          data_pos , 
                                          image_data , 
                                          palette_data))
                else:
                    pos += 0x20
            elif image_type_id == 0x80:
                im_type = '4BPP'
                palette_size = 0x40
                palette_color_nums = 16
                if (texture_size > 0) and (texture_size == (0x40 + 0x20 + width * height /2)) :
                    palette_data = efx_buffer.read(palette_size)
                    data_pos = efx_buffer.tell()
                    image_data = efx_buffer.read(width * height)
                    pos += texture_size
                    efx_info_list.append((im_type , 
                                          palette_color_nums , 
                                          width , 
                                          height , 
                                          data_pos , 
                                          image_data , 
                                          palette_data))
                else:
                    pos += 0x20
            else:
                pos += 0x20
    
    
    return efx_info_list
def getPNG_extinfo(fn):
    im = Image.open('cnpng\\%s'%fn).convert('RGBA')
    width,height=(im.size[0],im.size[1])
    return (width , height ,im)
    
def getTIM2_extinfo(tim_buffer):
    TIM2_MAGIC = tim_buffer.read(4)
    tim_info_list = []
    if TIM2_MAGIC == 'TIM2':
        ver , im_nums = struct.unpack('2H' , tim_buffer.read(4))
        tim_buffer.seek(8 , 1)
        for i in xrange(im_nums):
            im_type = ''
            palette_type = ''
            tim_size , palette_size , data_size   = struct.unpack('3I' , tim_buffer.read(12))
            header_size , palette_color_nums = struct.unpack('2H' , tim_buffer.read(4))
            fourCC = struct.unpack('>4B' , tim_buffer.read(4))
            if (fourCC[2] , fourCC[3]) == (0 , 1):#16BPP
                im_type = 'RGBA4444'
            elif (fourCC[2] , fourCC[3]) == (0 , 2):#24BPP
                im_type = 'RGBA8880'
            elif (fourCC[2] , fourCC[3]) == (0 , 3):#32BPP
                im_type = 'RGBA8888'    
            elif (fourCC[2] , fourCC[3]) == (1 , 4):#4BPP
                im_type = '4BPP'
                palette_type = 'C16'
                if palette_size == 0:
                    palette_type = 'L4'
            elif (fourCC[2] , fourCC[3]) == (2 , 4):
                im_type = '4BPP'
                palette_type = 'C24'    
                if palette_size == 0:
                    palette_type = 'L4'                
            elif (fourCC[2] , fourCC[3]) == (3 , 4):
                im_type = '4BPP'
                palette_type = 'C32'
                if palette_size == 0:
                    palette_type = 'L4'                
            elif (fourCC[2] , fourCC[3]) == (1 , 5):#8BPP
                im_type = '8BPP'
                palette_type = 'C16'
                if palette_size == 0:
                    palette_type = 'L8'
            elif (fourCC[2] , fourCC[3]) == (2 , 5):
                im_type = '8BPP'
                palette_type = 'C24'    
                if palette_size == 0:
                    palette_type = 'L8'                
            elif (fourCC[2] , fourCC[3]) == (3 , 5):
                im_type = '8BPP'
                palette_type = 'C32'
                if palette_size == 0:
                    palette_type = 'L8'
            m_width , m_height = struct.unpack('2H' , tim_buffer.read(4))
            TEX_0 , TEX_1 , TEX_A = struct.unpack('QQI' , tim_buffer.read(0x14))
            TEXCLUT , = struct.unpack('I' , tim_buffer.read(4))
            tim_buffer.seek(header_size-0x30 , 1)
            data_pos = tim_buffer.tell()
            image_data = tim_buffer.read(data_size)
            palette_data = tim_buffer.read(palette_size)
            tim_info_list.append((im_type , 
                                  palette_type , 
                                  palette_color_nums , 
                                  m_width , 
                                  m_height , 
                                  data_pos , 
                                  image_data , 
                                  palette_data))
    return tim_info_list
            
            
        
    
def TEX2PNG(fn):
    tim_pos_list = forceGetTIM2pos(fn)
    fp = open(fn , 'rb')
    for i in xrange(len(tim_pos_list)):
        (tim_pos , tim_size) = tim_pos_list[i]
        fp.seek(tim_pos)
        tim_buffer = StringIO()
        tim_data = fp.read(tim_size)
        tim_buffer.write(tim_data)
        tim_buffer.seek(0)
        tim_info_list = getTIM2_extinfo(tim_buffer)
        for j in xrange(len(tim_info_list)):
            im_type , palette_type , palette_color_nums , \
                m_width , m_height , data_pos , image_data , \
                palette_data = tim_info_list[j]
            print(im_type ,palette_type)
            if palette_type == 'C16':
                byte_len = 2
                palette_list = getPaletteData(palette_data , \
                                              0x80 , 2 , False , 0 )
            if palette_type == 'C24':
                byte_len = 3
                palette_list = getPaletteData(palette_data , \
                                              0x80 , 3 , False , 0 )
            if palette_type == 'C32':
                byte_len = 4            
                palette_list = getPaletteData(palette_data , \
                                              0x80 , 4 , False , 0 )   
            if palette_type == 'L4':
                palette_list = setAlphaPalette16()
                
            if palette_type == 'L8':
                palette_list = setAlphaPalette256()
            
            if im_type == '4BPP':
                pixel_list = paint_4BPP(m_width, m_height, m_width, m_height, 
                                       image_data, 
                                       palette_list, 
                                       'BIG', 
                                       'PS2')
            if im_type == '8BPP':
                palette_list = tile_pal(palette_list, 8 , 2)
                pixel_list = paint8BPP(m_width, m_height, m_width, m_height, 
                                       image_data, 
                                       palette_list, 
                                       'linear', 
                                       16 , 16 , 'PS2')
            if im_type == 'RGBA4444':
                pixel_list = paintRGBA4444(m_width, m_height, m_width, m_height,image_data,
                                           'RGBA' , 'PS2')
            if im_type == 'RGBA8880':
                pixel_list = paintRGBA8880(m_width, m_height, m_width, m_height,image_data,
                                           'RGBA' , 'PS2')
            if im_type == 'RGBA8888':
                pixel_list = paintRGBA8888(m_width, m_height, m_width, m_height,image_data,
                                           'RGBA' , 'PS2')
            im = Image.new('RGBA', (m_width, m_height))
            im.putdata(tuple(pixel_list))
            im.save('png\\%s.tm2.%d.%d.%s.%s.png'%(fn[4:] , i , j ,
                                               im_type , palette_type))
            
    fp.close()
def EFX2PNG(fn):
    efx_pos_list = forceGetEFXpos(fn)
    fp = open(fn , 'rb')
    for i in xrange(len(efx_pos_list)):
        (efx_pos , efx_size) = efx_pos_list[i]
        fp.seek(efx_pos)
        efx_buffer = StringIO()
        efx_data = fp.read(efx_size)
        efx_buffer.write(efx_data)
        efx_buffer.seek(0)
        efx_info_list = getEFX_extinfo(efx_buffer)
        for j in xrange(len(efx_info_list)):
            im_type , palette_color_nums , \
                m_width , m_height , data_pos , image_data , \
                palette_data = efx_info_list[j]
            if im_type == '8BPP':
                image_data = efx2tim(m_width , m_height, image_data, 'EFX2TIM')
                palette_list = getPaletteData(palette_data , \
                                              0x80 , 4 , False , 0 )
                palette_list = tile_pal(palette_list, 8 , 2)
                pixel_list = paint8BPP(m_width, m_height, m_width, m_height, 
                                       image_data, 
                                       palette_list, 
                                       'linear', 
                                       16 , 16 , 'PS2')
                im = Image.new('RGBA', (m_width, m_height))
                im.putdata(tuple(pixel_list))
                im.save('png\\%s.efx.%d.%d.%s.png'%(fn[4:] , i , j ,
                                                   im_type))
            
        
def PNG2TIM(fn):
    print('Load image :%s'%fn)
    if '.tm2' in fn.lower():
        image_fldr = 'img'
        src_fldr = 'iso'
        o_file_name = '.tm2'.join(fn.split('.tm2')[:-1])
        id0 , id1 , im_type , palette_type = fn.split('.tm2')[-1].split('.')[1:5]
        id0 = int(id0)
        id1 = int(id1)
        dst = image_fldr+r'//%s'%o_file_name
        src = src_fldr+r'//%s'%o_file_name
        if not os.path.exists(image_fldr+r'//%s'%o_file_name):
            shutil.copy(src, dst)
        tim_pos_list = forceGetTIM2pos(dst)
        tim_pos , tim_size = tim_pos_list[id0]
        fp = open(dst , 'rb+')
        fp.seek(tim_pos)
        tim_buffer = StringIO()
        tim_data = fp.read(tim_size)
        tim_buffer.write(tim_data)
        tim_buffer.seek(0)
        tim_info_list = getTIM2_extinfo(tim_buffer)
        im_type , \
            palette_type , \
            palette_color_nums , \
            m_width , \
            m_height , \
            data_pos , \
            image_data , \
            palette_data = tim_info_list[id1]
        palette_list = []
        if palette_type == 'C16':
                byte_len = 2
                palette_list = getPaletteData(palette_data , \
                                              0x80 , 2 , False , 0 )
        if palette_type == 'C24':
                byte_len = 3
                palette_list = getPaletteData(palette_data , \
                                              0x80 , 3 , False , 0 )
        if palette_type == 'C32':
                byte_len = 4            
                palette_list = getPaletteData(palette_data , \
                                              0x80 , 4 , False , 0 )   
        if palette_type == 'L4':
                palette_list = setAlphaPalette16()
                
        if palette_type == 'L8':
                palette_list = setAlphaPalette256()
        (width , height ,im) = getPNG_extinfo(fn)
        imdata = ''
        if (width == m_width) and (height == m_height):
            if im_type == '8BPP':
                print('write 8bpp')
                imdata = create8BPP(width, height, width, height, im, 
                                               palette_list, 
                                               'tile', 
                                               8, 2)
            if im_type == '4BPP':
                print('write 4bpp')
                imdata = create4BPP(width, height, width, height, im, 
                                               palette_list[:16], 
                                               'BIG')
        f_pos = data_pos + tim_pos
        fp.seek(f_pos)
        fp.write(imdata)
        fp.close()
                
    
def PNG2EFX(fn , forceUseTM2):
    print('Load image :%s'%fn)
    if '.efx' in fn.lower():
        image_fldr = 'img'
        src_fldr = 'iso'
        o_file_name , image_ext , id0 , id1 , im_type = fn.split('.')[:5]
        id0 = int(id0)
        id1 = int(id1)
        dst = image_fldr+r'//%s'%o_file_name
        src = src_fldr+r'//%s'%o_file_name
        if not os.path.exists(image_fldr+r'//%s'%o_file_name):
            shutil.copy(src, dst)
        efx_pos_list = forceGetEFXpos(dst)
        (efx_pos , efx_size) = efx_pos_list[id0]
        fp = open(dst , 'rb+')
        fp.seek(efx_pos)
        efx_buffer = StringIO()
        efx_data = fp.read(efx_size)
        efx_buffer.write(efx_data)
        efx_buffer.seek(0)
        efx_info_list = getEFX_extinfo(efx_buffer)
        im_type , palette_color_nums , \
            m_width , m_height , data_pos , image_data , \
            palette_data = efx_info_list[id1]
        palette_list = getPaletteData(palette_data , \
                                      0x80 , 4 , False , 0 )
        if forceUseTM2 ==True:
            if os.path.exists('cntm2//%s.tm2'%fn[:-4]):
                print('force use tm2 data')
                tm2_name = 'cntm2//%s.tm2'%fn[:-4]
                tim_buffer = open(tm2_name  , 'rb')
                tim_info_list = getTIM2_extinfo(tim_buffer)
                simage_data , spalette_data = tim_info_list[0][-2] , tim_info_list[0][-1]
                if len(palette_data) == 0x400:
                    imdata = simage_data[:m_width*m_height]
                    width, height = m_width, m_height
                    imdata = efx2tim(width, height, imdata, 'TIM2EFX')
                    f_pos = data_pos + efx_pos
                    fp.seek(f_pos - 0x400)
                    fp.write(spalette_data)
                    fp.seek(f_pos)
                    fp.write(imdata)
                    fp.close()
                    return None
        (width , height ,im) = getPNG_extinfo(fn)
        imdata = ''
        if (width == m_width) and (height == m_height):
            imdata = create8BPP(width, height, width, height, im, 
                               palette_list, 
                               'tile', 
                               8, 2)
            imdata = efx2tim(width, height, imdata, 'TIM2EFX')
        f_pos = data_pos + efx_pos
        fp.seek(f_pos)
        fp.write(imdata)
        fp.close()
        
def test():
    fn = '1C_60'
    tim_pos_list = forceGetTIM2pos(fn)
    fp = open(fn , 'rb')
    for i in xrange(len(tim_pos_list)):
        (tim_pos , tim_size) = tim_pos_list[i]
        fp.seek(tim_pos)
        tim_buffer = StringIO()
        tim_data = fp.read(tim_size)
        dest = open('%s.%d.tm2'%(fn , i) , 'wb')
        dest.write(tim_data)
        dest.close()
    fp.close()
def atest():
    if not os.path.exists('png'):
        os.mkdirs('png')
    fl = dir_fn('iso')
    for fn in fl:
        fp = open(fn , 'rb')
        magic = fp.read(4)
        fp.close()
        print(u'读取文件：%s'%fn)
        EFX2PNG(fn)
    print('ok')
def btest():
    fl=glob.iglob(r'cnpng/*.png')
    for fn in fl:
        fn = fn.split("\\")[-1]
        print(u'读取文件：%s'%fn)
        PNG2EFX(fn , forceUseTM2 =False)
    print('ok')
def ctest():
    fl=glob.iglob(r'cnpng/*.png')
    for fn in fl:
        fn = fn.split("\\")[-1]
        print(u'读取文件：%s'%fn)
        PNG2EFX(fn , forceUseTM2 =True)
    print('ok')
def dtest():
    if not os.path.exists('png'):
        os.mkdirs('png')
    fl = dir_fn('iso')
    for fn in fl:
        print(u'读取文件：%s'%fn)
        TEX2PNG(fn)
def etest():
    if not os.path.exists('png'):
        os.mkdirs('png')
    fl=glob.iglob(r'cnpng/*.png')
    for fn in fl:
        fn = fn.split("\\")[-1]
        print(u'读取文件：%s'%fn)
        PNG2TIM(fn)
