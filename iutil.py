import getopt
import os
import sys
from exif import Image


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
    print('\t-d, --dir : directory')
    print("\t-r, --rename : rename the contents file to data time's type name")
    print("\t-g, --gps : set the gps information")
    print("\t-l, --location : show the gps information")
    print('\t-h, --help : help')
    print('Example:')
    print('\tiutil -rd /data/files/')
    # print(bin_name + )


def rename_files(files_dir):
    os.chdir(files_dir)
    print('Rename in ', os.getcwd())
    print('-------------------------------------------------')

    for f in os.listdir():
        file_name, file_ext = os.path.splitext(f)
        with open(f, "rb") as image_stream:
            img = Image(image_stream)
            datetime = get_datetime(img)

        new_datetime = get_new_file_name(datetime)
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


def set_gps(file_dir):
    path, filename = os.path.split(file_dir)
    os.chdir(path)
    with open(filename, "rb") as f:
        img = Image(f)

    print(dir(img))

    # with open(filename, "wb") as f:
    #     # setattr(img, 'gps_latitude', (37.0, 31.0, 20.0))
    #     img.gps_latitude = (37.0, 31.0, 20.0)
    #     img.gps_longitude = (127.0, 6.0, 59.6)
    #     f.write(img.get_file())

    # print("{}\t-> ({}, {})".format(f, img.gps_latitude, img.gps_longitude))


def print_location(files_dir):
    os.chdir(files_dir)
    print('Show GPS location in ', os.getcwd())
    print('-------------------------------------------------')

    for f in os.listdir():
        file_name, file_ext = os.path.splitext(f)

        with open(f, "rb") as image_stream:
            try:
                img = Image(image_stream)
            except AssertionError:
                # 동영상인 경우 처리 필요
                print(f)
                continue

            # print(dir(img))

        if "gps_latitude" in dir(img):
            print("{}\t-> ({}, {})".format(f, img.gps_latitude, img.gps_longitude))
        else:
            print("{}\t-> NO GPS".format(f))


def argv_process(argv):
    target = ''
    flag_rename = False
    flag_gps = False
    flag_location = False

    try:
        opts, args = getopt.getopt(argv, "hrl:g:d:", ["help", "rename", "location=", "dir=", "gps="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
            sys.exit(2)
        elif opt in ("-r", "--rename"):
            flag_rename = True
        elif opt in ("-d", "--dir"):
            target = arg
        elif opt in ("-g", "--gps"):
            flag_gps = True
            target = arg
        elif opt in ("-l", "--location"):
            flag_location = True
            target = arg

    if flag_rename:
        rename_files(target)
    elif flag_gps:
        set_gps(target)
    elif flag_location:
        print_location(target)

    sys.exit(0)


if __name__ == '__main__':
    argv_process(sys.argv[1:])




