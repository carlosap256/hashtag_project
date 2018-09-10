from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import PageBegin, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.doctemplate import LayoutError
import os
import itertools
import re
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger(__name__)


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
        logger.info("Report lab initialized to export file: "+str(report_filepath))

    def generate_report(self, hashtag_list):
        """
        Generates base PDF file
        :param hashtag_list:
        :return:
        """
        story = []
        story.append(PageBegin())

        ptext = '<font size=18>Hashtag Report</font>'

        story.append(Paragraph(ptext, self.styles["Center"]))
        story.append(Spacer(1, 24))

        ptext = '<font size=12>Showing the {0} top words, ' \
                'and {1} of the references per document</font>'.format(self.max_results, self.max_ref_per_document)
        story.append(Paragraph(ptext, self.styles["Left"]))
        story.append(Spacer(1, 24))

        table_data = []
        table_data.append(['Word(#)', 'Documents', 'Sentences containing the word'])

        logger.debug("Generating rows")
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
        try:
            self.doc.build(story)
        except LayoutError:
            logger.error("Cannot create table.  Try reducing the 'max_ref_per_document' argument")
        else:
            logger.debug("Report saved to file")

    def generate_word_row(self, word: str, metadata):
        """
        Generates a row containing the Word (hashtag), the list of documents that references it, and some sentences
        per document according
        :param word:
        :param metadata:
        :return:
        """
        styleSheet = getSampleStyleSheet()

        documents = [Paragraph(file, styleSheet["BodyText"]) for file in metadata['references'].keys()]

        highlighted_sentences = []
        for sentences_per_document in metadata['references'].values():
            for sentence in itertools.islice(sentences_per_document, self.max_ref_per_document):
                bolded_text = re.sub('(' + word + ')', r'<b>\g<1></b>', sentence, flags=re.IGNORECASE)
                highlighted_sentences.append(Paragraph(bolded_text, styleSheet["BodyText"]))

        logger.debug("Generated row for: '"+word+"'")
        return [word.capitalize(), documents, highlighted_sentences]


