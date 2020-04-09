# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.HEALTH.
#
# SENAITE.HEALTH is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.health import bikaMessageFactory as _
from bika.lims import deprecated
from zope.component import getAdapters
from zope.interface import Interface
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class ICustomPubPref(Interface):
    """Marker for custom Publication Preferences
    """

@deprecated("integration-1.3 artifact")
class CustomPubPrefVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = [
            (_('Email'),'email'),
            (_('PDF'), 'pdf')
        ]
        for name, item in getAdapters((context, ), ICustomPubPref):
            items.append(item)
        return SimpleVocabulary.fromItems(items)

CustomPubPrefVocabularyFactory = CustomPubPrefVocabulary()
