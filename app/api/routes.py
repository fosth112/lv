from flask import jsonify, request, Blueprint, Response
import requests
import binascii
from datetime import datetime
import json
from app.core.jwt_token import get_jwt
from app.core.encrypt import Encrypt_ID, encrypt_api
from app.core.parser import get_available_room

routes = Blueprint("routes", __name__)


def fetch_player_data(player_id):
    token = get_jwt()
    if not token:
        raise Exception("JWT Token is empty")

    try:
        encrypted = encrypt_api(f"08{Encrypt_ID(player_id)}1007")
        data = bytes.fromhex(encrypted)
    except Exception as e:
        raise Exception("Failed to encrypt payload")

    url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
    headers = {
        "X-Unity-Version": "2018.4.11f1",
        "ReleaseVersion": "OB48",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-GA": "v1 1",
        "Authorization": f"Bearer {token}",
        "Content-Length": "16",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)",
        "Host": "clientbp.ggblueshark.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }

    response = requests.post(url, headers=headers, data=data, verify=False)

    if response.status_code != 200:
        raise Exception(f"API request failed with status code: {response.status_code}")

    hex_response = binascii.hexlify(response.content).decode("utf-8")
    parsed = json.loads(get_available_room(hex_response))
    return parsed


@routes.route("/api/player-info", methods=["GET"])
def get_player_info():
    player_id = request.args.get("id")
    if not player_id:
        return jsonify({
            "status": "error",
            "message": "Player ID is required",
            "credits": "nexxlokesh",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }), 400

    try:
        parsed_data = fetch_player_data(player_id)

        player_data = {
            "playerInformation": {
                "name": parsed_data["1"]["data"]["3"]["data"],
                "uid": player_id,
                "likes": parsed_data["1"]["data"]["21"]["data"],
                "level": parsed_data["1"]["data"]["6"]["data"],
                "server": parsed_data["1"]["data"]["5"]["data"],
                "signature": parsed_data["9"]["data"]["9"]["data"],
                "booyah_pass_level": parsed_data["1"]["data"]["18"]["data"],
                "account_created": datetime.fromtimestamp(
                    parsed_data["1"]["data"]["44"]["data"]
                ).strftime("%Y-%m-%d %H:%M:%S"),
            }
        }

        try:
            player_data["animal"] = {
                "name": parsed_data["8"]["data"]["2"]["data"]
            }
        except:
            player_data["animal"] = None

        try:
            player_data["Guild"] = {
                "guildName": parsed_data["6"]["data"]["2"]["data"],
                "guildId": parsed_data["6"]["data"]["1"]["data"],
                "guildLevel": parsed_data["6"]["data"]["4"]["data"],
                "guildMembers": parsed_data["6"]["data"]["6"]["data"],
                "guildLeader": {
                    "uid": parsed_data["6"]["data"]["3"]["data"],
                    "nickName": parsed_data["7"]["data"]["3"]["data"],
                    "playerLevel": parsed_data["7"]["data"]["6"]["data"],
                    "booyah_pass_level": parsed_data["7"]["data"]["18"]["data"],
                    "likes": parsed_data["7"]["data"]["21"]["data"],
                    "account_created": datetime.fromtimestamp(
                        parsed_data["7"]["data"]["44"]["data"]
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                },
            }
        except:
            player_data["Guild"] = None

        return Response(
            json.dumps({"data": player_data, "credits": "nexxlokesh"}, indent=2),
            mimetype="application/json"
        )

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "credits": "nexxlokesh"
        }), 500


@routes.route("/api/check-lv", methods=["GET"])
def check_lv():
    player_id = request.args.get("id")
    if not player_id:
        return jsonify({"status": "error", "message": "Player ID is required"}), 400

    try:
        parsed_data = fetch_player_data(player_id)
        name = parsed_data["1"]["data"]["3"]["data"]
        level = int(parsed_data["1"]["data"]["6"]["data"])

        return jsonify({
            "uid": player_id,
            "name": name,
            "level": level,
            "status": "✅ ผ่าน (LV ≥ 30)" if level >= 30 else "❌ ไม่ผ่าน (LV < 30)"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
