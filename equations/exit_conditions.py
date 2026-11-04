# The three channels, as exit_reason names them; read by the collector and the tests.
EXIT_CAUSES = ("bankruptcy", "share", "non-renewal")


def exit_reason(
    net_worth: float,
    share: float,
    min_share: float,
    non_renewal: bool,
    has_capacity: bool,
) -> str | None:
    """Three channels, the same for both types: bankruptcy (NW < 0), a share below f_min,
    and non-renewal (the last plant retired and is not rebuilt)."""
    if net_worth < 0.0:
        return "bankruptcy"
    if non_renewal or not has_capacity:
        return "non-renewal"
    if share < min_share:
        return "share"
    return None
