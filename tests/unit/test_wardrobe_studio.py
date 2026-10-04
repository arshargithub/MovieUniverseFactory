import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('wardrobe_studio',Path(__file__).resolve().parents[2]/'src/movie_factory/adapters/blender/wardrobe_studio.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.mark.parametrize('job',[None,{}, {'operation':'exec'}, {'operation':'preview01','code':'x'}, {'operation':'preview01','path':'/tmp'}])
def test_enum_only(job):
    with pytest.raises(ValueError):module.validate(job)

def test_pin_and_no_overwrite(monkeypatch,tmp_path):
    source=tmp_path/'input.blend';source.touch()
    monkeypatch.setattr(module,'SOURCE',source);monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.SOURCE_SHA)
    out=module.validate({'operation':'preview01'});out.mkdir()
    with pytest.raises(ValueError,match='overwrite'):module.validate({'operation':'preview01'})
    monkeypatch.setattr(module,'digest',lambda p:'bad')
    with pytest.raises(ValueError,match='Pinned'):module.validate({'operation':'preview02'})

def test_local_fold_field():
    assert module.smoothstep(-1)==0 and module.smoothstep(2)==1
    assert module.smoothstep(.5)==pytest.approx(.5)
    assert all(0<=module.wrinkle(z/20,1.2)<=1 for z in range(-250,30))

def test_articulated_torso_support():
    for z in range(-8,2):
        weights=module.torso_weights(z)
        assert all(0<=v<=1 for v in weights.values())
        assert sum(weights.values())==pytest.approx(1)
    assert module.torso_weights(-2)['chest']==1
    assert module.torso_weights(-6)['pelvis']==1
    assert module.torso_weights(-4.8)['spine']==1

def test_tailoring_pressure_is_local():
    assert module.compression_weight(0)==1
    assert module.compression_weight(.32)==0
    assert module.compression_weight(1)==0
    assert 0<module.compression_weight(.15)<1

def test_material_mutation_not_in_transform_helper():
    import inspect
    assert 'augment' not in inspect.getsource(module.torso_matrix)
    assert 'augment' in inspect.getsource(module.make_materials)

def test_neutral_cloth_support_includes_both_actual_sleeves():
    import inspect
    source=inspect.getsource(module.settle_scarf)
    assert 'MF_171_fitted_sleeve_L_173_visible' in source
    assert 'MF_171_fitted_sleeve_R_173_visible' in source

def test_scarf_dressing_preserves_settled_crown():
    assert module.fall_wrap_weight(1)==0
    assert module.fall_wrap_weight(-1.45)==0
    assert module.fall_wrap_weight(-2.85)==pytest.approx(1)
    assert 0<module.fall_wrap_weight(-2)<1

def test_tuck_destinations_stay_inside_wrap_not_on_free_hem():
    for x in (-9,-2,0,2,9):
        for row in (-10,0,20,40,90):
            i,j=module.wrap_tuck_indices(x,-1.3,row)
            assert 12<=i<=68 and 12<=j<=22
    assert module.wrap_tuck_indices(-1,-1.3,20)[0]<40
    assert module.wrap_tuck_indices(1,-1.3,20)[0]>40

def test_wrap_return_starts_below_head_not_after_chest_opening():
    assert module.wrap_tuck_weight(-1.6)==0
    assert module.wrap_tuck_weight(-2.2)==pytest.approx(1)
    assert module.wrap_tuck_weight(0)==0
    assert 0<module.wrap_tuck_weight(-1.9)<1

def test_dressing_tucks_against_final_pressured_layer():
    import inspect
    source=inspect.getsource(module.pose_wardrobe)
    assert source.index('compress_cloth')<source.index('tuck_scarf_ends')<source.index('leather_paths')
    assert 'reference[vertex.index].vector' in inspect.getsource(module.tuck_scarf_ends)
    assert 'single_surface_mesh(scarf)' in inspect.getsource(module.tuck_scarf_ends)
    assert "mod.type=='SUBSURF'" in inspect.getsource(module.tuck_scarf_ends)
    assert 'destination=grid_sample(wrap_points,i,j)' in inspect.getsource(module.tuck_scarf_ends)
    assert 'groom=tree_for' in inspect.getsource(module.tuck_scarf_ends)

def test_grid_interpolation_is_continuous():
    points=[float(i*10+j) for i in range(81) for j in range(33)]
    assert module.grid_sample(points,20.25,14.5)==pytest.approx(217.)

def test_single_sheet_long_and_short_returns():
    assert module.shawl_return(0,0)==(80,32,1)
    assert module.shawl_return(.30,1)==(0,0,1)
    assert module.shawl_return(.70,0)==(80,32,-1)
    assert module.shawl_return(1,1)==(60,0,-1)

def test_shawl_blend_preserves_crown_and_continuous_tails():
    assert module.shawl_blend(.5)==0
    assert module.shawl_blend(.40)==0
    assert module.shawl_blend(.60)==0
    assert module.shawl_blend(.30)==1
    assert module.shawl_blend(.70)==pytest.approx(1)
    assert module.shawl_blend(.35)==pytest.approx(.5)

def test_major_folds_are_bounded_and_unequal():
    samples=[module.shawl_relief(s/10,v/40) for s in range(11) for v in range(41)]
    assert min(samples)>=0 and max(samples)<.25
    assert module.shawl_relief(.3,.2)!=module.shawl_relief(.3,.8)

def test_rear_ease_does_not_change_front_or_chest_tails():
    assert module.rear_ease_weight(.5,-1)==0
    assert module.rear_ease_weight(.1,1)==0
    assert module.rear_ease_weight(.9,1)==0
    assert module.rear_ease_weight(.5,1)==1

def test_selected_native_must_match_binding(monkeypatch,tmp_path):
    import json
    source=tmp_path/'input.blend';source.touch()
    selected=tmp_path/'wardrobe173-seal01';selected.mkdir()
    (selected/'dressed-fit.blend').touch();(selected/'result.json').write_text(json.dumps({'native_sha256':'expected'}))
    monkeypatch.setattr(module,'SOURCE',source);monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda path:module.SOURCE_SHA if path==source else 'bad')
    with pytest.raises(ValueError,match='Selected native'):module.validate({'operation':'verify01'})

def test_binding_rejects_unadmitted_source_paths(monkeypatch,tmp_path):
    import json
    out=tmp_path/'wardrobe173-operating';out.mkdir()
    (out/'source-binding.json').write_text(json.dumps({'source_files':[{'path':'../../outside','sha256':'x'}]}))
    monkeypatch.setattr(module,'BASE',tmp_path)
    with pytest.raises(ValueError,match='Unexpected source'):module.source_binding()
