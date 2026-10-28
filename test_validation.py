import copy, json
import networkx as nx
import pytest
from graph_validation import validate_graph_data, validate_networkx_graph, ValidationPolicy, trace_downstream_with_metrics

def test_baseline_valid(raw_data):
    r=validate_graph_data(raw_data); assert r['valid'], r['errors']
    assert r['summary']['node_count']==19 and r['summary']['edge_count']==21
@pytest.mark.parametrize(('cat','expected'), [('suppliers',2),('parts',5),('products',2),('orders',10)])
def test_node_categories(raw_data,cat,expected): assert len(raw_data['nodes'][cat])==expected
@pytest.mark.parametrize(('cat','expected'), [('supplies',6),('used_in',5),('fulfills',10)])
def test_edge_categories(raw_data,cat,expected): assert len(raw_data['edges'][cat])==expected

def test_duplicate_ids_before_graph_build(raw_data):
    x=copy.deepcopy(raw_data); x['nodes']['parts'][0]['id']=x['nodes']['suppliers'][0]['id']
    assert 'DUPLICATE_NODE_ID' in {e['code'] for e in validate_graph_data(x)['errors']}
def test_missing_node_id(raw_data):
    x=copy.deepcopy(raw_data); del x['nodes']['parts'][0]['id']; assert 'MISSING_NODE_ID' in {e['code'] for e in validate_graph_data(x)['errors']}
def test_invalid_reference(raw_data):
    x=copy.deepcopy(raw_data); x['edges']['supplies'][0]['target']='MISSING'; assert 'INVALID_EDGE_REFERENCE' in {e['code'] for e in validate_graph_data(x)['errors']}
def test_reversed_direction(raw_data):
    x=copy.deepcopy(raw_data); x['edges']['supplies'][0]['source'],x['edges']['supplies'][0]['target']=x['edges']['supplies'][0]['target'],x['edges']['supplies'][0]['source']; assert 'INVALID_EDGE_DIRECTION' in {e['code'] for e in validate_graph_data(x)['errors']}
def test_missing_edge_field(raw_data):
    x=copy.deepcopy(raw_data); del x['edges']['supplies'][0]['source']; assert 'MISSING_EDGE_FIELD' in {e['code'] for e in validate_graph_data(x)['errors']}
def test_invalid_top_level(): assert not validate_graph_data([])['valid']
def test_cycles_policy():
    g=nx.DiGraph(); g.add_node('a',kind='supplier'); g.add_node('b',kind='part'); g.add_edge('a','b',relation='SUPPLIES'); g.add_edge('b','a',relation='USED_IN')
    assert not validate_networkx_graph(g,ValidationPolicy(require_acyclic=True,check_baseline_counts=False))['valid']
    assert 'CYCLE_DETECTED' not in {e['code'] for e in validate_networkx_graph(g,ValidationPolicy(require_acyclic=False,check_baseline_counts=False))['errors']}
def test_undefined_policy_warning(raw_data):
    r=validate_graph_data(raw_data,ValidationPolicy(require_acyclic=None)); assert any(w['code']=='ACYCLICITY_POLICY_UNDEFINED' for w in r['warnings'])
def test_json_serializable(raw_data): json.dumps(validate_graph_data(raw_data))
def test_exact_supplier_descendants(client):
    expected={'SUP-01': {'PART-01','PART-02','PART-05','PROD-01','ORD-01','ORD-02','ORD-03','ORD-04','ORD-05','ORD-06'}, 'SUP-02': {'PART-03','PART-04','PART-05','PROD-01','PROD-02','ORD-01','ORD-02','ORD-03','ORD-04','ORD-05','ORD-06','ORD-07','ORD-08','ORD-09','ORD-10'}}
    for sid, nodes in expected.items():
        r=client.get('/api/downstream/'+sid).get_json(); assert set(r['downstream'])==nodes and sid not in r['downstream']
def test_trace_unknown(raw_data):
    g=nx.DiGraph(); assert trace_downstream_with_metrics(g,'nope')['exists'] is False
def test_validation_endpoint(client):
    r=client.get('/api/validation'); assert r.status_code==200; j=r.get_json(); assert j['baseline']['valid']; assert j['baseline']['summary']['node_count']==19
def test_existing_routes_delete_undo_reset(client):
    assert client.get('/api/graph').status_code==200
    assert client.get('/api/impact/SUP-01').status_code==200
    d=client.delete('/api/node/SUP-01'); assert d.status_code==200
    assert client.post('/api/undo').status_code==200
    reset=client.post('/api/reset'); assert reset.status_code==200 and reset.get_json()['node_count']==19
def test_unknown_node(client): assert client.get('/api/impact/UNKNOWN').status_code==404
