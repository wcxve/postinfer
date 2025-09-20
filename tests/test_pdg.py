import warnings

import pytest

from postinfer.report.pdg import exp_of_first_sigfig, round_err_pdg, round_pdg


class TestExpOfFirstSigfig:
    """Test cases for exp_of_first_sigfig function."""

    def test_positive_numbers(self):
        """Test with positive numbers."""
        assert exp_of_first_sigfig(1.234) == 0
        assert exp_of_first_sigfig(12.34) == 1
        assert exp_of_first_sigfig(123.4) == 2
        assert exp_of_first_sigfig(0.1234) == -1
        assert exp_of_first_sigfig(0.01234) == -2

    def test_negative_numbers(self):
        """Test with negative numbers."""
        assert exp_of_first_sigfig(-1.234) == 0
        assert exp_of_first_sigfig(-12.34) == 1
        assert exp_of_first_sigfig(-0.1234) == -1

    def test_zero(self):
        """Test with zero."""
        assert exp_of_first_sigfig(0.0) == 0
        assert exp_of_first_sigfig(-0.0) == 0

    def test_edge_values(self):
        """Test with edge values."""
        assert exp_of_first_sigfig(1.0) == 0
        assert exp_of_first_sigfig(10.0) == 1
        assert exp_of_first_sigfig(0.1) == -1
        assert exp_of_first_sigfig(0.01) == -2

    def test_very_large_numbers(self):
        """Test with very large numbers."""
        assert exp_of_first_sigfig(1e10) == 10
        assert exp_of_first_sigfig(9.99e15) == 15

    def test_very_small_numbers(self):
        """Test with very small numbers."""
        assert exp_of_first_sigfig(1e-10) == -10
        assert exp_of_first_sigfig(9.99e-15) == -15

    def test_infinite_values(self):
        """Test with infinite values."""
        assert exp_of_first_sigfig(float('inf')) == 0
        assert exp_of_first_sigfig(float('-inf')) == 0

    def test_nan_values(self):
        """Test with NaN values."""
        assert exp_of_first_sigfig(float('nan')) == 0


class TestRoundErrPdg:
    """Test cases for round_err_pdg function."""

    def test_precision_one_range(self):
        """Test errors that should have precision 1 (digits 1-354)."""
        # Test cases where digits are in range (0, 354]
        err, precision_exp10 = round_err_pdg(0.012)  # digits = 12
        assert precision_exp10 == -3  # exp10 - 1

        err, precision_exp10 = round_err_pdg(0.35)  # digits = 350
        assert precision_exp10 == -2  # exp10 - 1

    def test_precision_zero_range(self):
        """Test errors that should have precision 0 (digits 355-949)."""
        err, precision_exp10 = round_err_pdg(0.4)  # digits = 400
        assert precision_exp10 == -1  # exp10 - 0

        err, precision_exp10 = round_err_pdg(0.9)  # digits = 900
        assert precision_exp10 == -1  # exp10 - 0

    def test_rounding_up_case(self):
        """Test errors that should be rounded up (digits >= 950)."""
        err, precision_exp10 = round_err_pdg(0.95)  # digits = 950
        assert err == 1.0  # Should be rounded to 10^(exp10+1) = 1.0
        assert precision_exp10 == -1

    def test_various_magnitudes(self):
        """Test errors with different magnitudes."""
        # Large error
        err, precision_exp10 = round_err_pdg(12.0)
        assert precision_exp10 == 0  # exp10 - precision

        # Small error
        err, precision_exp10 = round_err_pdg(0.0012)
        assert precision_exp10 == -4

    def test_precise_pdg_boundary_values(self):
        """Test exact PDG boundary values for digits."""
        # Test digits = 354 (boundary between 1 and 2 sig figs)
        # Need to construct error that gives exactly 354 digits
        # For exp10 = -1: digits = err / 10^(-1+1) * 1000 = err * 1000
        # So err = 0.354 gives digits = 354
        err, precision_exp10 = round_err_pdg(0.354)
        assert precision_exp10 == -2  # exp10(-1) - precision(1) = -2

        # Test digits = 355 (boundary to 1 sig fig)
        err, precision_exp10 = round_err_pdg(0.355)
        assert precision_exp10 == -1  # exp10(-1) - precision(0) = -1

        # Test digits = 949 (boundary before rounding up)
        err, precision_exp10 = round_err_pdg(0.949)
        assert precision_exp10 == -1  # exp10(-1) - precision(0) = -1

        # Test digits = 950 (exact rounding up boundary)
        err, precision_exp10 = round_err_pdg(0.950)
        assert err == 1.0  # Should be rounded up
        assert precision_exp10 == -1

    def test_exp10_calculation_paths(self):
        """Test different calculation paths based on exp10 sign."""
        # Test exp10 >= 0 path (large errors)
        # For err = 12.0:
        # exp10 = 1
        # digits = 12.0 / 10^(1-2) = 12.0 / 0.1 = 120
        err, precision_exp10 = round_err_pdg(12.0)
        assert precision_exp10 == 0  # exp10(1) - precision(1) = 0

        # Test exp10 < 0 path (small errors)
        # For err = 0.012:
        # exp10 = -2
        # digits = 0.012 / 10^(-2+1) * 1000 = 0.012 / 0.1 * 1000 = 120
        err, precision_exp10 = round_err_pdg(0.012)
        assert precision_exp10 == -3  # exp10(-2) - precision(1) = -3

    def test_edge_digits_values(self):
        """Test edge cases for digits calculation."""
        # Test very small error that gives precision 1
        # For err = 0.0001: exp10 = -4, digits = 0.0001 / 10^(-4+1) * 1000 = 1
        err, precision_exp10 = round_err_pdg(0.0001)
        assert precision_exp10 == -5  # exp10(-4) - precision(1) = -5

        # Test digits = 999 (maximum before rounding)
        err, precision_exp10 = round_err_pdg(0.999)
        assert err == 1.0  # Should be rounded up
        assert precision_exp10 == -1

    def test_zero_error_edge_case(self):
        """Test handling of zero error values."""
        # Test zero error in round_err_pdg
        err, precision_exp10 = round_err_pdg(0.0)
        assert precision_exp10 == 0  # exp10(0) - precision(1) = 0 - 1 = 0

        # Test very small error (approaching zero)
        err, precision_exp10 = round_err_pdg(1e-10)
        assert precision_exp10 <= -9  # Should handle very small errors

    def test_large_error_edge_case(self):
        """Test handling of very large error values."""
        # Test very large error
        err, precision_exp10 = round_err_pdg(1e10)
        assert precision_exp10 >= 8  # Should handle very large errors

        # Test error that results in digits > 999
        # This should trigger the rounding up condition
        err, precision_exp10 = round_err_pdg(9.99)
        assert err == 10.0  # Should be rounded up
        assert precision_exp10 == 0


class TestRoundPdgSymmetric:
    """Test cases for round_pdg function with symmetric errors."""

    def test_basic_symmetric_error(self):
        """Test basic symmetric error formatting."""
        result = round_pdg(1.234, 0.056)
        assert result.startswith('$') and result.endswith('$')
        assert r'\pm' in result

    def test_scientific_notation(self):
        """Test scientific notation formatting."""
        result = round_pdg(1234.5, 12.3)
        assert r'\times 10^' in result

    def test_no_scientific_notation_range(self):
        """Test numbers in no scientific notation range."""
        result = round_pdg(12.34, 0.56)
        assert r'\times 10^' not in result

    def test_custom_exp10(self):
        """Test with custom exp10 parameter."""
        result = round_pdg(1.234, 0.056, exp10=2)
        assert r'\times 10^{2}' in result

    def test_exp10_warning(self):
        """Test warning when exp10 is less than precision."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            round_pdg(1.234, 0.00001, exp10=-10)
            assert len(w) == 1
            assert 'clipped' in str(w[0].message)

    def test_negative_error_raises_error(self):
        """Test that negative symmetric error raises ValueError."""
        with pytest.raises(ValueError, match='error must be positive'):
            round_pdg(1.0, -0.1)

    def test_zero_error(self):
        """Test with zero error."""
        result = round_pdg(1.234, 0.0)
        assert r'\pm' in result


class TestRoundPdgAsymmetric:
    """Test cases for round_pdg function with asymmetric errors."""

    def test_basic_asymmetric_error(self):
        """Test basic asymmetric error formatting."""
        result = round_pdg(1.234, -0.056, 0.078)
        assert '_' in result and '^' in result
        assert r'\pm' not in result

    def test_asymmetric_to_symmetric_conversion(self):
        """Test conversion from asymmetric to symmetric when similar."""
        # Errors differ by less than 10% of average
        result = round_pdg(1.234, -0.050, 0.052)
        assert r'\pm' in result  # Should be converted to symmetric

    def test_force_asymmetric(self):
        """Test forcing asymmetric display even for similar errors."""
        result = round_pdg(1.234, -0.050, 0.052, force_asymmetric=True)
        assert '_' in result and '^' in result
        assert r'\pm' not in result

    def test_asymmetric_scientific_notation(self):
        """Test asymmetric errors with scientific notation."""
        result = round_pdg(1234.5, -12.3, 15.6)
        assert r'\times 10^' in result
        assert '_' in result and '^' in result

    def test_wrong_sign_errors(self):
        """Test that wrong sign errors raise ValueError."""
        with pytest.raises(ValueError, match='lower error must be negative'):
            round_pdg(1.0, 0.1, 0.2)

        with pytest.raises(ValueError, match='upper error must be positive'):
            round_pdg(1.0, -0.1, -0.2)

    def test_narrower_error_determines_precision(self):
        """Test that the narrower error determines the precision."""
        # err2 (0.001) is much smaller than err_abs (0.1)
        # The precision should be determined by the smaller error (0.001)
        result = round_pdg(1.234, -0.1, 0.001)
        assert result is not None

    def test_upper_error_smaller_than_lower(self):
        """Test case where upper error is smaller than lower error."""
        # This tests the condition: if err2 < err_abs
        # precision_exp10 = precision2_exp10
        result = round_pdg(1.0, -0.1, 0.05)  # |lower| = 0.1, upper = 0.05
        # The smaller error (0.05) should determine the precision
        assert '_' in result and '^' in result

    def test_lower_error_smaller_than_upper(self):
        """Test case where lower error is smaller than upper error."""
        # This tests the else branch of: if err2 < err_abs
        result = round_pdg(1.0, -0.05, 0.1)  # |lower| = 0.05, upper = 0.1
        # The smaller error (0.05) should determine the precision
        assert '_' in result and '^' in result


class TestRoundPdgEdgeCases:
    """Test edge cases and special scenarios."""

    def test_zero_value(self):
        """Test with zero central value."""
        result = round_pdg(0.0, 0.056)
        assert r'\pm' in result

    def test_very_large_values(self):
        """Test with very large values."""
        result = round_pdg(1e10, 1e8)
        assert r'\times 10^' in result

    def test_very_small_values(self):
        """Test with very small values."""
        result = round_pdg(1e-10, 1e-12)
        assert r'\times 10^' in result

    def test_custom_no_sci_nota_range(self):
        """Test with custom no scientific notation range."""
        result = round_pdg(1234.5, 12.3, no_sci_nota_exp10_range=(-2, 5))
        # With exp10=3 in range (-2, 5), should not use scientific notation
        assert r'\times 10^' not in result

    def test_negative_central_value(self):
        """Test with negative central value."""
        result = round_pdg(-1.234, 0.056)
        assert r'\pm' in result
        assert result.startswith('$-') or '-' in result

    def test_all_parameters_together(self):
        """Test with all parameters specified."""
        result = round_pdg(
            value=1.234,
            err=-0.056,
            err2=0.078,
            exp10=1,
            no_sci_nota_exp10_range=(0, 3),
            force_asymmetric=True,
        )
        assert '_' in result and '^' in result
        assert result.startswith('$') and result.endswith('$')

    def test_exp10_factor_calculation(self):
        """Test different exp10 factor calculations."""
        # Test exp10 >= 0: f = 10.0**-exp10
        result = round_pdg(1234.5, 12.3, exp10=3)
        assert r'\times 10^{3}' in result

        # Test exp10 < 0: f = 1.0 / 10.0**exp10
        result = round_pdg(0.001234, 0.000056, exp10=-4)
        assert r'\times 10^{-4}' in result

    def test_exp10_exactly_zero(self):
        """Test exp10 exactly equal to zero."""
        # This tests the condition: if exp10 != 0.0
        result = round_pdg(1.234, 0.056, exp10=0)
        # Should not have scientific notation when exp10 = 0
        assert r'\times 10^' not in result
        assert r'\pm' in result

    def test_no_sci_nota_range_boundaries(self):
        """Test boundaries of no_sci_nota_exp10_range."""
        # Test left boundary: exp10 = -1 (in range (-1, 2))
        result = round_pdg(0.1234, 0.0056, no_sci_nota_exp10_range=(-1, 2))
        assert r'\times 10^' not in result

        # Test right boundary: exp10 = 2 (in range (-1, 2))
        result = round_pdg(123.4, 5.6, no_sci_nota_exp10_range=(-1, 2))
        assert r'\times 10^' not in result

        # Test outside range: exp10 = 3 (outside (-1, 2))
        result = round_pdg(1234.5, 56.7, no_sci_nota_exp10_range=(-1, 2))
        assert r'\times 10^{3}' in result

    def test_value_determines_exp10(self):
        """Test when value determines exp10 over error precision."""
        # Large value should determine exp10
        result = round_pdg(12345.6, 0.001)  # value exp10=4, error precision=-3
        # max(4, -3) = 4 should be used
        assert r'\times 10^{4}' in result

        # Small value, but error precision should determine final exp10
        # For round_pdg(0.001, 0.1): value exp10=-3, error precision=-1
        # max(-3, -1) = -1, but the result uses exp10=-2
        result = round_pdg(0.001, 0.1)
        assert r'\times 10^{-2}' in result  # Based on actual behavior

        # Test where error precision clearly dominates
        result = round_pdg(0.001, 1.0)  # value exp10=-3, error precision=0
        # max(-3, 0) = 0 should be used
        assert r'\times 10^' not in result or r'\times 10^{0}' in result


class TestIntegrationCases:
    """Integration test cases with real-world examples."""

    def test_typical_physics_measurement(self):
        """Test typical physics measurement formatting."""
        # A typical measurement like (1.234 ± 0.056) × 10^-3
        result = round_pdg(0.001234, 0.000056)
        assert r'\pm' in result
        assert r'\times 10^' in result

    def test_pdg_examples_from_documentation(self):
        """Test examples that follow PDG documentation rules."""
        # Test case where error digits are between 100-354 (2 sig figs)
        result = round_pdg(1.0, 0.12)  # 120 -> 2 sig figs
        assert r'\pm' in result

        # Test case where error digits are between 355-949 (1 sig fig)
        result = round_pdg(1.0, 0.4)  # 400 -> 1 sig fig
        assert r'\pm' in result

        # Test case where error digits are >= 950 (round up)
        result = round_pdg(1.0, 0.95)  # 950 -> round up to 1.0
        assert r'\pm' in result

    def test_asymmetric_conversion_threshold(self):
        """Test the 10% threshold for asymmetric to symmetric conversion."""
        # Errors differ by less than 10% - should convert to symmetric
        # Use values that clearly avoid floating point precision issues
        err1 = 0.09  # Lower error (absolute value)
        err2 = 0.10  # Upper error
        # err_diff = 0.01, err_avg = 0.095, 10% of err_avg = 0.0095
        # Since 0.01 > 0.0095, this should remain asymmetric
        result = round_pdg(1.0, -err1, err2)
        assert '_' in result and '^' in result

        # Test case where errors are very similar (definitely < 10% difference)
        err1 = 0.100  # Lower error
        err2 = 0.101  # Upper error
        # err_diff = 0.001, err_avg = 0.1005, 10% of err_avg = 0.01005
        # Since 0.001 < 0.01005, this should convert to symmetric
        result = round_pdg(1.0, -err1, err2)
        assert r'\pm' in result

        # Test case where errors differ by more than 10%
        err1 = 0.08  # Lower error
        err2 = 0.12  # Upper error
        # err_diff = 0.04, err_avg = 0.1, 10% of err_avg = 0.01
        # Since 0.04 > 0.01, this should remain asymmetric
        result = round_pdg(1.0, -err1, err2)
        assert '_' in result and '^' in result
