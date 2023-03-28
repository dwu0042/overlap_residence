import overlap_residence as ov

def test_single_overlap_check():
    interval_1 = ov.Interval(3.0, 8.0)
    interval_2 = ov.Interval(5.0, 10.0)

    assert ov.overlap_time(interval_1, interval_2) == 3.0


def test_residence_data_basic():
    data = [
        ('A', '_Z', 0, 6),
        ('B', '_Z', 4, 9),
        ('A', '_Y', 6, 10),
        ('C', '_Y', 8, 12),
    ]

    rsdt = ov.compute_shared_residence_times(data)
    print(rsdt)

    assert True