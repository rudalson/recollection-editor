import getopt
import os
import shutil
import sys

import exiftool
from exif import Image
import datetime


def get_datetime(image):
    if "datetime" in dir(image):
        return image.datetime
    else:
        return None


def get_new_file_name(date_time):
    if date_time is None:
        return None

    date, time = date_time.split(" ")
    # print(date, time)
    date_replaced = date.replace(":", "-")
    time_replaced = time.replace(":", ".")

    return date_replaced + " " + time_replaced


def print_usage():
    base = os.path.basename(__file__)
    bin_name, _ = os.path.splitext(base)
    print('Usage:')
    # print('\t-t, --target : target directory')
    print("\t-r, --rename : rename the contents file to data time's type name")
    # print("\t-g, --gps : set the gps information")
    print("\t-l, --location : show the gps information")
    print('\t-h, --help : help')
    print('Example:')
    print('\tmutil -r /data/files/')
    print('\tmutil -l /data/files/')
    # print(bin_name + )


def is_image_file(filename_ext):
    if filename_ext.lower() in ['.jpg', '.jpeg']:
        return True
    return False


def is_movie_file(filename_ext):
    if filename_ext.lower() in ['.mov', '.mp4', '.avi']:
        return True
    return False


def get_image_gps(file_path):
    with open(file_path, "rb") as image_stream:
        try:
            img = Image(image_stream)
            if "gps_latitude" in dir(img):
                print(img.gps_latitude)
                return img.gps_latitude, img.gps_longitude
        except:
            print(file_path, "-> failed")
    return None, None


def get_movie_gps(file_path):
    with exiftool.ExifTool() as et:
        try:
            meta_data = et.get_metadata(file_path)
            if "Composite:GPSLatitude" in meta_data:
                return meta_data["Composite:GPSLatitude"], meta_data["Composite:GPSLongitude"]
        except:
            print(file_path, "-> failed")

    return None, None


def argv_process(argv):
    target = ''
    path = ''
    flag_rename = False
    flag_gps = False
    flag_location = False
    flag_nogps = False

    try:
        opts, args = getopt.getopt(argv, "hr:l:g:m:", ["help", "rename=", "location=", "move=", "gps=", "nogps="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
            sys.exit(2)
        elif opt in ("-m", "--move"):
            target = arg
        elif opt in ("-r", "--rename"):
            flag_rename = True
            path = arg
        elif opt in ("-l", "--location"):
            flag_location = True
            path = arg
        elif opt in ("-g", "--gps"):
            flag_gps = True
            path = arg
        elif opt in "--nogps":
            flag_nogps = True
            path = arg

    if flag_rename:
        rename_files(path)
    elif flag_location:
        print_location(path)
    elif flag_gps:
        print_gps(path, target)
    elif flag_nogps:
        print_nogps(path, target)

    sys.exit(0)


def rename_files(files_dir):
    os.chdir(files_dir)
    print('Rename in ', os.getcwd())
    print('-------------------------------------------------')

    for f in os.listdir():
        file_name, file_ext = os.path.splitext(f)

        if is_image_file(file_ext):
            with open(f, "rb") as image_stream:
                try:
                    img = Image(image_stream)
                    date_time = get_datetime(img)
                except AssertionError:
                    print(f)
                    continue
        elif is_movie_file(file_ext):
            # with exiftool.ExifTool() as et:
            #     meta_data = et.get_metadata(f)
            #     print(file_name)
            #     dt = datetime.datetime.strptime(meta_data["QuickTime:MediaCreateDate"], "%Y:%m:%d %H:%M:%S")
            #     dt += datetime.timedelta(hours=9)   # 여긴 한국이니깐
            #     date_time = dt.strftime("%Y-%m-%d %H.%M.%S")
            dt = datetime.datetime.strptime(file_name, "%Y%m%d_%H%M%S")
            date_time = dt.strftime("%Y-%m-%d %H.%M.%S")
        else:
            continue

        new_datetime = get_new_file_name(date_time)
        if file_name == new_datetime:
            print(f)
            continue

        final_name = new_datetime
        for i in range(1, 11):
            if os.path.exists(os.path.join(os.getcwd(), final_name + file_ext)):
                final_name = new_datetime + '(' + str(i) + ')'
            else:
                break

        print("{} -> {}".format(f, final_name + file_ext))
        # os.rename(f, final_name + file_ext)


def print_location(path):
    os.chdir(path)
    print('Show GPS location in ', os.getcwd())
    print('-------------------------------------------------')

    for f in sorted(os.listdir()):
        file_name, file_ext = os.path.splitext(f)

        if is_image_file(file_ext):
            latitude, longitude = get_image_gps(f)
        elif is_movie_file(file_ext):
            latitude, longitude = get_movie_gps(f)
        else:
            continue

        if latitude is not None:
            print("{}\t-> {}, {}".format(f, latitude, longitude))
        else:
            print("{}\t-> NO GPS".format(f))

        # print(dir(img))


def print_gps(path, target_dir):
    os.chdir(path)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for f in sorted(os.listdir(path)):
        if os.path.isdir(f):
            continue

        with open(f, "rb") as image_stream:
            try:
                img = Image(image_stream)
            except AssertionError:
                # 동영상인 경우 처리 필요
                # print(f)
                continue

            # print(dir(img))

        if "gps_latitude" in dir(img):
            if target_dir == '':
                print(f)
            else:
                src = os.path.join(path, f)
                dst = os.path.join(target_dir, f)
                print("{} -> {}".format(src, dst))
                shutil.move(src, dst)


def print_nogps(path, target_dir):
    os.chdir(path)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for f in sorted(os.listdir(path)):
        if os.path.isdir(f):
            continue

        _, file_ext = os.path.splitext(f)
        if file_ext.lower() in ('.mp4', '.mov'):
            print(f)
            continue

        with open(f, "rb") as image_stream:
            try:
                img = Image(image_stream)
            except AssertionError:
                # 동영상인 경우 처리 필요
                # print(f)
                continue
            except:
                print("Exception : {}".format(f))
                # sys.stderr("Exception : {}".format(f))
                exit()

            # print(dir(img))

        if "gps_latitude" in dir(img):
            print(f)
        else:
            if target_dir == '':
                print(f)
            else:
                src = os.path.join(path, f)
                dst = os.path.join(target_dir, f)
                print("{} -> {}".format(src, dst))
                shutil.move(src, dst)


if __name__ == '__main__':
    argv_process(sys.argv[1:])
