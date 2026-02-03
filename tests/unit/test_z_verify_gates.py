
def test_intentional_fail():
    """
    This test is designed to fail to verify shipit quality gates.
    We need enough content to bypass the 'minor change' detection (<10 lines).
    So here is some filler text to ensure we are over the limit.
    Line 6
    Line 7
    Line 8
    Line 9
    Line 10
    Line 11
    Line 12
    """
    assert False, "Quality Gate Verification: This test SHOULD fail."
