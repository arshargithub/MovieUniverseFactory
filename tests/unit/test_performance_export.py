from movie_factory.performance_export import _reproducibility_text


def test_reproduction_guide_covers_controls_assets_and_limitations():
    summary={"run_path":"runs/3d04/accepted"}
    control={"run_path":"runs/3d04-controls/control-run"}
    guide=_reproducibility_text(summary,control)

    assert "execution-source/" in guide and "control-source/" in guide
    assert "review/index-original-broken.html" in guide
    assert "assets/admitted-staging/. source/.runtime/assets/3d-03/staged-v1/" in guide
    assert "performance_scene_controls" in guide
    assert "in-place treadmill run" in guide
    assert "human review time was not recorded" in guide
