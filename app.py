from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os
import traceback

app = Flask(__name__)

QQ_EMAIL = os.environ.get("QQ_EMAIL")
QQ_AUTH_CODE = os.environ.get("QQ_AUTH_CODE")


@app.route("/")
def home():
    return "QQ Mail Agent API 运行成功！"


@app.route("/send-email", methods=["POST"])
def send_email():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "没有收到JSON数据"
            }), 400

        to_email = data.get("to")
        subject = data.get("subject")
        content = data.get("content")

        if not to_email or not subject or not content:
            return jsonify({
                "success": False,
                "message": "缺少 to、subject 或 content"
            }), 400

        if not QQ_EMAIL or not QQ_AUTH_CODE:
            return jsonify({
                "success": False,
                "message": "QQ邮箱环境变量没有读取到"
            }), 500

        message = MIMEText(content, "plain", "utf-8")
        message["From"] = QQ_EMAIL
        message["To"] = to_email
        message["Subject"] = Header(subject, "utf-8")

        # QQ邮箱 SMTP：587端口 + STARTTLS
        server = smtplib.SMTP(
            "smtp.qq.com",
            587,
            timeout=20
        )

        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(
            QQ_EMAIL,
            QQ_AUTH_CODE
        )

        server.sendmail(
            QQ_EMAIL,
            [to_email],
            message.as_string()
        )

        server.quit()

        return jsonify({
            "success": True,
            "message": "邮件发送成功",
            "to": to_email
        })

    except Exception as e:
        print("========== EMAIL ERROR ==========")
        print("错误类型:", type(e).__name__)
        print("错误信息:", str(e))
        traceback.print_exc()
        print("=================================")

        return jsonify({
            "success": False,
            "error": type(e).__name__,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )