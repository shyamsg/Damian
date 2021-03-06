"""The dna module for damian.

This module contains the dna classes for the damian application. It
includes, among other things, functions to translate ambiguity bases,
reverse complement, reverse, check if the dna strings are valid dna strings.
It also includes a definition of the class dna_pair, which is used to store
tag pair or primer pair.

Attributes
----------
DNA_UNAMBIGUOUS_CHARS : string
    String of upper and lower case chars when no ambiguity is allowed.
DNA_UNAMBIGUOUS_REV : string
    The reverse (dna wise) of the DNA_UNAMBIGUOUS_CHARS string.
DNA_AMBIGUOUS_CHARS: string
    String of upper and lower case chars, including ambiguity bases.
DNA_AMBIGUOUS_REV: string
    The reverse bases for the DNA_AMBIGUOUS_CHARS string.
COMPLEMENT_UNAMBIGOUS_DNA :
    The translation table for complementing dna sequences without ambiuity
    bases.
COMPLEMENT_AMBIGOUS_DNA :
    The translation table for complementing dna sequencing with ambiguity
    bases.
AMB_REGEX_DICT : dict
    The dictionary containing the corresponding regex string for each possible
    base, including ambiguity bases.

"""

import regex

from textdistance import hamming

DNA_UNAMBIGUOUS_CHARS = "ACGTUNIacgtuni"
DNA_UNAMBIGUOUS_REV = "TGCAANItgcaani"
DNA_AMBIGUOUS_CHARS = "ACGTURYSWKMBDHVNIacgturyswkmbdhvni"
DNA_AMBIGUOUS_REV = "TGCAAYRWSMKVHDBNItgcaayrwsmkvhdbni"
# COMPLEMENT_UNAMBIGOUS_DNA = maketrans(DNA_UNAMBIGUOUS_CHARS,
#                                       DNA_UNAMBIGUOUS_REV)
# COMPLEMENT_AMBIGOUS_DNA = maketrans(DNA_AMBIGUOUS_CHARS, DNA_AMBIGUOUS_REV)

# SUBSET = {"A": "A", "C": "C", "G": "G", "T": "T", "U": "U", "R": "AG",
#         "Y": "CT", "S": "GC", "W": "AT", "K": "GT", "M": "AC", "B": "CGTYSK",
#         "D": "AGTRWK", "V": "ACTYWM", "H": "ACGRSM",
#         "N": "ACGTURYSWKMBDHVNI", "I": "ACGTURYSWKMBDHVNI"}
AMB_REGEX_DICT = {"A": r"A", "a": r"a", "C": r"C", "c": r"c", "G": r"G",
                  "g": r"g", "T": r"T", "t": r"t", "U": r"U", "u": r"u",
                  "R": r"[AG]", "r": r"[ag]", "Y": r"[CT]", "y": r"[ct]",
                  "S": r"[GC]", "s": r"[gc]", "W": r"[AT]", "w": r"[at]",
                  "K": r"[GT]", "k": r"[gt]", "M": r"[AC]", "m": r"[AC]",
                  "B": r"[CGT]", "b": r"[cgt]", "D": r"[AGT]", "d": r"[agt]",
                  "V": r"[ACT]", "v": r"[act]", "H": r"[ACG]", "h": r"[acg]",
                  "N": r"[ACGT]", "n": r"[acgt]", "I": r"[ACGT]",
                  "i": r"[acgt]"}


class dna_utility(object):
    """Helper class to manipulate dna sequences.

    This class has helper functions to manipulate dna sequences.

    """

    @staticmethod
    def conv_ambig_regex(sequence, mismatches=0, preserve_case=False):
        """Convert the ambigous bases to regular expressions.

        This function takes a dna sequence with ambiguous bases in it, and
        converts the ambiuity bases to regular expressions, so that we can use
        these for string matching.

        Parameters
        ----------
        sequence : string
            dna sequence
        preserve_case : bool
            preserve case of input dna, if false, convert to upper case.

        Returns
        -------
        :obj: compiled regex obect
            compiled dna regex with modified ambiguity bases, ready for use in
            string matching.

        Raises
        ------
        KeyError
            when character is not in dna dictionary.

        """
        if not preserve_case:   # convert to upper case if not preserve case
            sequence = sequence.upper()
        dna_regex = r"(?b)("  # best match set
        for c in sequence:
            if c in AMB_REGEX_DICT:
                dna_regex += AMB_REGEX_DICT[c]
            else:
                raise KeyError(c + "is not an allowed DNA character.")
        dna_regex = dna_regex + r"){s<="+str(mismatches)+r"}"
        dna_regex = regex.compile(dna_regex)
        return dna_regex

    @staticmethod
    def __find_match(matcher_regex, target_dna):
        """Find first match of given sequence in an unambiguous sequence.

        Given a target sequence, find the first/best match of this target
        sequence in a given unambiguous dna sequence.

        Parameters
        ----------
        matcher_regex : compiled regex pattern
            compiled regular expression object
        target_dna : string
            dna sequence

        Returns
        -------
        (int, int)
            start and end positions of best match (first if many),
            -1 if no matches.

        """
        firstmatch = matcher_regex.search(target_dna)
        if firstmatch is None:
            return((-1, -1))
        else:
            return(firstmatch.span())

    @staticmethod
    def find_last_match(matcher_regex, target_dna):
        """Find last match of given sequence in an unambiguous sequence.

        Given a target sequence, find the last best match of this target
        sequence in a given unambiguous dna sequence.

        Parameters
        ----------
        matcher_regex : compiled regex pattern
            compiled regular expression object
        target_dna : string
            dna sequence

        Returns
        -------
        (int, int, int)
            start and end positions of last match (first if many),
            -1 if no matches. Also returns the number of matches found

        """
        cur_end = 0
        last_start = 0
        last_end = 0
        number_found = 0
        while True:
            target_dna = target_dna[cur_end:]
            cur_start, cur_end = dna_utility.__find_match(matcher_regex,
                                                          target_dna)
            if cur_start == -1:
                break
            number_found += 1
            last_start = last_end + cur_start
            last_end = last_end + cur_end
        if last_start == 0 and last_end == 0:
            last_start = -1
            last_end = -1
        return ((last_start, last_end, number_found))

    @staticmethod
    def find_first_match(matcher_regex, target_dna):
        """Find first match of given sequence in an unambiguous sequence.

        Given a target sequence, find the first best match of this target
        sequence in a given unambiguous dna sequence.

        Parameters
        ----------
        matcher_regex : compiled regex pattern
            compiled regular expression object
        target_dna : string
            dna sequence

        Returns
        -------
        (int, int, int)
            start and end positions of last match (first if many),
            -1 if no matches. Also returns the number of matches found

        """
        (first_start, first_end) = dna_utility.__find_match(matcher_regex,
                                                            target_dna)
        cur_end = 0
        number_found = 0
        while True:
            target_dna = target_dna[cur_end:]
            cur_start, cur_end = dna_utility.__find_match(matcher_regex,
                                                          target_dna)
            if cur_start == -1:
                break
            number_found += 1
        return ((first_start, first_end, number_found))

    @staticmethod
    def find_hamming_distance(target_seq, source_seq, look_at_end=True):
        """Find hamming distance between sequences.

        Find the hamming distance between given sequences, assuming no
        ambiguity in the sequences.

        Parameters
        ----------
        target_seq :  string
            The string to be searched for
        sourse_seq :  strings
            The string to be searced in
        look_at_end : bool
            If true, look for match at the end of string, else beginning

        Returns
        -------
        dist : int
            Substitution distance between the strings

        """
        tlen = len(target_seq)
        slen = len(source_seq)
        if tlen > slen:
            return(tlen)
        if look_at_end:
            sseq = source_seq[(slen-tlen):]
        else:
            sseq = source_seq[0:tlen]
        return(hamming.distance(target_seq, sseq))
