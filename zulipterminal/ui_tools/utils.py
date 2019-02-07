from typing import Any, Iterable, List, Union, Dict

import urwid
import time

from zulipterminal.ui_tools.boxes import MessageBox


def create_msg_box_list(model: Any, messages: Union[None, Iterable[Any]]=None,
                        focus_msg_id: Union[None, int]=None,
                        last_message: Union[None, Any]=None,
                        stream_details: Any=None,
                        pm_details: Any=None) -> List[Any]:
    """
    MessageBox for every message displayed is created here.
    """
    if not model.narrow and messages is None:
        messages = list(model.index['all_messages'])
    if messages is not None:
        message_list = [model.index['messages'][id] for id in messages]
    message_list.sort(key=lambda msg: msg['timestamp'])
    w_list = []
    focus_msg = None
    last_msg = last_message
    muted_msgs = 0  # No of messages that are muted.
    if last_msg is not None and last_msg['id'] is None:
        last_message = None
    # We create a dummy message to show in narrows with
    # no previous messages, whose author is welcome bot.
    if (message_list == [] and (stream_details is not None or
                                pm_details is not None)):
        msg = {}  # type: Dict[str, Any]
        if stream_details is not None:
            msg = {
                'type': 'stream',
                'display_recipient': stream_details['caption'],
                'stream_id': model.stream_id,
                'subject': stream_details['description']
                }
        elif pm_details is not None:
            msg = {
                'type': 'private',
                'display_recipient': [{'full_name': pm_details['caption'],
                                       'email': pm_details['recipient_email'],
                                       'id': None}],
                'sender_id': pm_details['sender_id'],
                }
        msg.update({
            'content': "<p> There are no messages in this " +
            msg['type'] + " narrow. </p>",
            'sender_full_name': 'Welcome Bot',
            'sender_email': 'welcome-bot@zulip.com',
            'timestamp': int(time.time()),
            'id': None,
            'reactions': [],
            'flags': ['read']
            })
        message_list.append(msg)
        is_empty_narrow = True
    else:
        is_empty_narrow = False

    for msg in message_list:
        # Remove messages of muted topics / streams.
        if is_muted(msg, model):
            muted_msgs += 1
            continue

        msg_flag = 'unread'  # type: Union[str, None]
        flags = msg.get('flags')
        # update_messages sends messages with no flags
        # but flags are set to [] when fetching old messages.
        if flags and ('read' in flags):
            msg_flag = None
        elif focus_msg is None:
            focus_msg = message_list.index(msg) - muted_msgs
        if msg['id'] == focus_msg_id:
            focus_msg = message_list.index(msg) - muted_msgs
        w_list.append(urwid.AttrMap(
                    MessageBox(msg, model, last_msg, is_empty_narrow),
                    msg_flag,
                    'msg_selected'
        ))
        # We don't want to set dummy message as last message.
        if not is_empty_narrow:
            last_msg = msg
    if focus_msg is not None:
        model.set_focus_in_current_narrow(focus_msg)
    return w_list


def is_muted(msg: Dict[Any, Any], model: Any) -> bool:
    # PMs cannot be muted
    if msg['type'] == 'private':
        return False
    # In a topic narrow
    elif len(model.narrow) == 2:
        return False
    elif msg['stream_id'] in model.muted_streams:
        return True
    elif [msg['display_recipient'], msg['subject']] in model.muted_topics:
        return True
    return False
