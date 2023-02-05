import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
# https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/events/receive

def snnd_openai_text(question_json_str):
    if request.method == "POST":
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(question_json_str),
            temperature=0.6,
            #     temperature min 0 ，max0.9
            max_tokens=1024,
            top_p=1,
            stop=["Human:", "AI:"],  # ["wunike:","sage:"]  ["Human:", "AI:"]
            frequency_penalty=0,
            presence_penalty=0,
        )
        # print("openAi api response text --->" + response.choices[0].text)
        return "问："+question_json_str+" \n答："+response.choices[0].text
        # return response.choices[0].text
    return "OPENAI PAI 接口没有返回内容，或请求参数错误。"


def generate_prompt(question_json_str):
    """ 对于连续性的提问 需要将聊天记录一起发送，用'\n\n'分隔每句话 TODO """
    print("你说 --> " + question_json_str)
    return question_json_str.capitalize()
