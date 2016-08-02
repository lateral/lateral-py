import re
from collections import namedtuple
from bs4 import BeautifulSoup

Piece = namedtuple('Piece', "content head tail sid pos")

def cut_pieces_html(soup, length, overlap, context):
    return cut_pieces_txt(soup.text, length, overlap, context)

def cut_pieces_txt(text, length, overlap, context=0):
    """
    cut `text` into chunks of length `length`/`overlap` and recombine them
    to pieces of length `length`, letting inner parts of
    `text` be overlapped by `overlap` pieces. Keep `context` chunks as head
    and tail of piece.
    """
    ch_len = int(round(length/overlap))
    text_chunks = [text[i:i + ch_len] for i in xrange(0, len(text), ch_len)]
    n_chunks = len(text_chunks)

    for i_ch in range(n_chunks + 1 - overlap):
        content = ''.join(text_chunks[i_ch:min(i_ch + overlap, n_chunks)])
        head = ''.join(text_chunks[max(i_ch - context, 0):i_ch])
        tail = ''.join(text_chunks[i_ch:min(i_ch + overlap + context, n_chunks)])
        yield Piece(content, head, tail, sid=i_ch, pos=i_ch * ch_len)

def idlize(txt):
    pre_txt = txt.lower().strip().replace(" ", "_").replace(".", "-")
    return re.sub("[^a-z0-9-_]", "", pre_txt, flags=re.MULTILINE)


# proper html tree slicing
# def break_head(soup, length, overlap):
#     break_tail(soup.)
#     acclen = 0
#     for child in soup.recursiveChildGenerator():
#         name = getattr(child, "name", None)
#         if name is None:
#             acclen += len(child.string)
#         if acclen > length:
#             child.replace_with(child.string[length-acclen:])
#         else:
#             child.replace_with("")
#
#     text_piece = u""
#     acclen = 0
#     piece_idx = 0
#     for child in soup.recursiveChildGenerator():
#         name = getattr(child, "name", None)
#         if name is None:
#             acclen += len(child.string)
#             text_piece += child.string
#             if acclen > length:
#                 yield text_piece[:length-acclen]
#                 acclen = round(length/overlap)
#                 text_piece = text_piece[acclen:]
#                 tag = soup.new_tag("segment", pos=piece_idx)
#                 child.insert_after(tag)
#                 piece_idx += 1
#     yield text_piece
