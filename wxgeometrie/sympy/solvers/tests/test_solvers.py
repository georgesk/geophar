from sympy import (Matrix, Symbol, solve, exp, log, cos, acos, Rational, Eq,
    sqrt, oo, LambertW, pi, I, sin, asin, Function, diff, Derivative, symbols,
    S, sympify, var, simplify, Integral, sstr, Wild, solve_linear, Interval,
    And, Or, Lt, Gt, Q, re, im, expand, zoo, tan, Poly, cosh, sinh, atanh,
    atan, Dummy)

from sympy.solvers import solve_linear_system, solve_linear_system_LU,dsolve,\
     tsolve, solve_undetermined_coeffs
from sympy.solvers.solvers import unrad, _invert

from sympy.utilities.pytest import XFAIL, raises

from sympy.abc import x, y

def NS(e, n=15, **options):
    return sstr(sympify(e).evalf(n, **options), full_prec=True)

def test_free_symbols():
    x = Symbol('x')
    f = Function('f')
    raises(NotImplementedError, "solve(Eq(log(f(x)), Integral(x, (x, 1, f(x)))), f(x))")

def test_swap_back():
    f, g = map(Function, 'fg')
    x, y = symbols('x,y')
    a, b = f(x), g(x)
    assert solve([a + y - 2, a - b - 5], a, y, b) == \
                 {a: b + 5, y: -b - 3}
    assert solve(a + b*x - 2, [a, b]) == {a: 2, b: 0}
    assert solve(a + b**2*x - y, [a, b]) == [{a: y - b**2*x}]

def guess_solve_strategy(eq, symbol):
    try:
        solve(eq, symbol)
        return True
    except:
        return False

def test_guess_poly():
    """
    See solvers.guess_solve_strategy
    """
    x, y, a = symbols('x,y,a')

    # polynomial equations
    assert guess_solve_strategy( S(4), x ) #== GS_POLY
    assert guess_solve_strategy( x, x ) #== GS_POLY
    assert guess_solve_strategy( x + a, x ) #== GS_POLY
    assert guess_solve_strategy( 2*x, x ) #== GS_POLY
    assert guess_solve_strategy( x + sqrt(2), x) #== GS_POLY
    assert guess_solve_strategy( x + 2**Rational(1,4), x) #== GS_POLY
    assert guess_solve_strategy( x**2 + 1, x ) #== GS_POLY
    assert guess_solve_strategy( x**2 - 1, x ) #== GS_POLY
    assert guess_solve_strategy( x*y + y, x ) #== GS_POLY
    assert guess_solve_strategy( x*exp(y) + y, x) #== GS_POLY
    assert guess_solve_strategy( (x - y**3)/(y**2*sqrt(1 - y**2)), x) #== GS_POLY

def test_guess_poly_cv():
    x, y = symbols('x,y')
    # polynomial equations via a change of variable
    assert guess_solve_strategy( sqrt(x) + 1, x ) #== GS_POLY_CV_1
    assert guess_solve_strategy( x**Rational(1,3) + sqrt(x) + 1, x ) #== GS_POLY_CV_1
    assert guess_solve_strategy( 4*x*(1 - sqrt(x)), x ) #== GS_POLY_CV_1

    # polynomial equation multiplying both sides by x**n
    assert guess_solve_strategy( x + 1/x + y, x ) #== GS_POLY_CV_2

def test_guess_rational_cv():
    # rational functions
    x, y = symbols('x,y')
    assert guess_solve_strategy( (x+1)/(x**2 + 2), x) #== GS_RATIONAL
    assert guess_solve_strategy( (x - y**3)/(y**2*sqrt(1 - y**2)), y) #== GS_RATIONAL_CV_1

    # rational functions via the change of variable y -> x**n
    assert guess_solve_strategy( (sqrt(x) + 1)/(x**Rational(1,3) + sqrt(x) + 1), x ) \
                                #== GS_RATIONAL_CV_1

def test_guess_transcendental():
    x, y, a, b = symbols('x,y,a,b')
    #transcendental functions
    assert guess_solve_strategy( exp(x) + 1, x ) #== GS_TRANSCENDENTAL
    assert guess_solve_strategy( 2*cos(x)-y, x ) #== GS_TRANSCENDENTAL
    assert guess_solve_strategy( exp(x) + exp(-x) - y, x ) #== GS_TRANSCENDENTAL
    assert guess_solve_strategy(3**x-10, x) #== GS_TRANSCENDENTAL
    assert guess_solve_strategy(-3**x+10, x) #== GS_TRANSCENDENTAL

    assert guess_solve_strategy(a*x**b-y, x) #== GS_TRANSCENDENTAL

def test_solve_args():
    a, b, x, y = symbols('a,b,x,y')
    #implicit symbol to solve for
    assert set(int(tmp) for tmp in solve(x**2-4)) == set([2,-2])
    assert solve([x+y-3,x-y-5]) == {x: 4, y: -1}
    #no symbol to solve for
    assert solve(42) == []
    assert solve([1, 2]) is None
    #multiple symbols: take the first linear solution
    assert solve(x + y - 3, [x, y]) == [{x: 3 - y}]
    # unless it is an undetermined coefficients system
    assert solve(a + b*x - 2, [a, b]) == {a: 2, b: 0}
    # failing undetermined system
    assert solve(a*x + b**2/(x + 4) - 3*x - 4/x, a, b) == \
        [{a: (-b**2*x + 3*x**3 + 12*x**2 + 4*x + 16)/(x**3 + 4*x**2)}]
    # failed single equation
    assert solve(1/(1/x - y + exp(y))) ==  []
    raises(NotImplementedError, 'solve(exp(x) + sin(x) + exp(y) + sin(y))')
    # failed system
    # --  when no symbols given, 1 fails
    assert solve([y, exp(x) + x]) == [{x: -LambertW(1), y: 0}]
    #     both fail
    assert solve((exp(x) - x, exp(y) - y)) == [{x: -LambertW(-1), y: -LambertW(-1)}]
    # --  when symbols given
    solve([y, exp(x) + x], x, y) == [(-LambertW(1), 0)]
    #symbol is not a symbol or function
    raises(TypeError, "solve(x**2-pi, pi)")
    # no equations
    assert solve([], [x]) == []
    # overdetermined system
    # - nonlinear
    assert solve([(x + y)**2 - 4, x + y - 2]) == [{x: -y + 2}]
    # - linear
    assert solve((x + y - 2, 2*x + 2*y - 4)) == {x: -y + 2}

def test_solve_polynomial1():
    x, y, a = symbols('x,y,a')

    assert solve(3*x-2, x) == [Rational(2,3)]
    assert solve(Eq(3*x, 2), x) == [Rational(2,3)]

    assert solve(x**2-1, x) in [[-1, 1], [1, -1]]
    assert solve(Eq(x**2, 1), x) in [[-1, 1], [1, -1]]

    assert solve( x - y**3, x) == [y**3]
    assert sorted(solve( x - y**3, y)) == sorted([
        (-x**Rational(1,3))/2 + I*sqrt(3)*x**Rational(1,3)/2,
        x**Rational(1,3),
        (-x**Rational(1,3))/2 - I*sqrt(3)*x**Rational(1,3)/2,
    ])

    a11,a12,a21,a22,b1,b2 = symbols('a11,a12,a21,a22,b1,b2')

    assert solve([a11*x + a12*y - b1, a21*x + a22*y - b2], x, y) == \
        {
        x : (a22*b1 - a12*b2)/(a11*a22 - a12*a21),
        y : (a11*b2 - a21*b1)/(a11*a22 - a12*a21),
        }

    solution = {y: S.Zero, x: S.Zero}

    assert solve((x - y, x+y),  x, y ) == solution
    assert solve((x - y, x+y), (x, y)) == solution
    assert solve((x - y, x+y), [x, y]) == solution

    assert set(solve(x**3 - 15*x - 4, x)) == set([-2 + 3**Rational(1,2),
                                           S(4),
                                           -2 - 3**Rational(1,2) ])

    assert sorted(solve((x**2 - 1)**2 - a, x)) == \
           sorted([sqrt(1 + sqrt(a)), -sqrt(1 + sqrt(a)),
                   sqrt(1 - sqrt(a)), -sqrt(1 - sqrt(a))])

def test_solve_polynomial2():
    x = Symbol('x')
    assert solve(4, x) == []

def test_solve_polynomial_cv_1a():
    """
    Test for solving on equations that can be converted to a polynomial equation
    using the change of variable y -> x**Rational(p, q)
    """

    x = Symbol('x')
    assert solve( sqrt(x) - 1, x) == [1]
    assert solve( sqrt(x) - 2, x) == [4]
    assert solve( x**Rational(1,4) - 2, x) == [16]
    assert solve( x**Rational(1,3) - 3, x) == [27]
    # XXX there are imaginary roots that are being missed
    assert solve(sqrt(x)+x**Rational(1,3)+x**Rational(1,4),x) == [0]

def test_solve_polynomial_cv_1b():
    x, a = symbols('x a')
    assert set(solve(4*x*(1 - a*sqrt(x)), x)) == set([S(0), 1/a**2])
    assert set(solve(x * (x**(S(1)/3) - 3), x)) == set([S(0), S(27)])

def test_solve_polynomial_cv_2():
    """
    Test for solving on equations that can be converted to a polynomial equation
    multiplying both sides of the equation by x**m
    """
    x = Symbol('x')

    assert solve(x + 1/x - 1, x) in \
        [[ Rational(1,2) + I*sqrt(3)/2, Rational(1,2) - I*sqrt(3)/2],
         [ Rational(1,2) - I*sqrt(3)/2, Rational(1,2) + I*sqrt(3)/2]]

def test_solve_rational():
    """Test solve for rational functions"""
    x, y, a, b = symbols('x,y,a,b')

    assert solve( ( x - y**3 )/( (y**2)*sqrt(1 - y**2) ), x) == [y**3]

def test_linear_system():
    x, y, z, t, n, a = symbols('x,y,z,t,n,a')

    assert solve([x - 1, x - y, x - 2*y, y - 1], [x,y]) is None

    assert solve([x - 1, x - y, x - 2*y, x - 1], [x,y]) is None
    assert solve([x - 1, x - 1, x - y, x - 2*y], [x,y]) is None

    assert solve([x + 5*y - 2, -3*x + 6*y - 15], x, y) == {x: -3, y: 1}

    M = Matrix([[0,0,n*(n+1),(n+1)**2,0],
                [n+1,n+1,-2*n-1,-(n+1),0],
                [-1, 0, 1, 0, 0]])

    assert solve_linear_system(M, x, y, z, t) == \
           {y: 0, z: t*(-n - 1)/n, x: t*(-n - 1)/n}

    assert solve([x + y + z + t, -z - t], x, y, z, t) == {x: -y, z: -t}

    assert solve([a(0, 0) + a(0, 1) + a(1, 0) + a(1, 1), -a(1, 0) - a(1, 1)],
        a(0, 0), a(0, 1), a(1, 0), a(1, 1)) == {a(1, 0): -a(1, 1), a(0, 0): -a(0, 1)}

def test_linear_systemLU():
    x, y, z, n = symbols('x,y,z,n')

    M = Matrix([[1,2,0,1],[1,3,2*n,1],[4,-1,n**2,1]])

    assert solve_linear_system_LU(M, [x,y,z]) == {z: -3/(n**2+18*n),
                                                  x: 1-12*n/(n**2+18*n),
                                                  y: 6*n/(n**2+18*n)}

# Note: multiple solutions exist for some of these equations, so the tests
# should be expected to break if the implementation of the solver changes
# in such a way that a different branch is chosen
def test_tsolve():
    a, b = symbols('a,b')
    x, y, z = symbols('x,y,z')
    assert solve(exp(x)-3, x) == [log(3)]
    assert solve((a*x+b)*(exp(x)-3), x) == [-b/a, log(3)]
    assert solve(cos(x)-y, x) == [acos(y)]
    assert solve(2*cos(x)-y,x)== [acos(y/2)]
    assert solve(Eq(cos(x), sin(x)), x) == [-3*pi/4, pi/4]

    assert solve(exp(x) + exp(-x) - y, x) == [
                        log(y/2 - sqrt(y**2 - 4)/2),
                        log(y/2 + sqrt(y**2 - 4)/2),
                        ]
    assert solve(exp(x)-3, x) == [log(3)]
    assert solve(Eq(exp(x), 3), x) == [log(3)]
    assert solve(log(x)-3, x) == [exp(3)]
    assert solve(sqrt(3*x)-4, x) == [Rational(16,3)]
    assert solve(3**(x+2), x) == [zoo]
    assert solve(3**(2-x), x) == [oo]
    assert solve(x+2**x, x) == [-LambertW(log(2))/log(2)]
    assert solve(3*x+5+2**(-5*x+3), x) in [
        [-((25*log(2) - 3*LambertW(-10240*2**(Rational(1, 3))*log(2)/3))/(15*log(2)))],
        [Rational(-5, 3) + LambertW(log(2**(-10240*2**(Rational(1, 3))/3)))/(5*log(2))],
        [-Rational(5,3) + LambertW(-10240*2**Rational(1,3)*log(2)/3)/(5*log(2))],
        [(-25*log(2) + 3*LambertW(-10240*2**(Rational(1, 3))*log(2)/3))/(15*log(2))],
        [-((25*log(2) - 3*LambertW(-10240*2**(Rational(1, 3))*log(2)/3)))/(15*log(2))],
        [-(25*log(2) - 3*LambertW(log(2**(-10240*2**Rational(1, 3)/3))))/(15*log(2))],
        [(25*log(2) - 3*LambertW(log(2**(-10240*2**Rational(1, 3)/3))))/(-15*log(2))]
        ]
    assert solve(5*x-1+3*exp(2-7*x), x) == \
        [Rational(1,5) + LambertW(-21*exp(Rational(3, 5))/5)/7]
    assert solve(2*x+5+log(3*x-2), x) == \
        [Rational(2,3) + LambertW(2*exp(-Rational(19, 3))/3)/2]
    assert solve(3*x+log(4*x), x) == [LambertW(Rational(3,4))/3]
    assert solve((2*x+8)*(8+exp(x)), x) == [-4, log(8) + pi*I]
    eq = 2*exp(3*x+4)-3
    ans = solve(eq, x)
    assert  len(ans) == 3 and all(eq.subs(x, a).n(chop=True) == 0 for a in ans)
    assert solve(2*log(3*x+4)-3, x) == [(exp(Rational(3,2))-4)/3]
    assert solve(exp(x)+1, x) == [pi*I]
    assert solve(x**2 - 2**x, x) == [2]
    assert solve(x**3 - 3**x, x) == [-3*LambertW(-log(3)/3)/log(3)]

    A = -7*2**Rational(4, 5)*6**Rational(1, 5)*log(7)/10
    B = -7*3**Rational(1, 5)*log(7)/5

    result = solve(2*(3*x+4)**5 - 6*7**(3*x+9), x)

    assert len(result) == 1 and expand(result[0]) in [
        Rational(-4, 3) - 5/log(7)/3*LambertW(A),
        Rational(-4, 3) - 5/log(7)/3*LambertW(B),
    ]

    assert solve(z*cos(x)-y, x)      == [acos(y/z)]
    assert solve(z*cos(2*x)-y, x)    == [acos(y/z)/2]
    assert solve(z*cos(sin(x))-y, x) == [asin(acos(y/z))]

    assert solve(z*cos(x), x)        == [acos(0)]

    # issue #1409
    assert solve(y - b*x/(a+x), x) in [[-a*y/(y - b)], [a*y/(b - y)]]
    assert solve(y - b*exp(a/x), x) == [a/log(y/b)]
    # issue #1408
    assert solve(y-b/(1+a*x), x) in [[(b - y)/(a*y)], [-((y - b)/(a*y))]]
    # issue #1407
    assert solve(y-a*x**b , x) == [(y/a)**(1/b)]
    # issue #1406
    assert solve(z**x - y, x) == [log(y)/log(z)]
    # issue #1405
    assert solve(2**x - 10, x) == [log(10)/log(2)]

def test_solve_for_functions_derivatives():
    t = Symbol('t')
    x = Function('x')(t)
    y = Function('y')(t)
    a11,a12,a21,a22,b1,b2 = symbols('a11,a12,a21,a22,b1,b2')

    soln = solve([a11*x + a12*y - b1, a21*x + a22*y - b2], x, y)
    assert soln == {
        x : (a22*b1 - a12*b2)/(a11*a22 - a12*a21),
        y : (a11*b2 - a21*b1)/(a11*a22 - a12*a21),
        }

    assert solve(x - 1, x) == [1]
    assert solve(3*x - 2, x) == [Rational(2, 3)]

    soln = solve([a11*x.diff(t) + a12*y.diff(t) - b1, a21*x.diff(t) +
            a22*y.diff(t) - b2], x.diff(t), y.diff(t))
    assert soln == { y.diff(t) : (a11*b2 - a21*b1)/(a11*a22 - a12*a21),
            x.diff(t) : (a22*b1 - a12*b2)/(a11*a22 - a12*a21) }

    assert solve(x.diff(t)-1, x.diff(t)) == [1]
    assert solve(3*x.diff(t)-2, x.diff(t)) == [Rational(2,3)]

    eqns = set((3*x - 1, 2*y-4))
    assert solve(eqns, set((x,y))) == { x : Rational(1, 3), y: 2 }
    x = Symbol('x')
    f = Function('f')
    F = x**2 + f(x)**2 - 4*x - 1
    assert solve(F.diff(x), diff(f(x), x)) == [-((x - 2)/f(x))]

    # Mixed cased with a Symbol and a Function
    x = Symbol('x')
    y = Function('y')(t)

    soln = solve([a11*x + a12*y.diff(t) - b1, a21*x +
            a22*y.diff(t) - b2], x, y.diff(t))
    assert soln == { y.diff(t) : (a11*b2 - a21*b1)/(a11*a22 - a12*a21),
            x : (a22*b1 - a12*b2)/(a11*a22 - a12*a21) }

def test_issue626():
    x = Symbol("x")
    f = Function("f")
    F = x**2 + f(x)**2 - 4*x - 1
    e = F.diff(x)
    assert solve(e, f(x).diff(x)) in [[(2 - x)/f(x)], [-((x - 2)/f(x))]]

def test_solve_linear():
    x, y = symbols('x y')
    w = Wild('w')
    assert solve_linear(x, x) == (0, 1)
    assert solve_linear(x, y - 2*x) in [(x, y/3), (y, 3*x)]
    assert solve_linear(x, y - 2*x, exclude=[x]) ==(y, 3*x)
    assert solve_linear(3*x - y, 0) in [(x, y/3), (y, 3*x)]
    assert solve_linear(3*x - y, 0, [x]) == (x, y/3)
    assert solve_linear(3*x - y, 0, [y]) == (y, 3*x)
    assert solve_linear(x**2/y, 1) == (y, x**2)
    assert solve_linear(w, x) in [(w, x), (x, w)]
    assert solve_linear(cos(x)**2 + sin(x)**2 + 2 + y) == \
           (y, -2 - cos(x)**2 - sin(x)**2)
    assert solve_linear(cos(x)**2 + sin(x)**2 + 2 + y, symbols=[x]) == (0, 1)
    assert solve_linear(Eq(x, 3)) == (x, 3)
    assert solve_linear(1/(1/x - 2)) == (0, 0)
    raises(ValueError, 'solve_linear(Eq(x, 3), 3)')

def test_solve_undetermined_coeffs():
    a, b, c, x = symbols('a, b, c, x')

    assert solve_undetermined_coeffs(a*x**2 + b*x**2 + b*x  + 2*c*x + c + 1, [a, b, c], x) == \
        {a: -2, b: 2, c: -1}
    # Test that rational functions work
    assert solve_undetermined_coeffs(a/x  + b/(x + 1) - (2*x + 1)/(x**2 + x), [a, b], x) == \
        {a: 1, b: 1}
    # Test cancellation in rational functions
    assert solve_undetermined_coeffs(((c + 1)*a*x**2 + (c + 1)*b*x**2 +
    (c + 1)*b*x  + (c + 1)*2*c*x + (c + 1)**2)/(c + 1), [a, b, c], x) == \
        {a: -2, b: 2, c: -1}

def test_solve_inequalities():
    system = [Lt(x**2 - 2, 0), Gt(x**2 - 1, 0)]

    assert solve(system) == \
        And(Or(And(Lt(-sqrt(2), re(x)), Lt(re(x), -1)),
               And(Lt(1, re(x)), Lt(re(x), sqrt(2)))), Eq(im(x), 0))
    assert solve(system, assume=Q.real(x)) == \
        Or(And(Lt(-sqrt(2), x), Lt(x, -1)), And(Lt(1, x), Lt(x, sqrt(2))))

def test_issue_1694():
    x, y, z = symbols('x,y,z')
    assert solve(1/x) == []
    assert solve(x*(1 - 5/x)) == [5]
    assert solve(x + sqrt(x) - 2) == [1]
    assert solve(-(1 + x)/(2 + x)**2 + 1/(2 + x)) == []
    assert solve(-x**2 - 2*x + (x + 1)**2 - 1) == []
    assert solve((x/(x + 1) + 3)**(-2)) == []
    assert solve(x/sqrt(x**2 + 1),x) == [0]
    assert solve(exp(x) - y, x) == [log(y)]
    assert solve(exp(x)) == []
    assert solve(x**2 + x + sin(y)**2 + cos(y)**2 - 1, x) in [[0, -1], [-1, 0]]
    eq = 4*3**(5*x + 2) - 7
    ans = solve(eq, x)
    assert len(ans) == 5 and all(eq.subs(x, a).n(chop=True) == 0 for a in ans)
    assert solve(log(x**2) - y**2/exp(x), x, y) == [{y: -sqrt(exp(x)*log(x**2))},
                                                    {y: sqrt(exp(x)*log(x**2))}]
    assert solve(x**2*z**2 - z**2*y**2) == [{x: -y}, {x: y}]
    assert solve((x - 1)/(1 + 1/(x - 1))) == []
    assert solve(x**(y*z) - x, x) == [1]
    raises(NotImplementedError, 'solve(log(x) - exp(x), x)')

    # 2072
    assert solve(sqrt(x)) == solve(sqrt(x**3)) == [0]
    assert solve(sqrt(x - 1)) == [1]
    # 1363
    a = symbols('a')
    assert solve(-3*a/sqrt(x),x) == []
    # 1387
    assert solve(2*x/(x + 2) - 1,x) == [2]
    # 1397
    assert solve((x**2/(7 - x)).diff(x)) == [0, 14]
    # 1596
    f = Function('f')
    assert solve((3 - 5*x/f(x))*f(x), f(x)) == [5*x/3]
    # 1398
    assert solve(1/(5 + x)**(S(1)/5) - 9, x) == [-295244/S(59049)]

    assert solve(sqrt(x) + sqrt(sqrt(x)) - 4) == [-9*sqrt(17)/2 + 49*S.Half]
    assert solve(Poly(sqrt(exp(x)) + sqrt(exp(-x)) - 4)) == \
            [2*log(-sqrt(3) + 2), 2*log(sqrt(3) + 2)]
    assert solve(Poly(exp(x) + exp(-x) - 4)) == [log(-sqrt(3) + 2), log(sqrt(3) + 2)]
    assert solve(x**y + x**(2*y) - 1, x) == [(-S.Half + sqrt(5)/2)**(1/y), (-S.Half - sqrt(5)/2)**(1/y)]

    assert solve(exp(x/y)*exp(-z/y) - 2, y) == [(x - z)/log(2)]
    assert solve(x**z*y**z - 2, z) in [[log(2)/(log(x) + log(y))], [log(2)/(log(x*y))]]
    # if you do inversion too soon then multiple roots as for the following will
    # be missed, e.g. if exp(3*x) = exp(3) -> 3*x = 3
    E = S.Exp1
    assert solve(exp(3*x) - exp(3), x) == \
           [1, log(-E/2 - sqrt(3)*E*I/2), log(-E/2 + sqrt(3)*E*I/2)]

def test_issue_2098():
    x = Symbol('x', real=True)
    assert solve(x**2 + 1, x) == []
    n = Symbol('n', integer=True, positive=True)
    assert solve((n - 1)*(n + 2)*(2*n - 1), n) == [1]
    x = Symbol('x', positive=True)
    y = Symbol('y')
    assert solve([x + 5*y - 2, -3*x + 6*y - 15], x, y) == None # not {x: -3, y: 1} b/c x is positive
    # The solution following should not contain (-sqrt(2), sqrt(2))
    assert solve((x + y)*n - y**2 + 2, x, y) == [(sqrt(2), -sqrt(2))]
    y = Symbol('y', positive=True)
    # The solution following should not contain {y: -x*exp(x/2)}
    assert solve(x**2 - y**2/exp(x), x, y) == [{y: x*exp(x/2)}]
    x, y, z = symbols('x y z', positive=True)
    assert solve(z**2*x**2 - z**2*y**2/exp(x), x, y, z) == [{y: x*exp(x/2)}]

@XFAIL
def test_failing():
    # better Lambert detection is needed if the expression is expanded
    # this case has a double generator: (7**x, x); this will pass if the
    # x-terms are factored
    assert solve((2*(3*x+4)**5 - 6*7**(3*x+9)).expand(), x)

def test_checking():
    assert solve(x*(x - y/x),x, check=False) == [0, -sqrt(y), sqrt(y)]
    assert solve(x*(x - y/x),x, check=True) == [-sqrt(y), sqrt(y)]
    # {x: 0, y: 4} sets denominator to 0 in the following so system should return None
    assert solve((1/(1/x + 2), 1/(y - 3) - 1)) is None
    # 0 sets denominator of 1/x to zero so [] is returned
    assert solve(1/(1/x + 2)) == []

def test_issue_1572_1364_1368():
    assert solve((sqrt(x**2 - 1) - 2)) in ([sqrt(5), -sqrt(5)],
                                           [-sqrt(5), sqrt(5)])
    assert solve((2**exp(y**2/x) + 2)/(x**2 + 15), y) == (
        [-sqrt(x)*sqrt(log((log(2) + I*pi)/log(2))),
          sqrt(x)*sqrt(log((log(2) + I*pi)/log(2)))]
          )

    C1, C2 = symbols('C1 C2')
    f = Function('f')
    assert solve(C1 + C2/x**2 - exp(-f(x)), f(x)) == [log(x**2/(C1*x**2 + C2))]
    a = symbols('a')
    E = S.Exp1
    assert solve(1 - log(a + 4*x**2), x) in (
                                        [-sqrt(-a + E)/2, sqrt(-a + E)/2],
                                        [sqrt(-a + E)/2, -sqrt(-a + E)/2]
                                        )
    assert solve(log(a**(-3) - x**2)/a, x) in (
                            [-sqrt(-1 + a**(-3)), sqrt(-1 + a**(-3))],
                            [sqrt(-1 + a**(-3)), -sqrt(-1 + a**(-3))],)
    assert solve(1 - log(a + 4*x**2), x) in (
                                             [-sqrt(-a + E)/2, sqrt(-a + E)/2],
                                             [sqrt(-a + E)/2, -sqrt(-a + E)/2],)
    assert solve((a**2 + 1) * (sin(a*x) + cos(a*x)), x) == [-pi/(4*a), 3*pi/(4*a)]
    assert solve(3 - (sinh(a*x) + cosh(a*x)), x) == [2*atanh(S.Half)/a]
    assert solve(3-(sinh(a*x) + cosh(a*x)**2), x) == \
             [
             2*atanh(-1 + sqrt(2))/a,
             2*atanh(S(1)/2 + sqrt(5)/2)/a,
             2*atanh(-sqrt(2) - 1)/a,
             2*atanh(-sqrt(5)/2 + S(1)/2)/a
             ]
    assert solve(atan(x) - 1) == [tan(1)]

def test_issue_2033():
    r, t, z = symbols('r,t,z')
    assert solve([r - x**2 - y**2, tan(t) - y/x], [x, y]) == \
     [
     (-sqrt(r*sin(t)**2)/tan(t), -sqrt(r*sin(t)**2)),
     (sqrt(r*sin(t)**2)/tan(t), sqrt(r*sin(t)**2))]
    assert solve([exp(x) - sin(y), 1/y - 3], [x, y]) == \
        [(log(sin(S(1)/3)), S(1)/3)]
    assert solve([exp(x) - sin(y), 1/exp(y) - 3], [x, y]) == \
        [(log(-sin(log(3))), -log(3))]
    assert solve([exp(x) - sin(y), y**2 - 4], [x, y]) == \
        [(log(-sin(2)), -2), (log(sin(2)), 2)]
    eqs = [exp(x)**2 - sin(y) + z**2, 1/exp(y) - 3]
    assert solve(eqs) == \
        [
        {x: log(-sqrt(-z**2 - sin(log(3)))), y: -log(3)},
        {x: log(sqrt(-z**2 - sin(log(3)))), y: -log(3)}]
    assert solve(eqs, x, z) == \
        [
        {x: log(-sqrt(-z**2 + sin(y)))},
        {x: log(sqrt(-z**2 + sin(y)))}]
    assert solve(eqs, x, y) == \
        [
        (log(-sqrt(-z**2 - sin(log(3)))), -log(3)),
        (log(sqrt(-z**2 - sin(log(3)))), -log(3))]
    assert solve(eqs, y, z) == \
        [
        (-log(3), -sqrt(-exp(2*x) - sin(log(3)))),
        (-log(3), sqrt(-exp(2*x) - sin(log(3))))]
    eqs = [exp(x)**2 - sin(y) + z, 1/exp(y) - 3]
    assert solve(eqs) == \
        [
        {x: log(-sqrt(-z - sin(log(3)))), y: -log(3)},
        {x: log(sqrt(-z - sin(log(3)))), y: -log(3)}]
    assert solve(eqs, x, z) == \
        [
        {x: log(-sqrt(-z + sin(y)))},
        {x: log(sqrt(-z + sin(y)))}]
    assert solve(eqs, x, y) == \
        [
        (log(-sqrt(-z - sin(log(3)))), -log(3)),
        (log(sqrt(-z - sin(log(3)))), -log(3))]
    assert solve(eqs, z, y) == \
        [(-exp(2*x) - sin(log(3)), -log(3))]
    assert solve((sqrt(x**2 + y**2) - sqrt(10), x + y - 4)) == \
        [{x: 1, y: 3}, {x: 3, y: 1}]
    assert solve((sqrt(x**2 + y**2) - sqrt(10), x + y - 4), x, y) == \
        [(1, 3), (3, 1)]

@XFAIL
def test_issue_2236():
    """ This system can be solved in steps:
        >>> yy = solve(reqs[0],y)[0]
        >>> a00 = solve(reqs[1].subs(y,yy),a0)[0]
        >>> xx = solve(reqs[2].subs(((y,yy), (a0,a00))),x)
        >>> len(xx)
        2

        So there are two values for x, y and a0.
    """
    lam, a0, conc = symbols('lam a0 conc')
    eqs = [lam + 2*y - a0*(1 - x/2)*x - 0.005*x/2*x,
           a0*(1 - x/2)*x - 1*y - 0.743436700916726*y,
           x + y - conc]
    sym = [x, y, a0]
    reqs = [nsimplify(e, rational=True) for e in eqs]
    assert solve(reqs, sym) # doesn't fail

def test_issue_2668():
    assert solve([x**2 + y + 4], [x]) == [(-sqrt(-y - 4),), (sqrt(-y - 4),)]

def test_polysys():
    from sympy.abc import x, y
    assert solve([x**2 + 2/y - 2 , x + y - 3], [x, y]) == \
        [(1, 2), (1 + sqrt(5), 2 - sqrt(5)), (1 - sqrt(5), 2 + sqrt(5))]
    assert solve([x**2 + y - 2, x**2 + y]) is None
    # the ordering should be whatever the user requested
    assert solve([x**2 + y - 3, x - y - 4], (x, y)) != solve([x**2 + y - 3, x - y - 4], (y, x))

def test_unrad():
    from sympy.abc import x, y, a, b, c, d
    s = symbols('s', cls=Dummy)

    # checkers to deal with possibility of answer coming
    # back with a sign change (cf issue 2104)
    def check(rv, ans):
        rv, ans = list(rv), list(ans)
        rv[0] = rv[0].expand()
        ans[0] = ans[0].expand()
        return rv[0] in [ans[0], -ans[0]] and rv[1:] == ans[1:]
    def s_check(rv, ans):
        # get the dummy
        rv = list(rv)
        d = rv[0].atoms(Dummy)
        reps = zip(d, [s]*len(d))
        # replace s with this dummy
        rv = (rv[0].subs(reps).expand(), [(p[0].subs(reps), p[1].subs(reps))
                                   for p in rv[1]],
                                   [a.subs(reps) for a in rv[2]])
        ans = (ans[0].subs(reps).expand(), [(p[0].subs(reps), p[1].subs(reps))
                                   for p in ans[1]],
                                   [a.subs(reps) for a in ans[2]])
        return str(rv[0]) in [str(ans[0]), str(-ans[0])] and \
               str(rv[1:]) == str(ans[1:])

    assert check(unrad(sqrt(x)),
                   (x, [], []))
    assert check(unrad(sqrt(x) + 1),
                   (x - 1, [], []))
    assert s_check(unrad(sqrt(x) + x**Rational(1,3) + 2),
                   (2 + s**2 + s**3, [(s, x - s**6)], []))
    assert check(unrad(sqrt(x)*x**Rational(1, 3) + 2),
                   (x**5 - 64, [], []))
    assert check(unrad(sqrt(x) + (x + 1)**Rational(1,3)),
                   (x**3 - (x + 1)**2, [], []))
    assert check(unrad(sqrt(x) + sqrt(x + 1) + sqrt(2*x)),
                (-2*sqrt(2)*x - 2*x + 1, [], []))
    assert check(unrad(sqrt(x) + sqrt(x + 1) + 2),
               (16*x - 9, [], []))
    assert check(unrad(sqrt(x) + sqrt(x + 1) + sqrt(1 - x)),
               (-4*x + 5*x**2, [], []))
    assert check(unrad(a*sqrt(x) + b*sqrt(x) + c*sqrt(y) + d*sqrt(y)),
                ((a*sqrt(x) + b*sqrt(x))**2 - (c*sqrt(y) + d*sqrt(y))**2, [], []))
    assert check(unrad(sqrt(x) + sqrt(1 - x)),
                (2*x - 1, [], []))
    assert check(unrad(sqrt(x) + sqrt(1 - x) - 3),
                (36*x + (2*x - 10)**2 - 36, [], []))
    assert check(unrad(sqrt(x) + sqrt(1 - x) + sqrt(2 + x)),
                (-5*x**2 + 2*x - 1, [], []))
    assert check(unrad(sqrt(x) + sqrt(1 - x) + sqrt(2 + x) - 3),
        (-25*x**4 - 376*x**3 - 1256*x**2 + 2272*x - 784, [], []))
    assert check(unrad(sqrt(x) + sqrt(1 - x) + sqrt(2 + x) - sqrt(1 - 2*x)),
                (-41*x**4 - 40*x**3 - 232*x**2 + 160*x - 16, [], []))
    assert check(unrad(sqrt(x) + sqrt(x + 1)), (S(1), [], []))

    eq = sqrt(x) + sqrt(x + 1) + sqrt(1 - sqrt(x))
    assert check(unrad(eq),
               (16*x**3 - 9*x**2, [], []))
    assert solve(eq, check=False) == [0, S(9)/16]
    assert solve(eq) == []
    # but this one really does have those solutions
    assert solve(sqrt(x) - sqrt(x + 1) + sqrt(1 - sqrt(x))) == [0, S(9)/16]
    ans = solve(sqrt(x) + sqrt(x + 1) + sqrt(1 - x) - 6*sqrt(5)/5)
    assert len(ans) == 2 and S(4)/5 in ans
    ans = solve(sqrt(x) + sqrt(x + 1) - \
                 sqrt(1 - x) - sqrt(2 + x))
    assert len(ans) == 1 and NS(ans[0])[:4] == '0.73'
    # the fence optimization problem
    # http://code.google.com/p/sympy/issues/detail?id=1694#c159
    x, y, a, F = symbols('x y a F')
    eq = F - (2*x + 2*y + sqrt(x**2 + y**2))
    X = solve(eq, x, hint='minimal')[0]
    Y = solve((x*y).subs(x, X).diff(y), y, simplify=False, minimal=True)
    ans = 2*F/7 - sqrt(2)*F/14
    assert any((a - ans).expand().is_zero for a in Y)

    raises(ValueError, 'unrad(sqrt(x) + sqrt(x+1) + sqrt(1-sqrt(x)) + 3)')
    raises(ValueError, 'unrad(sqrt(x) + (x+1)**Rational(1,3) + 2*sqrt(y))')
    # same as last but consider only y
    assert check(unrad(sqrt(x) + (x+1)**Rational(1,3) + 2*sqrt(y), y),
           (4*y - (sqrt(x) + (x + 1)**(S(1)/3))**2, [], []))
    assert check(unrad(sqrt(x/(1 - x)) + (x+1)**Rational(1,3)),
                (x**3/(-x + 1)**3 - (x + 1)**2, [], [(-x + 1)**3]))
    # same as last but consider only y; no y-containing denominators now
    assert s_check(unrad(sqrt(x/(1 - x)) + 2*sqrt(y), y),
           (x/(-x + 1) - 4*y, [], []))
    assert check(unrad(sqrt(x)*sqrt(1-x) + 2, x),
           (x*(-x + 1) - 4, [], []))

    # http://tutorial.math.lamar.edu/Classes/Alg/SolveRadicalEqns.aspx#Solve_Rad_Ex2_a
    assert solve(Eq(x, sqrt(x + 6))) == [3]
    assert solve(Eq(x + sqrt(x - 4), 4)) == [4]
    assert solve(Eq(1, x + sqrt(2*x - 3))) == []
    assert solve(Eq(sqrt(5*x + 6) - 2, x)) == [-1, 2]
    assert solve(Eq(sqrt(2*x - 1) - sqrt(x - 4), 2)) == [5, 13]
    assert solve(Eq(sqrt(x + 7) + 2, sqrt(3 - x))) == [-6]
    # http://www.purplemath.com/modules/solverad.htm
    assert solve((2*x-5)**Rational(1,3)-3) == [16]
    assert solve((x**3-3*x**2)**Rational(1,3)+1-x) == []
    assert solve(x+1-(x**4+4*x**3-x)**Rational(1,4)) == [-S(1)/2, -S(1)/3]
    assert solve(sqrt(2*x**2-7)-(3-x)) == [-8, 2]
    assert solve(sqrt(2*x+9)-sqrt(x+1)-sqrt(x+4)) == [0]
    assert solve(sqrt(x+4)+sqrt(2*x-1)-3*sqrt(x-1)) == [5]
    assert solve(sqrt(x)*sqrt(x-7)-12) == [16]
    assert solve(sqrt(x-3)+sqrt(x)-3) == [4]
    assert solve(sqrt(9*x**2+4)-(3*x+2)) == [0]
    assert solve(sqrt(x)-2-5) == [49]
    assert solve(sqrt(x-3)-sqrt(x)-3) == []
    assert solve(sqrt(x-1)-x+7) == [10]
    assert solve(sqrt(x-2)-5) == [27]

@XFAIL
def test_unrad1():
    # unrad not implemented
    assert solve(sqrt(x) - sqrt(x - 1) + sqrt(sqrt(x))) is not None
@XFAIL
def test_unrad3():
    # unrad not implemented
    assert solve(sqrt(17*x-sqrt(x**2-5))-7) == [3]
@XFAIL
def test_unrad2():
    assert solve((x**3-3*x**2)**Rational(1,3)+1-x) == [S(1)/3] # b/c (-8/27)**(1/3) -> 2*(-1)**(1/3)/3 instead of -2/3

@XFAIL
def test_multivariate():
    from sympy.abc import x
    assert solve((x**2 - 2*x + 1).subs(x, log(x) + 3*x)) == [LambertW(3*S.Exp1)/3]
    assert solve((x**2 - 2*x + 1).subs(x, (log(x) + 3*x)**2 - 1)) == \
          [LambertW(3*exp(-sqrt(2)))/3, LambertW(3*exp(sqrt(2)))/3]
    assert solve((x**2 - 2*x - 2).subs(x, log(x) + 3*x)) == \
          [LambertW(3*exp(1 - sqrt(3)))/3, LambertW(3*exp(1 + sqrt(3)))/3]
    assert solve(x*log(x) + 3*x + 1, x) == [exp(-3 + LambertW(-exp(3)))]
    # symmetry
    assert solve(3*sin(x) - x*sin(3), x) == [3]

def test__invert():
    assert _invert(x - 2) == (2, x)
    assert _invert(2) == (2, 0)
