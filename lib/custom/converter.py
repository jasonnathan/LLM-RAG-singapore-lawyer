import logging
from typing import Optional, Union, Any, Dict, Callable
from bs4 import BeautifulSoup, SoupStrainer, NavigableString, Tag
from .md_formatter import *

from ..logger import logger


default_bs_parser = 'lxml'  # parser for bs4


def md_converter_sg_acts(html: str) -> str:
    '''
    convert html from sg act into mark down text
    # act_header
    ## part a: part header
    #### provision c (aka. section): provision number and header
    ## schedule: schedule header
    args:
        html (str): html in unicode string
    returns:
        text (str): formatted text in unicode string
    '''

    def format_prov1Txt(tag: Tag) -> str:
        text = ""
        for c in tag.children:
            if type(c) == NavigableString:
                text += idt1(c) + br
            elif c.name in ('a', 'strong'):
                pass
            elif c.name not in ('span', 'table'):
                text += idt1(c.get_text(strip=True))
            else:
                if c.has_attr('class') and 'prov2TxtIL' in c['class']:
                    text += idt1(format_prov2TxtIL(c)) + br
                elif c.select('.prov2Txt'):
                    text += idt1(format_prov2Txt(c.select_one('.prov2Txt'))) + br
                elif c.select('.def'):
                    text += idt1(format_def(c.select_one('.def'))) + br
                else:
                    text += idt2(c.get_text(strip=True)) + br

        return text.rstrip()

    def format_prov2TxtIL(tag: Tag) -> str:
        text = ""
        for c in tag.children:
            if type(c) == NavigableString:
                text += idt1(c[1:]) + br
            elif c.select('.def'):
                text += idt1(format_def(c.select_one('.def'))) + br
            elif c.has_attr('class') and 'p1_1' in c['class']:
                text += idt1(format_p1_1(c)) + br
            else:
                text += idt2(c.get_text(strip=True)) + br
        return text.rstrip()

    def format_prov2Txt(tag: Tag) -> str:
        text = ""
        for c in tag.children:
            if type(c) == NavigableString:
                text += idt1(c) + br
            elif c.has_attr('class') and 'p1_1' in c['class']:
                text += idt1(format_p1_1(c)) + br
            else:
                text += idt2(c.get_text(strip=True)) + br
        return text.rstrip()

    def format_def(tag: Tag) -> str:
        text = ""
        for c in tag.children:
            if type(c) == NavigableString:
                text += idt1(c) + br
            elif c.has_attr('class') and 'p1_1' in c['class']:
                text += idt1(format_p1_1(c)) + br
            else:
                text += idt2(c.get_text(strip=True)) + br
        return text.rstrip()

    def format_p1_1(tag: Tag) -> str:
        # table .p1_1
        text = ""
        for r in tag.select('.p1_1 > tbody > tr'):
            if len(r.select('td')) == 1:
                hdr = r.select('td')[0].get_text(strip=True)
                text += idt1(hdr) + br
            elif len(r.select('td')) == 2:
                idx = r.select('td')[0].get_text(strip=True)
                val = r.select('td')[1].get_text(strip=True)
                text += idt1(idx + " " + val) + br
            else:
                idx = r.select('td')[0].get_text(strip=True)
                val = r.select('td')[1].get_text(strip=True)
                others = " ".join(
                    td.get_text(strip=True) for td in r.select('td')[2:]
                )
                text += idt1(idx + " " + val) + br
                text += idt2(others)

        return text.rstrip()

    html = html.replace("<em>", "").replace("</em>", "")
    bs = BeautifulSoup(html, default_bs_parser,
                       parse_only=SoupStrainer(id="legis"))
    text = ""
    try:
        # Act header
        act = dict(
            # <td class="actHd" id="aT-">Holidays Act 1998</td>
            title=bs.select_one('.actHd').get_text(),
            # <td class="longTitle" id="al-"> An Act relating to the observance of public holidays in Singapore.</td>
            long_title=bs.select_one('.longTitle').get_text(strip=True),
            # <td class="cDate">[10 April 1998]</td>
            create_on=bs.select_one('.cDate').get_text(strip=True),
        )
        text += hd1(act['title']) + br
        text += act['long_title'] + act['create_on'] + br2

        # each part
        if bs.select_one('#legis .part'):
            for pa in bs.select('#legis .part'):
                if not (pa.select('.partNo') and pa.select('.partHdr')):
                    continue

                part = dict(
                    number=pa.select_one('.partNo').get_text(strip=True),
                    title=pa.select_one('.partHdr').get_text(strip=True),
                )
                text += br + hd2(part['number'] + " " + part['title']) + br2

                for pr in pa.select('.prov1'):
                    if not (pr.select('.prov1Txt strong') and pr.select('.prov1Hdr') and pr.select('.prov1Txt')):
                        continue

                    prov = dict(
                        number=pr.select_one(
                            '.prov1Txt strong').get_text(strip=True),
                        title=pr.select_one(
                            '.prov1Hdr').get_text(strip=True),
                        content=format_prov1Txt(pr.select_one('.prov1Txt')),
                    )
                    text += hd3(prov['number'] + " " + prov['title']) + br
                    text += prov['content'] + br2
        else:
            # if no part structure, just loop each provision
            for pr in bs.select('#legis .prov1'):
                if not (pr.select('.prov1Txt strong') and pr.select('.prov1Hdr') and pr.select('.prov1Txt')):
                    continue

                prov = dict(
                    number=pr.select_one(
                        '.prov1Txt strong').get_text(strip=True),
                    title=pr.select_one('.prov1Hdr').get_text(strip=True),
                    content=format_prov1Txt(pr.select_one('.prov1Txt')),
                )
                text += hd3(prov['number'] + prov['title']) + br
                text += prov['content'] + br2

        # each schedule
        for s in bs.select('#legis .schedule'):
            # TBD
            pass
    except Exception as e:
        logger.error(str(e))

    return text
