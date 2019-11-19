import argparse
import cchardet as chardet
import os
import sys

# _____ ARGUMENTS PARSER _______________________________________________________________________________________________


parser = argparse.ArgumentParser(
    prog='ass2srt',
    description='Convert SubStationAlpha v4.00+ (.ass) into SubRip (.srt)',
    epilog='GitHub Page: https://github.com/locobastos/ass2srt-python'
)

parser.add_argument('-id', '--input-directory',
                    type=str,
                    action='append',
                    nargs='+',
                    help='the path to the directory containing all .ass files')
parser.add_argument('-if', '--input-file',
                    type=str,
                    action='append',
                    nargs='+',
                    help='the path to the input file.')
args = parser.parse_args()


# _____ FUNCTiONS ______________________________________________________________________________________________________


def convert_ass_to_srt(in_file, out_file, in_char_enc):
    with open(in_file, 'r', encoding=in_char_enc) as infile, open(out_file, 'w', encoding=in_char_enc) as outfile:
        event_line = False
        dialogue_number = 1
        for line in infile:
            if not event_line:
                """
                Removes the [Script Info] and [V4+ Styles] headers
                """
                if line.startswith("Format: Layer"):
                    event_line = True
            else:
                """
                We are now on the Dialogue lines
                """
                if line not in ['\n', '\r\n'] or len(line.strip()) != 0:
                    outfile.write(str(dialogue_number) + '\n')
                    tmp_line = line.split(",", 9)
                    outfile.write(tmp_line[1].replace(".", ",") + " --> " + tmp_line[2].replace(".", ",") + '\n')
                    outfile.write(tmp_line[9].replace('\n', '').replace("\\N", '\n') + '\n\n')
                    dialogue_number += 1
    outfile.close()
    infile.close()


# _____ MAiN ___________________________________________________________________________________________________________


if not len(sys.argv) == 1:
    if args.input_file is not None:
        for ass_file in range(len(args.input_file)):
            ass_filename = args.input_file[ass_file][0]
            output_srt_file = ass_filename[:-4] + ".srt"
            if ass_filename.lower().endswith('.ass'):
                try:
                    with open(ass_filename, 'rb') as ass_opened_file:
                        char_enc = chardet.detect(ass_opened_file.read()).get('encoding')
                    ass_opened_file.close()
                    convert_ass_to_srt(ass_filename, output_srt_file, char_enc)
                except EnvironmentError:
                    print("The file " + ass_filename + " does not exist")
                    exit(10)

    if args.input_directory is not None:
        for ass_dir in args.input_directory:
            for ass_file in os.listdir(ass_dir[0]):
                ass_filename = ass_dir[0] + ass_file
                output_srt_file = ass_filename[:-4] + ".srt"
                if ass_filename.lower().endswith('.ass'):
                    try:
                        with open(ass_filename, 'rb') as ass_opened_file:
                            char_enc = chardet.detect(ass_opened_file.read()).get('encoding')
                        ass_opened_file.close()
                        convert_ass_to_srt(ass_filename, output_srt_file, char_enc)
                    except EnvironmentError:
                        print("The file " + ass_filename + " does not exist")
                        exit(10)
else:
    parser.print_help()
