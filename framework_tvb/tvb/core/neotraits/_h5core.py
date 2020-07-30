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
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

import importlib
import typing
import os.path
import uuid
from datetime import datetime
import numpy
import scipy.sparse
from tvb.basic.logger.builder import get_logger
from tvb.basic.neotraits._attr import Final
from tvb.basic.neotraits.ex import TraitFinalAttributeError
from tvb.core.entities.file.exceptions import MissingDataSetException
from tvb.core.entities.file.hdf5_storage_manager import HDF5StorageManager
from tvb.basic.neotraits.api import HasTraits, Attr, List, NArray, Range
from tvb.core.entities.generic_attributes import GenericAttributes
from tvb.core.neotraits._h5accessors import Uuid, Scalar, Accessor, DataSet, Reference, JsonFinal, Json, JsonRange, \
    EquationScalar, \
    SparseMatrix, ReferenceList
from tvb.core.neotraits.view_model import DataTypeGidAttr
from tvb.core.utils import date2string, string2date
from tvb.datatypes.equations import Equation

LOGGER = get_logger(__name__)


class H5File(object):
    """
    A H5 based file format.
    This class implements reading and writing to a *specific* h5 based file format.
    A subclass of this defines a new file format.
    """
    KEY_WRITTEN_BY = 'written_by'
    is_new_file = False

    def __init__(self, path):
        # type: (str) -> None
        self.path = path
        storage_path, file_name = os.path.split(path)
        self.storage_manager = HDF5StorageManager(storage_path, file_name)
        # would be nice to have an opened state for the chunked api instead of the close_file=False

        # common scalar headers
        self.gid = Uuid(HasTraits.gid, self)
        self.written_by = Scalar(Attr(str), self, name=self.KEY_WRITTEN_BY)
        self.create_date = Scalar(Attr(str), self, name='create_date')

        # Generic attributes descriptors
        self.generic_attributes = GenericAttributes()
        self.invalid = Scalar(Attr(bool), self, name='invalid')
        self.is_nan = Scalar(Attr(bool), self, name='is_nan')
        self.subject = Scalar(Attr(str), self, name='subject')
        self.state = Scalar(Attr(str), self, name='state')
        self.type = Scalar(Attr(str), self, name='type')
        self.user_tag_1 = Scalar(Attr(str), self, name='user_tag_1')
        self.user_tag_2 = Scalar(Attr(str), self, name='user_tag_2')
        self.user_tag_3 = Scalar(Attr(str), self, name='user_tag_3')
        self.user_tag_4 = Scalar(Attr(str), self, name='user_tag_4')
        self.user_tag_5 = Scalar(Attr(str), self, name='user_tag_5')
        self.visible = Scalar(Attr(bool), self, name='visible')
        self.metadata_cache = None

        if not self.storage_manager.is_valid_hdf5_file():
            self.written_by.store(self.__class__.__module__ + '.' + self.__class__.__name__)
            self.is_new_file = True

    @classmethod
    def file_name_base(cls):
        return cls.__name__.replace("H5", "")

    def read_subtype_attr(self):
        return None

    def iter_accessors(self):
        # type: () -> typing.Generator[Accessor]
        for accessor in self.__dict__.values():
            if isinstance(accessor, Accessor):
                yield accessor

    def iter_datasets(self):
        for dataset in self.__dict__.values():
            if isinstance(dataset, DataSet):
                yield dataset

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.storage_manager.close_file()

    def store(self, datatype, scalars_only=False, store_references=True):
        # type: (HasTraits, bool, bool) -> None
        for accessor in self.iter_accessors():
            f_name = accessor.trait_attribute.field_name
            if f_name is None:
                # skipp attribute that does not seem to belong to a traited type
                # accessor is an independent Accessor
                continue
            if scalars_only and not isinstance(accessor, Scalar):
                continue
            if not store_references and isinstance(accessor, Reference):
                continue
            accessor.store(getattr(datatype, f_name))

    def load_into(self, datatype):
        # type: (HasTraits) -> None
        for accessor in self.iter_accessors():
            if isinstance(accessor, (Reference, ReferenceList)):
                # we do not load references recursively
                continue
            f_name = accessor.trait_attribute.field_name
            if f_name is None:
                # skipp attribute that does not seem to belong to a traited type
                continue

            # handle optional data, that will be missing from the h5 files
            try:
                value = accessor.load()
            except MissingDataSetException:
                if accessor.trait_attribute.required:
                    raise
                else:
                    value = None

            if isinstance(accessor, JsonFinal):
                current_attr = getattr(datatype, f_name)
                for k, v in current_attr.items():
                    current_attr[k] = value[k]
            else:
                try:
                    setattr(datatype, f_name, value)
                except TraitFinalAttributeError:
                    if getattr(datatype, f_name) != value:
                        raise
                    else:
                        LOGGER.info(
                            'Cannot overwrite Final attribute: {} on {}, but it already has the expected value'.format(
                                f_name, type(datatype).__name__))

    def store_generic_attributes(self, generic_attributes, create=True):
        # type: (GenericAttributes, bool) -> None
        # write_metadata  creation time, serializer class name, etc
        if create:
            self.create_date.store(date2string(datetime.now()))

        self.generic_attributes.fill_from(generic_attributes)
        self.invalid.store(self.generic_attributes.invalid)
        self.is_nan.store(self.generic_attributes.is_nan)
        self.subject.store(self.generic_attributes.subject)
        self.state.store(self.generic_attributes.state)
        self.type.store(self.generic_attributes.type)
        self.user_tag_1.store(self.generic_attributes.user_tag_1)
        self.user_tag_2.store(self.generic_attributes.user_tag_2)
        self.user_tag_3.store(self.generic_attributes.user_tag_3)
        self.user_tag_4.store(self.generic_attributes.user_tag_4)
        self.user_tag_5.store(self.generic_attributes.user_tag_5)
        self.visible.store(self.generic_attributes.visible)

    def load_generic_attributes(self):
        # type: () -> GenericAttributes
        self.generic_attributes.invalid = self.invalid.load()
        self.generic_attributes.is_nan = self.is_nan.load()
        self.generic_attributes.subject = self.subject.load()
        self.generic_attributes.state = self.state.load()
        self.generic_attributes.type = self.type.load()
        self.generic_attributes.user_tag_1 = self.user_tag_1.load()
        self.generic_attributes.user_tag_2 = self.user_tag_2.load()
        self.generic_attributes.user_tag_3 = self.user_tag_3.load()
        self.generic_attributes.user_tag_4 = self.user_tag_4.load()
        self.generic_attributes.user_tag_5 = self.user_tag_5.load()
        self.generic_attributes.visible = self.visible.load()
        self.generic_attributes.create_date = string2date(str(self.create_date.load())) or None
        return self.generic_attributes

    def gather_references(self, datatype_cls=None):
        ret = []
        for accessor in self.iter_accessors():
            trait_attribute = None
            if datatype_cls:
                if hasattr(datatype_cls, accessor.field_name):
                    trait_attribute = getattr(datatype_cls, accessor.field_name)
            if not trait_attribute:
                trait_attribute = accessor.trait_attribute
            if isinstance(accessor, Reference):
                ret.append((trait_attribute, accessor.load()))
            if isinstance(accessor, ReferenceList):
                hex_gids = accessor.load()
                gids = [uuid.UUID(hex_gid) for hex_gid in hex_gids]
                ret.append((trait_attribute, gids))
        return ret

    def determine_datatype_from_file(self):
        config_type = self.type.load()
        package, cls_name = config_type.rsplit('.', 1)
        module = importlib.import_module(package)
        datatype_cls = getattr(module, cls_name)
        return datatype_cls

    @staticmethod
    def determine_type(path):
        # type: (str) -> typing.Type[HasTraits]
        base_dir, fname = os.path.split(path)
        storage_manager = HDF5StorageManager(base_dir, fname)
        meta = storage_manager.get_metadata()
        type_class_fqn = meta.get('type')
        if type_class_fqn is None:
            return HasTraits
        package, cls_name = type_class_fqn.rsplit('.', 1)
        module = importlib.import_module(package)
        cls = getattr(module, cls_name)
        return cls

    @staticmethod
    def h5_class_from_file(path):
        # type: (str) -> typing.Type[H5File]
        base_dir, fname = os.path.split(path)
        storage_manager = HDF5StorageManager(base_dir, fname)
        meta = storage_manager.get_metadata()
        h5file_class_fqn = meta.get(H5File.KEY_WRITTEN_BY)
        if h5file_class_fqn is None:
            return H5File(path)
        package, cls_name = h5file_class_fqn.rsplit('.', 1)
        module = importlib.import_module(package)
        cls = getattr(module, cls_name)
        return cls

    @staticmethod
    def from_file(path):
        # type: (str) -> H5File
        cls = H5File.h5_class_from_file(path)
        return cls(path)

    def __repr__(self):
        return '<{}("{}")>'.format(type(self).__name__, self.path)


class ViewModelH5(H5File):

    def __init__(self, path, view_model):
        super(ViewModelH5, self).__init__(path)
        self.view_model = type(view_model)
        attrs = self.view_model.declarative_attrs
        self._generate_accessors(attrs)

    def _generate_accessors(self, view_model_fields):
        for attr_name in view_model_fields:
            attr = getattr(self.view_model, attr_name)
            if not issubclass(type(attr), Attr):
                raise ValueError('expected a Attr, got a {}'.format(type(attr)))

            if isinstance(attr, DataTypeGidAttr):
                ref = Uuid(attr, self)
            elif isinstance(attr, NArray):
                ref = DataSet(attr, self)
            elif isinstance(attr, List):
                if issubclass(attr.element_type, HasTraits):
                    ref = ReferenceList(attr, self)
                else:
                    ref = Json(attr, self)
            elif issubclass(type(attr), Attr):
                if attr.field_type is scipy.sparse.spmatrix:
                    ref = SparseMatrix(attr, self)
                elif attr.field_type is numpy.random.RandomState:
                    continue
                elif attr.field_type is uuid.UUID:
                    ref = Uuid(attr, self)
                elif issubclass(attr.field_type, Equation):
                    ref = EquationScalar(attr, self)
                elif attr.field_type is Range:
                    ref = JsonRange(attr, self)
                elif isinstance(attr, Final) and attr.field_type == dict:
                    ref = JsonFinal(attr, self)
                elif issubclass(attr.field_type, HasTraits):
                    ref = Reference(attr, self)
                else:
                    ref = Scalar(attr, self)
            else:
                ref = Accessor(attr, self)
            setattr(self, attr.field_name, ref)

    def gather_references_by_uuid(self):
        """
        Mind that ViewModelH5 stores references towards ViewModel objects (eg. Coupling) as Reference attributes, and
        references towards existent Datatypes (eg. Connectivity) as Uuid.
        Thus, the method gather_references will return only references towards other ViewModels, and we need this
        method to gather also the other references.
        """
        ret = []
        for accessor in self.iter_accessors():
            if isinstance(accessor, Uuid) and not isinstance(accessor, Reference):
                if accessor.field_name is 'gid':
                    continue
                ret.append((accessor.trait_attribute, accessor.load()))
        return ret