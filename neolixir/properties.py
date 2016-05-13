# -*- coding: utf-8 -*-
# 
# The MIT License (MIT)
# 
# Copyright (c) 2013 Ivaylo Tzvetkov, ChallengeU
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

from types import FunctionType
from inspect import getargspec
from collections import Iterable
from decimal import Decimal, InvalidOperation
from datetime import datetime
from utils import IN, OUT, classproperty
from observable import Observable

__all__ = ['Boolean', 'String', 'Enum', 'Integer', 'Float', 'Numeric', 'DateTime',
           'RelOut', 'RelIn', 'RelOutOne', 'RelInOne']

class FieldDescriptor(Observable):

    def __init__(self, name=None, observers=None):
        self._name = None
        self.name = name
        if isinstance(observers, dict):
            self.add_observers(observers)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if self._name is None:
            self._name = name

    def fire_event(self, event, target, *args):
        entity, field = target
        if not entity.is_expunged():
            super(FieldDescriptor, self).fire_event(event, target, *args)

class Property(FieldDescriptor):

    __value_type__ = None

    def __init__(self, name=None, default=None, observers=None):
        super(Property, self).__init__(name=name, observers=observers)
        self._default = default

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            value = instance.properties.get(self.name)
            return self.normalize(value if value is not None else self.get_default(instance))
    
    def __set__(self, instance, value):
        instance.properties[self.name] = self.normalize(value)
    
    def __delete__(self, instance):
        del instance.properties[self.name]

    def get_default(self, instance):
        if hasattr(self._default, '__call__'):
            if isinstance(self._default, FunctionType) and len(getargspec(self._default).args) == 1:
                return self._default(instance)
            else:
                return self._default()
        else:
            return self._default

    def normalize(self, value):
        if value is not None and self.__value_type__ is not None:
            if not isinstance(value, self.__value_type__):
                value = self.__value_type__(value)
        return value

class Boolean(Property):

    __value_type__ = bool

class String(Property):

    __value_type__ = unicode

class Enum(String):

    def __init__(self, *args, **kwargs):
        super(Enum, self).__init__(name=kwargs.get('name'),
                                   default=kwargs.get('default'),
                                   observers=kwargs.get('observers'))
        self.values = args
    
    def __set__(self, instance, value):
        if value is not None and value not in self.values:
            raise ValueError(u"Invalid value for Enum: {0}".format(value))
        super(Enum, self).__set__(instance, value)

class Integer(Property):

    __value_type__ = int

class Float(Property):

    __value_type__ = float

class Numeric(Property):

    __value_type__ = Decimal

    def __init__(self, scale=None, name=None, default=None, observers=None):
        super(Numeric, self).__init__(name=name, default=default, observers=observers)
        self.scale = scale
    
    def __set__(self, instance, value):
        if value is not None:
            value = str(self.normalize(value))
        instance.properties[self.name] = value

    def normalize(self, value):
        if value is not None:
            try:
                value = super(Numeric, self).normalize(unicode(value))
            except InvalidOperation:
                raise ValueError(u"Invalid value for Numeric: {0}".format(value))
        if self.scale is not None and isinstance(value, Decimal):
            value = value.quantize(Decimal('1.' + '0' * self.scale))
        return value

class DateTime(Property):

    __value_type__ = datetime

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            value = instance.properties.get(self.name)
            if value is not None and not isinstance(value, datetime):
                value = self.parse(value)
            return value if value is not None else self.get_default(instance)
    
    def __set__(self, instance, value):
        if value is not None:
            if not isinstance(value, datetime):
                value = self.parse(value)
            if isinstance(value, datetime):
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                raise ValueError(u"Invalid value for DateTime: {0}".format(value))
        instance.properties[self.name] = value

    @classmethod
    def format(cls, value):
        if not isinstance(value, datetime):
            value = cls.parse(value)
        return value.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def parse(cls, value):
        if isinstance(value, basestring):
            try:
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass
            try:
                return datetime.strptime(value, "%Y-%m-%d %H:%M")
            except ValueError:
                pass
            try:
                return datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                pass
            try:
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                pass
            try:
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                pass
        return None

class Array(Property):

    __value_type__ = list

    def __init__(self, type=None, name=None, observers=None):
        raise NotImplementedError("Array support not yet implemented")
        super(Array, self).__init__(name=name, observers=observers)
        self._content_type = type

    def __get__(self, instance, owner=None):
        value = super(Array, self).__get__(instance, owner)
        if instance is not None and not isinstance(value, TypedList):
            value = TypedList(value, type=self._content_type)
            super(Array, self).__set__(instance, value)
        return value

    def __set__(self, instance, value):
        if not isinstance(value, TypedList):
            value = TypedList(value, type=self._content_type)
        super(Array, self).__set__(instance, value)

class TypedList(list):
    
    # TODO: implement type checking, casting and enforcing

    def __init__(self, list=None, type=None):
        raise NotImplementedError("Array support not yet implemented")
        super(TypedList, self).__init__(list or [])
        self._content_type = type

class RelDescriptor(FieldDescriptor):

    def __init__(self, direction, type, name=None, observers=None, multiple=False, relview_cls=None):
        super(RelDescriptor, self).__init__(name=name, observers=observers)
        self.direction = direction
        self.type = type
        self.multiple = multiple
        self.relview_cls = relview_cls

    @classproperty
    def __relview_cls__(cls):
        from relmap import RelView
        return RelView

    def get_relview(self, instance):
        try:
            return instance._relfilters[self.name]
        except KeyError:
            relview_cls = self.relview_cls or self.__relview_cls__
            instance._relfilters[self.name] = relview_cls(instance, self.name,
                                                          self.direction, self.type,
                                                          multiple=self.multiple)
            return instance._relfilters[self.name]

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            return self.get_relview(instance)

    def __set__(self, instance, value):
        relview = self.get_relview(instance)
        items = value if isinstance(value, Iterable) else [value]

        for item in items:
            relview.append(item)

class RelOut(RelDescriptor):

    def __init__(self, *args, **kwargs):
        super(RelOut, self).__init__(OUT, *args, **kwargs)

class RelIn(RelDescriptor):

    def __init__(self, *args, **kwargs):
        super(RelIn, self).__init__(IN, *args, **kwargs)

class RelDescriptorOne(RelDescriptor):

    def __init__(self, *args, **kwargs):
        self.reverse = kwargs.pop('reverse', False)
        super(RelDescriptorOne, self).__init__(*args, **kwargs)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            relview = self.get_relview(instance)
            data = relview.sorted(reverse=self.reverse) if self.multiple else relview
            try:
                return data[-1] # return the "latest" one if multiple
            except IndexError:
                return None

    def __set__(self, instance, value):
        relview = self.get_relview(instance)
        current = list(relview)

        if value is None:
            for item in current:
                relview.remove(item)
        elif self.multiple or len(current) == 0:
            relview.append(value)
        elif len(current) == 1 and current[0] is not value:
            relview.remove(current[0])
            relview.append(value)
        elif len(current) > 1:
            removed = []
            for item in current:
                if item is not value:
                    relview.remove(item)
                    removed.append(item)
            if len(removed) == len(current):
                relview.append(value)

class RelOutOne(RelDescriptorOne):

    def __init__(self, *args, **kwargs):
        super(RelOutOne, self).__init__(OUT, *args, **kwargs)

class RelInOne(RelDescriptorOne):

    def __init__(self, *args, **kwargs):
        super(RelInOne, self).__init__(IN, *args, **kwargs)
