import os
from django.core.exceptions import ValidationError

valid_ext_dict ={   '.bmp': 'BMP', '.dib': 'DIB', '.gif': 'GIF', '.tif': 'TIFF', '.tiff': 'TIFF',
        '.jfif': 'JPEG', '.jpe': 'JPEG', '.jpg':
        'JPEG', '.jpeg': 'JPEG', '.pbm': 'PPM', '.pgm': 'PPM', '.ppm': 'PPM', 
        '.pnm': 'PPM', '.png': 'PNG', '.apng': 'PNG', '.blp': 'BLP', '.bufr': 'BUFR', 
        '.cur': 'CUR', '.pcx': 'PCX', '.dcx': 'DCX', '.dds': 'DDS', '.ps': 'EPS', 
        '.eps': 'EPS', '.fit': 'FITS', '.fits': 'FITS', '.fli': 'FLI', '.flc': 'FLI', 
        '.ftc': 'FTEX', '.ftu': 'FTEX', '.gbr': 'GBR', '.grib': 'GRIB', '.h5': 'HDF5', 
        '.hdf': 'HDF5', '.jp2': 'JPEG2000', '.j2k': 'JPEG2000', '.jpc': 'JPEG2000', 
        '.jpf': 'JPEG2000', '.jpx': 'JPEG2000', '.j2c': 'JPEG2000', '.icns': 'ICNS', 
        '.ico': 'ICO', '.im': 'IM', '.iim': 'IPTC', '.mpg': 'MPEG', '.mpeg': 'MPEG', 
        '.mpo': 'MPO', '.msp': 'MSP', '.palm': 'PALM', '.pcd': 'PCD', '.pdf': 'PDF', 
        '.pxr': 'PIXAR', '.psd': 'PSD', '.bw': 'SGI', '.rgb': 'SGI', '.rgba': 'SGI', 
        '.sgi': 'SGI', '.ras': 'SUN', '.tga': 'TGA', '.icb': 'TGA', '.vda': 'TGA', 
        '.vst': 'TGA', '.webp': 'WEBP', '.wmf': 'WMF', '.emf': 'WMF', '.xbm': 'XBM', '.xpm': 'XPM'}

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    if not ext in valid_ext_dict:
        raise ValidationError(f'Unsupported file extension. only {", ".join(valid_ext_dict)}')