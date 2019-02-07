import pytest
from zulipterminal.ui_tools.utils import is_muted, create_msg_box_list


@pytest.mark.parametrize('msg, narrow, muted_streams, muted_topics,\
                         muted', [
    (   # PM TEST
        {
            'type': 'private',
            # ...
        },
        [],
        [1, 2],
        [
            ['foo', 'boo foo'],
            ['boo', 'foo boo'],
        ],
        False
    ),
    (
        {
            'type': 'stream',
            # ...
        },
        [['stream', 'foo'], ['topic', 'boo']],
        [1, 2],
        [
            ['foo', 'boo foo'],
            ['boo', 'foo boo'],
        ],
        False
    ),
    (
        {
            'type': 'stream',
            'stream_id': 1,
            # ...
        },
        [['stream', 'foo']],
        [1, 2],
        [
            ['foo', 'boo foo'],
            ['boo', 'foo boo'],
        ],
        True
    ),
    (
        {
            'type': 'stream',
            'stream_id': 2,
            'display_recipient': 'boo',
            'subject': 'foo boo',
            # ...
        },
        [],
        [1, 2],
        [
            ['foo', 'boo foo'],
            ['boo', 'foo boo'],
        ],
        True
    ),
    (
        {
            'type': 'stream',
            'stream_id': 3,
            'display_recipient': 'zoo',
            'subject': 'foo koo',
            # ...
        },
        [],
        [1, 2],
        [
            ['foo', 'boo foo'],
            ['boo', 'foo boo'],
        ],
        False
    ),
])
def test_is_muted(mocker, msg, narrow, muted_streams, muted_topics, muted):
    model = mocker.Mock()
    model.narrow = narrow
    model.muted_streams = muted_streams
    model.muted_topics = muted_topics
    return_value = is_muted(msg, model)
    assert return_value is muted


@pytest.mark.parametrize('narrow, index, messages, focus_msg_id, muted,\
                         stream_details, pm_details, len_w_list', [
    (
        # No muted messages
        [],
        {
            'all_messages': {1, 2},
            'messages': {
                1: {
                    'id': 1,
                    'flags': ['read'],
                    'timestamp': 10,
                },
                2: {
                    'id': 2,
                    'flags': [],
                    'timestamp': 10,
                }
            },
            'pointer': {},
        },
        None,
        None,
        False,
        None,
        None,
        2,
    ),
    (
        # No muted messages
        [['stream', 'foo']],
        {
            'all_messages': {1, 2},
            'messages': {
                1: {
                    'id': 1,
                    'flags': ['read'],
                    'timestamp': 10,
                },
                2: {
                    'id': 2,
                    'flags': [],
                    'timestamp': 10,
                }
            },
            'pointer': {},
        },
        [1],
        None,
        False,
        None,
        None,
        1,
    ),
    (
        # No muted messages
        [['stream', 'foo']],
        {
            'all_messages': {1, 2},
            'messages': {
                1: {
                    'id': 1,
                    'flags': ['read'],
                    'timestamp': 10,
                },
                2: {
                    'id': 2,
                    'flags': [],
                    'timestamp': 10,
                }
            },
            'pointer': {},
        },
        [1],
        None,
        True,
        None,
        None,
        0,
    ),
    (
        # Displays dummy stream message
        [['stream', 'foo']],
        {
            'all_messages': {1, 2},
            'messages': {},
            'pointer': {}
        },
        [],
        None,
        False,
        {
            'caption': 'Boo',
            'description': 'News about Boo',
            'subject': 'Boo is hungry'
        },
        None,
        1,
    ),
    (
        # Displays dummy private message
        [['pm_with', 'boo@zulip.com']],
        {
            'all_messages': {1, 2},
            'messages': {},
            'pointer': {}
        },
        [],
        None,
        False,
        None,
        {
            'caption': 'Boo Boo',
            'recipient_email': 'bar@zulip.com',
            'sender_id': 8
        },
        1,
    )
])
def test_create_msg_box_list(mocker, narrow, index,  messages, focus_msg_id,
                             muted, stream_details, pm_details, len_w_list):
    model = mocker.Mock()
    model.narrow = narrow
    model.index = index
    msg_box = mocker.patch('zulipterminal.ui_tools.utils.MessageBox')
    mocker.patch('zulipterminal.ui_tools.utils.urwid.AttrMap',
                 return_value='MSG')
    mocker.patch('zulipterminal.ui_tools.utils.is_muted', return_value=muted)
    return_value = create_msg_box_list(model, messages, focus_msg_id,
                                       stream_details=stream_details,
                                       pm_details=pm_details)
    assert len(return_value) == len_w_list
