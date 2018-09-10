from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, PageBegin, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import StringIO
import base64
import os
import itertools
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MetadataToPDF:

    def __init__(self, report_filename, max_results=20, max_ref_per_document=1):
        report_filepath = os.path.join(BASE_DIR, 'output', report_filename)
        self.doc = SimpleDocTemplate(report_filepath, pagesize=A4,
                                     rightMargin=72, leftMargin=72,
                                     topMargin=72, bottomMargin=18)
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        self.styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
        self.styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT))
        self.styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))

        self.max_results = max_results
        self.max_ref_per_document = max_ref_per_document

    def generate_report(self, hashtag_list):
        story = []
        story.append(PageBegin())

        ptext = '<font size=18>Hashtag Report</font>'

        story.append(Paragraph(ptext, self.styles["Center"]))
        story.append(Spacer(1, 24))

        table_data = []
        table_data.append(['Word(#)', 'Documents', 'Sentences containing the word'])

        for word_metadata in itertools.islice(hashtag_list, self.max_results):
            table_data.append(self.generate_word_row(word_metadata[1], word_metadata[2]))

        table = Table(table_data, colWidths=[3 * cm, 2.1 * cm, 11 * cm], repeatRows=1)
        table.setStyle(TableStyle([('ALIGN', (1, 1), (-2, -2), 'RIGHT'),
                                   ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                   ('TEXTCOLOR', (1, 0), (0, -1), colors.blue),
                                   ('TEXTCOLOR', (0, 0), (0, 3), colors.black),
                                   ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                   ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                   ]))

        story.append(table)
        self.doc.build(story)

    def generate_word_row(self, word: str, metadata):
        styleSheet = getSampleStyleSheet()

        documents = [Paragraph(file, styleSheet["BodyText"]) for file in metadata['references'].keys()]

        highlighted_sentences = []
        for sentences_per_document in metadata['references'].values():
            for sentence in itertools.islice(sentences_per_document, self.max_ref_per_document):
                bolded_text = re.sub('(' + word + ')', r'<b>\g<1></b>', sentence, flags=re.IGNORECASE)
                highlighted_sentences.append(Paragraph(bolded_text, styleSheet["BodyText"]))

        return [word.capitalize(), documents, highlighted_sentences]


if __name__ == "__main__":
    file_list = ['doc' + str(filenumber) + '.txt' for filenumber in range(1, 7)]

    import hashtag_core

    result = hashtag_core.get_hashtags_from_files(file_list)
    sorted_by_counter = hashtag_core.sort_metadata(result)

    m = MetadataToPDF('test.pdf')

    m.generate_report(sorted_by_counter)
