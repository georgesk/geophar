from sympy.matrices.expressions.blockmatrix import (block_collapse, bc_matmul,
        bc_block_plus_ident, BlockDiagMatrix, BlockMatrix, bc_dist, bc_matadd)
from sympy.matrices.expressions import (MatrixSymbol, Identity, MatMul,
        Inverse, Trace)
from sympy.matrices import Matrix
from sympy.core import Tuple, symbols
from sympy.functions import transpose

k, l, m, n, p = symbols('k:n, p', integer=True)
G = MatrixSymbol('G', n, n)
H = MatrixSymbol('H', n, n)
b1 = BlockMatrix([[G, H]])
b2 = BlockMatrix([[G], [H]])

def test_bc_matmul():
    assert bc_matmul(H*b1*b2*G) == H*BlockMatrix([[G*G + H*H]])*G

def test_bc_matadd():
    assert bc_matadd(BlockMatrix([[G, H]]) + BlockMatrix([[H, H]])) == \
            BlockMatrix([[G+H, H+H]])

def test_bc_dist_diag():
    A = MatrixSymbol('A', n, n)
    B = MatrixSymbol('B', m, m)
    C = MatrixSymbol('C', l, l)
    X = BlockDiagMatrix(A, B, C)

    assert bc_dist(X+X).equals(BlockDiagMatrix(2*A, 2*B, 2*C))

def test_block_plus_ident():
    A = MatrixSymbol('A', n, n)
    B = MatrixSymbol('B', n, m)
    C = MatrixSymbol('C', m, n)
    D = MatrixSymbol('D', m, m)
    X = BlockMatrix([[A, B], [C, D]])
    assert bc_block_plus_ident(X+Identity(m+n)) == \
            BlockDiagMatrix(Identity(n), Identity(m)) + X

def test_BlockMatrix():
    A = MatrixSymbol('A', n, m)
    B = MatrixSymbol('B', n, k)
    C = MatrixSymbol('C', l, m)
    D = MatrixSymbol('D', l, k)
    M = MatrixSymbol('M', m + k, p)
    N = MatrixSymbol('N', l + n, k + m)
    X = BlockMatrix(Matrix([[A, B], [C, D]]))

    assert X.__class__(*X.args) == X

    # block_collapse does nothing on normal inputs
    E = MatrixSymbol('E', n, m)
    assert block_collapse(A + 2*E) == A + 2*E
    F = MatrixSymbol('F', m, m)
    assert block_collapse(E.T*A*F) == E.T*A*F

    assert X.shape == (l + n, k + m)
    assert X.blockshape == (2, 2)
    assert transpose(X) == BlockMatrix(Matrix([[A.T, C.T], [B.T, D.T]]))
    assert transpose(X).shape == X.shape[::-1]

    # Test that BlockMatrices and MatrixSymbols can still mix
    assert (X*M).is_MatMul
    assert X._blockmul(M).is_MatMul
    assert (X*M).shape == (n + l, p)
    assert (X + N).is_MatAdd
    assert X._blockadd(N).is_MatAdd
    assert (X + N).shape == X.shape

    E = MatrixSymbol('E', m, 1)
    F = MatrixSymbol('F', k, 1)

    Y = BlockMatrix(Matrix([[E], [F]]))

    assert (X*Y).shape == (l + n, 1)
    assert block_collapse(X*Y).blocks[0, 0] == A*E + B*F
    assert block_collapse(X*Y).blocks[1, 0] == C*E + D*F

    # block_collapse passes down into container objects, transposes, and inverse
    assert block_collapse(transpose(X*Y)) == transpose(block_collapse(X*Y))
    assert block_collapse(Tuple(X*Y, 2*X)) == (
        block_collapse(X*Y), block_collapse(2*X))

    # Make sure that MatrixSymbols will enter 1x1 BlockMatrix if it simplifies
    Ab = BlockMatrix([[A]])
    Z = MatrixSymbol('Z', *A.shape)
    assert block_collapse(Ab + Z) == A + Z


def test_BlockMatrix_Trace():
    A, B, C, D = map(lambda s: MatrixSymbol(s, 3, 3), 'ABCD')
    X = BlockMatrix([[A, B], [C, D]])
    assert Trace(X) == Trace(A) + Trace(D)


def test_squareBlockMatrix():
    A = MatrixSymbol('A', n, n)
    B = MatrixSymbol('B', n, m)
    C = MatrixSymbol('C', m, n)
    D = MatrixSymbol('D', m, m)
    X = BlockMatrix([[A, B], [C, D]])
    Y = BlockMatrix([[A]])

    assert X.is_square

    assert (block_collapse(X + Identity(m + n)) ==
        BlockMatrix([[A + Identity(n), B], [C, D + Identity(m)]]))
    Q = X + Identity(m + n)

    assert block_collapse(Q.inverse()) == Inverse(block_collapse(Q))

    assert (X + MatrixSymbol('Q', n + m, n + m)).is_MatAdd
    assert (X * MatrixSymbol('Q', n + m, n + m)).is_MatMul

    assert Y.I.blocks[0, 0] == A.I
    assert X.inverse(expand=True) == BlockMatrix([
        [(-B*D.I*C + A).I, -A.I*B*(D + -C*A.I*B).I],
        [-(D - C*A.I*B).I*C*A.I, (D - C*A.I*B).I]])

    assert isinstance(X.inverse(expand=False), Inverse)
    assert isinstance(X.inverse(), Inverse)

    assert not X.is_Identity

    Z = BlockMatrix([[Identity(n), B], [C, D]])
    assert not Z.is_Identity


def test_BlockDiagMatrix():
    A = MatrixSymbol('A', n, n)
    B = MatrixSymbol('B', m, m)
    C = MatrixSymbol('C', l, l)
    M = MatrixSymbol('M', n + m + l, n + m + l)

    X = BlockDiagMatrix(A, B, C)
    Y = BlockDiagMatrix(A, 2*B, 3*C)

    assert X.blocks[1, 1] == B
    assert X.shape == (n + m + l, n + m + l)
    assert all(X.blocks[i, j].is_ZeroMatrix if i != j else X.blocks[i, j] in [A, B, C]
            for i in range(3) for j in range(3))
    assert X.__class__(*X.args) == X

    assert isinstance(block_collapse(X.I * X), Identity)

    assert bc_matmul(X*X) == BlockDiagMatrix(A*A, B*B, C*C)
    assert block_collapse(X*X) == BlockDiagMatrix(A*A, B*B, C*C)
    #XXX: should be == ??
    assert block_collapse(X + X).equals(BlockDiagMatrix(2*A, 2*B, 2*C))
    assert block_collapse(X*Y) == BlockDiagMatrix(A*A, 2*B*B, 3*C*C)
    assert block_collapse(X + Y) == BlockDiagMatrix(2*A, 3*B, 4*C)

    # Ensure that BlockDiagMatrices can still interact with normal MatrixExprs
    assert (X*(2*M)).is_MatMul
    assert (X + (2*M)).is_MatAdd

    assert (X._blockmul(M)).is_MatMul
    assert (X._blockadd(M)).is_MatAdd
