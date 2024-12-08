from flask import Flask, request, jsonify
import requests
import threading
import re

app = Flask(__name__)

# دالة لتفعيل العرض
def subscribe_to_promotion(username, password, attempt):
    try:
        url_token = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        data_token = {
            "username": username,
            "password": password,
            "grant_type": "password",
            "client_secret": "a2ec6fff-0b7f-4aa4-a733-96ceae5c84c3",
            "client_id": "my-vodafone-app"
        }
        headers_token = {
            "Accept": "application/json, text/plain, */*",
            "Connection": "keep-alive",
            "x-agent-operatingsystem": "10.1.0.264C185",
            "clientId": "AnaVodafoneAndroid",
            "x-agent-device": "HWDRA-MR",
            "x-agent-version": "2022.1.2.3",
            "x-agent-build": "500",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "okhttp/4.9.1"
        }

        # طلب التوكن
        response_token = requests.post(url_token, data=data_token, headers=headers_token)

        if response_token.status_code == 200 and "access_token" in response_token.json():
            access_token = response_token.json()["access_token"]

            # استدعاء العرض
            url_promo = "https://web.vodafone.com.eg/services/dxl/promo/promotion?@type=Promo&$.context.type=rechargeProgram"
            headers_promo = {
                "Host": "web.vodafone.com.eg",
                "Connection": "keep-alive",
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "vodafoneandroid",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "clientId": "WebsiteConsumer",
                "channel": "APP_PORTAL"
            }

            response_promo = requests.get(url_promo, headers=headers_promo)
            if response_promo.status_code == 200:
                return {"status": "success", "message": f"Attempt {attempt} succeeded!"}
            else:
                return {"status": "failed", "message": f"Attempt {attempt} failed."}
        else:
            return {"status": "error", "message": "Authentication failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# API لاستدعاء الوظيفة عبر HTTP
@app.route("/voda", methods=["GET"])
def api_handler():
    try:
        username = request.args.get("username")
        password = request.args.get("password")
        repetitions = int(request.args.get("repetitions", 1))

        if not username or not password or repetitions < 1:
            return jsonify({"error": "Missing or invalid parameters"}), 400

        results = []
        threads = []

        def worker(attempt):
            result = subscribe_to_promotion(username, password, attempt)
            results.append(result)

        for attempt in range(1, repetitions + 1):
            thread = threading.Thread(target=worker, args=(attempt,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
