# -*- coding: utf-8 -*-

# ******************************************************************************
#
# Copyright (C) 2006-2011 Olivier Tilloy <olivier@tilloy.net>
# Copyright (C) 2015-2016 Vincent Vande Vyvre <vincent.vandevyvre@oqapy.eu>
#
# This file is part of the py3exiv2 distribution.
#
# py3exiv2 is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 3 as published by the Free Software Foundation.
#
# py3exiv2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with py3exiv2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, 5th Floor, Boston, MA 02110-1301 USA.
#
# Maintainer: Vincent Vande Vyvre <vincent.vandevyvre@oqapy.eu>
#
# ******************************************************************************

"""
XMP specific code.
"""

import libexiv2python

from pyexiv2.utils import FixedOffset, is_fraction, make_fraction, \
                          GPSCoordinate, DateTimeFormatter

import datetime
import re


class XmpValueError(ValueError):

    """
    Exception raised when failing to parse the *value* of an XMP tag.

    :attribute value: the value that fails to be parsed
    :type value: string
    :attribute type: the XMP type of the tag
    :type type: string
    """
    def __init__(self, value, type_):
        self.value = value
        self.type = type

    def __str__(self):
        return 'Invalid value for XMP type [%s]: [%s]' % \
               (self.type, self.value)


class XmpTag(object):

    """Define an XMP tag.

    Here is a correspondance table between the XMP types and the possible
    python types the value of a tag may take:

    - alt, bag, seq: list of the contained simple type
    - lang alt: dict of (language-code: value)
    - Boolean: boolean
    - Colorant: *[not implemented yet]*
    - Date: :class:`datetime.date`, :class:`datetime.datetime`
    - Dimensions: *[not implemented yet]*
    - Font: *[not implemented yet]*
    - GPSCoordinate: :class:`pyexiv2.utils.GPSCoordinate`
    - Integer: int
    - Locale: *[not implemented yet]*
    - MIMEType: 2-tuple of strings
    - Rational: :class:`fractions.Fraction`
    - Real: *[not implemented yet]*
    - AgentName, ProperName, Text: unicode string
    - Thumbnail: *[not implemented yet]*
    - URI, URL: string
    - XPath: *[not implemented yet]*
    """

    # strptime is not flexible enough to handle all valid Date formats, we use a
    # custom regular expression
    _time_zone_re = r'Z|((?P<sign>\+|-)(?P<ohours>\d{2}):(?P<ominutes>\d{2}))'
    _time_re = r'(?P<hours>\d{2})(:(?P<minutes>\d{2})(:(?P<seconds>\d{2})(.(?P<decimal>\d+))?)?(?P<tzd>%s))?' % _time_zone_re
    _date_re = re.compile(r'(?P<year>\d{4})(-(?P<month>\d{2})(-(?P<day>\d{2})(T(?P<time>%s))?)?)?' % _time_re)

    def __init__(self, key, value=None, _tag=None):
        """The tag can be initialized with an optional value which expected
        type depends on the XMP type of the tag.

        Args:
        key -- the key of the tag
        value -- the value of the tag
        """
        super(XmpTag, self).__init__()
        if _tag is not None:
            self._tag = _tag

        else:
            self._tag = libexiv2python._XmpTag(key)

        self._raw_value = None
        self._value = None
        self._value_cookie = False
        if value is not None:
            #type_ = self._tag._getType()
            self._set_value(value)

    def _set_owner(self, metadata):
        self._tag._setParentImage(metadata._image)

    @staticmethod
    def _from_existing_tag(_tag):
        """Build a tag from an already existing libexiv2python._XmpTag.

        """
        tag = XmpTag(_tag._getKey(), _tag=_tag)
        type_ = _tag._getExiv2Type()
        # Do not set the raw_value property, as it would call
        # _tag._set{Text,Array,LangAlt}Value
        # (see https://bugs.launchpad.net/pyexiv2/+bug/582445).
        if type_ == 'XmpText':
            tag._raw_value = _tag._getTextValue()

        elif type_ in ('XmpAlt', 'XmpBag', 'XmpSeq'):
            tag._raw_value = _tag._getArrayValue()

        elif type_ == 'LangAlt':
            tag._raw_value = _tag._getLangAltValue()

        tag._value_cookie = True
        return tag

    @property
    def key(self):
        """The key of the tag in the dotted form
        ``familyName.groupName.tagName`` where ``familyName`` = ``xmp``.

        """
        return self._tag._getKey()

    @property
    def type(self):
        """The XMP type of the tag.

        """
        return self._tag._getType()

    @property
    def name(self):
        """The name of the tag (this is also the third part of the key).

        """
        return self._tag._getName()

    @property
    def title(self):
        """The title (label) of the tag.

        """
        return self._tag._getTitle()

    @property
    def description(self):
        """The description of the tag.

        """
        return self._tag._getDescription()

    def _get_raw_value(self):
        return self._raw_value

    def _set_raw_value(self, value):
        type_ = self._tag._getExiv2Type()
        
        if type_ == 'XmpText':
            self._tag._setTextValue(value)

        elif type_ in ('XmpAlt', 'XmpBag', 'XmpSeq'):
            if not value:
                raise ValueError('Empty array')
            self._tag._setArrayValue(value)

        elif type_ == 'LangAlt':
            if not value:
                raise ValueError('Empty LangAlt')
            self._tag._setLangAltValue(value)

        self._raw_value = value
        self._value_cookie = True

    raw_value = property(fget=_get_raw_value, fset=_set_raw_value,
                         doc='The raw value of the tag as a [list of] ' \
                             'string(s).')

    def _compute_value(self):
        # Lazy computation of the value from the raw value
        if self.type.startswith(('seq', 'bag', 'alt')):
            type_ = self.type[4:]

            if type_.lower().startswith('closed choice of'):
                type_ = type[17:]

            self._value = [self._convert_to_python(v, type_) for v in self._raw_value]

        elif self.type == 'Lang Alt':
            self._value = {}
            for k, v in self._raw_value.items():
                try:
                    self._value[k] = v
                except TypeError:
                    raise XmpValueError(self._raw_value, self.type)

        elif self.type.lower().startswith('closed choice of'):
            self._value = self._convert_to_python(self._raw_value, self.type[17:])

        elif self.type == '':
            self._value = self._raw_value

        else:
            self._value = self._convert_to_python(self._raw_value, self.type)

        self._value_cookie = False

    def _get_value(self):
        if self._value_cookie:
            self._compute_value()
        return self._value

    def _set_value(self, value):
        type_ = self._tag._getExiv2Type()
        if type_ == 'XmpText':
            stype = self.type
            if stype.lower().startswith('closed choice of'):
                stype = stype[17:]
            self.raw_value = self._convert_to_string(value, stype)

        elif type_ in ('XmpAlt', 'XmpBag', 'XmpSeq'):
            if not isinstance(value, (list, tuple)):
                raise TypeError('Expecting a list of values')

            stype = self.type[4:]
            if stype.lower().startswith('closed choice of'):
                stype = stype[17:]
            self.raw_value = [self._convert_to_string(v, stype) for v in value]

        elif type_ == 'LangAlt':
            if isinstance(value, str):
                value = {'x-default': value}

            if not isinstance(value, dict):
                raise TypeError('Expecting a dictionary mapping language codes to values')

            raw_value = {}
            for k, v in value.items():
                if isinstance(v, str):
                    try:
                        v = v.encode('utf-8')
                    except TypeError:
                        raise XmpValueError(value, type_)
                raw_value[k] = v

            self.raw_value = raw_value

        self._value = value
        self._value_cookie = False

    value = property(fget=_get_value, fset=_set_value,
                     doc='The value of the tag as a [list of] python ' \
                         'object(s).')

    def _convert_to_python(self, value, type_):
        """Convert a raw value to its corresponding python type.

        Args:
        value -- the raw value to be converted
        type_ -- the simple type of the raw value

        Return: the value converted to its corresponding python type

        Raise XmpValueError: if the conversion fails
        """
        if type_ == 'Boolean':
            if value == 'True':
                return True

            elif value == 'False':
                return False

            else:
                raise XmpValueError(value, type_)

        elif type_ == 'Colorant':
            # TODO
            raise NotImplementedError('XMP conversion for type [%s]' % type_)

        elif type_ == 'Date':
            match = self._date_re.match(value)
            if match is None:
                raise XmpValueError(value, type_)

            gd = match.groupdict()
            if gd['month'] is not None:
                month = int(gd['month'])

            else:
                month = 1

            if gd['day'] is not None:
                day = int(gd['day'])

            else:
                day = 1

            if gd['time'] is None:
                try:
                    return datetime.date(int(gd['year']), month, day)
                except ValueError:
                    raise XmpValueError(value, type_)

            else:
                if gd['minutes'] is None:
                    # Malformed time
                    raise XmpValueError(value, type_)

                if gd['seconds'] is not None:
                    seconds = int(gd['seconds'])

                else:
                    seconds = 0

                if gd['decimal'] is not None:
                    microseconds = int(float('0.%s' % gd['decimal']) * 1E6)

                else:
                    microseconds = 0

                if gd['tzd'] == 'Z':
                    tzinfo = FixedOffset()

                else:
                    tzinfo = FixedOffset(gd['sign'], int(gd['ohours']),
                                         int(gd['ominutes']))

                try:
                    return datetime.datetime(int(gd['year']), month, day,
                                             int(gd['hours']), int(gd['minutes']),
                                             seconds, microseconds, tzinfo)
                except ValueError:
                    raise XmpValueError(value, type_)

        elif type_ == 'Dimensions':
            # TODO
            raise NotImplementedError('XMP conversion for type [%s]' % type_)

        elif type_ == 'Font':
            # TODO
            raise NotImplementedError('XMP conversion for type [%s]' % type_)

        elif type_ == 'GPSCoordinate':
            try:
                return GPSCoordinate.from_string(value)
            except ValueError:
                raise XmpValueError(value, type_)

        elif type_ == 'Integer':
            try:
                return int(value)
            except ValueError:
                raise XmpValueError(value, type_)

        elif type_ == 'Locale':
            # TODO
            # See RFC 3066
            raise NotImplementedError('XMP conversion for type [%s]' % type_)

        elif type_ == 'MIMEType':
            if value.count('/') != 1:
                raise XmpValueError(value, type_)
            try:
                return tuple(value.split('/', 1))
            except ValueError:
                raise XmpValueError(value, type_)

        elif type_ == 'Rational':
            try:
                return make_fraction(value)
            except (ValueError, ZeroDivisionError):
                raise XmpValueError(value, type_)

        elif type_ == 'Real':
            # TODO
            raise NotImplementedError('XMP conversion for type [%s]' % type_)

        elif type_ in ('AgentName', 'ProperName', 'Text'):
            if isinstance(value, bytes):
                try:
                    value = str(value, 'utf-8')
                except TypeError:
                    raise XmpValueError(value, type_)
            return value

        elif type_ == 'Thumbnail':
            # TODO
            raise NotImplementedError('XMP conversion for type [%s]' % type_)

        elif type_ in ('URI', 'URL'):
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8')
                except UnicodeDecodeError:
                    # Unknow encoding, return the raw value
                    pass
            return value

        elif type_ == 'XPath':
            # TODO
            raise NotImplementedError('XMP conversion for type [%s]' % type_)

        raise NotImplementedError('XMP conversion for type [%s]' % type_)

    def _convert_to_string(self, value, type_):
        """Convert a value to its corresponding string representation.

        Args:
        value -- the value to be converted
        type_ -- the simple type of the value

        Return: the value converted to its corresponding string representation

        Raise XmpValueError: if the conversion fails
        """
        if type_ == 'Boolean':
            if isinstance(value, bool):
                return str(value)
            else:
                raise XmpValueError(value, type_)

        elif type_ == 'Date':
            if isinstance(value, (datetime.date, datetime.datetime)):
                return DateTimeFormatter.xmp(value)

            else:
                raise XmpValueError(value, type_)

        elif type_ == 'GPSCoordinate':
            if isinstance(value, GPSCoordinate):
                return str(value)

            else:
                raise XmpValueError(value, type_)

        elif type_ == 'Integer':
            if isinstance(value, int):
                return str(value)

            else:
                raise XmpValueError(value, type_)

        elif type_ == 'MIMEType':
            if isinstance(value, tuple) and len(value) == 2:
                return '/'.join(value)

            else:
                raise XmpValueError(value, type_)

        elif type_ in ('AgentName', 'ProperName', 'Text', 'URI', 'URL'):
            if isinstance(value, str):
                try:
                    return value.encode('utf-8')
                except UnicodeEncodeError:
                    raise XmpValueError(value, type_)

            elif isinstance(value, bytes): 
                return value 

            raise XmpValueError(value, type_)

        elif type_ == 'Rational':
            if is_fraction(value):
                return str(value)

            else:
                raise XmpValueError(value, type_)

        elif type_ == '':
            # Undefined type
            if isinstance(value, str):
                try:
                    return value.encode('utf-8')
                except UnicodeEncodeError:
                    raise XmpValueError(value, type_)

            elif isinstance(value, (datetime.date, datetime.datetime)):
                return DateTimeFormatter.xmp(value)

        raise NotImplementedError('XMP conversion for type [%s]' % type_)

    def __str__(self):
        """Return a string representation of the XMP tag for debugging purposes

        """
        left = '%s [%s]' % (self.key, self.type)
        if self._raw_value is None:
            right = '(No value)'

        else:
             right = self._raw_value

        return '<%s = %s>' % (left, right)

    # Support for pickling.
    def __getstate__(self):
        return (self.key, self.raw_value)

    def __setstate__(self, state):
        key, raw_value = state
        self._tag = libexiv2python._XmpTag(key)
        self.raw_value = raw_value


def register_namespace(name, prefix):
    """Register a custom XMP namespace.

    Overriding the prefix of a known or previously registered namespace is not
    allowed.

    Args:
    name -- the name of the custom namespace (ending with a ``/``),
            typically a URL (e.g. http://purl.org/dc/elements/1.1/)
    prefix -- the prefix for the custom namespace (keys in this namespace
              will be in the form ``Xmp.{prefix}.{something}``)


    Raise ValueError: if the name doesn’t end with a ``/``
    Raise KeyError: if a namespace already exist with this prefix
    """
    if not name.endswith('/'):
        raise ValueError('Name should end with a /')

    libexiv2python._registerXmpNs(name, prefix)


def unregister_namespace(name):
    """Unregister a custom XMP namespace.

    A custom namespace is identified by its name, **not** by its prefix.

    Attempting to unregister an unknown namespace raises an error, as does
    attempting to unregister a builtin namespace.

    Args:
    name -- the name of the custom namespace (ending with a ``/``),
            typically a URL (e.g. http://purl.org/dc/elements/1.1/)

    Raise ValueError: if the name doesn’t end with a ``/``
    Raise KeyError: if the namespace is unknown or a builtin namespace
    """
    if not name.endswith('/'):
        raise ValueError('Name should end with a /')

    libexiv2python._unregisterXmpNs(name)


def unregister_namespaces():
    """Unregister all custom XMP namespaces.

    Builtin namespaces are not unregistered.
    This function always succeeds.
    """
    libexiv2python._unregisterAllXmpNs()

