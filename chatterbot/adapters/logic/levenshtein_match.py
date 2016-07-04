from .base_match import BaseMatchAdapter
from Levenshtein.StringMatcher import StringMatcher
from heapq import nlargest


class LevenshteinMatchAdapter(BaseMatchAdapter):
    """
    The ClosestMatchAdapter creates a response by
    using fuzzywuzzy's process class to extract the most similar
    response to the input. This adapter selects a response to an
    input statement by selecting the closest known matching
    statement based on the Levenshtein Distance between the text
    of each statement.
    """

    def get(self, input_statement):
        """
        Takes a statement string and a list of statement strings.
        Returns the closest matching statement from the list.
        """
        statement_list = self.context.storage.get_response_statements()

        if not statement_list:
            if self.has_storage_context:
                # Use a randomly picked statement
                return 0, self.context.storage.get_random()
            else:
                raise self.EmptyDatasetException()

        # Get the text of each statement
        text_of_all_statements = []
        for statement in statement_list:
            text_of_all_statements.append(statement.text)

        # Check if an exact match exists
        if input_statement.text in text_of_all_statements:
            return 1, input_statement

        # Get the closest matching statement from the database
        closest_match, confidence = nlargest(1, [
            (StringMatcher(seq1=input_statement.text, seq2=text).ratio(), text)
            for text in text_of_all_statements
        ])[0]

        return confidence, next(
            (s for s in statement_list if s.text == closest_match), None
        )
