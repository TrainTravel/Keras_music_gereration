from neurotune.theory import build_scale, parse_note, snap_to_scale


def test_parse_note():
    assert parse_note("C3") == 48
    assert parse_note("A4") == 69
    assert parse_note("F#2") == 42
    assert parse_note("Bb3") == 58


def test_build_scale_pentatonic():
    scale = build_scale(parse_note("C3"), "major_pentatonic", 1)
    assert scale == [48, 50, 52, 55, 57, 60]


def test_snap_to_scale():
    scale = build_scale(parse_note("C3"), "major_pentatonic", 1)
    assert snap_to_scale(49, scale) in (48, 50)
    assert all(snap_to_scale(p, scale) in scale for p in range(40, 70))
