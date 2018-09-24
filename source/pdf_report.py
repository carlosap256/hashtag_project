import os
import itertools
import re
import logging
from typing import List, Iterator

from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Flowable, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import PageBegin, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, StyleSheet1
from reportlab.platypus.doctemplate import LayoutError

from hashtag_core import Hashtag
from word_metadata import WordMetadata
from report_settings import ReportSettings
import util

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger(__name__)


class MetadataToPDF:
    report_settings: ReportSettings
    report_data: List[Flowable]

    def __init__(self, report_settings: ReportSettings):
        self.report_settings = report_settings
        self._init_doc_template()

    def _init_doc_template(self):
        report_file_path = os.path.join(BASE_DIR, 'output', self.report_settings.report_file_path)
        self.doc = SimpleDocTemplate(report_file_path, pagesize=A4,
                                     rightMargin=72, leftMargin=72,
                                     topMargin=72, bottomMargin=18)
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        self.styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
        self.styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT))
        self.styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
        logger.info("Report lab initialized to export file: " + report_file_path)

    def generate_report(self, hashtags: Hashtag) -> None:
        self._init_report_data()
        self._include_header()
        self._include_settings_description()
        self._include_table(hashtags)
        self._build_report()

    def _init_report_data(self) -> None:
        self.report_data = list()
        self.report_data.append(PageBegin())

    def _include_header(self) -> None:
        ptext = '<font size=18>Hashtag Report</font>'
        self.report_data.append(Paragraph(ptext, self.styles["Center"]))
        self.report_data.append(Spacer(1, 24))

    def _include_settings_description(self) -> None:
        ptext = '<font size=12>Showing the top {0} words, with minimum length of {1} characters, ' \
                'and {2} of the references per document.</font>'.format(self.report_settings.max_results,
                                                                        self.report_settings.min_word_length,
                                                                        self.report_settings.max_references_per_document)
        self.report_data.append(Paragraph(ptext, self.styles["Left"]))
        self.report_data.append(Spacer(1, 24))

    def _include_table(self, hashtags: Hashtag):
        table_data = self._create_table_data(hashtags)
        table = self._generate_table_field(table_data)
        self.report_data.append(table)

    def _create_table_data(self, hashtag: Hashtag):
        table_data = list()
        table_data = self._append_table_header(table_data)
        logger.debug("Generating rows")

        for result in util._loop_first_n_results(hashtag, self.report_settings.max_results):
            word = result[1]
            wordmetadata = result[2]
            table_data.append(self._generate_row(word, wordmetadata))

        return table_data

    def _append_table_header(self, table_data):
        table_data.append(['Word(#)', 'Documents', 'Sentences containing the word'])
        return table_data

    def _generate_row(self, word: str, metadata: WordMetadata):
        style_sheet = getSampleStyleSheet()
        documents_column = self._generate_documents_column(metadata.documents, style_sheet["BodyText"])
        highlighted_sentences = [hs for hs in self._generate_references_column(metadata, style_sheet["BodyText"])]

        logger.debug("Generated row for: '" + word + "'")
        return [word.capitalize(), documents_column, highlighted_sentences]

    def _generate_documents_column(self, documents, style: StyleSheet1) -> List[Flowable]:
        return [Paragraph(file_name, style) for file_name in documents]

    def _generate_references_column(self, metadata: WordMetadata, style: StyleSheet1) -> Iterator[Flowable]:
        for sentences_per_document in metadata.get_references():
            for sentence in itertools.islice(sentences_per_document, self.report_settings.max_references_per_document):
                bolded_text = re.sub('(' + metadata.word + ')', r'<b>\g<1></b>', sentence, flags=re.IGNORECASE)
                yield Paragraph(bolded_text, style)

    def _generate_table_field(self, table_data: List[Flowable]) -> Table:
        table = Table(table_data, colWidths=[3 * cm, 2.1 * cm, 11 * cm], repeatRows=1)
        table.setStyle(TableStyle([('ALIGN', (1, 1), (-2, -2), 'RIGHT'),
                                   ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                   ('TEXTCOLOR', (1, 0), (0, -1), colors.blue),
                                   ('TEXTCOLOR', (0, 0), (0, 3), colors.black),
                                   ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                   ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                   ]))
        return table

    def _build_report(self):
        try:
            self.doc.build(self.report_data)
        except LayoutError:
            logger.error("Cannot create table.  Try reducing the 'max_ref_per_document' argument")
        else:
            logger.debug("Report saved to file")
