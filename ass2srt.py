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


def replace_ass_n_by_system_n(str_temp):
    return str_temp.replace(r'\N', '\n')


def replace_italic_tags(str_temp):
    return str_temp.replace(r'{\i1}', '<i>').replace(r'{\i0}', '</i>')


def replace_bold_tags(str_temp):
    return str_temp.replace(r'{\b1}', '<b>').replace(r'{\b0}', '</b>')


def remove_b100_to_b900_explicit_bold_weight(str_temp):
    return re.sub(r'{\\b[1-9]00}', '', str_temp)


def replace_underline_tags(str_temp):
    return str_temp.replace(r'{\u1}', '<u>').replace(r'{\u0}', '</u>')


def remove_strikeout_tags(str_temp):
    return re.sub(r'\{\\s[0-1]\}', '', str_temp)


def remove_border_tags_and_extended(str_temp):
    return re.sub(r'\{\\[x-y]?bord[0-9]*\.?[0-9]*\}', '', str_temp)


def remove_shadow_distance_and_extended(str_temp):
    return re.sub(r'\{\\[x-y]?shad[0-9]*\.?[0-9]*\}', '', str_temp)


def remove_blur_edge_gaussian_kernel(str_temp):
    return re.sub(r'\{\\blur[0-9]*\.?[0-9]*\}', '', str_temp)


def remove_font_name(str_temp):
    regex_fonts_name = "|".join(fonts_name_list)
    return re.sub(r'{\\fn(' + regex_fonts_name + ')}', '', str_temp)


def remove_font_size(str_temp):
    return re.sub(r'\{\\fs[1-9]*\}', '', str_temp)


def remove_font_scale(str_temp):
    return re.sub(r'\{\\fsc[x-y]?[0-9]*\}', '', str_temp)


def remove_letter_spacing(str_temp):
    return re.sub(r'\{\\fsp\-?[0-9]*\.?[0-9]*\}', '', str_temp)


def remove_text_rotation(str_temp):
    return re.sub(r'\{\\fr[x-z]?[0-9]*\}', '', str_temp)


def remove_text_shearing(str_temp):
    return re.sub(r'\{\\fa[x-y]+[0-9]*\.?[0-9]*\}', '', str_temp)


def remove_font_encoding(str_temp):
    return re.sub(r'\{\\fe[0-9]*\}', '', str_temp)


def remove_text_color(str_temp):
    return re.sub(r'\{\\[1-4]?c\&H[0-9a-fA-F]*&\}', '', str_temp)


def remove_transparency_text_alpha(str_temp):
    return re.sub(r'\{\\[1-4]?a(?:lpha)?\&H[0-9a-fA-F]*\}', '', str_temp)


def remove_line_alignment(str_temp):
    return re.sub(r'\{\\a[n]?[0-9]+\}', '', str_temp)


def remove_karaoke_effect(str_temp):
    return re.sub(r'\{\\[k,K][f,o]?[0-9]*\}', '', str_temp)


def remove_wrap_style(str_temp):
    return re.sub(r'\{\\q[0-3]*\}', '', str_temp)


def remove_reset_style(str_temp):
    regex_style_names = "|".join(style_list)
    return re.sub(r'{\\r(' + regex_style_names + ')?}', '', str_temp)


def remove_text_position(str_temp):
    return re.sub(r'\{\\pos\([0-9]*\,[0-9]*\)\}', '', str_temp)


def remove_movement(str_temp):
    return re.sub(r'\{\\move\([0-9]*\,[0-9]*\,[0-9]*\,[0-9]*\,?[0-9]*\,?[0-9]*\)\}', '', str_temp)


def remove_rotation(str_temp):
    return re.sub(r'\{\\org\([0-9]*\,[0-9]*\)\}', '', str_temp)


def remove_fade(str_temp):
    return re.sub(r'\{\\fad\([0-9]*\,[0-9]*\,?[0-9]*\,?[0-9]*\,?[0-9]*\,?[0-9]*\,?[0-9]*\)\}', '', str_temp)


def remove_animated_transform(str_temp):
    return re.sub(r'\\t\(\\?[0-9a-zA-Z&]*\.?[0-9]*\,?\\?[0-9a-zA-Z&]*\.?[0-9]*\,?\\?[0-9a-zA-Z&]*\.?[0-9]*\,?\\?[0-9a-zA-Z&]*\.?[0-9]*\)\}', '', str_temp)


def remove_clip_rectangle(str_temp):
    return re.sub(r'\{\\[i]?clip\([0-9]*\,[0-9]*\,[0-9]*\,[0-9]*\\)\}', '', str_temp)


def remove_ass_tags(str_input):
    # Remove current \n
    str_temp = str_input.replace('\n', '')
    str_temp = replace_ass_n_by_system_n(str_temp)

    # Source of all ASS Tags: http://docs.aegisub.org/3.2/ASS_Tags/
    str_temp = replace_italic_tags(str_temp)
    str_temp = replace_bold_tags(str_temp)
    str_temp = remove_b100_to_b900_explicit_bold_weight(str_temp)
    str_temp = replace_underline_tags(str_temp)
    str_temp = remove_strikeout_tags(str_temp)
    str_temp = remove_border_tags_and_extended(str_temp)
    str_temp = remove_shadow_distance_and_extended(str_temp)
    str_temp = remove_blur_edge_gaussian_kernel(str_temp)
    str_temp = remove_font_name(str_temp)
    str_temp = remove_font_size(str_temp)
    str_temp = remove_font_scale(str_temp)
    str_temp = remove_letter_spacing(str_temp)
    str_temp = remove_text_rotation(str_temp)
    str_temp = remove_text_shearing(str_temp)
    str_temp = remove_font_encoding(str_temp)
    str_temp = remove_text_color(str_temp)
    str_temp = remove_transparency_text_alpha(str_temp)
    str_temp = remove_line_alignment(str_temp)
    str_temp = remove_karaoke_effect(str_temp)
    str_temp = remove_wrap_style(str_temp)
    str_temp = remove_reset_style(str_temp)
    str_temp = remove_text_position(str_temp)
    str_temp = remove_movement(str_temp)
    str_temp = remove_rotation(str_temp)
    str_temp = remove_fade(str_temp)
    str_temp = remove_animated_transform(str_temp)
    str_temp = remove_clip_rectangle(str_temp)

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
