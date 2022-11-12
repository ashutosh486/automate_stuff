import requests
import pandas as pd
import os
import json
from datetime import datetime, timezone
import random
import time
from PIL import Image, ImageFont, ImageDraw
import textwrap


def text_formatting(text, width, style):
    if len(text) <= width:
        return [text]
    lines = textwrap.wrap(text, width)

    if style == 'j':
        lines = [line.split(' ') for line in lines]
        strings = []
        for line in lines[:-1]:
            blanks = len(line) -1
            add_blanks = width - (sum(map(len, line)) + len(line) -1)
            for i in range(add_blanks):
                if i < blanks:
                    line[i] += ' '
                else:
                    line[i%blanks] += ' '
            strings += [' '.join(line)]
        strings += [' '.join(lines[-1])]
        return strings

def create_post(template_image_path, output_image_path, font_path, setup_line, punchline, author_credit, 
                font_size = 4.5, x1_offset = 130, x2_offset=90, vertical_space=20):
    
    im = Image.open(template_image_path)
    draw = ImageDraw.Draw(im)
    image_width, image_height = im.size

    font_size = 4.5
    print("font_size", int(image_height * font_size) // 100)
    story_font = ImageFont.truetype(font=font_path, size=int(image_height * font_size) // 100)

    ## text wrapping
    width_offset = x1_offset + x2_offset
    char_width, char_height = story_font.getsize('p')
    chars_per_line = (image_width-width_offset) // char_width
    setup_lines = text_formatting(setup_line, chars_per_line, 'j')
    punchlines = text_formatting(punchline, chars_per_line, 'j')

    #Setup Text displayed on template image
    n_lines = len(setup_lines) +len(punchlines)
    y = (image_height - (char_height+vertical_space)*(n_lines+1))//2
    for line in setup_lines:
        line_width, line_height = story_font.getsize(line)
        line_height = line_height+vertical_space
        x = x1_offset
        draw.text((x, y), line, fill='white', font=story_font, stroke_width=0, stroke_fill='white')
        y += line_height

    ## Punchline text displayed on template image
    y+=line_height
    for line in punchlines:
        line_width, line_height = story_font.getsize(line)
        line_height = line_height+vertical_space
        x = x1_offset
        draw.text((x, y), line, fill='white', font=story_font, stroke_width=0, stroke_fill='white')
        y += line_height

    ## Credit
    credit_font = ImageFont.truetype(font=font_path, size=60)
    credit_char_width, credit_char_height = credit_font.getsize('A')
    n_lines_left = (image_height - y)//credit_char_height

    if n_lines_left-5>0:
        y_offset = y+(n_lines_left-5)*credit_char_height
        draw.text((x1_offset, y_offset), author_credit.rjust(58, ' '), fill='white', font=credit_font, stroke_width=0, stroke_fill='white')

    ## Resize the image
    # im = im.resize((1080, 1080))
    im.save(output_image_path)