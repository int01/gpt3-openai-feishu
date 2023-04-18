import redis
import os
import json
from dotenv import load_dotenv, find_dotenv
# load env parameters form file named .env
# load_dotenv(find_dotenv())
load_dotenv(dotenv_path='.env.aichat',override=True)

host = os.getenv("AICHAT_REDIS_HOST")
port = os.getenv("AICHAT_REDIS_PORT")
password = os.getenv("AICHAT_REDIS_PASSWORD")
db = os.getenv("AICHAT_REDIS_DATABASE")
MAX_LEN_TOKEN = os.getenv("MAX_LEN_TOKEN")

pool = redis.ConnectionPool(host=host, port=port, password=password, db=db, decode_responses=True)
r = redis.Redis(connection_pool=pool)

# r = redis.Redis(host=host, port=port, decode_responses=True)

redis_msg_key = "ADCHAT:MESSIGE_ID:"
redis_msg_txt_key = "ADCHAT:MSG:TEXT:USER_OPENID:"
redis_msg_jsonarr_key = "ADCHAT:MSG:JSONARR:USER_OPENID:"


def set_msg(msgId):
    """过期时间15m"""
    r.set(redis_msg_key + msgId, msgId, ex=15 * 60)


def get_msg(msgId):
    return r.get(redis_msg_key + msgId)


def if_msg_value_repetition(msgId):
    # print("msgId ---> ",msgId)
    key = redis_msg_key + msgId
    # print("r.exists(key)->",key)
    # print(get_msg(msgId))
    if r.exists(key):
        # print("get_msg(msgId) ---> ", get_msg(msgId))
        return get_msg(msgId) is not None
    else:
        # 是新消息
        set_msg(msgId)
        return False

def if_msg_json_repetition(msgId):
    # print("msgId ---> ",msgId)
    key = redis_msg_key + msgId
    # print("r.exists(key)->",key)
    print(get_msg(msgId))
    if r.exists(key):
        # print("get_msg(msgId) ---> ", get_msg(msgId))
        return get_msg(key) is not None
    else:
        # 是新消息
        set_msg(key)
        return False


def set_msg_txt(userOpenId, text):
    """过期时间5m"""
    r.set(redis_msg_txt_key + userOpenId, text, ex=30)


def get_msg_txt(userOpenId):
    return r.get(redis_msg_txt_key + userOpenId)


def set_msg_arr_json(userOpenId, text):
    """过期时间5m"""
    r.set(redis_msg_jsonarr_key + userOpenId, json.dumps(text), ex=30)


def get_msg_arr_json(userOpenId):
    return json.loads(str(r.get(redis_msg_jsonarr_key + userOpenId)))


def build_req_msg_txt(userOpenId, text):
    """ 处理连续性的提问 需要将聊天记录一起发送，用'\n\n'分隔每句话 """
    key = redis_msg_txt_key + userOpenId
    if r.exists(key):
        r_text = ""
        if get_msg_txt(userOpenId) is not None:
            r_text = get_msg_txt(userOpenId) + "\n\n" + text
        else:
            r_text = text
        # 临时的处理逻辑
        if len(r_text) > 1024 - 24:  # int(MAX_LEN_TOKEN) - 24:
            set_msg_txt(userOpenId, text)
            return text

        set_msg_txt(userOpenId, r_text)
        return r_text
    else:
        set_msg_txt(userOpenId, text)
        return text


def build_resp_msg_txt(userOpenId, text):
    """将ai的回复加到问句中"""
    r_text = ""
    if get_msg_txt(userOpenId) is not None:
        r_text = get_msg_txt(userOpenId) + "\n\n" + text
    else:
        r_text = text
    set_msg_txt(userOpenId, r_text)


def build_req_msg_arr_json(userOpenId, text):
    """ 处理连续性的提问 需要将聊天记录一起发送 """
    key = redis_msg_jsonarr_key + userOpenId
    r_text = []
    # if r.exists(key) and get_msg_arr_json(userOpenId) is not None:
    #     r_text = get_msg_arr_json(userOpenId)
    #     # json.loads(
    #     # print("----------", r_text, dir(r_text))
    #     # print(json.loads(r_text))
    #     r_text.append(text)
    # else:
    #     r_text.append(text)
    # # print(r_text)
    # set_msg_arr_json(userOpenId, r_text)
    r_text.append(text)
    return r_text


def build_resp_msg_arr_json(userOpenId, text):
    """将ai的回复加到问句中"""
    r_text = []
    if get_msg_arr_json(userOpenId) is not None:
        r_text = get_msg_arr_json(userOpenId)
        r_text.append(text)
    else:
        r_text.append(text)
    set_msg_arr_json(userOpenId, r_text)
