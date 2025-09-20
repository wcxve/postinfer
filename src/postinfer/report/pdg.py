import math
import warnings


def exp_of_first_sigfig(value: float) -> int:
    """Get the exponent of the first significant figure of a number.

    Parameters
    ----------
    value : float
        The input number.

    Returns
    -------
    int
        The exponent of the first significant figure.
    """
    a = abs(float(value))
    if a == 0.0 or not math.isfinite(a):
        return 0
    return math.floor(math.log10(a))


def round_err_pdg(err: float) -> tuple[float, int]:
    """Round the error based on PDG convention [1]_.

    Parameters
    ----------
    err : float
        The error value.

    Returns
    -------
    float, int
        The `err` to display, and the exponent of last precise digit.

    References
    ----------
    .. [1] https://pdg.lbl.gov/2024/reviews/rpp2024-rev-rpp-intro.pdf
    """
    exp10 = exp_of_first_sigfig(err)
    if exp10 >= 0:
        digits = int(err / 10.0 ** (exp10 - 2))
    else:
        digits = int(err / 10.0 ** (exp10 + 1) * 1000)

    # PDG Rules
    if 0 < digits <= 354:
        precision = 1
    else:
        precision = 0

    if digits >= 950:
        err = 10.0 ** (exp10 + 1)

    return err, exp10 - precision


def round_pdg(
    value: float,
    err: float,
    err2: float | None = None,
    exp10: int | None = None,
    no_sci_nota_exp10_range: tuple[int, int] = (-1, 2),
    force_asymmetric: bool = False,
) -> str:
    """Round the value and error based on PDG convention [1]_.

    The PDG convention states that::

        If the three highest order digits of the error lie between 100
        and 354, we round to two significant digits. If they lie between
        355 and 949, we round to one significant digit. Finally, if they
        lie between 950 and 999, we round up to 1000 and keep two
        significant digits.

        In cases where there are asymmetric errors, if these errors differ
        by less than 10 percent of the average of the two errors, the average
        of the two errors is instead used as a symmetric error in the
        displayed result and the rounding is determined by this average.
        Otherwise, the narrower of the two asymmetric errors is used to
        determine the rounding on both.

    Parameters
    ----------
    value : float
        The value to be rounded.
    err : float
        The error value.
    err2 : float, optional
        If provided, the `err` is considered as the lower error,
        and `err2` as the upper error.
    exp10 : int, optional
        The exponent to display. If not provided, it will be determined based
        on the value and error.
    no_sci_nota_exp10_range : tuple of int, optional
        If the exponent of the last digit of errors is in this range,
        then the result will not be formatted in scientific notation.
        If `exp10` is provided, it will be ignored.
        The default is ``(-1, 2)``.
    force_asymmetric : bool, optional
        If ``True``, the asymmetric errors will be formatted as asymmetric,
        regardless of the difference between the two errors.
        The default is ``False``.

    Returns
    -------
    str
        The rounded value and error formatted in LaTeX.

    References
    ----------
    .. [1] https://pdg.lbl.gov/2024/reviews/rpp2024-rev-rpp-intro.pdf
    """
    value = float(value)
    err = float(err)
    if err2 is None:
        if err < 0.0:
            raise ValueError('error must be positive')
        err, precision_exp10 = round_err_pdg(err)
    else:
        err2 = float(err2)
        if err > 0.0:
            raise ValueError('lower error must be negative')
        if err2 < 0.0:
            raise ValueError('upper error must be positive')

        err_abs = abs(err)

        if not force_asymmetric:
            err_diff = abs(err_abs - err2)
            err_avg = 0.5 * (err_abs + err2)

            if err_diff <= 0.1 * err_avg:
                return round_pdg(
                    value,
                    err_avg,
                    exp10=exp10,
                    no_sci_nota_exp10_range=no_sci_nota_exp10_range,
                )

        err, precision_exp10 = round_err_pdg(err_abs)
        err2_ = err2
        err2, precision2_exp10 = round_err_pdg(err2)
        if err2_ < err_abs:
            precision_exp10 = precision2_exp10

    if exp10 is None:
        exp10 = max(exp_of_first_sigfig(value), precision_exp10)
        if no_sci_nota_exp10_range[0] <= exp10 <= no_sci_nota_exp10_range[1]:
            # Only set exp10=0 if it doesn't violate the precision constraint
            exp10 = 0 if precision_exp10 <= 0 else exp10
    else:
        if exp10 < precision_exp10:
            warnings.warn(
                f'for {value=}, {err=} and {err2=}, {exp10=} is clipped to '
                f'the error precision ({precision_exp10})',
                Warning,
            )
        exp10 = max(int(exp10), precision_exp10)

    f = 10.0**-exp10 if exp10 >= 0 else 1.0 / 10.0**exp10
    p = exp10 - precision_exp10
    value_str = f'{value * f:.{p}f}'
    err_str = f'{err * f:.{p}f}'
    if err2 is None:
        s = rf'{value_str} \pm {err_str}'
        if exp10 != 0.0:
            s = rf'\left({s}\right) \times 10^{{{exp10}}}'
    else:
        err2_str = f'{err2 * f:.{p}f}'
        s = f'{value}_{{-{err_str}}}^{{+{err2_str}}}'
        if exp10 != 0.0:
            s = rf'{s} \times 10^{{{exp10}}}'
    return f'${s}$'
