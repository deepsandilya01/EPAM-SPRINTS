import json, pathlib, pytest
ROOT=pathlib.Path(__file__).resolve().parents[1]
@pytest.fixture
def raw_data(): return json.loads((ROOT/'photon_sprint1_graph_data.json').read_text(encoding='utf-8'))
@pytest.fixture
def client():
    pytest.importorskip("flask", reason="Flask is not installed in this execution environment")
    import app as app_module
    app_module.GRAPH = app_module._build_graph(app_module.RAW)
    app_module.UNDO_STACK.clear()
    app_module.app.config['TESTING']=True
    with app_module.app.test_client() as c: yield c
    app_module.GRAPH = app_module._build_graph(app_module.RAW)
    app_module.UNDO_STACK.clear()
