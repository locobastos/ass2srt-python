import argparse
import cchardet
import re
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


# _____ SHARED VARiABLES _______________________________________________________________________________________________

fonts_name_list = []
style_list = []

# _____ FUNCTiONS ______________________________________________________________________________________________________


def convert_ass_to_srt(ass_filename):
    output_srt_file = ass_filename[:-4] + ".srt"
    if ass_filename.lower().endswith('.ass'):
        try:
            with open(ass_filename, 'rb') as ass_opened_file:
                char_enc = cchardet.detect(ass_opened_file.read()).get('encoding')
            with open(ass_filename, 'r', encoding=char_enc) as infile, open(output_srt_file, 'w', encoding=char_enc) as outfile:
                # I'm doing a loop over each lines, event_line is used to know if we have reach the [Events] section
                event_line = False
                dialogue_number = 1  # the number indicating which subtitle it is in the sequence.
                for line in infile:
                    if not event_line:
                        """
                        Removes the [Script Info] and [V4+ Styles] headers
                        + The Format line on the [Events] section
                        """
                        if line.startswith("Style: "):
                            split_line = line.split(",")
                            style_name = split_line[0]
                            if style_name not in style_list:
                                style_list.append(style_name)
                            font_name = split_line[1]
                            if font_name not in fonts_name_list:
                                fonts_name_list.append(font_name)
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
                            outfile.write(remove_ass_tags(tmp_line[9]))
                            dialogue_number += 1
            outfile.close()
            infile.close()
        except EnvironmentError:
            print("The file " + ass_filename + " does not exist")
            exit(10)


def remove_ass_tags(str_input):
    # Remove current \n
    str_temp = str_input.replace('\n', '')
    # Replace ASS \N by \n
    str_temp = str_temp.replace(r'\N', '\n')

    # Source of all ASS Tags: http://docs.aegisub.org/3.2/ASS_Tags/
    # Replace italic tags
    str_temp = str_temp.replace(r'{\i1}', '<i>').replace(r'{\i0}', '</i>')
    # Replace bold tags
    str_temp = str_temp.replace(r'{\b1}', '<b>').replace(r'{\b0}', '</b>')
    # Remove {\b100} to {\b900} explicit bold weight
    re.sub(r'{\\b[1-9]00}', '', str_temp)
    # Replace underline tags
    str_temp = str_temp.replace(r'{\u1}', '<u>').replace(r'{\u0}', '</u>')
    # Remove Strikeout tags
    re.sub(r'\{\\s[0-1]\}', '', str_temp)
    # Remove border tags + extended
    re.sub(r'\{\\[x-y]?bord[0-9]*\.?[0-9]*\}', '', str_temp)
    # Remove shadow distance + extended
    re.sub(r'\{\\[x-y]?shad[0-9]*\.?[0-9]*\}', '', str_temp)
    # Remove blur edge (Gaussian kernel)
    re.sub(r'\{\\blur[0-9]*\.?[0-9]*\}', '', str_temp)
    # Remove font name
    regex_fonts_name = "|".join(fonts_name_list)
    re.sub(r'{\\fn(' + regex_fonts_name + ')}', '', str_temp)
    # Remove font size
    re.sub(r'\{\\fs[1-9]*\}', '', str_temp)
    # Remove font scale
    re.sub(r'\{\\fsc[x-y]?[0-9]*\}', '', str_temp)
    # Remove letter spacing
    re.sub(r'\{\\fsp\-?[0-9]*\.?[0-9]*\}', '', str_temp)
    # Remove text rotation
    re.sub(r'\{\\fr[x-z]?[0-9]*\}', '', str_temp)
    # Remove text shearing
    re.sub(r'\{\\fa[x-y]+[0-9]*\.?[0-9]*\}', '', str_temp)
    # Remove font encoding
    re.sub(r'\{\\fe[0-9]*\}', '', str_temp)
    # Remove text color
    re.sub(r'\{\\[1-4]?c\&H[0-9a-fA-F]*&\}', '', str_temp)
    # Remove transparency text (alpha)
    re.sub(r'\{\\[1-4]?a(?:lpha)?\&H[0-9a-fA-F]*\}', '', str_temp)
    # Remove line alignment
    re.sub(r'\{\\a[n]?[0-9]+\}', '', str_temp)
    # Remove karaoke effect
    re.sub(r'\{\\[k,K][f,o]?[0-9]*\}', '', str_temp)
    # Remove wrap style
    re.sub(r'\{\\q[0-3]*\}', '', str_temp)
    # Remove reset style
    regex_style_names = "|".join(style_list)
    re.sub(r'{\\r(' + regex_style_names + ')?}', '', str_temp)
    # Remove text position
    re.sub(r'\{\\pos\([0-9]*\,[0-9]*\)\}', '', str_temp)
    # Remove movement
    re.sub(r'\{\\move\([0-9]*\,[0-9]*\,[0-9]*\,[0-9]*\,?[0-9]*\,?[0-9]*\)\}', '', str_temp)
    # Remove rotation
    re.sub(r'\{\\org\([0-9]*\,[0-9]*\)\}', '', str_temp)
    # Remove fade
    re.sub(r'\{\\fad\([0-9]*\,[0-9]*\,?[0-9]*\,?[0-9]*\,?[0-9]*\,?[0-9]*\,?[0-9]*\)\}', '', str_temp)
    # Remove animated transform
    re.sub(r'\\t\(\\?[0-9a-zA-Z&]*\.?[0-9]*\,?\\?[0-9a-zA-Z&]*\.?[0-9]*\,?\\?[0-9a-zA-Z&]*\.?[0-9]*\,?\\?[0-9a-zA-Z&]*\.?[0-9]*\)\}', '', str_temp)
    # Remove clip (rectangle)
    re.sub(r'\{\\[i]?clip\([0-9]*\,[0-9]*\,[0-9]*\,[0-9]*\\)\}', '', str_temp)
    # Add \n at the end of the line
    str_temp += '\n\n'

    return str_temp

# _____ MAiN ___________________________________________________________________________________________________________


if not len(sys.argv) == 1:
    if args.input_file is not None:
        for ass_file in range(len(args.input_file)):
            convert_ass_to_srt(args.input_file[ass_file][0])

    if args.input_directory is not None:
        for ass_dir in args.input_directory:
            for ass_file in os.listdir(ass_dir[0]):
                convert_ass_to_srt(ass_dir[0] + ass_file)
else:
    parser.print_help()
