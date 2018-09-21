import logging
import configparser
import os
from os import listdir
from os.path import isfile, join

from pdf_report import MetadataToPDF, ReportSettings

from hashtag_core import Hashtag

FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
          '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_doc_file_paths():
    resources_dir = os.path.join(BASE_DIR, 'resources')
    text_files = [f for f in listdir(resources_dir) if isfile(join(resources_dir, f)) and f.endswith('.txt')]
    return map(lambda f: join(resources_dir, f), text_files)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    logger.info("Reading config file 'config.ini'")
    config.read('config.ini')

    top_words = 20
    references_per_document = 1
    min_word_length = 6

    if 'reportlab' in config:

        top_words = config.getint('reportlab', 'top_words', fallback=top_words)
        references_per_document = config.getint('reportlab', 'references_per_document',
                                                fallback=references_per_document)
    else:
        logger.warning("No 'reportlab' section in the config.ini file.  Using defaults")

    if 'hashtag_core' in config:

        min_word_length = config.getint('hashtag_core', 'min_word_length', fallback=min_word_length)

    else:
        logger.warning("No 'hashtag_core' section in the config.ini file.  Using defaults")

    """Generating sample filelist"""
    file_list = get_doc_file_paths()

    logger.info("Extracting hashtag from files: " + str(file_list))
    hashtag = Hashtag(min_word_length)

    for file_path in file_list:
        hashtag.append_to_hashtags(file_path)

    sorted_by_counter = hashtag.get_sorted_hashtags()

    logger.info("Found " + str(len(sorted_by_counter)) + " hashtags")

    logger.info("Initializing ReportLab to show top " + str(top_words) +
                " and " + str(references_per_document) + " references per document")
    report_file = 'test.pdf'
    logger.info("Output to file: " + report_file)

    report_settings = ReportSettings()
    report_settings.report_file_path = report_file
    report_settings.max_results = top_words
    report_settings.max_references_per_document = references_per_document
    report_settings.min_word_length = min_word_length
    metadata_report = MetadataToPDF(report_settings)

    logger.info("Generating report")
    metadata_report.generate_report(sorted_by_counter)
    logger.info("Done")
