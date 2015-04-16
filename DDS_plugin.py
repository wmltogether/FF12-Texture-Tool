import os,struct
from PIL import Image
import GIDecode
from cStringIO import StringIO
def math_mipmap_level(dwHeight , dwWidth,dw_MIPMAP_Count):
    count = 0
    for i in xrange(dw_MIPMAP_Count):
        t = dwHeight  * dwWidth / (4**i)
        if t >= 4*4:
            count += t
    return count
def getDDSsize(dds_texture_block):
    dxt_texture_buffer = StringIO()
    dxt_texture_buffer.write(dds_texture_block)
    dxt_texture_buffer.seek(0)
    dds_macig = dxt_texture_buffer.read(4)
    '''
    DWORD dwSize (Size of structure. This member must be set to 124.)
    DWORD dwFlags (Flags to indicate valid fields. Always include
                                    DDSD_CAPS, DDSD_PIXELFORMAT, DDSD_WIDTH, DDSD_HEIGHT.)
    DWORD dwHeight (Height of the main image in pixels)
    DWORD dwWidth  (Width of the main image in pixels)
    '''
    dwSize , dwFlags , dwHeight , dwWidth = struct.unpack('4I' , dxt_texture_buffer.read(16))
    dwPitchOrLinearSize, = struct.unpack('I' , dxt_texture_buffer.read(4))
    dwDepth , dw_MIPMAP_Count = struct.unpack('2I' , dxt_texture_buffer.read(8))

    dxt_texture_buffer.seek(0x2c , 1)#0000004C h
    dwSize1 , dwFlags1 = struct.unpack('2I' , dxt_texture_buffer.read(8))
    if dwFlags1 == 0x4:
        dwFlags_value = 'DDPF_FOURCC'
    elif dwFlags1 == 0x5:
        dwFlags_value = 'DDPF_FOURCC_A'
    elif dwFlags1 == 0x40:
        dwFlags_value = 'DDPF_RGB'
    elif dwFlags1 == 0x41:
        dwFlags_value = 'DDPF_RGBA'
    else:
        dwFlags_value = 'DDPF_UNKNOWN'
    #dwSize1 ALWAYS 0x20
    dwFourCC = dxt_texture_buffer.read(4)
    dwRGBBitCount, = struct.unpack('I' , dxt_texture_buffer.read(4))
    dwRBitMask , dwGBitMask , dwBBitMask , dwRGBAlphaBitMask= struct.unpack('4I' , dxt_texture_buffer.read(0x10))
    v0 , v1, v2, v3 = struct.unpack('4B' , dxt_texture_buffer.read(4))
    DDSCAPS_COMPLEX = v0
    DDSCAPS_MIPMAP = v2 <<16
    DDSCAPS_TEXTURE = v1 << 8
    if DDSCAPS_MIPMAP == 0x400000:
        dxt_full_size = math_mipmap_level(dwHeight , dwWidth,dw_MIPMAP_Count)
    else:
        #print(dwHeight , dwWidth)
        #print(hex(math_mipmap_level(dwHeight , dwWidth,1)) , hex(dwSize))
        dxt_full_size = math_mipmap_level(dwHeight , dwWidth,1)
    pixel_list = []
    #print(dwFourCC , dwFlags_value , hex(dwFlags1))
    if dwFourCC == 'DXT1' and dwFlags_value == 'DDPF_FOURCC':
        dxt_full_size = dxt_full_size /2  + dwSize + 4
    if dwFourCC == 'DXT1' and dwFlags_value == 'DDPF_FOURCC_A':
        dxt_full_size = dxt_full_size /2  + dwSize + 4
    elif dwFourCC == 'DXT3' and dwFlags_value == 'DDPF_FOURCC':
        dxt_full_size = dxt_full_size /2 + dwSize + 4
    elif dwFourCC == 'DXT3' and dwFlags_value == 'DDPF_FOURCC_A':
        dxt_full_size = dxt_full_size /2   + dwSize + 4
    elif dwFourCC == 'DXT5' and dwFlags_value == 'DDPF_FOURCC':
        dxt_full_size = dxt_full_size + dwSize + 4
    elif dwFourCC == 'DXT5' and dwFlags_value == 'DDPF_FOURCC_A':
        dxt_full_size = dxt_full_size  + dwSize + 4
    elif dwRGBBitCount == 32 and dwFlags_value == 'DDPF_RGBA':
        dxt_full_size = dxt_full_size *4 + dwSize + 4

    elif dwRGBBitCount == 16 and dwFlags_value == 'DDPF_RGBA':
        dxt_full_size = dxt_full_size *4 + dwSize + 4
    else:
        dxt_full_size = dwSize + 4
    dxt_texture_buffer.flush()
    #print('size:' + hex(dxt_full_size))
    return dxt_full_size
def get_DDS_texture_info(dds_texture_block):
    dxt_texture_buffer = StringIO()
    dxt_texture_buffer.write(dds_texture_block)
    dxt_texture_buffer.seek(0)
    dds_macig = dxt_texture_buffer.read(4)
    '''
    DWORD dwSize (Size of structure. This member must be set to 124.)
    DWORD dwFlags (Flags to indicate valid fields. Always include
                                    DDSD_CAPS, DDSD_PIXELFORMAT, DDSD_WIDTH, DDSD_HEIGHT.)
    DWORD dwHeight (Height of the main image in pixels)
    DWORD dwWidth  (Width of the main image in pixels)
    '''
    dwSize , dwFlags , dwHeight , dwWidth = struct.unpack('4I' , dxt_texture_buffer.read(16))
    dwPitchOrLinearSize, = struct.unpack('I' , dxt_texture_buffer.read(4))
    dwDepth , dw_MIPMAP_Count = struct.unpack('2I' , dxt_texture_buffer.read(8))

    dxt_texture_buffer.seek(0x2c , 1)#0000004C h
    dwSize1 , dwFlags1 = struct.unpack('2I' , dxt_texture_buffer.read(8))
    if dwFlags1 == 0x4:
        dwFlags_value = 'DDPF_FOURCC'
    elif dwFlags1 == 0x5:
        dwFlags_value = 'DDPF_FOURCC_A'
    elif dwFlags1 == 0x40:
        dwFlags_value = 'DDPF_RGB'
    elif dwFlags1 == 0x41:
        dwFlags_value = 'DDPF_RGBA'
    else:
        dwFlags_value = 'DDPF_UNKNOWN'
    #dwSize1 ALWAYS 0x20
    dwFourCC = dxt_texture_buffer.read(4)
    dwRGBBitCount, = struct.unpack('I' , dxt_texture_buffer.read(4))
    dwRBitMask , dwGBitMask , dwBBitMask , dwRGBAlphaBitMask= struct.unpack('4I' , dxt_texture_buffer.read(0x10))
    v0 , v1, v2, v3 = struct.unpack('4B' , dxt_texture_buffer.read(4))
    DDSCAPS_COMPLEX = v0
    DDSCAPS_MIPMAP = v2 <<16
    DDSCAPS_TEXTURE = v1 << 8
    pixel_list = []
    dxt_texture_buffer.seek(0x80)
    if dwFourCC == 'DXT1' and dwFlags_value == 'DDPF_FOURCC_A':
        dxt_data_block =  dxt_texture_buffer.read(dwHeight * dwWidth / 2)
        pixel_list = GIDecode.decodeDXT1(dwWidth , dwHeight , dxt_data_block , True)
    elif dwFourCC == 'DXT1' and dwFlags_value == 'DDPF_FOURCC':
        dxt_data_block =  dxt_texture_buffer.read(dwHeight * dwWidth / 2)
        pixel_list = GIDecode.decodeDXT1(dwWidth , dwHeight , dxt_data_block , False)
    elif dwFourCC == 'DXT3':
        dxt_data_block =  dxt_texture_buffer.read(dwHeight * dwWidth / 2)
        pixel_list = GIDecode.decodeDXT3(dwWidth , dwHeight , dxt_data_block)
    elif dwFourCC == 'DXT5':
        dxt_data_block =  dxt_texture_buffer.read(dwHeight * dwWidth)
        pixel_list = GIDecode.decodeDXT5(dwWidth , dwHeight , dxt_data_block)
    elif dwRGBBitCount == 32 and dwFlags_value == 'DDPF_RGBA':
        dwFourCC = 'BGRA8888'
        dxt_data_block =  dxt_texture_buffer.read(dwHeight * dwWidth*4)
        pixel_list = GIDecode.paintRGBA8888(dwWidth , dwHeight ,dwWidth , dwHeight, dxt_data_block , 'BGRA' , 'win32')
    elif dwRGBBitCount == 16 and dwFlags_value == 'DDPF_RGBA':
        dwFourCC = 'GBAR4444'
        dxt_data_block =  dxt_texture_buffer.read(dwHeight * dwWidth*4)
        pixel_list = GIDecode.paintRGBA4444(dwWidth , dwHeight ,dwWidth , dwHeight, dxt_data_block , 'GBAR' , 'win32')
    else:
        pixel_list = []
    dxt_texture_buffer.flush()
    return pixel_list,dwWidth, dwHeight
