"""This module defines the function used to display long strings of text."""
import pygame, os, sys
from pygame.locals import *

def text(paragraphs, top_position, screen, background, colors=[(255,255,255)], serial=[0]):
    """This function takes a list of paragraphs and displays them to the \n
    screen, inserting hard returns when necessary."""

    # sets serial tuples if not given
    if serial[0] == 0:
        serial = [0]
        zeros = []
        for i in range(len(paragraphs)):
            zeros.append(0)
        serial.append(zeros)

    if colors == [(255,255,255)]:
        colors = [(255,255,255)]*len(paragraphs)

    lines = []
    lines_colors = []
    lines_serial = [] # serial refers to how long that lines should be present
    for p in range(len(paragraphs)):
        new_p = paragraphs[p]
        lines_colors.append(colors[p])
        lines_serial.append(serial[1][p])
        while len(new_p) > 0:
            if len(new_p) < 76:
                lines.append(new_p)
                new_p = new_p.strip(new_p)
                lines_colors.append(colors[p])
                lines_serial.append(serial[1][p])
            elif new_p[76] == " ":
                lines.append(new_p[0:76])
                new_p = new_p[(76+1):]
                lines_colors.append(colors[p])
                lines_serial.append(serial[1][p])
            else:
                found_space = 0; string_counter = 1
                while found_space == 0:
                    if new_p[76-string_counter] == " ":
                        lines.append(new_p[0:(76-string_counter)])
                        new_p = new_p[(76-string_counter+1):]
                        lines_colors.append(colors[p])
                        lines_serial.append(serial[1][p])
                        found_space = 1
                    else:
                        string_counter += 1
        lines.append("")

    positions = [(top_position)]
    for l in range(len(lines)):
        positions.append((top_position[0],top_position[1]+27*(l+1)))

    rendered_ps = []
    font = pygame.font.Font(None, 24)
    for l in range(len(lines)):
        rendered_ps.append(font.render(lines[l], 1, lines_colors[l]))

    try:
        rects = {}
        for i in range(len(rendered_ps)):
            rects['rect' + str(i+1)] = rendered_ps[i].get_rect()
            rects['rect' + str(i+1)].topleft = positions[i]

        screen.blit(background, (0, 0))

        for i in range(len(rendered_ps)):
            screen.blit(rendered_ps[i], rects['rect' + str(i+1)])

            # serial[0] > 0 makes features come up one at a time
            if (serial[0] > 0 and lines_serial[i] > 0):
                pygame.display.flip()
                pygame.time.delay(lines_serial[i])
        if (serial[0] == 0 or lines_serial[i] == 0):
            pygame.display.flip()

    except:
        TypeError
        rect = rendered_ps.get_rect()
        rect.topleft = positions
        screen.blit(background, (0, 0))
        screen.blit(rendered_ps, rect)
        pygame.display.flip()
