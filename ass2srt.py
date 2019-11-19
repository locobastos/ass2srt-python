# coding=utf-8
import argparse

# _____ ARGUMENTS PARSER _______________________________________________________________________________________________


parser = argparse.ArgumentParser(
    prog='ass2srt',
    description='Convert Sub Station Alpha v4.00+ subtitle format (.ass) into SubRip subtitle format (.srt)',
    epilog='GitHub Page: https://github.com/locobastos/ass2srt-python'
)

parser.add_argument('-i', '--input',
                    metavar="input.ass",
                    type=str,
                    action='append',
                    nargs='+',
                    help='the path to the input file.')
parser.add_argument('-c', '--charenc',
                    metavar="utf-8",
                    type=str,
                    help='the input file\'s characters encoding.')
args = parser.parse_args()


# _____ FUNCTiONS ______________________________________________________________________________________________________


def convert_ass_to_srt(in_file, out_file):
    with open(in_file, 'r', encoding='utf-8') as infile, open(out_file, 'w', encoding='utf-8') as outfile:
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

for ass_file in range(len(args.input)):
    output_srt_file = args.input[ass_file][0][:-4] + ".srt"
    convert_ass_to_srt(args.input[ass_file][0], output_srt_file)
