from dfm.cleaning import QualityFilter
import pytest


class TestQualityFilter:
    """Unit tests for the QualityFilter class"""

    @pytest.fixture(scope="class")
    def tweet_texts(self):
        return [
            "jeg er glad",
            "56789okd23456789098765sds",
            "jeg er glad...",
            "jeg er glad…",
            "67 54 13 B7",
            "#yolo # test ##",
        ]

    @pytest.fixture(scope="class")
    def long_text(self):
        return """
        Helt normal tekst:
        Første vindstød af stærk storm - andre steder i landet ramt
        Frederikshavn blev det første sted, der mærkede vindstød af stormstyrke,
        og nu er det også det første sted, der har mærket vindstød af stærk storm. Hvis det er noget at prale af.

        Der er nemlig målt vindstød på 29,3 meter i sekundet. Det er stærk storm,
        når det er over 28,5 meter i sekundet.

        Andre dele af landet har nu også mærket de første vindstød af stormstyrke. 

        Odense Lufthavn har haft 24,5 meter i sekundet, mens Grønlandshavnen i Aalborg har ramt 24,7
        meter i sekundet. Det er mest centrale sted i landet, hvor der indtil videre er målet stormstyrke.
        """

    @pytest.fixture(scope="class")
    def bullets_text(self):
        return """
        [summary]

        - test 1
        - test 1
            - test 2
            - test 3
                - test 1
        """

    @pytest.fixture(scope="class")
    def ellipsis_text(self):
        return """
        [summary]

        * test 1
            * test 2
            * test 3
        * test 1
            * test 2
                * test 3
        """

    @pytest.fixture(scope="class")
    def all_texts(self, tweet_texts, long_text, bullets_text, ellipsis_text):
        return tweet_texts + [long_text] + [bullets_text] + [ellipsis_text]


    @pytest.fixture(scope="class")
    def stop_words(self):
        return set([
                "er",
                "jeg",
                "det",
                "du",
                "ikke",
                "at",
                "en",
                "og",
                "har",
                "vi",
                "til",
                "på",
                "hvad",
                "mig",
                "med",
                "de",
                "for",
                "den",
                "så",
                "der",
                "dig",
                "han",
                "kan",
                "af",
            ])

    @pytest.fixture(scope="class")
    def qfilter(self):
        return QualityFilter()

    def test_good_stop_words(self, qfilter, stop_words):
        assert (
            qfilter.stop_word(qfilter.nlp("jeg er glad"), n=2, stop_words=stop_words) is True
        )

    def test_bad_stop_words(self, qfilter, stop_words):
        assert (
            qfilter.stop_word(qfilter.nlp("56789okd23456789098765sds"), n=1, stop_words=stop_words) is False
        )

    def test_good_bullets(self, qfilter):
        assert (
            qfilter.line_bullets_or_ellipsis(
                qfilter.nlp("56789okd23456789098765sds"), max_p_bullets=0.5, max_p_ellipsis=1
            )
            is True
        )

    def test_bad_bullets(self, qfilter, ellipsis_text):
        assert (
            qfilter.line_bullets_or_ellipsis(
                qfilter.nlp(ellipsis_text), max_p_bullets=0.5, max_p_ellipsis=1
            )
            is False
        )

    def test_bad_bullets2(self, qfilter, bullets_text):
        assert (
            qfilter.line_bullets_or_ellipsis(
                qfilter.nlp(bullets_text), max_p_bullets=0.5, max_p_ellipsis=1
            )
            is False
        )

    def test_good_ellipsis(self, qfilter, ellipsis_text):
        assert (
            qfilter.line_bullets_or_ellipsis(
                qfilter.nlp(ellipsis_text), max_p_bullets=1.0, max_p_ellipsis=0.5
            )
            is True
        )

    def test_bad_ellipsis(self, qfilter):
        assert (
            qfilter.line_bullets_or_ellipsis(
                qfilter.nlp("jeg er glad..."), max_p_bullets=1.0, max_p_ellipsis=0.5
            )
            is False
        )

    def test_bad_ellipsis2(self, qfilter):
        assert (
            qfilter.line_bullets_or_ellipsis(
                qfilter.nlp("jeg er glad…"), max_p_bullets=1.0, max_p_ellipsis=0.5
            )
            is False
        )

    def test_good_find_alpha(self, qfilter):
        assert qfilter.alpha(qfilter.nlp("jeg er glad"), ratio=0.8) is True

    def test_bad_alpha(self, qfilter):
        assert qfilter.alpha(qfilter.nlp("67 54 13 B7"), ratio=0.8) is False

    def test_good_mean_word_length(self, qfilter):
        assert (
            qfilter.mean_word_length(qfilter.nlp("jeg er glad"), mean_word_length=(3, 10))
            is True
        )

    def test_bad_mean_word_length(self, qfilter):
        assert (
            qfilter.mean_word_length(qfilter.nlp("56789okd23456789098765sds"), mean_word_length=(3, 10))
            is False
        )

    def test_good_doc_length(self, qfilter, ellipsis_text):
        assert qfilter.doc_length(qfilter.nlp(ellipsis_text), doc_length=(5, 100)) is True

    def test_bad_doc_length(self, qfilter):
        assert qfilter.doc_length(qfilter.nlp("jeg er glad"), doc_length=(5, 100)) is False

    def test_quality_filter(self, qfilter, all_texts):
        filtered = list(qfilter(all_texts))
        assert len(filtered) == 1
        assert sum(qfilter.filtered.values()) == (len(all_texts) - 1)