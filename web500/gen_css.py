import codecs

from glob import glob
from scss import Scss
from os.path import basename, splitext, join, exists
from os import makedirs

def _convert(src, dst):
    css = Scss()
    source = codecs.open(src, 'r', encoding='utf-8').read()
    output = css.compile(source)
    outfile = codecs.open(dst, 'w', encoding='utf-8')
    outfile.write(output)
    outfile.close()

def convert_dir(source_dir, dest_dir):
    """Converts all .scss files in source_dir to .css files in dest_dir
    """
    #make directory if it doesn't already exist
    if not exists(dest_dir):
        makedirs(dest_dir)
    for filename in glob(join(source_dir, '*.scss')):
        res_filename = splitext(basename(filename))[0] + '.css'
        dst = join(dest_dir, res_filename)
        _convert(filename, dst)
        print('Compiled %s -> %s' % (filename, dst))
