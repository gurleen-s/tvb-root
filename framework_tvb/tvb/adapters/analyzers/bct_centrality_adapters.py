# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2020, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
# Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
# Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
# The Virtual Brain: a simulator of primate brain network dynamics.
# Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

from tvb.adapters.analyzers.bct_adapters import BaseBCT, BaseUndirected, bct_description, LABEL_CONNECTIVITY_BINARY, \
    BaseBCTForm
from tvb.core.entities.load import load_entity_by_gid
from tvb.core.entities.model.model_operation import AlgorithmTransientGroup
from tvb.core.neocom import h5

BCT_GROUP_CENTRALITY = AlgorithmTransientGroup("Centrality Algorithms", "Brain Connectivity Toolbox", "bctcentrality")

class CentralityNodeBinaryForm(BaseBCTForm):
    @staticmethod
    def get_connectivity_label():
        return LABEL_CONNECTIVITY_BINARY

class CentralityNodeBinary(BaseBCT):
    """
    """
    _ui_group = BCT_GROUP_CENTRALITY
    _ui_connectivity_label = LABEL_CONNECTIVITY_BINARY

    _ui_name = "Node Betweenness Centrality Binary"
    _ui_description = bct_description("betweenness_bin.m")
    _matlab_code = "C = betweenness_bin(A);"

    def get_form_class(self):
        return CentralityNodeBinaryForm

    def launch(self, view_model):
        connectivity = self.get_connectivity(view_model)
        data = dict([('A', connectivity.weights)])

        result = self.execute_matlab(self._matlab_code, data=data)
        measure = self.build_connectivity_measure(result, 'C', connectivity,
                                                  "Node Betweenness Centrality Binary", "Nodes")
        measure_index = self.load_entity_by_gid(measure.gid.hex)
        return [measure_index]

class CentralityNodeWeightedForm(BaseBCTForm):
    @staticmethod
    def get_connectivity_label():
        return "Weighted (directed/undirected)  connection matrix"

class CentralityNodeWeighted(BaseBCT):
    """
    """
    _ui_group = BCT_GROUP_CENTRALITY

    _ui_name = "Node Betweenness Centrality Weighted"
    _ui_description = bct_description("betweenness_wei.m")
    _matlab_code = "C = betweenness_wei(A);"

    def get_form_class(self):
        return CentralityNodeWeightedForm

    def launch(self, view_model):
        connectivity = self.get_connectivity(view_model)
        data = dict([('A', connectivity.weights)])

        result = self.execute_matlab(self._matlab_code, data=data)
        measure = self.build_connectivity_measure(result, 'C', connectivity,
                                                  "Node Betweenness Centrality Weighted", "Nodes")
        measure_index = self.load_entity_by_gid(measure.gid.hex)
        return [measure_index]


class CentralityEdgeBinary(CentralityNodeBinary):
    """
    """
    _ui_name = "Edge Betweenness Centrality Weighted"
    _ui_description = bct_description("edge_betweenness_bin.m")
    _matlab_code = "[EBC,BC] = edge_betweenness_bin(A);"


    def launch(self, view_model):
        connectivity = self.get_connectivity(view_model)
        data = dict([('A', connectivity.weights)])

        result = self.execute_matlab(self._matlab_code, data=data)
        measure1 = self.build_connectivity_measure(result, 'EBC', connectivity, "Edge Betweenness Centrality Matrix")
        measure_index1 = self.load_entity_by_gid(measure1.gid.hex)
        measure2 = self.build_connectivity_measure(result, 'BC', connectivity, "Node Betweenness Centrality Vector")
        measure_index2 = self.load_entity_by_gid(measure2.gid.hex)
        return [measure_index1, measure_index2]


class CentralityEdgeWeighted(CentralityNodeWeighted):
    """
    """
    _ui_name = "Edge Betweenness Centrality Weighted"
    _ui_description = bct_description("edge_betweenness_wei.m")
    _matlab_code = "[EBC,BC] = edge_betweenness_wei(A);"


    def launch(self, view_model):
        connectivity = self.get_connectivity(view_model)
        data = dict([('A', connectivity.weights)])

        result = self.execute_matlab(self._matlab_code, data=data)
        measure1 = self.build_connectivity_measure(result, 'EBC', connectivity, "Edge Betweenness Centrality Matrix")
        measure_index1 = self.load_entity_by_gid(measure1.gid.hex)
        measure2 = self.build_connectivity_measure(result, 'BC', connectivity, "Node Betweenness Centrality Vector")
        measure_index2 = self.load_entity_by_gid(measure2.gid.hex)
        return [measure_index1, measure_index2]


class CentralityEigenVector(BaseUndirected):
    """
    """
    _ui_group = BCT_GROUP_CENTRALITY

    _ui_name = "EigenVector Centrality"
    _ui_description = bct_description("eigenvector_centrality_und.m")
    _matlab_code = "v = eigenvector_centrality_und(CIJ)"


    def launch(self, view_model):
        connectivity = self.get_connectivity(view_model)
        data = dict([('CIJ', connectivity.weights)])

        result = self.execute_matlab(self._matlab_code, data=data)
        measure = self.build_connectivity_measure(result, 'v', connectivity, "Eigen vector centrality")
        measure_index = self.load_entity_by_gid(measure.gid.hex)
        return [measure_index]

class CentralityKCorenessForm(BaseBCTForm):
    @staticmethod
    def get_connectivity_label():
        return LABEL_CONNECTIVITY_BINARY

class CentralityKCoreness(BaseUndirected):
    """
    """
    _ui_group = BCT_GROUP_CENTRALITY
    _ui_connectivity_label = LABEL_CONNECTIVITY_BINARY

    _ui_name = "K-coreness centrality BU"
    _ui_description = bct_description("kcoreness_centrality_bu.m")
    _matlab_code = "[coreness, kn] = kcoreness_centrality_bu(CIJ);"

    def get_form_class(self):
        return CentralityKCorenessForm

    def launch(self, view_model):
        connectivity = self.get_connectivity(view_model)
        data = dict([('CIJ', connectivity.binarized_weights)])

        result = self.execute_matlab(self._matlab_code, data=data)
        measure1 = self.build_connectivity_measure(result, 'coreness', connectivity, "Node coreness BU")
        measure_index1 = self.load_entity_by_gid(measure1.gid.hex)
        measure2 = self.build_connectivity_measure(result, 'kn', connectivity, "Size of k-core")
        measure_index2 = self.load_entity_by_gid(measure2.gid.hex)
        return [measure_index1, measure_index2]


class CentralityKCorenessBD(CentralityNodeBinary):
    """
    """
    _ui_name = "K-coreness centrality BD"
    _ui_description = bct_description("kcoreness_centrality_bd.m")
    _matlab_code = "[coreness, kn] = kcoreness_centrality_bd(CIJ);"


    def launch(self, view_model):
        connectivity = self.get_connectivity(view_model)
        data = dict([('CIJ', connectivity.binarized_weights)])

        result = self.execute_matlab(self._matlab_code, data=data)
        measure1 = self.build_connectivity_measure(result, 'coreness', connectivity, "Node coreness BD")
        measure_index1 = self.load_entity_by_gid(measure1.gid.hex)
        measure2 = self.build_connectivity_measure(result, 'kn', connectivity, "Size of k-core")
        measure_index2 = self.load_entity_by_gid(measure2.gid.hex)
        return [measure_index1, measure_index2]

class CentralityShortcutsForm(BaseBCTForm):
    @staticmethod
    def get_connectivity_label():
        return "Binary directed connection matrix"

class CentralityShortcuts(CentralityNodeBinary):
    """
    """

    _ui_name = "Centrality Shortcuts"
    _ui_description = bct_description("erange.m")
    _matlab_code = "[Erange,eta,Eshort,fs]  = erange(A);"

    def get_form_class(self):
        return CentralityShortcutsForm

    def launch(self, view_model):
        connectivity = self.get_connectivity(view_model)
        data = dict([('A', connectivity.binarized_weights)])

        result = self.execute_matlab(self._matlab_code, data=data)

        measure1 = self.build_connectivity_measure(result, 'Erange', connectivity, "Range for each edge")
        measure_index1 = self.load_entity_by_gid(measure1.gid.hex)
        value1 = self.build_int_value_wrapper(result, 'eta', "Average range for entire graph")
        measure2 = self.build_connectivity_measure(result, 'Eshort', connectivity, "Shortcut edges")
        measure_index2 = self.load_entity_by_gid(measure2.gid.hex)
        value2 = self.build_float_value_wrapper(result, 'fs', "Fraction of shortcuts in the graph")
        return [measure_index1, value1, measure_index2, value2]


class FlowCoefficients(CentralityNodeBinary):
    """
    """
    _ui_name = "Node-wise flow coefficients"
    _ui_description = bct_description("flow_coef_bd.m")
    _matlab_code = "[fc,FC,total_flo] = flow_coef_bd(CIJ);"


    def launch(self, view_model):
        connectivity = self.get_connectivity(view_model)
        data = dict([('CIJ', connectivity.binarized_weights)])

        result = self.execute_matlab(self._matlab_code, data=data)

        measure1 = self.build_connectivity_measure(result, 'fc', connectivity, "Flow coefficient for each node")
        measure_index1 = self.load_entity_by_gid(measure1.gid.hex)
        value1 = self.build_float_value_wrapper(result, 'FC', "Average flow coefficient over the network")
        measure2 = self.build_connectivity_measure(result, 'total_flo', connectivity,
                                                   "Number of paths that flow across the central node")
        measure_index2 = self.load_entity_by_gid(measure2.gid.hex)
        return [measure_index1, value1, measure_index2]

class ParticipationCoefficientForm(BaseBCTForm):
    @staticmethod
    def get_connectivity_label():
        return "Binary/weighted, directed/undirected connection matrix"

class ParticipationCoefficient(BaseBCT):
    """
    """
    _ui_group = BCT_GROUP_CENTRALITY

    _ui_name = "Participation Coefficient"
    _ui_description = bct_description("participation_coef.m")
    _matlab_code = "[Ci, Q]=modularity_dir(W); P = participation_coef(W, Ci);"

    def get_form_class(self):
        return ParticipationCoefficientForm

    def launch(self, view_model):
        connectivity = self.get_connectivity(view_model)
        data = dict([('W', connectivity.weights)])

        result = self.execute_matlab(self._matlab_code, data=data)

        measure = self.build_connectivity_measure(result, 'P', connectivity, "Participation Coefficient")
        measure_index = self.load_entity_by_gid(measure.gid.hex)
        return [measure_index]


class ParticipationCoefficientSign(ParticipationCoefficient):
    """
    """
    _ui_name = "Participation Coefficient Sign"
    _ui_description = bct_description("participation_coef_sign.m")
    _matlab_code = "[Ci, Q]=modularity_dir(W); [Ppos, Pneg] = participation_coef_sign(W, Ci);"


    def launch(self, view_model):
        connectivity = self.get_connectivity(view_model)
        data = dict([('W', connectivity.weights)])

        result = self.execute_matlab(self._matlab_code, data=data)

        measure1 = self.build_connectivity_measure(result, 'Ppos', connectivity,
                                                   "Participation Coefficient from positive weights")
        measure_index1 = self.load_entity_by_gid(measure1.gid.hex)
        measure2 = self.build_connectivity_measure(result, 'Pneg', connectivity,
                                                   "Participation Coefficient from negative weights")
        measure_index2 = self.load_entity_by_gid(measure2.gid.hex)
        return [measure_index1, measure_index2]

class SubgraphCentralityForm(BaseBCTForm):
    @staticmethod
    def get_connectivity_label():
        return "Adjacency matrix (binary)"

class SubgraphCentrality(CentralityNodeBinary):
    """
    """

    _ui_name = "Subgraph centrality of a network"
    _ui_description = bct_description("subgraph_centrality.m")
    _matlab_code = "Cs = subgraph_centrality(CIJ);"

    def get_form_class(self):
        return SubgraphCentralityForm

    def launch(self, view_model):
        connectivity = self.get_connectivity(view_model)
        data = dict([('CIJ', connectivity.binarized_weights)])

        result = self.execute_matlab(self._matlab_code, data=data)

        measure = self.build_connectivity_measure(result, 'Cs', connectivity, "Subgraph Centrality")
        measure_index = self.load_entity_by_gid(measure.gid.hex)
        return [measure_index]
