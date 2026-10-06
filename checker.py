"""Udyam registration check ki core logic (portal se baat karne wala hissa)."""
import re

import requests

URL = "https://www.udyamregistration.gov.in/ForgotRegNo.aspx"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0 Safari/537.36"
}


def check(identifier: str):
    """Returns (status, message). status: REGISTERED / NOT_REGISTERED / INVALID / ERROR / UNKNOWN"""
    identifier = identifier.strip()
    is_email = "@" in identifier

    if is_email:
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", identifier):
            return "INVALID", "Email ka format sahi nahi hai."
    else:
        if not re.match(r"^[6789]\d{9}$", identifier):
            return "INVALID", "Mobile 10 digit ka hona chahiye, 6/7/8/9 se shuru."

    s = requests.Session()
    s.headers.update(HEADERS)

    html = s.get(URL, timeout=30).text

    def fld(name: str) -> str:
        m = re.search(r'name="%s"[^>]*value="([^"]*)"' % re.escape(name), html)
        return m.group(1) if m else ""

    viewstate = fld("__VIEWSTATE")
    if not viewstate:
        return "ERROR", "Portal se form load nahi hua. Thodi der baad retry karo."

    data = {
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": fld("__VIEWSTATEGENERATOR"),
        "__VIEWSTATEENCRYPTED": "",
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "ctl00$ContentPlaceHolder1$rblRetrieveOpt": "2",
        "ctl00$ContentPlaceHolder1$rblUamOtp": "2" if is_email else "1",
        "ctl00$ContentPlaceHolder1$txtUamNo": identifier,
        "ctl00$ContentPlaceHolder1$hdnSetPassword": "",
        "ctl00$ContentPlaceHolder1$hdnMobile": "",
        "ctl00$ContentPlaceHolder1$btnUamGetOtp": "Validate & Generate OTP",
    }

    r = s.post(URL, data=data, timeout=30)
    t = r.text

    m = re.search(
        r'id="ctl00_ContentPlaceHolder1_lblUamMsg"[^>]*>(.*?)</span>', t, re.S
    )
    msg = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""
    low = msg.lower()

    if "not registered" in low:
        return "NOT_REGISTERED", msg or "Entered Mobile/Email is not registered."
    if "otp" in low and ("sent" in low or "success" in low or "generate" in low):
        return "REGISTERED", msg
    if msg:
        return "UNKNOWN", "Portal bola: " + msg
    return "UNKNOWN", "Portal se koi clear jawab nahi mila."
