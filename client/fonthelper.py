from itertools import chain
import pygame


def truncline(text, font, maxwidth):
    real = len(text)
    stext = text
    l = font.size(text)[0]
    cut = 0
    a = 0
    done = 1
    while l > maxwidth:
        a = a + 1
        n = text.rsplit(None, a)[0]
        if stext == n:
            cut += 1
            stext = n[:-cut]
        else:
            stext = n
        l = font.size(stext)[0]
        real = len(stext)
        done = 0
    return real, done, stext


def wrapline(text, font, maxwidth):
    done = 0
    wrapped = []

    while not done:
        nl, done, stext = truncline(text, font, maxwidth)
        wrapped.append(stext.strip())
        text = text[nl:]
    return wrapped


def wrap_multi_line(text, font, maxwidth):
    """ returns text taking new lines into account.
    """
    lines = chain(*(wrapline(line, font, maxwidth)
                    for line in text.splitlines()))
    return list(lines)


def render_text(text, font, color, maxwidth):
    lines = wrap_multi_line(text, font, maxwidth)
    height = max(font.size(line)[1] for line in lines) * 1.05
    surface = pygame.Surface((maxwidth, height * len(lines)), pygame.SRCALPHA)
    for idx, line in enumerate(lines):
        text = font.render(line, True, color)
        text_pos = text.get_rect(top=idx * height)
        surface.blit(text, text_pos)
    return surface
