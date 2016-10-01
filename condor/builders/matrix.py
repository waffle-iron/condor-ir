"""Helpers to build a term document matrix with several different options.

.. note:: this module can receive list of already resolved models but it should
    not use the database or anything related with sqlalchemy.
"""

import collections
import itertools
import numpy

from condor.normalize import CompleteNormalizer


BuildMatrixResult = collections.namedtuple(
    'BuildMatrixResult',
    ['words', 'matrix', 'options']
)


def build_matrix(bibset):
    """Builds a term document matrix using a bibliography set.
    """
    words = word_set(bibset)
    nwords = len(words)
    ndocs = len(bibset.bibliographies)
    frequency = numpy.zeros((ndocs, nwords), dtype=int)
    for row, col, freq in matrix(bibset, words):
        frequency[row, col] = freq
    return BuildMatrixResult(
        words,
        frequency,
        str(CompleteNormalizer.__mro__),
    )


def get_tokens(record, fields=None, list_fields=None):
    fields = fields or ['title', 'description', ]
    list_fields = list_fields or ['keywords', ]
    tokens = []
    for field in fields:
        tokens.extend(record.get(field, '').split())
    for field in list_fields:
        value = record.get(field, '{""}')
        if value == '{""}':
            continue
        tokens.extend(word for val in value[1:-1].split(',') for word in val.split())
    return tokens


def raw_data(bib):
    normalizer = CompleteNormalizer(language=bib.language)
    return [normalizer.apply_to(token) for token in get_tokens(bib.__dict__)]


def word_set(bibset):
    def words():
        for bib in bibset.bibliographies:
            yield raw_data(bib)
    return sorted(set(itertools.chain.from_iterable(words())))


def matrix(bibset, words):
    word_dict = {word: pos for pos, word in enumerate(words)}
    for ind, bib in enumerate(bibset.bibliographies):
        raw = list(raw_data(bib))
        frequency = collections.Counter(raw)
        for word, freq in frequency.items():
            yield ind, word_dict[word], freq
