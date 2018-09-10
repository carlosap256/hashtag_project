import hashtag_core
from pdf_report import MetadataToPDF
import logging
import configparser

FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
          '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    file_list = ['doc' + str(filenumber) + '.txt' for filenumber in range(1, 7)]

    logger.info("Extracting hashtag from files: " + str(file_list))
    hashtag_results = hashtag_core.get_hashtags_from_files(file_list, min_word_length)
    sorted_by_counter = hashtag_core.sort_metadata(hashtag_results)

    logger.info("Found " + str(len(sorted_by_counter)) + " hashtags")

    logger.info("Initializing ReportLab to show top " + str(top_words) +
                " and " + str(references_per_document) + " references per document")
    report_file = 'test.pdf'
    logger.info("Output to file: " + report_file)
    metadata_report = MetadataToPDF(report_file, top_words, references_per_document)

    logger.info("Generating report")
    metadata_report.generate_report(sorted_by_counter)
    logger.info("Done")
