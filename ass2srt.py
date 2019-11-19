# coding=utf-8
import argparse

parser = argparse.ArgumentParser(
    prog='ass2srt',
    description='Convert Sub Station Alpha v4.00+ subtitle format (.ass) into SubRip subtitle format (.srt)',
    epilog='GitHub Page: https://github.com/locobastos/ass2srt-python'
)

parser.add_argument('-i', '--input', metavar="input.ass", type=str, help='the path to the input file.')
parser.add_argument('-c', '--charenc', metavar="utf-8", type=str, help='the input file\'s characters encoding.')
args = parser.parse_args()

input_ass_file = args[0]
input_charenc = args[1]
temp_ass = input_ass_file + ".tmp"

with open(input_ass_file, 'r', encoding='utf-8') as infile, open(temp_ass, 'w', encoding='utf-8') as tmpfile:
    event_line = False
    dialogue_number = 1
    for line in infile:
        if not event_line:
            """
            Removes the [Script Info] and [V4+ Styles] headers
            """
            if line.startswith("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"):
                event_line = True
        else:
            if line not in ['\n', '\r\n'] or len(line.strip()) != 0:
                tmpfile.write(str(dialogue_number) + '\n')
                tmp_line = line.split(",", 9)
                tmpfile.write(tmp_line[1].replace(".", ",") + " --> " + tmp_line[2].replace(".", ",") + '\n')
                tmpfile.write(tmp_line[9].replace('\n', '').replace("\\N", '\n') + '\n\n')
                dialogue_number += 1
    tmpfile.close()
    infile.close()
