import logging
import os

import openai
import traceback
from flask import Flask, redirect, render_template, request, url_for
from redisUtil import build_req_msg_txt, build_resp_msg_txt

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
MAX_LEN_TOKEN = os.getenv("MAX_LEN_TOKEN")


# https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/events/receive

def snnd_openai_text(question_json_str, open_id):
    if request.method == "POST":
        try:
            prompt = generate_prompt(question_json_str, open_id)
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0.9,
                #     temperature min 0 ，max0.9
                max_tokens=1024,  # int(MAX_LEN_TOKEN),len(prompt) + 24
                top_p=1,
                stop=["Human:", "AI:"],  # ["wunike:","sage:"]  ["Human:", "AI:"]
                frequency_penalty=0,
                presence_penalty=0,
            )
            resp_text = response.choices[0].text.lstrip('\n')
            print("openAi api response text --->" + resp_text)
            if resp_text == "" or resp_text is None:
                return "\"AI\"没有回复您的消息，这是一句开发者留下的提示回馈。"
            # return "问："+question_json_str+" \n答："+response.choices[0].text
            build_resp_msg_txt(open_id, resp_text)
            return resp_text
        except Exception as e:
            # logging.warn(e)
            print(traceback.format_exc())
            return "AI没有回复你的问题，但是你抓到了一个异常，他说：" + str(e)


def generate_prompt(question_json_str, open_id):
    req_text = build_req_msg_txt(open_id, question_json_str)
    # print("open_id 说 --> ", open_id, req_text)
    return req_text.capitalize()
