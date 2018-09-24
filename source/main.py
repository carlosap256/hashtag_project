import logging
import configparser
import os
from os import listdir
from os.path import isfile, join

from pdf_report import MetadataToPDF
from report_settings import ReportSettings

from hashtag_core import Hashtag

FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
          '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MainApp:
    hashtag: Hashtag
    pdf_report: MetadataToPDF

    def __init__(self):
        report_settings = self._init_config_file()
        self.hashtag = Hashtag(report_settings.min_word_length)
        self.pdf_report = MetadataToPDF(report_settings)

    def _init_config_file(self)->ReportSettings:
        logger.info("Reading config file 'config.ini'")
        return ReportSettings('config.ini')

    def execute(self):
        self.hashtag.reset_hashtags()
        self._process_doc_files()
        sorted_hashtags = self.hashtag.get_sorted_hashtags()
        logger.info("Generating report")
        self.pdf_report.generate_report(sorted_hashtags)
        logger.info("Done")

    def _process_doc_files(self):
        file_list = self._get_doc_file_paths()
        for file_path in file_list:
            logger.info("Extracting hashtag from file: " + str(file_path))
            self.hashtag.append_to_hashtags(file_path)

    def _get_doc_file_paths(self):
        resources_dir = os.path.join(BASE_DIR, 'resources')
        text_files = [f for f in listdir(resources_dir) if isfile(join(resources_dir, f)) and f.endswith('.txt')]
        return map(lambda f: join(resources_dir, f), text_files)


if __name__ == "__main__":

    main = MainApp()
    main.execute()

