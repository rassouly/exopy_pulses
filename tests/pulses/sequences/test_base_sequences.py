# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test for the handling of indexing b sequences.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from ecpy_pulses.pulses.pulse import Pulse
from ecpy_pulses.pulses.sequences.base_sequences\
    import RootSequence, BaseSequence
from ecpy_pulses.pulses.shapes.square_shape import SquareShape
from ecpy_pulses.testing.context import TestContext


def add_children(seq, children):
    """Add a sequence of item to a BaseSequence.

    """
    for i, c in enumerate(children):
        seq.add_child_item(i, c)


def test_sequence_time_constaints_observation():
    """Test adding, moving, deleting pulse in a sequence.

    """
    root = RootSequence()
    context = TestContext()
    root.context = context
    sequence = BaseSequence()
    root.add_child_item(0, sequence)

    assert root.linkable_vars == []

    sequence.time_constrained = True

    assert (sorted(root.linkable_vars) ==
            sorted(['1_start', '1_stop', '1_duration']))

    sequence.time_constrained = False

    assert root.linkable_vars == []


def test_sequence_indexing1():
    """Test adding, moving, deleting pulse in a sequence.

    """
    root = RootSequence()
    root.time_constrained = True
    root.sequence_duration = '1.0'
    context = TestContext()
    root.context = context

    pulse1 = Pulse()
    pulse2 = Pulse()
    pulse3 = Pulse()

    root.add_child_item(0, pulse1)
    assert pulse1.index == 1
    assert pulse1.root is root
    assert (sorted(root.linkable_vars) ==
            (sorted(['sequence_end', '1_start', '1_stop', '1_duration'])))

    root.add_child_item(1, pulse2)
    assert pulse1.index == 1
    assert pulse2.index == 2
    assert pulse2.root is root
    assert (sorted(root.linkable_vars) ==
            sorted(['sequence_end', '1_start', '1_stop', '1_duration',
                    '2_start', '2_stop', '2_duration']))

    root.add_child_item(2, pulse3)
    assert pulse1.index == 1
    assert pulse2.index == 2
    assert pulse3.index == 3
    assert pulse3.root is root
    assert (sorted(root.linkable_vars) ==
            sorted(['sequence_end', '1_start', '1_stop', '1_duration',
                    '2_start', '2_stop', '2_duration',
                    '3_start', '3_stop', '3_duration']))

    root.time_constrained = False
    root.remove_child_item(1)
    assert pulse1.index == 1
    assert pulse2.index == 0
    assert pulse3.index == 2
    assert pulse2.root is None
    assert (sorted(root.linkable_vars) ==
            sorted(['1_start', '1_stop', '1_duration',
                    '2_start', '2_stop', '2_duration']))

    root.add_child_item(1, pulse2)
    assert pulse1.index == 1
    assert pulse2.index == 2
    assert pulse3.index == 3
    assert pulse2.root is root
    assert (sorted(root.linkable_vars) ==
            sorted(['1_start', '1_stop', '1_duration',
                    '2_start', '2_stop', '2_duration',
                    '3_start', '3_stop', '3_duration']))


def test_sequence_indexing2():
    """Test adding, moving, deleting a sequence in a sequence.

    """
    root = RootSequence()
    context = TestContext()
    root.context = context

    pulse1 = Pulse()
    pulse2 = Pulse()
    pulse3 = Pulse()
    pulse4 = Pulse()

    sequence1 = BaseSequence()
    sequence2 = BaseSequence()

    root.add_child_item(0, pulse1)
    root.add_child_item(1, sequence1)
    root.add_child_item(2, pulse2)

    assert sequence1.parent is root
    assert sequence1.root is root

    sequence1.add_child_item(0, sequence2)

    assert sequence2.parent is sequence1
    assert sequence2.root is root
    assert pulse1.index == 1
    assert pulse2.index == 4
    assert (sorted(root.linkable_vars) ==
            sorted(['1_start', '1_stop', '1_duration',
                    '4_start', '4_stop', '4_duration']))

    pulse1.index = 200
    sequence2.add_child_item(0, pulse3)

    assert pulse3.parent is sequence2
    assert pulse3.root is root
    assert pulse2.index == 5
    assert pulse3.index == 4
    assert (sorted(root.linkable_vars) ==
            sorted(['1_start', '1_stop', '1_duration',
                    '4_start', '4_stop', '4_duration',
                    '5_start', '5_stop', '5_duration']))

    # Check that only the pulse below the modified sequence are updated.
    assert pulse1.index == 200
    pulse1.index = 0

    sequence1.add_child_item(0, pulse4)

    assert pulse4.index == 3
    assert sequence2.index == 4
    assert pulse3.index == 5
    assert pulse2.index == 6
    assert (sorted(root.linkable_vars) ==
            sorted(['1_start', '1_stop', '1_duration',
                    '3_start', '3_stop', '3_duration',
                    '5_start', '5_stop', '5_duration',
                    '6_start', '6_stop', '6_duration']))

    sequence1.remove_child_item(1)

    assert sequence2.parent is None
    assert sequence2.index == 0
    assert pulse2.index == 4
    assert (sorted(root.linkable_vars) ==
            sorted(['1_start', '1_stop', '1_duration',
                    '3_start', '3_stop', '3_duration',
                    '4_start', '4_stop', '4_duration']))

    sequence1.index = 200
    root2 = RootSequence()
    sequence2.root = root2
    while True:
        sequence2.remove_child_item(0)
        if not sequence2.items:
            break

    # Check the observer was properly removed
    assert sequence1.index == 200


def test_traverse_sequence():
    """Test traversing a pulse sequence.

    """
    root = RootSequence()
    context = TestContext()
    root.context = context
    root.external_vars = {'a': 1.5}

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='10',
                   kind='Analogical', shape=SquareShape())
    pulse4 = Pulse(def_1='{2_stop} + 0.5', def_2='10',
                   kind='Analogical', shape=SquareShape())
    seq = BaseSequence()
    add_children(root, [pulse1, pulse2, pulse3, seq])
    add_children(seq, [pulse4])

    items = root.traverse()
    assert len(list(items)) == 10

    assert list(root.traverse(0)) == [root, pulse1, pulse2, pulse3, seq]


def test_build_from_config():
    """Test building a pulse sequence.

    """
    root = RootSequence()
    context = TestContext()
    root.context = context
    root.external_vars = {'a': 1.5}

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='10',
                   kind='Analogical', shape=SquareShape())
    pulse4 = Pulse(def_1='{2_stop} + 0.5', def_2='10',
                   kind='Analogical', shape=SquareShape())
    seq = BaseSequence()
    add_children(root, [pulse1, pulse2, pulse3, seq])
    add_children(seq, [pulse4])

    pref = root.preferences_from_members()
    dependecies = {'ecpy.pulses.items':
                   {'ecpy_pulses.BaseSequence': BaseSequence,
                    'ecpy_pulses.Pulse': Pulse},
                   'ecpy.pulses.shapes':
                   {'ecpy_pulses.SquareShape': SquareShape},
                   'ecpy.pulses.contexts':
                   {'ecpy_pulses.TestContext': TestContext}}

    aux = RootSequence.build_from_config(pref, dependecies)
    assert aux.external_vars == {'a': 1.5}
    assert len(aux.items) == 4
    assert isinstance(aux.context, TestContext)

    pulse1 = aux.items[0]
    assert pulse1.def_1 == '1.0'
    assert pulse1.def_2 == '{a}'

    pulse2 = aux.items[1]
    assert pulse2.def_1 == '{a} + 1.0'
    assert pulse2.def_2 == '3.0'

    pulse3 = aux.items[2]
    assert pulse3.def_1 == '{2_stop} + 0.5'
    assert pulse3.def_2 == '10'
    assert pulse3.kind == 'Analogical'
    assert isinstance(pulse3.shape, SquareShape)

    seq = aux.items[3]
    assert len(seq.items) == 1
