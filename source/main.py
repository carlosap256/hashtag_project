import hashtag_core
from pdf_report import MetadataToPDF
import logging

FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
               '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    file_list = ['doc' + str(filenumber) + '.txt' for filenumber in range(1, 7)]

    logger.info("Extracting hashtag from files: " + str(file_list))
    hashtag_results = hashtag_core.get_hashtags_from_files(file_list)
    sorted_by_counter = hashtag_core.sort_metadata(hashtag_results)

    logger.info("Found " + str(len(sorted_by_counter)) + " hashtags")

    top_words = 20
    references_per_document = 1
    logger.info("Initializing ReportLab to show top " + str(top_words) +
                " and " + str(references_per_document) + " reference per document")
    report_file = 'test.pdf'
    logger.info("Output to file: "+report_file)
    metadata_report = MetadataToPDF(report_file, top_words, references_per_document)

    logger.info("Generating report")
    metadata_report.generate_report(sorted_by_counter)
    logger.info("Done")
