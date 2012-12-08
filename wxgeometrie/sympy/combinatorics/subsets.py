from sympy.core import Basic
from sympy.combinatorics.graycode import GrayCode

import itertools

class Subset(Basic):
    """
    Represents a basic subset object.

    We generate subsets using essentially two techniques,
    binary enumeration and lexicographic enumeration.
    The Subset class takes two arguments, the first one
    describes the intial subset to consider and the second
    describes the superset.

    Examples:
    >>> from sympy.combinatorics.subsets import Subset
    >>> a = Subset(['c','d'], ['a','b','c','d'])
    >>> a.next_binary().subset
    ['b']
    >>> a.prev_binary().subset
    ['c']
    """

    _rank_binary = None
    _rank_lex = None
    _rank_graycode = None
    _subset = None
    _superset = None

    def __new__(cls, subset, superset):
        """
        Default constructor.

        It takes the subset and its superset as its parameters.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset(['c','d'], ['a','b','c','d'])
        >>> a.subset
        ['c', 'd']
        >>> a.superset
        ['a', 'b', 'c', 'd']
        >>> a.size
        2
        """
        if len(subset) > len(superset):
            raise ValueError('Invalid arguments have been provided. The superset must be larger than the subset.')
        for elem in subset:
            if elem not in superset:
                raise ValueError('The superset provided is invalid as it does not contain the element %i' % elem)
        obj = Basic.__new__(cls)
        obj._subset = subset
        obj._superset = superset
        return obj

    def iterate_binary(self, k):
        """
        This is a helper function. It iterates over the
        binary subsets by k steps. This variable can be
        both positive or negative.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset(['c','d'], ['a','b','c','d'])
        >>> a.iterate_binary(-2).subset
        ['d']
        >>> a = Subset(['a','b','c'], ['a','b','c','d'])
        >>> a.iterate_binary(2).subset
        []
        """
        bin_list = Subset.bitlist_from_subset(self.subset, self.superset)
        next_bin_list = list(bin((int(reduce(lambda x, y:
                                             x + y, bin_list), 2) + k)
                                 % 2**self.superset_size))[2:]
        next_bin_list = [0] * (self.superset_size - len(next_bin_list)) + \
                        next_bin_list
        return Subset.subset_from_bitlist(self.superset, next_bin_list)


    def next_binary(self):
        """
        Generates the next binary ordered subset.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset(['c','d'], ['a','b','c','d'])
        >>> a.next_binary().subset
        ['b']
        >>> a = Subset(['a','b','c','d'], ['a','b','c','d'])
        >>> a.next_binary().subset
        []
        """
        return self.iterate_binary(1)

    def prev_binary(self):
        """
        Generates the previous binary ordered subset.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset([], ['a','b','c','d'])
        >>> a.prev_binary().subset
        ['a', 'b', 'c', 'd']
        >>> a = Subset(['c','d'], ['a','b','c','d'])
        >>> a.prev_binary().subset
        ['c']
        """
        return self.iterate_binary(-1)

    def next_lexicographic(self):
        """
        Generates the next lexicographically ordered subset.

        Examples:
        """
        raise NotImplementedError()

    def prev_lexicographic(self):
        """
        Generates the previous lexicographically ordered subset.

        Examples:
        """
        raise NotImplementedError()

    def iterate_graycode(self, k):
        """
        Helper function used for prev_gray and next_gray.
        It performs k step overs to get the respective Gray codes.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset([1,2,3], [1,2,3,4])
        >>> a.iterate_graycode(3).subset
        [1, 4]
        >>> a.iterate_graycode(-2).subset
        [1, 2, 4]
        """
        unranked_code = GrayCode.unrank(self.superset_size,
                                       (self.rank_gray + k) % self.cardinality)
        return Subset.subset_from_bitlist(self.superset,
                                          unranked_code)

    def next_gray(self):
        """
        Generates the next Gray code ordered subset.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset([1,2,3], [1,2,3,4])
        >>> a.next_gray().subset
        [1, 3]
        """
        return self.iterate_graycode(1)

    def prev_gray(self):
        """
        Generates the previous Gray code ordered subset.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset([2,3,4], [1,2,3,4,5])
        >>> a.prev_gray().subset
        [2, 3, 4, 5]
        """
        return self.iterate_graycode(-1)

    @property
    def rank_binary(self):
        """
        Computes the binary ordered rank.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset([], ['a','b','c','d'])
        >>> a.rank_binary
        0
        >>> a = Subset(['c','d'], ['a','b','c','d'])
        >>> a.rank_binary
        3
        """
        if self._rank_binary == None:
            self._rank_binary = int("".join(
                Subset.bitlist_from_subset(self.subset,
                                           self.superset)), 2)
        return self._rank_binary

    @property
    def rank_lexicographic(self):
        """
        Computes the lexicographic ranking of the subset.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset(['c','d'], ['a','b','c','d'])
        >>> a.rank_lexicographic
        14
        >>> a = Subset([2,4,5], [1,2,3,4,5,6])
        >>> a.rank_lexicographic
        43
        """
        if self._rank_lex == None:
            superset_index = list(xrange(self.superset_size))
            subset_index = [self.superset.index(j) for j in self.subset]
            def ranklex(self, subset_index, i, n):
                if subset_index == [] or i > n:
                    return 0
                if i in subset_index:
                    subset_index.remove(i)
                    return 1 + ranklex(self, subset_index, i + 1, n)
                return 2**(n - i - 1) + ranklex(self, subset_index, i + 1, n)
            self._rank_lex = ranklex(self, subset_index, 0, self.superset_size)
        return self._rank_lex

    @property
    def rank_gray(self):
        """
        Computes the Gray code ranking of the subset.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset(['c','d'], ['a','b','c','d'])
        >>> a.rank_gray
        2
        >>> a = Subset([2,4,5], [1,2,3,4,5,6])
        >>> a.rank_gray
        27
        """
        if self._rank_graycode == None:
            bits = Subset.bitlist_from_subset(self.subset, self.superset)
            self._rank_graycode = GrayCode(len(bits), start=bits).rank
        return self._rank_graycode

    @property
    def subset(self):
        """
        Gets the subset represented by the current instance.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset(['c','d'], ['a','b','c','d'])
        >>> a.subset
        ['c', 'd']
        """
        return self._subset

    @property
    def size(self):
        """
        Gets the size of the subset.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset(['c','d'], ['a','b','c','d'])
        >>> a.size
        2
        """
        return len(self.subset)

    @property
    def superset(self):
        """
        Gets the superset of the subset.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset(['c','d'], ['a','b','c','d'])
        >>> a.superset
        ['a', 'b', 'c', 'd']
        """
        return self._superset

    @property
    def superset_size(self):
        """
        Returns the size of the superset.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset(['c','d'], ['a','b','c','d'])
        >>> a.superset_size
        4
        """
        return len(self.superset)

    @property
    def cardinality(self):
        """
        Returns the number of all possible subsets.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> a = Subset(['c','d'], ['a','b','c','d'])
        >>> a.cardinality
        16
        """
        return 2**(self.superset_size)

    @classmethod
    def subset_from_bitlist(self, super_set, bitlist):
        """
        Gets the subset defined by the bitlist.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> Subset.subset_from_bitlist(['a','b','c','d'], '0011').subset
        ['c', 'd']
        """
        if len(super_set) != len(bitlist):
            raise ValueError("The sizes of the lists are not equal")
        ret_set = []
        for i in xrange(len(bitlist)):
            if bitlist[i] == '1':
                ret_set.append(super_set[i])
        return Subset(ret_set, super_set)

    @classmethod
    def bitlist_from_subset(self, subset, superset):
        """
        Gets the bitlist corresponding to a subset.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> Subset.bitlist_from_subset(['c','d'], ['a','b','c','d'])
        '0011'
        """
        bitlist = ['0'] * len(superset)
        if type(subset) is Subset:
            subset = subset.args[0]
        for i in subset:
            bitlist[superset.index(i)] = '1'
        return ''.join(bitlist)

    @classmethod
    def unrank_binary(self, rank, superset):
        """
        Gets the binary ordered subset of the specified rank.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> Subset.unrank_binary(4, ['a','b','c','d']).subset
        ['b']
        """
        bin_list = list(bin(rank))[2:]
        bin_list = [0] * (len(superset) - len(bin_list)) + bin_list
        return Subset.subset_from_bitlist(superset, bin_list)

    @classmethod
    def unrank_gray(self, rank, superset):
        """
        Gets the Gray code ordered subset of the specified rank.

        Examples:
        >>> from sympy.combinatorics.subsets import Subset
        >>> Subset.unrank_gray(4, ['a','b','c']).subset
        ['a', 'b']
        >>> Subset.unrank_gray(0, ['a','b','c']).subset
        []
        """
        graycode_bitlist = GrayCode.unrank(len(superset), rank)
        return Subset.subset_from_bitlist(superset, graycode_bitlist)

def ksubsets(superset, k):
    """
    Finds the subsets of size k in lexicographic order.

    This uses the itertools generator.

    Examples:
    >>> from sympy.combinatorics.subsets import ksubsets
    >>> list(ksubsets([1,2,3], 2))
    [(1, 2), (1, 3), (2, 3)]
    >>> list(ksubsets([1,2,3,4,5], 2))
    [(1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), \
    (2, 5), (3, 4), (3, 5), (4, 5)]
    """
    return (itertools.combinations(superset, k))
