"""
  ___        _          _____                _ _
 / _ \      | |        |  ___|              (_) |
/ /_\ \_   _| |_ ___   | |__ _ __ ___   __ _ _| | ___ _ __
|  _  | | | | __/ _ \  |  __| '_ ` _ \ / _` | | |/ _ \ '__|
| | | | |_| | || (_) | | |__| | | | | | (_| | | |  __/ |
\_| |_/\__,_|\__\___/  \____/_| |_| |_|\__,_|_|_|\___|_|


V1.0.0: Script to generate a gif based on images captured from webcam
"""

# import modules
import os
import sys
import cv2
import imageio

from pathlib import Path
from time import strftime, gmtime
from PIL import Image


def get_images(capture_individual: bool = False, annot: str = None) -> list:
    cap = cv2.VideoCapture(0)

    frames = []
    image_count = 0
    font = cv2.FONT_HERSHEY_SIMPLEX

    while True:
        ret, frame = cap.read()
        cv2.imshow("frame", frame)

        if capture_individual:
            key = cv2.waitKey(delay=0)
            if key == ord("a"):
                image_count += 1
                frames.append(frame)
                print("Adding new image: {0}".format(image_count))
            elif key == ord("q"):
                break
        else:
            key = cv2.waitKey(delay=1)
            image_count += 1
            # Add annotations if required
            # TODO: Figure out a way to automatically handle different annotation per frame group
            if annot is not None:
                cv2.putText(frame, annot, (400, 600), font, 3, (237, 230, 211), 4, cv2.LINE_4)
            frames.append(frame)
            print("Adding new image: {0}".format(image_count))

        if key == ord("q"):
            break

    print("Number of images captured: {0}".format(len(frames)))

    # release the cap object
    cap.release()

    # close all windows
    cv2.destroyAllWindows()

    return frames


def make_gif_from_frames(frames: list, out_path: str) -> bool:
    with imageio.get_writer(out_path, format='GIF-PIL', mode='I') as writer:
        for idx, frame in enumerate(frames):
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            writer.append_data(rgb_frame)

    return True


def resize_gif(path: str, save_as: str = None, resize_to: tuple = None) -> bool:
    """
    Resizes a GIF saved at path to a given length:

    :param path: Path to the original gif file
    :param save_as: Path + filename to use for the new resized gif. If None, the path variable will be used (this will overwrite the original gif)
    :param resize_to: Optional tuple to customize the size of the new gif. If None, (x,y) sizes of the resized gif will default to (x//2, y//2) of the original gif
    :return: True
    """

    all_frames = extract_and_resize_frames(path, resize_to)

    if not save_as:
        save_as = path

    if len(all_frames) == 1:
        print("Warning: only 1 frame found")
        all_frames[0].save(save_as, optimize=True)
    else:
        all_frames[0].save(save_as, optimize=True, save_all=True, append_images=all_frames[1:], loop=1000)

    return True


def analyse_image(path: str) -> dict:
    """
    Pre-process pass over the image to determine the mode (full or additive). Necessary as assessing single frames isn't reliable. Need to know the mode before processing all frames.

    :param path: Path to the original gif to resize
    :return: The image size and the mode as a dict
    """

    im = Image.open(path)
    results = {'size': im.size, 'mode': 'full'}

    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass

    return results


def extract_and_resize_frames(path: str, resize_to: tuple = None) -> list:
    """
    Iterate the GIF, extracting each frame and resizing them

    :param path: Path to the original gif
    :param resize_to: Optional tuple to customize the size of the new gif. If None, (x,y) sizes of the resized gif will default to (x//2, y//2) of the original gif
    :return: A list containing all the resized frames
    """

    mode = analyse_image(path)['mode']

    im = Image.open(path)

    if resize_to is None:
        resize_to = (im.size[0] // 2, im.size[1] // 2)

    i = 0
    p = im.getpalette()
    last_frame = im.convert('RGBA')

    all_frames = []

    try:
        while True:
            # If the GIF uses local colour tables, each frame will have its own palette.
            # If not, we need to apply the global palette to the new frame.
            if not im.getpalette():
                im.putpalette(p)

            new_frame = Image.new('RGBA', im.size)

            # Is this file a "partial"-mode GIF where frames update a region of a different size to the entire image?
            # If so, we need to construct the new frame by pasting it on top of the preceding frames.
            if mode == 'partial':
                new_frame.paste(last_frame)

            new_frame.paste(im, (0, 0), im.convert('RGBA'))

            new_frame.thumbnail(resize_to, Image.ANTIALIAS)
            all_frames.append(new_frame)

            i += 1
            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        pass

    return all_frames


def run(out_path: str, annot: str = None, resize: bool = False) -> bool:
    # Generate the current time for file naming convention
    current_time = strftime('%Y-%m-%d_%H%M%S', gmtime())
    out_path = out_path + current_time
    out_path = os.path.join(out_path, "image_capture")

    # Make sure that the storage directory exists if it's not none. If it doesn't, create it.
    if out_path is not None:
        Path(out_path).mkdir(parents=True, exist_ok=True)

    frames = get_images(capture_individual=False, annot=annot)

    gif_ = make_gif_from_frames(frames=frames, out_path=out_path + 'generated_gif.gif')

    if gif_:
        print('Gif saved')

    if resize:
        gif_resized = resize_gif(path=out_path + 'generated_gif.gif', save_as=out_path + 'resized_generated_gif.gif')
        if gif_resized:
            print('Gif resized')

    return True


if __name__ == '__main__':
    # Run script here.  We'll want to add options for adding text, as well as image compression
    path_to_save = '../../data/saved_gif_'
    annotation = 'PAAAACHO'
    # annotation = None
    resize_output_gif = True
    res_ = run(out_path=path_to_save, annot=annotation, resize=resize_output_gif)
    if res_:
        print('Process complete')

    sys.exit()
