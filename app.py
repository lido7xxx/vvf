from flask import Flask, request, jsonify
import requests
import threading

app = Flask(__name__)

def subscribe_to_promotion(number, password, repetitions):
    try:
        url_token = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        data_token = {
            "username": number,
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

        response_token = requests.post(url_token, data=data_token, headers=headers_token)

        if response_token.status_code == 200 and "access_token" in response_token.json():
            access_token = response_token.json()["access_token"]
            url_promo = f"https://web.vodafone.com.eg/services/dxl/ramadanpromo/promotion?@type=RamadanHub&channel=website&msisdn={number}"
            headers_promo = {
                "Host": "web.vodafone.com.eg",
                "Connection": "keep-alive",
                "msisdn": number,
                "api-host": "PromotionHost",
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "x-dtreferer": "https://web.vodafone.com.eg/spa/portal/hub",
                "Accept": "application/json",
                "clientId": "WebsiteConsumer",
                "User-Agent": "Mozilla/5.0"
            }

            responses = []
            for _ in range(repetitions):
                response_promo = requests.get(url_promo, headers=headers_promo)
                responses.append(response_promo.json())

            return responses
        else:
            return {"error": "Failed to authenticate"}
    except Exception as e:
        return {"error": str(e)}

@app.route("/vvf", methods=["GET"])
def api_handler():
    try:
        number = str(request.args.get("num"))
        password = str(request.args.get("pas"))
        repetitions = int(request.args.get("reps"))

        if not number or not password or not repetitions:
            return jsonify({"error": "Missing required parameters"}), 400

        result = subscribe_to_promotion(number, password, repetitions)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
