import logging
import os

import openai
import traceback
from flask import Flask, redirect, render_template, request, url_for
from redisUtil import build_req_msg_arr_json, build_resp_msg_arr_json

from dotenv import load_dotenv, find_dotenv
# load env parameters form file named .env
# load_dotenv(find_dotenv())
load_dotenv(dotenv_path='.env.aichat',override=True)

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# MAX_LEN_TOKEN = os.getenv("MAX_LEN_TOKEN")


# https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/events/receive

def snnd_openai_text(question_json_str, open_id):
    if request.method == "POST":
        try:
            message_arr_str = generate_prompt(question_json_str, open_id)
            # print(message_arr_str)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=message_arr_str
                # [
                #     {"role": "system", "content": "You are a helpful assistant."},
                #     {"role": "user", "content": "Who won the world series in 2020?"},
                #     {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
                #     {"role": "user", "content": "Where was it played?"}
                # ]
            )
            # print(response)
            resp_text = response.choices[0].message.content.lstrip('\n')
            if resp_text == "" or resp_text is None:
                return "\"AI\"没有回复您的消息，这是一句开发者留下的提示回馈。"
            # {"role": "helper", "content": "You are a helpful assistant."},
            # build_resp_msg_arr_json(open_id, {"role": "assistant", "content": resp_text})
            return resp_text
        except Exception as e:
            # logging.warn(e)
            print(traceback.format_exc())
            return "AI没有回复你的问题，但是你抓到了一个异常，他说：" + str(e)


def generate_prompt(question_json_str, open_id):
    msg_json_arr = {"role": "user", "content": question_json_str}
    req_arr = build_req_msg_arr_json(open_id, msg_json_arr)
    print("open_id 说 --> ", open_id, req_arr)
    return req_arr
