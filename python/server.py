#!/usr/bin/env python3.8

import os
import logging
import requests
import json
from api import MessageApiClient
from event import MessageReceiveEvent, UrlVerificationEvent, EventManager
from flask import Flask, jsonify

from gevent import pywsgi

from openaiApi35 import snnd_openai_text
from utils import resp_replace
from redisUtil import if_msg_value_repetition

from dotenv import load_dotenv, find_dotenv
# load env parameters form file named .env
# load_dotenv(find_dotenv())
load_dotenv(dotenv_path='.aichatenv',override=True)

app = Flask(__name__)

# load from env
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY")
LARK_HOST = os.getenv("LARK_HOST")
AI_NAME = os.getenv("AI_NAME")


# init service
message_api_client = MessageApiClient(APP_ID, APP_SECRET, LARK_HOST)
event_manager = EventManager()


@event_manager.register("url_verification")
def request_url_verify_handler(req_data: UrlVerificationEvent):
    # url verification, just need return challenge
    if req_data.event.token != VERIFICATION_TOKEN:
        raise Exception("VERIFICATION_TOKEN is invalid")
    return jsonify({"challenge": req_data.event.challenge})


@event_manager.register("im.message.receive_v1")
def message_receive_event_handler(req_data: MessageReceiveEvent):
    sender_id = req_data.event.sender.sender_id
    message = req_data.event.message
    # req_header = req_data.header
    # print("req_header", req_header)
    # print("req_header app_id", req_header.app_id)
    if message.message_type != "text":
        logging.warn("Other types of messages have not been processed yet")
        return jsonify()
        # get open_id and text_content
    # 使用open_id 对用户的对话进行缓存
    open_id = sender_id.open_id
    # print (if_msg_value_repetition(message.message_id))
    if not if_msg_value_repetition(message.message_id):
        # print("chat_id --", message.chat_id)
        # print("chat_type --", message.chat_type)
        # print("json.loads(message.content)", json.loads(message.content)["text"])
        if message.chat_type != "p2p":
            # resp_id = message.chat_id
            # message_api_client.send_text_with_chat_id(resp_id, text_content_resp)
            # print(dir(message))
            if hasattr(message, 'mentions'):
                req_text = json.loads(message.content)["text"]
                # print(len(message.mentions))
                # print("mentions ->", message.mentions[0].key)
                mentions = message.mentions
                if_mention_ai = False
                for mention in message.mentions:
                    # print(mention.name, mention.id, mention.id.open_id)
                    if_mention_ai =  mention.name == AI_NAME # 提到了ai
                    req_text.replace(mention.key, "")
                #         for end
                if if_mention_ai:
                    text_content = resp_replace(snnd_openai_text(req_text, open_id))
                    # text_content_resp = str({"text": text_content.capitalize()})
                        # .replace("\n","")
                    text_content_resp = "{\"text\":\"" + str(text_content.capitalize()) + "\"}"
                    # print("回复你 text_content_resp--- 》" + text_content_resp)
                    message_api_client.send_reply_text_with_message_id(message.message_id, text_content_resp)
            return jsonify()
        else:
            text_content = resp_replace(snnd_openai_text(json.loads(message.content)["text"], open_id))
            # text_content_resp = str({"text": text_content.capitalize()})
            # .replace("\n","")
            text_content_resp = "{\"text\":\"" + str(text_content.capitalize()) + "\"}"
            # print("我回复你 text_content_resp--- 》" + text_content_resp)
            message_api_client.send_text_with_open_id(open_id, text_content_resp)
            return jsonify()
    return jsonify()


@app.errorhandler
def msg_error_handler(ex):
    logging.error(ex)
    response = jsonify(message=str(ex))
    response.status_code = (
        ex.response.status_code if isinstance(ex, requests.HTTPError) else 500
    )
    return response


@app.route("/", methods=["POST"])
def callback_event_handler():
    # print("你发信息来了啊！！")
    # init callback instance and handle
    event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)

    return event_handler(event)


if __name__ == "__main__":
    # init()
    # 开发运行
    # app.run(host="0.0.0.0", port=8080, debug=True)
    # 服务器运行
    server = pywsgi.WSGIServer(('0.0.0.0', 3000), app)
    print("启动成功")
    server.serve_forever()

