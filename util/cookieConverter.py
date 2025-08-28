import json

with open('cookies.json', 'r') as f:
    cookies = json.load(f)

pw_cookies = []
for c in cookies:
    cookie = {
        "name": c["name"],
        "value": c["value"],
        "domain": c["domain"],
        "path": c.get("path", "/"),
        "httpOnly": c.get("httpOnly", False),
        "secure": c.get("secure", False),
    }

    # convert expirationDate → expires
    if "expirationDate" in c:
        cookie["expires"] = int(c["expirationDate"])

    # convert sameSite
    ss = c.get("sameSite")
    if ss:
        if ss == "no_restriction":
            cookie["sameSite"] = "None"
        elif ss in ["lax", "Lax"]:
            cookie["sameSite"] = "Lax"
        elif ss in ["strict", "Strict"]:
            cookie["sameSite"] = "Strict"

    pw_cookies.append(cookie)

with open("pw_cookies.json", "w") as f:
    json.dump(pw_cookies, f, indent=2)

print("✅ Converted cookies saved to pw_cookies.json")
