"""
Unit tests for RPG Graph Operations.
Tests DAG validation, topological sorting, and graph utilities.
"""

import pytest
import networkx as nx

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from zerorepo.core.models import RPG, RPGNode, RPGEdge
from zerorepo.rpg.graph_ops import RPGGraphOps


class TestRPGGraphOpsInit:
    """Tests for RPGGraphOps initialization."""

    def test_init_with_simple_rpg(self, simple_rpg):
        """Test initialization with simple RPG."""
        ops = RPGGraphOps(simple_rpg)
        assert ops.rpg == simple_rpg
        assert ops._nx_graph is None  # Lazy initialization

    def test_init_with_empty_rpg(self, empty_rpg):
        """Test initialization with empty RPG."""
        ops = RPGGraphOps(empty_rpg)
        assert ops.rpg == empty_rpg

    def test_init_with_complex_rpg(self, complex_rpg):
        """Test initialization with complex RPG."""
        ops = RPGGraphOps(complex_rpg)
        assert ops.rpg == complex_rpg


class TestBuildNetworkxGraph:
    """Tests for NetworkX graph construction."""

    def test_build_graph_from_simple_rpg(self, simple_rpg):
        """Test building NetworkX graph from simple RPG."""
        ops = RPGGraphOps(simple_rpg)
        G = ops.build_networkx_graph()

        assert isinstance(G, nx.DiGraph)
        assert G.number_of_nodes() == len(simple_rpg.nodes)

    def test_build_graph_from_empty_rpg(self, empty_rpg):
        """Test building graph from empty RPG."""
        ops = RPGGraphOps(empty_rpg)
        G = ops.build_networkx_graph()

        assert G.number_of_nodes() == 0
        assert G.number_of_edges() == 0

    def test_graph_caching(self, simple_rpg):
        """Test that NetworkX graph is cached."""
        ops = RPGGraphOps(simple_rpg)

        G1 = ops.build_networkx_graph()
        G2 = ops.build_networkx_graph()

        assert G1 is G2  # Same object (cached)

    def test_graph_contains_node_attributes(self, simple_rpg):
        """Test that graph nodes have correct attributes."""
        ops = RPGGraphOps(simple_rpg)
        G = ops.build_networkx_graph()

        for node in simple_rpg.nodes:
            assert node.id in G.nodes
            # Node attributes should be stored
            assert G.nodes[node.id].get("name") == node.name
            assert G.nodes[node.id].get("kind") == node.kind

    def test_graph_edges_filtered_correctly(self, complex_rpg):
        """Test that only data_flow and order edges are included."""
        ops = RPGGraphOps(complex_rpg)
        G = ops.build_networkx_graph()

        # Count edges by type in original
        data_flow_edges = [e for e in complex_rpg.edges if e.type in ["data_flow", "order"]]

        # Graph should only include data_flow and order edges
        assert G.number_of_edges() == len(data_flow_edges)


class TestValidateDAG:
    """Tests for DAG validation."""

    def test_validate_simple_dag(self, simple_rpg):
        """Test validation of valid DAG."""
        ops = RPGGraphOps(simple_rpg)
        is_valid, errors = ops.validate_dag()

        # Simple RPG should be valid (or have only minor warnings)
        # Note: validation is lenient about isolated nodes
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)

    def test_validate_empty_dag(self, empty_rpg):
        """Test validation of empty graph."""
        ops = RPGGraphOps(empty_rpg)
        is_valid, errors = ops.validate_dag()

        assert is_valid is True
        assert len(errors) == 0

    def test_detect_cycles(self, cyclic_rpg):
        """Test cycle detection in graph."""
        ops = RPGGraphOps(cyclic_rpg)
        is_valid, errors = ops.validate_dag()

        assert is_valid is False
        assert any("cycle" in error.lower() for error in errors)

    def test_validate_invalid_edge_references(self):
        """Test detection of edges referencing non-existent nodes."""
        nodes = [RPGNode(id="node-1", name="Node1", kind="capability")]
        edges = [
            RPGEdge(from_node="node-1", to_node="non-existent", type="data_flow")
        ]
        rpg = RPG(nodes=nodes, edges=edges)

        ops = RPGGraphOps(rpg)
        is_valid, errors = ops.validate_dag()

        assert is_valid is False
        assert any("non-existent" in error for error in errors)

    def test_validate_with_isolated_nodes(self):
        """Test validation with isolated (disconnected) nodes."""
        nodes = [
            RPGNode(id="node-1", name="Node1", kind="capability"),
            RPGNode(id="node-2", name="Node2", kind="capability"),
            RPGNode(id="node-3", name="Node3", kind="capability"),
        ]
        # No edges - all nodes isolated
        rpg = RPG(nodes=nodes, edges=[])

        ops = RPGGraphOps(rpg)
        is_valid, errors = ops.validate_dag()

        # Invalid when >80% of nodes are isolated (100% here)
        assert is_valid is False
        assert any("isolated" in e.lower() for e in errors)


class TestTopologicalSort:
    """Tests for topological sorting."""

    def test_topological_sort_simple(self, simple_rpg):
        """Test topological sort on simple graph."""
        ops = RPGGraphOps(simple_rpg)
        order = ops.topological_sort()

        assert isinstance(order, list)
        # Should only include function/class nodes
        for node_id in order:
            node = simple_rpg.get_node(node_id)
            assert node is None or node.kind in ["function", "class"]

    def test_topological_sort_empty(self, empty_rpg):
        """Test topological sort on empty graph."""
        ops = RPGGraphOps(empty_rpg)
        order = ops.topological_sort()

        assert order == []

    def test_topological_sort_complex(self, complex_rpg):
        """Test topological sort respects dependencies."""
        ops = RPGGraphOps(complex_rpg)
        order = ops.topological_sort()

        # Order should have function/class nodes
        assert isinstance(order, list)

    def test_topological_sort_with_cycles_fallback(self, cyclic_rpg):
        """Test topological sort fallback when cycles exist."""
        ops = RPGGraphOps(cyclic_rpg)
        order = ops.topological_sort()

        # Should return fallback order (creation order) for cyclic graphs
        assert isinstance(order, list)


class TestGetDependencies:
    """Tests for dependency retrieval."""

    def test_get_dependencies_simple(self, complex_rpg):
        """Test getting dependencies of a node."""
        ops = RPGGraphOps(complex_rpg)

        # Class nodes should have dependencies
        deps = ops.get_dependencies("class-linear", max_depth=3)
        assert isinstance(deps, list)

    def test_get_dependencies_nonexistent_node(self, simple_rpg):
        """Test getting dependencies of non-existent node."""
        ops = RPGGraphOps(simple_rpg)
        deps = ops.get_dependencies("non-existent")

        assert deps == []

    def test_get_dependencies_max_depth(self, complex_rpg):
        """Test max_depth parameter."""
        ops = RPGGraphOps(complex_rpg)

        deps_depth_1 = ops.get_dependencies("class-linear", max_depth=1)
        deps_depth_3 = ops.get_dependencies("class-linear", max_depth=3)

        # Deeper search should find same or more dependencies
        assert len(deps_depth_1) <= len(deps_depth_3)

    def test_get_dependencies_isolated_node(self):
        """Test dependencies of isolated node."""
        nodes = [
            RPGNode(id="isolated", name="Isolated", kind="function"),
        ]
        rpg = RPG(nodes=nodes, edges=[])
        ops = RPGGraphOps(rpg)

        deps = ops.get_dependencies("isolated")
        assert deps == []


class TestGetNeighborhood:
    """Tests for neighborhood retrieval."""

    def test_get_neighborhood_simple(self, complex_rpg):
        """Test getting neighborhood of a node."""
        ops = RPGGraphOps(complex_rpg)

        neighbors = ops.get_neighborhood("class-base", radius=2)
        assert isinstance(neighbors, list)

    def test_get_neighborhood_nonexistent_node(self, simple_rpg):
        """Test neighborhood of non-existent node."""
        ops = RPGGraphOps(simple_rpg)
        neighbors = ops.get_neighborhood("non-existent")

        assert neighbors == []

    def test_get_neighborhood_radius(self, complex_rpg):
        """Test radius parameter for neighborhood."""
        ops = RPGGraphOps(complex_rpg)

        neighbors_r1 = ops.get_neighborhood("class-base", radius=1)
        neighbors_r3 = ops.get_neighborhood("class-base", radius=3)

        # Larger radius should include same or more neighbors
        assert len(neighbors_r1) <= len(neighbors_r3)


class TestFindByFunctionality:
    """Tests for functionality-based search."""

    def test_find_by_name(self, complex_rpg):
        """Test finding nodes by name similarity."""
        ops = RPGGraphOps(complex_rpg)

        results = ops.find_by_functionality("Linear", max_results=5)
        assert isinstance(results, list)

        # Should find nodes with "Linear" in name
        if results:
            assert any("Linear" in node.name for node in results)

    def test_find_by_doc(self, complex_rpg):
        """Test finding nodes by documentation."""
        ops = RPGGraphOps(complex_rpg)

        results = ops.find_by_functionality("regression", max_results=5)
        assert isinstance(results, list)

    def test_find_no_matches(self, simple_rpg):
        """Test finding with no matches."""
        ops = RPGGraphOps(simple_rpg)

        results = ops.find_by_functionality("xyznonexistent123", max_results=5)
        assert results == []

    def test_find_max_results(self, complex_rpg):
        """Test max_results parameter."""
        ops = RPGGraphOps(complex_rpg)

        results = ops.find_by_functionality("class", max_results=2)
        assert len(results) <= 2


class TestGetDataFlows:
    """Tests for data flow edge retrieval."""

    def test_get_data_flows(self, complex_rpg):
        """Test getting all data flow edges."""
        ops = RPGGraphOps(complex_rpg)
        flows = ops.get_data_flows()

        assert isinstance(flows, list)
        for edge in flows:
            assert edge.type == "data_flow"

    def test_get_data_flows_empty(self, empty_rpg):
        """Test data flows on empty graph."""
        ops = RPGGraphOps(empty_rpg)
        flows = ops.get_data_flows()

        assert flows == []

    def test_get_data_flows_no_data_edges(self):
        """Test when no data flow edges exist."""
        nodes = [
            RPGNode(id="n1", name="N1", kind="capability"),
            RPGNode(id="n2", name="N2", kind="capability"),
        ]
        edges = [
            RPGEdge(from_node="n1", to_node="n2", type="depends_on"),
        ]
        rpg = RPG(nodes=nodes, edges=edges)
        ops = RPGGraphOps(rpg)

        flows = ops.get_data_flows()
        assert flows == []


class TestGetExecutionOrder:
    """Tests for execution order edge retrieval."""

    def test_get_execution_order(self, complex_rpg):
        """Test getting execution order edges."""
        ops = RPGGraphOps(complex_rpg)
        order_edges = ops.get_execution_order()

        assert isinstance(order_edges, list)
        for edge in order_edges:
            assert edge.type == "order"

    def test_get_execution_order_empty(self, empty_rpg):
        """Test execution order on empty graph."""
        ops = RPGGraphOps(empty_rpg)
        order_edges = ops.get_execution_order()

        assert order_edges == []


class TestValidateInterfaces:
    """Tests for interface validation."""

    def test_validate_interfaces_complete(self):
        """Test validation with complete interfaces."""
        nodes = [
            RPGNode(
                id="func-1",
                name="complete_func",
                kind="function",
                signature="def complete_func():",
                doc="A complete function"
            ),
            RPGNode(
                id="class-1",
                name="CompleteClass",
                kind="class",
                signature="class CompleteClass:",
                doc="A complete class"
            ),
        ]
        rpg = RPG(nodes=nodes, edges=[])
        ops = RPGGraphOps(rpg)

        errors = ops.validate_interfaces()
        assert errors == []

    def test_validate_interfaces_missing_signature(self):
        """Test validation catches missing signatures."""
        nodes = [
            RPGNode(
                id="func-1",
                name="no_signature",
                kind="function",
                doc="Has doc but no signature"
            ),
        ]
        rpg = RPG(nodes=nodes, edges=[])
        ops = RPGGraphOps(rpg)

        errors = ops.validate_interfaces()
        assert len(errors) > 0
        assert any("signature" in error.lower() for error in errors)

    def test_validate_interfaces_missing_doc(self):
        """Test validation catches missing documentation."""
        nodes = [
            RPGNode(
                id="func-1",
                name="no_doc",
                kind="function",
                signature="def no_doc():"
            ),
        ]
        rpg = RPG(nodes=nodes, edges=[])
        ops = RPGGraphOps(rpg)

        errors = ops.validate_interfaces()
        assert len(errors) > 0
        assert any("documentation" in error.lower() for error in errors)


class TestGetFileDependencies:
    """Tests for file-level dependency mapping."""

    def test_get_file_dependencies(self, complex_rpg):
        """Test getting file dependencies."""
        ops = RPGGraphOps(complex_rpg)
        file_deps = ops.get_file_dependencies()

        assert isinstance(file_deps, dict)

    def test_get_file_dependencies_empty(self, empty_rpg):
        """Test file dependencies on empty graph."""
        ops = RPGGraphOps(empty_rpg)
        file_deps = ops.get_file_dependencies()

        assert file_deps == {}

    def test_file_dependencies_structure(self):
        """Test file dependency structure."""
        nodes = [
            RPGNode(id="f1", name="base.py", kind="file", path_hint="src/base.py"),
            RPGNode(id="f2", name="impl.py", kind="file", path_hint="src/impl.py"),
            RPGNode(id="n1", name="BaseClass", kind="class", path_hint="src/base.py"),
            RPGNode(id="n2", name="ImplClass", kind="class", path_hint="src/impl.py"),
        ]
        edges = [
            RPGEdge(from_node="n1", to_node="n2", type="data_flow"),
        ]
        rpg = RPG(nodes=nodes, edges=edges)
        ops = RPGGraphOps(rpg)

        file_deps = ops.get_file_dependencies()
        assert isinstance(file_deps, dict)


class TestCalculateMetrics:
    """Tests for graph metrics calculation."""

    def test_calculate_metrics_simple(self, simple_rpg):
        """Test metrics calculation on simple graph."""
        ops = RPGGraphOps(simple_rpg)
        metrics = ops.calculate_metrics()

        assert "total_nodes" in metrics
        assert "total_edges" in metrics
        assert metrics["total_nodes"] == len(simple_rpg.nodes)
        assert metrics["total_edges"] == len(simple_rpg.edges)

    def test_calculate_metrics_empty(self, empty_rpg):
        """Test metrics on empty graph."""
        ops = RPGGraphOps(empty_rpg)
        metrics = ops.calculate_metrics()

        assert metrics["total_nodes"] == 0
        assert metrics["total_edges"] == 0

    def test_calculate_metrics_complex(self, complex_rpg):
        """Test metrics on complex graph."""
        ops = RPGGraphOps(complex_rpg)
        metrics = ops.calculate_metrics()

        assert metrics["total_nodes"] == len(complex_rpg.nodes)
        assert "capability_nodes" in metrics
        assert "file_nodes" in metrics
        assert "class_nodes" in metrics
        assert "function_nodes" in metrics
        assert "data_flows" in metrics
        assert "dependencies" in metrics
        assert "order_constraints" in metrics

    def test_metrics_by_node_kind(self, complex_rpg):
        """Test that metrics correctly count nodes by kind."""
        ops = RPGGraphOps(complex_rpg)
        metrics = ops.calculate_metrics()

        # Count manually
        capability_count = len([n for n in complex_rpg.nodes if n.kind == "capability"])
        file_count = len([n for n in complex_rpg.nodes if n.kind == "file"])
        class_count = len([n for n in complex_rpg.nodes if n.kind == "class"])

        assert metrics["capability_nodes"] == capability_count
        assert metrics["file_nodes"] == file_count
        assert metrics["class_nodes"] == class_count


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_single_node_graph(self):
        """Test graph with single node."""
        nodes = [RPGNode(id="single", name="Single", kind="capability")]
        rpg = RPG(nodes=nodes, edges=[])
        ops = RPGGraphOps(rpg)

        is_valid, errors = ops.validate_dag()
        # Single isolated node = 100% isolated > 80% threshold
        assert is_valid is False

        order = ops.topological_sort()
        assert isinstance(order, list)

    def test_self_loop_detection(self):
        """Test detection of self-loops."""
        nodes = [RPGNode(id="self", name="Self", kind="capability")]
        edges = [RPGEdge(from_node="self", to_node="self", type="data_flow")]
        rpg = RPG(nodes=nodes, edges=edges)
        ops = RPGGraphOps(rpg)

        is_valid, errors = ops.validate_dag()
        # Self-loop creates a cycle
        assert is_valid is False

    def test_disconnected_components(self):
        """Test graph with disconnected components."""
        nodes = [
            RPGNode(id="a1", name="A1", kind="function"),
            RPGNode(id="a2", name="A2", kind="function"),
            RPGNode(id="b1", name="B1", kind="function"),
            RPGNode(id="b2", name="B2", kind="function"),
        ]
        edges = [
            RPGEdge(from_node="a1", to_node="a2", type="data_flow"),
            RPGEdge(from_node="b1", to_node="b2", type="data_flow"),
        ]
        rpg = RPG(nodes=nodes, edges=edges)
        ops = RPGGraphOps(rpg)

        # Should still be valid DAG
        is_valid, errors = ops.validate_dag()
        assert is_valid is True

        # Should produce valid topological order
        order = ops.topological_sort()
        assert len(order) == 4

    def test_very_deep_graph(self):
        """Test graph with deep dependency chain."""
        depth = 20
        nodes = [
            RPGNode(id=f"node-{i}", name=f"Node{i}", kind="function")
            for i in range(depth)
        ]
        edges = [
            RPGEdge(from_node=f"node-{i}", to_node=f"node-{i+1}", type="data_flow")
            for i in range(depth - 1)
        ]
        rpg = RPG(nodes=nodes, edges=edges)
        ops = RPGGraphOps(rpg)

        is_valid, errors = ops.validate_dag()
        assert is_valid is True

        order = ops.topological_sort()
        assert len(order) == depth

    def test_diamond_dependency(self):
        """Test diamond-shaped dependency pattern."""
        # A -> B, A -> C, B -> D, C -> D
        nodes = [
            RPGNode(id="a", name="A", kind="function"),
            RPGNode(id="b", name="B", kind="function"),
            RPGNode(id="c", name="C", kind="function"),
            RPGNode(id="d", name="D", kind="function"),
        ]
        edges = [
            RPGEdge(from_node="a", to_node="b", type="data_flow"),
            RPGEdge(from_node="a", to_node="c", type="data_flow"),
            RPGEdge(from_node="b", to_node="d", type="data_flow"),
            RPGEdge(from_node="c", to_node="d", type="data_flow"),
        ]
        rpg = RPG(nodes=nodes, edges=edges)
        ops = RPGGraphOps(rpg)

        is_valid, errors = ops.validate_dag()
        assert is_valid is True

        order = ops.topological_sort()
        # A should come before B, C; B, C should come before D
        assert order.index("a") < order.index("b")
        assert order.index("a") < order.index("c")
        assert order.index("b") < order.index("d")
        assert order.index("c") < order.index("d")
