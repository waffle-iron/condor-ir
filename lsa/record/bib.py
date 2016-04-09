import bibtexparser
import hashlib
import re

from .base import RecordIterator
from .base import RecordParser
from .base import LanguageGuesser


class BibtexRecordParser(RecordParser):

    mappings = {
        'keywords': 'keyword',
        'description': 'abstract',
    }

    guesser = LanguageGuesser()

    def _clear_keywords(self, raw):
        line = raw.get(self.get_mapping('keywords'), '')
        return re.split(r'[,; ]+', line)

    def _clear_uuid(self, raw):
        sha = hashlib.sha1()
        data = self.clear('title', raw) + self.clear('description', raw)
        sha.update(data.encode('utf-8'))
        return sha.hexdigest()

    def _clear_language(self, raw):
        data = self.clear('title', raw) + self.clear('description', raw)
        data += ' '.join(self.clear('keywords', raw))
        return raw.get('language', self.guesser.guess(data))

    def clear(self, field, raw):
        return raw.get(field, super().clear(field, raw))

    def parse(self, raw):
        if isinstance(raw, str):
            return super().parse(bibtexparser.loads(raw).entries[0])
        return super().parse(raw)


class BibtexRecordIterator(RecordIterator):

    '''
    Iterates over bibtex reccords
    '''

    parser_class = BibtexRecordParser

    def get_buffer(self):
        with open(self.filename, 'r') as bibtex:
            database = bibtexparser.load(bibtex)
            for entry in database.entries:
                yield entry
