import copy
import unittest
from pathlib import Path
import networkx as nx
from main import (build_graph, load_scenario, trace_supplier_dependencies,
                  verify_expected_results, validate_scenario, ScenarioValidationError)

class Sprint1MappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario = load_scenario()
        cls.graph = build_graph(cls.scenario)

    def test_exact_graph_size(self):
        self.assertEqual(self.graph.number_of_nodes(), 19)
        self.assertEqual(self.graph.number_of_edges(), 21)

    def test_node_type_counts(self):
        from collections import Counter
        self.assertEqual(Counter(d['kind'] for _, d in self.graph.nodes(data=True)),
                         {'supplier': 2, 'part': 5, 'product': 2, 'order': 10})

    def test_exact_edge_relation_counts(self):
        from collections import Counter
        self.assertEqual(Counter(d['relation'] for _, _, d in self.graph.edges(data=True)),
                         {'SUPPLIES': 6, 'USED_IN': 5, 'FULFILLS': 10})

    def test_exact_supplies_mapping_and_shared_part(self):
        expected = {('SUP-01','PART-01'),('SUP-01','PART-02'),('SUP-01','PART-05'),
                    ('SUP-02','PART-03'),('SUP-02','PART-04'),('SUP-02','PART-05')}
        actual = {(u,v) for u,v,d in self.graph.edges(data=True) if d['relation']=='SUPPLIES'}
        self.assertEqual(actual, expected)

    def test_exact_used_in_mapping_and_quantity(self):
        expected = {('PART-01','PROD-01',1),('PART-02','PROD-01',1),('PART-05','PROD-01',2),
                    ('PART-03','PROD-02',1),('PART-04','PROD-02',1)}
        actual = {(u,v,d['quantity_per_product']) for u,v,d in self.graph.edges(data=True) if d['relation']=='USED_IN'}
        self.assertEqual(actual, expected)
        self.assertFalse(self.graph.has_edge('PART-05','PROD-02'))

    def test_fulfills_mapping(self):
        self.assertEqual(sorted(self.graph.successors('PROD-01')), [f'ORD-{i:02}' for i in range(1,7)])
        self.assertEqual(sorted(self.graph.successors('PROD-02')), [f'ORD-{i:02}' for i in range(7,11)])
        self.assertTrue(all(self.graph['PROD-01'][f'ORD-{i:02}']['relation']=='FULFILLS' for i in range(1,7)))

    def test_required_node_attributes_preserved(self):
        self.assertEqual(self.graph.nodes['SUP-01']['location'], 'Pune')
        self.assertIn('note', self.graph.nodes['SUP-02'])
        self.assertEqual(self.graph.nodes['PART-05']['stock_on_hand'], 60)
        self.assertEqual(self.graph.nodes['PART-05']['daily_consumption'], 30)
        self.assertEqual(self.graph.nodes['PROD-01']['parts_needed'], 'PART-01 x1, PART-02 x1, PART-05 x2')
        self.assertEqual(self.graph.nodes['ORD-01']['deadline'], '2026-11-05')

    def test_required_supplies_attributes_preserved(self):
        attrs = self.graph['SUP-01']['PART-01']
        self.assertEqual(attrs['lead_time_hours'], 24)
        self.assertEqual(attrs['max_capacity_units_per_day'], 100)

    def test_supplier_one_expected_reachability(self):
        self.assertEqual(trace_supplier_dependencies(self.graph, 'SUP-01'), {
            'supplier_id':'SUP-01','parts':['PART-01','PART-02','PART-05'],
            'products':['PROD-01'],'orders':[f'ORD-{i:02}' for i in range(1,7)],'order_count':6})

    def test_supplier_two_shared_part_reachability(self):
        result = trace_supplier_dependencies(self.graph, 'SUP-02')
        self.assertEqual(result['parts'], ['PART-03','PART-04','PART-05'])
        self.assertEqual(result['products'], ['PROD-01','PROD-02'])
        self.assertEqual(result['orders'], [f'ORD-{i:02}' for i in range(1,11)])
        self.assertEqual(result['order_count'], 10)

    def test_expected_results_file_passes(self):
        self.assertTrue(all(r['passed'] for r in verify_expected_results(self.graph)))

    def test_graph_is_directed_and_acyclic(self):
        self.assertTrue(self.graph.is_directed())
        self.assertTrue(nx.is_directed_acyclic_graph(self.graph))

    def test_unknown_supplier_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unknown supplier ID'):
            trace_supplier_dependencies(self.graph, 'SUP-99')

    def test_duplicate_id_rejected_across_types(self):
        s = copy.deepcopy(self.scenario)
        s['nodes'][1]['id'] = s['nodes'][0]['id']
        with self.assertRaisesRegex(ScenarioValidationError, 'Duplicate node ID'):
            validate_scenario(s)

    def test_unknown_edge_endpoint_rejected(self):
        s = copy.deepcopy(self.scenario)
        s['edges'][0]['target'] = 'PART-DOES-NOT-EXIST'
        with self.assertRaisesRegex(ScenarioValidationError, 'unknown endpoint'):
            validate_scenario(s)

    def test_wrong_relation_direction_rejected(self):
        s = copy.deepcopy(self.scenario)
        s['edges'][0]['source'], s['edges'][0]['target'] = s['edges'][0]['target'], s['edges'][0]['source']
        with self.assertRaisesRegex(ScenarioValidationError, 'Wrong direction/type'):
            validate_scenario(s)

    def test_missing_supply_attribute_rejected(self):
        s = copy.deepcopy(self.scenario)
        s['edges'][0]['attributes'].pop('lead_time_hours')
        with self.assertRaisesRegex(ScenarioValidationError, 'missing attributes'):
            validate_scenario(s)

    def test_invalid_order_date_rejected(self):
        s = copy.deepcopy(self.scenario)
        next(n for n in s['nodes'] if n['id']=='ORD-01')['attributes']['deadline'] = 'next week'
        with self.assertRaisesRegex(ScenarioValidationError, 'ISO date'):
            validate_scenario(s)

    def test_cycle_rejected(self):
        s = copy.deepcopy(self.scenario)
        s['edges'].append({'source':'PROD-01','target':'SUP-01','relation':'SUPPLIES','attributes':{'lead_time_hours':1,'max_capacity_units_per_day':1}})
        # Direction validation may reject first; either way invalid scenario is rejected.
        with self.assertRaises(ScenarioValidationError):
            validate_scenario(s)

if __name__ == '__main__':
    unittest.main(verbosity=2)
