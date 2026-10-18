from pathlib import Path
from PIL import Image, ImageOps
import multiprocessing.pool
from functools import partial

def resize(f, *, small_pic_dir):
    REF = 1600
    image = Image.open(f)
    image = ImageOps.exif_transpose(image)
    w, h = image.size
    if w > h:
        image.thumbnail((REF, h * (REF / w)), Image.LANCZOS)
    else:
        image.thumbnail((w * (REF / h), REF), Image.LANCZOS)
    new_path = small_pic_dir / f.name
    image.save(new_path, 'JPEG', quality=95)

def resize_wrapper(arg):
    args, kwargs = arg
    return resize(*args, **kwargs)

if __name__ == "__main__":
    this_dir = Path(__file__).parent
    small_pic_dir = this_dir / 'small'

    exensions = {'jpg', 'JPG', 'jpeg', 'JPEG', 'png', 'PNG'}
    files = [f  for ext in exensions for f in this_dir.rglob(f'*.{ext}') if not f.is_relative_to(small_pic_dir)]
    if not files:
        print(f"No image files to resize in {this_dir}. Exiting")
        exit(0)
    print(f"Found {len(files)}")
    if small_pic_dir.is_dir():
        raise OSError(f"Directory {small_pic_dir} already exists.")
    small_pic_dir.mkdir()
    print(f"Resizing {len(files)} files.")

    with multiprocessing.pool.Pool() as pool:
        pool.map(partial(resize, small_pic_dir=small_pic_dir), files)
