#!/usr/bin/env python3
"""Create an empty DOCX using the approved reference's formatting, never its facts."""
import argparse
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.shared import Pt, RGBColor


def enforce_visuals(doc):
    # Explicit fonts and colors keep body text black and links blue.
    for name in ('Hyperlink', 'FollowedHyperlink'):
        if name not in doc.styles:
            doc.styles.add_style(name, WD_STYLE_TYPE.CHARACTER)
    for style in doc.styles:
        if not hasattr(style, 'font'):
            continue
        style.font.name = 'Arial'
        is_link = style.name in ('Hyperlink', 'FollowedHyperlink')
        style.font.color.rgb = RGBColor.from_string('0563C1') if is_link else RGBColor(0, 0, 0)
        if is_link:
            style.font.underline = True
        rp = style.element.get_or_add_rPr()
        fonts = rp.find(qn('w:rFonts'))
        if fonts is None:
            fonts = OxmlElement('w:rFonts')
            rp.insert(0, fonts)
        for key in list(fonts.attrib):
            if key.endswith('Theme'):
                del fonts.attrib[key]
        for key in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
            fonts.set(qn('w:' + key), 'Arial')
        for c in rp.findall(qn('w:color')):
            for key in ('themeColor', 'themeTint', 'themeShade'):
                c.attrib.pop(qn('w:' + key), None)
        for b in list(style.element.iter(qn('w:pBdr'))):
            b.getparent().remove(b)
    for part in doc.part.package.parts:
        if part.content_type.endswith('theme+xml'):
            from lxml import etree
            tree = etree.fromstring(part.blob)
            ns = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
            for kind in ('majorFont', 'minorFont'):
                for el in tree.findall('.//a:' + kind + '/a:latin', ns):
                    el.set('typeface', 'Arial')
                for el in tree.findall('.//a:' + kind + '/a:font', ns):
                    if el.get('script') in ('Cyrl', 'Grek'):
                        el.set('typeface', 'Arial')
            part._blob = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)


def create_document(reference, title=''):
    source = Document(reference)
    result = Document()  # Fresh relationships: old source links cannot leak.
    result.part._styles_part._element = deepcopy(source.styles.element)
    result.part.numbering_part._element = deepcopy(source.part.numbering_part.element)
    for attr in ('page_width', 'page_height', 'top_margin', 'bottom_margin',
                 'left_margin', 'right_margin', 'header_distance', 'footer_distance'):
        setattr(result.sections[0], attr, getattr(source.sections[0], attr))
    enforce_visuals(result)
    result.core_properties.title = title
    result.core_properties.subject = ''
    result.core_properties.author = ''
    result.core_properties.last_modified_by = ''
    result.core_properties.comments = ''
    result.core_properties.keywords = ''
    footer = result.sections[0].footer.paragraphs[0]
    footer.alignment = 2
    run = footer.add_run()
    run.font.name = 'Arial'
    run.font.size = Pt(9)
    field = OxmlElement('w:fldSimple')
    field.set(qn('w:instr'), 'PAGE')
    run._r.addnext(field)
    if title:
        result.add_paragraph(title, 'Title')
    return result


def self_test(reference):
    doc = create_document(reference, 'Проверка формата')
    source = Document(reference)
    assert len(doc.paragraphs) == 1 and not doc.tables and not doc.inline_shapes
    assert all(not rel.is_external for rel in doc.part.rels.values())
    for name in ('Normal', 'Title', 'Heading 1', 'Heading 2', 'Heading 3'):
        assert doc.styles[name].font.name == 'Arial'
        assert doc.styles[name].font.size == source.styles[name].font.size
        assert doc.styles[name].font.color.rgb == RGBColor(0, 0, 0)
    stream = BytesIO()
    doc.save(stream)
    stream.seek(0)
    readback = Document(stream)
    assert readback.paragraphs[0].text == 'Проверка формата'
    assert len(readback.tables) == 0
    assert 'отход' not in readback.part.element.xml.lower()
    for name in ('Hyperlink', 'FollowedHyperlink'):
        assert readback.styles[name].font.color.rgb == RGBColor.from_string('0563C1')
        assert readback.styles[name].font.underline is True
        assert 'themeColor' not in readback.styles[name].element.xml
    print('OK: reference formatting retained; no source content, images or external links copied.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', nargs='?')
    parser.add_argument('--title', default='')
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--reference', type=Path, default=Path(__file__).resolve().parents[1] / 'assets/reference.docx')
    args = parser.parse_args()
    if args.self_test:
        self_test(args.reference)
    else:
        if not args.output:
            parser.error('Specify output.docx or --self-test')
        path = Path(args.output)
        if path.exists():
            parser.error('Output exists; choose a new path instead of overwriting it')
        path.parent.mkdir(parents=True, exist_ok=True)
        create_document(args.reference, args.title).save(path)
        print(path)
