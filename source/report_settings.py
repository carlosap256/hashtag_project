import logging

from configparser import ConfigParser

logger = logging.getLogger(__name__)


class ReportSettings:
    report_file_path: str = "test.pdf"
    max_results: int = 20
    max_references_per_document: int = 1
    min_word_length: int = 6
    config_parser: ConfigParser

    def __init__(self, config_file: str):
        self.config_parser = ConfigParser()
        self._read_config_file(config_file)

    def _read_config_file(self, config_file: str):
        try:
            self.config_parser.read(config_file)
        except FileNotFoundError as e:
            logger.error("File '"+config_file+"' not found. "+str(e))

    def _read_section(self, section_name):
        if section_name in self.config_parser:

            self.max_results = self.config_parser.getint(section_name, 'top_words', fallback=self.max_results)
            self.max_references_per_document = self.config_parser.getint(section_name, 'max_references_per_document',
                                                                         fallback=self.max_references_per_document)
            self.min_word_length = self.config_parser.getint(section_name, 'min_word_length',
                                                             fallback=self.min_word_length)
        else:
            logger.warning("No '" + section_name + "' section in the config.ini file.  Using hardcoded defaults")
