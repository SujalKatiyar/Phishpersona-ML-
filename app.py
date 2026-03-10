# =====================================================
# IMPORTS
# =====================================================
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from flask import Flask, render_template, request, session, jsonify
from flask_cors import CORS
import json
import torch
import os
import random
import numpy as np
last_email_text = None

# =====================================================
# APP INITIALIZATION
# =====================================================

app = Flask(__name__)
CORS(app)
app.secret_key = "cyber_ai_secret"

PROFILE_FILE = "user_profile.json"

# =====================================================
# LOAD MODEL
# =====================================================

tokenizer = AutoTokenizer.from_pretrained(
    "SGHOSH1999/bert-email-spam-classifier_tuned"
)

model = AutoModelForSequenceClassification.from_pretrained(
    "SGHOSH1999/bert-email-spam-classifier_tuned"
)
model.eval()

# =====================================================
# INITIALIZE USER PROFILE
# =====================================================

if not os.path.exists(PROFILE_FILE):
    profile = {
        "total_tests": 0,
        "spam_detected": 0,
        "urgency": 0,
        "authority": 0,
        "financial": 0,
        "reward": 0,
        "fear": 0
    }

    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f)


def load_profile():
    with open(PROFILE_FILE, "r") as f:
        return json.load(f)


def save_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f)


# =====================================================
# HOME (PHISHING ANALYZER)
# =====================================================

@app.route("/", methods=["GET", "POST"])
def home():

    prediction_text = ""
    probability_text = ""
    technique_text = ""
    user_message = ""
    spam_prob= 0 

    profile = load_profile()

    if request.method == "POST":

        user_message = request.form["message"]

        if not user_message.strip():
            return render_template(
                "index.html",
                prediction_text="⚠ Please enter a message to analyze.",
                probability_text="",
                technique_text="",
                user_message=""
            )

        inputs = tokenizer(
            user_message,
            return_tensors="pt",
            truncation=True,
            padding=True
        )

        with torch.no_grad():
            outputs = model(**inputs)

        probabilities = torch.softmax(outputs.logits, dim=1)

        spam_prob = probabilities[0][1].item()

        high_risk_keywords = [
            "password","verify","urgent","winner","prize","free",
            "suspended","reset","compromised",
            "investment","crypto","profit","returns",
            "refund","salary","payroll","transaction",
            "kyc","update details","billing","payment",
            "deactivation","restricted","unusual activity",
            "confirm identity","security notice",
            "compliance","audit","limited seats",
            "processing fee","registration fee","zip",'hxxps'
        ]

        keyword_hits = sum(word in user_message.lower() for word in high_risk_keywords)

        if keyword_hits == 1:
            spam_prob += 0.10
        elif keyword_hits == 2:
            spam_prob += 0.20
        elif keyword_hits >= 3:
            spam_prob += 0.30

        spam_prob = min(spam_prob,1.0)
        spam_percentage = round(spam_prob*100,2)

        techniques = []
        message_lower = user_message.lower()

        urgency_words=[
            "urgent","immediately","now","today","deadline","act fast","final notice",
            "limited time","expires","last chance","within 24 hours","time sensitive",
            "action required","asap","instant","hurry","right away","quick response",
            "final warning","respond immediately","zip",'hxxps'
        ]
        authority_words=[
            "it department","hr","compliance","audit","government","administrator",
            "security team","support team","helpdesk","official","management",
            "corporate","finance department","bank official","system administrator",
            "technical team","compliance team","company policy","legal department",
            "service desk","zip",'hxxps'
        ]
        financial_words=[
            "salary","refund","payment","billing","investment","transaction",
            "invoice","bank","account","credit card","debit card","transfer",
            "wire","balance","deposit","withdrawal","processing fee","service charge",
            "tax refund","financial verification","zip",'hxxps'
        ]
        reward_words=[
            "selected","bonus","reward","cashback","exclusive","winner",
            "prize","lottery","gift","promotion","special offer","free",
            "lucky draw","congratulations","limited offer","claim reward",
            "voucher","giveaway","discount","premium benefit","zip",'hxxps'
        ]
        fear_words=[
            "restricted","suspension","locked","violation","breach",
            "unauthorized","suspicious activity","blocked","terminated",
            "security alert","account disabled","risk detected",
            "fraud detected","policy violation","account freeze",
            "unusual activity","investigation","legal action",
            "penalty","account compromise","zip",'hxxps',"returned"
        ]

        if any(w in message_lower for w in urgency_words):
            techniques.append("Urgency")
            profile["urgency"]+=1

        if any(w in message_lower for w in authority_words):
            techniques.append("Authority")
            profile["authority"]+=1

        if any(w in message_lower for w in financial_words):
            techniques.append("Financial")
            profile["financial"]+=1

        if any(w in message_lower for w in reward_words):
            techniques.append("Reward")
            profile["reward"]+=1

        if any(w in message_lower for w in fear_words):
            techniques.append("Fear")
            profile["fear"]+=1

        if spam_prob>=0.5:
            prediction_text="⚠️ PHISHING/SPAM DETECTED"
            profile["spam_detected"]+=1
        else:
            prediction_text="✅ SAFE MESSAGE"

        probability_text=f"Spam Confidence: {spam_percentage}%"

        if techniques:
            technique_text="Detected Manipulation: "+", ".join(techniques)
        else:
            technique_text="No strong manipulation pattern detected."

        # ✅ Now safely inside the POST block!
        profile["total_tests"]+=1
        save_profile(profile)

    # ✅ This remains outside so both GET and POST requests can render the page
    return render_template(
        "index.html",
        prediction_text=prediction_text,
        probability_text=probability_text,
        technique_text=technique_text,
        user_message=user_message
    )
# =====================================================
# PROFILE DASHBOARD
# =====================================================

@app.route("/profile")
def profile():

    profile = load_profile()

    total = profile["total_tests"]
    spam = profile["spam_detected"]

    risk_score = round((spam/max(total,1))*100,2)

    if risk_score<30:
        risk_level="Low Risk 🟢"
    elif risk_score<60:
        risk_level="Moderate Risk 🟡"
    else:
        risk_level="High Risk 🔴"

    highest_trait=max(
        ["urgency","authority","financial","reward","fear"],
        key=lambda x: profile[x]
    )

    insight=f"High exposure to {highest_trait.capitalize()} based phishing attacks."

    return render_template(
        "profile.html",
        profile=profile,
        risk_score=risk_score,
        risk_level=risk_level,
        insight=insight
    )


# =====================================================
# GENERATE ATTACK MESSAGE
# =====================================================

def generate_attack(profile):

    traits=["urgency","authority","financial","reward","fear"]
    dominant=max(traits,key=lambda x:profile[x])

    attacks={

"urgency":[
"URGENT: Your Microsoft 365 account will be locked in 20 minutes. Verify here.",
"Immediate Action Required: Payroll system verification pending.",
"Final Notice: Your email storage exceeded limit. Confirm immediately.",
"Deadline Today: Update company VPN credentials now.",
"Action Required: Your corporate account will expire today.",
"Security Alert: Immediate password validation required.",
"System Warning: Login verification required within 15 minutes.",
"IT Alert: Account authentication pending. Confirm access."
],

"authority":[
"IT Security Notice: Mandatory password reset required.",
"HR Department: Compliance document pending submission.",
"Corporate Audit Team requesting verification of employee ID.",
"Government digital identity verification required.",
"Company Security Office requesting credential validation.",
"Finance Department requests confirmation of payroll account.",
"Official Notice: Policy update requires login verification.",
"Administrator Message: Security compliance check required."
],

"financial":[
"Bank Alert: Suspicious transaction detected. Verify immediately.",
"Payment gateway failed. Update card to avoid service disruption.",
"Unusual payment detected in your account. Review transaction.",
"Invoice processing failed due to payment verification error.",
"Refund of ₹4,500 pending confirmation.",
"Payment reversal detected. Confirm details to process.",
"Your bank account requires billing verification.",
"Salary transfer delayed due to account validation."
],

"reward":[
"Congratulations! You were selected for ₹50,000 cashback reward.",
"Exclusive loyalty reward unlocked. Claim now.",
"You have been selected for a premium customer bonus.",
"Limited offer: Claim your Amazon reward voucher.",
"Congratulations! Your account qualified for loyalty cashback.",
"Special festive reward waiting for you. Claim now.",
"Exclusive customer appreciation reward unlocked.",
"Bonus payout ready. Verify account to receive funds."
],

"fear":[
"Security Alert: Your account may be restricted due to suspicious activity.",
"Compliance Violation: Your account is under review.",
"Your account has been flagged for suspicious login attempts.",
"Warning: Multiple failed login attempts detected.",
"Policy violation detected in your account activity.",
"Security Notice: Unusual device login detected.",
"Account monitoring system detected abnormal behavior.",
"Immediate review required due to compliance violation."
]

}

    return random.choice(attacks[dominant])


# =====================================================
# AI DEFENCE ADVISORY GENERATOR
# =====================================================

def generate_advisory(profile):

    traits=["urgency","authority","financial","reward","fear"]

    sorted_traits=sorted(traits,key=lambda x:profile[x],reverse=True)
    top3=tuple(sorted_traits[:3])

    advisory_map={

    ("urgency","authority","financial"):
    """Your activity shows vulnerability to **urgent requests from authority figures involving financial actions**.
Attackers may impersonate IT administrators, bank officials, or HR staff and pressure you to immediately verify payments or credentials.

Always pause when a message demands immediate financial action. Verify requests directly through official company portals or banking apps instead of links sent through messages. Real organizations rarely demand instant financial verification under pressure.""",

    ("urgency","financial","fear"):
    """Your behavioral signals indicate susceptibility to **financial panic scams**.
Attackers may claim suspicious transactions, failed payments, or account blocks to rush you into clicking malicious links.

If you receive sudden financial alerts, never react immediately through the provided link. Instead, log into the official banking website or mobile app directly to verify the alert.""",

    ("authority","fear","urgency"):
    """Your pattern suggests attackers may exploit **authority based pressure tactics**.
Fraudsters may impersonate IT departments, compliance officers, or government officials and create fear of penalties or account suspension.

Remember that legitimate organizations rarely threaten immediate punishment via email or SMS. Always verify the sender domain and confirm through official communication channels.""",

    ("reward","financial","urgency"):
    """Your profile shows increased exposure to **reward driven phishing attacks**.
These scams often promise cashback rewards, prizes, or loyalty benefits but require urgent verification of payment or card details.

Be cautious when unexpected rewards require financial information. Authentic promotions never request sensitive financial credentials through links.""",

    ("fear","authority","financial"):
    """Your behavioral pattern indicates vulnerability to **security warning scams**.
Attackers may send alarming messages claiming policy violations, security breaches, or account restrictions while impersonating authority figures.

Treat unexpected security alerts carefully and verify them directly through official platforms rather than email links.""",

    ("reward","urgency","fear"):
    """Your activity indicates susceptibility to **emotional manipulation scams combining reward and fear**.
Attackers may promise valuable rewards but warn that they will expire immediately unless you act.

Avoid reacting to time-limited offers that require personal or financial information. Genuine companies provide adequate time and official verification.""",

    ("authority","financial","reward"):
    """Your behavioral signals suggest attackers may combine **authority impersonation with financial incentives**.
For example, fake HR announcements promising bonuses or refunds that require credential verification.

Always confirm such announcements through official company portals or by contacting the department directly.""",

    ("fear","urgency","authority"):
    """Your risk profile suggests attackers may trigger **fear driven urgency using authority impersonation**.
Examples include fake government notices, compliance warnings, or IT security alerts demanding immediate action.

Pause before responding to threatening messages and verify them through official channels.""",

    ("financial","reward","urgency"):
    """Your behavior suggests vulnerability to **financial reward scams with urgency pressure**.
These scams promise fast profits, cashback rewards, or investment opportunities that require immediate payment or verification.

Be cautious of any opportunity promising unusually high financial gain within a short period.""",

    ("authority","urgency","reward"):
    """Your pattern indicates attackers may exploit **authority backed incentives**.
For example, a fake company executive offering a limited-time reward or bonus requiring quick action.

Always verify executive communications and reward announcements through internal company systems."""
    }

    advisory = advisory_map.get(top3)

    if not advisory:
        advisory=f"""
Your behavioral phishing profile indicates higher exposure to **{top3[0].capitalize()}**, 
**{top3[1].capitalize()}**, and **{top3[2].capitalize()}** manipulation tactics.

Attackers may combine these psychological triggers to pressure quick decisions, impersonate trusted authorities, or manipulate financial and reward based incentives.

Always pause before responding to urgent requests, verify the sender identity through official sources, and avoid clicking links requesting sensitive information.
"""

    return advisory


# =====================================================
# ADAPTIVE AI SIMULATION
# =====================================================

@app.route("/adaptive")
def adaptive():

    profile = load_profile()

    features = np.array([[
        profile["urgency"],
        profile["authority"],
        profile["financial"],
        profile["reward"],
        profile["fear"],
        profile["spam_detected"],
        profile["total_tests"]
    ]])

    advisory_model_output = "Adaptive advisory generated"

    advisory = generate_advisory(profile)

    message = generate_attack(profile)

    return render_template(
        "adaptive.html",
        advisory=advisory,
        advisory_model_output=advisory_model_output,
        message=message,
        profile=profile
    )


# =====================================================
# ADVANCED TRAINING QUESTION BANK
# =====================================================

training_sets=[

[
("Your bank asks you to verify account via secure-update-bank.net","phishing"),
("Your Slack workspace login alert from slack.com","safe"),
("HR requests salary revision form through Google Drive link","phishing"),
("GitHub security notification from github.com","safe"),
("Courier service asking ₹5 customs fee via unknown link","phishing")
],

[
("Amazon order invoice from amazon.in","safe"),
("Income tax refund requiring card verification","phishing"),
("Google password reset you requested","safe"),
("Crypto investment promising 300% profit","phishing"),
("Office VPN login alert from official portal","safe")
],

[
("LinkedIn login verification from linkedin.com","safe"),
("You won free airline tickets click link","phishing"),
("Bank OTP for payment you initiated","safe"),
("Netflix payment failed update card","phishing"),
("Dropbox file shared by colleague","safe")
],

[
("Company meeting invite via Outlook","safe"),
("Government subsidy asking processing fee","phishing"),
("PayPal login alert from paypal.com","safe"),
("Urgent KYC verification via unknown domain","phishing"),
("University portal password change confirmation","safe")
],

[
("Your Apple ID login alert from apple.com","safe"),
("Lottery reward claiming ₹1 lakh prize","phishing"),
("Google security notification for new device","safe"),
("Courier delivery asking address verification link","phishing"),
("Company payroll update via internal portal","safe")
],

# ---------------- NEW SETS ADDED ----------------

[
("Microsoft Teams asks you to re-login through teams-security-check.net","phishing"),
("Your company VPN login alert from official vpn.company.com","safe"),
("Income tax department asking KYC through sms-taxrefund.link","phishing"),
("Dropbox shared folder notification from dropbox.com","safe"),
("Urgent payroll correction form through unknown HR portal","phishing")
],

[
("Google security alert for new device login from google.com","safe"),
("Congratulations! Claim your ₹10,000 cashback reward now","phishing"),
("Your bank transaction OTP from official bank SMS","safe"),
("Investment opportunity promising guaranteed 200% returns","phishing"),
("Zoom meeting invite sent by your colleague","safe")
],

[
("Courier company requesting ₹2 address verification fee","phishing"),
("Slack password reset you requested","safe"),
("Government electricity subsidy asking bank verification","phishing"),
("GitHub repository access granted email","safe"),
("Netflix account suspended update payment immediately","phishing")
],

[
("Your university portal login alert","safe"),
("Crypto exchange asking urgent wallet verification","phishing"),
("LinkedIn connection request notification","safe"),
("Bank asking card verification via unknown domain","phishing"),
("Company HR sending official leave policy update","safe")
],

[
("Paytm payment received notification","safe"),
("Lottery winner announcement requiring processing fee","phishing"),
("Amazon delivery update from amazon.in","safe"),
("Your email storage almost full click to upgrade","phishing"),
("Office calendar meeting invitation","safe")
],

[
("Apple ID password change confirmation","safe"),
("Urgent compliance audit notice requiring credential verification","phishing"),
("Microsoft account sign-in alert from microsoft.com","safe"),
("Bank KYC update through suspicious shortened link","phishing"),
("Company internal newsletter email","safe")
],

[
("Your package is waiting pay ₹3 delivery charge","phishing"),
("Google Drive document shared with you","safe"),
("Exclusive airline reward claim within 10 minutes","phishing"),
("Office VPN access notification","safe"),
("Government tax refund requiring login via unknown link","phishing")
],

[
("PayPal payment confirmation from paypal.com","safe"),
("Crypto mining investment offer promising daily profits","phishing"),
("GitHub login verification email","safe"),
("Urgent account suspension notice from fake bank domain","phishing"),
("Company Slack workspace invitation","safe")
]

]


# =====================================================
# TRAINING MODE
# =====================================================

@app.route("/training",methods=["GET","POST"])
def training():

    if "score" not in session:
        session["score"]=0
        session["q"]=0
        session["set"]=random.choice(training_sets)

    if request.method=="POST":

        user_answer=request.form["answer"]
        correct_answer=request.form["correct"]

        if user_answer==correct_answer:
            session["score"]+=1

        session["q"]+=1

        if session["q"]==5:

            final_score=session["score"]

            if final_score>=4:
                feedback="Excellent phishing awareness!"
            elif final_score>=2:
                feedback="Moderate awareness."
            else:
                feedback="High phishing susceptibility."

            session.clear()

            return render_template(
                "training.html",
                finished=True,
                score=final_score,
                feedback=feedback
            )

    q_index=session["q"]
    question,correct=session["set"][q_index]

    return render_template(
        "training.html",
        message=question,
        correct_answer=correct,
        q_number=q_index+1,
        finished=False
    )


# =====================================================
# RESET PROFILE
# =====================================================

@app.route("/reset")
def reset():

    fresh_profile={
        "total_tests":0,
        "spam_detected":0,
        "urgency":0,
        "authority":0,
        "financial":0,
        "reward":0,
        "fear":0
    }

    save_profile(fresh_profile)

    return render_template(
        "profile.html",
        profile=fresh_profile,
        risk_score=0,
        risk_level="Low Risk 🟢",
        insight="Profile reset successfully."
    )

# =====================================================
# API TO SCAN EMAIL DIRECTLY (FOR EXTENSION)
# =====================================================
@app.route("/api/check_email", methods=["POST"])
def api_check_email():

    global last_email_text

    data = request.json
    user_message = data.get("email_text", "").strip()
    source = data.get("source", "gmail")
    if source == "analyzer":
        return jsonify({
            "prediction": "IGNORED",
            "spam_probability": 0
        })

    # 🚫 Ignore empty/default messages
    if not user_message or len(user_message) < 20:
        return jsonify({
            "prediction": "IGNORED",
            "spam_probability": 0
        })
    

    # 🚫 Ignore duplicate emails
    if user_message == last_email_text:
        return jsonify({
            "prediction": "IGNORED",
            "spam_probability": 0
        })

    # Save current email
    last_email_text = user_message

    profile = load_profile()

    inputs = tokenizer(
        user_message,
        return_tensors="pt",
        truncation=True,
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.softmax(outputs.logits, dim=1)

    spam_prob = probabilities[0][1].item()
    spam_percentage = round(spam_prob * 100, 2)

    # 🚫 Ignore analyzer default cycle
    if spam_percentage == 0:
        return jsonify({
            "prediction": "SAFE EMAIL",
            "spam_probability": 0
        })

    message_lower = user_message.lower()

    # Track whether a behavioral trigger is found
    trigger_found = False

    # Detect behavioral manipulation techniques
    if "urgent" in message_lower:
        profile["urgency"] += 1
        trigger_found = True

    if "bank" in message_lower or "payment" in message_lower:
        profile["financial"] += 1
        trigger_found = True

    if "winner" in message_lower or "prize" in message_lower:
        profile["reward"] += 1
        trigger_found = True

    if "security" in message_lower or "restricted" in message_lower:
        profile["fear"] += 1
        trigger_found = True

    if "admin" in message_lower or "hr" in message_lower:
        profile["authority"] += 1
        trigger_found = True


    # Prediction logic
    if spam_prob >= 0.5:
        prediction = "PHISHING/SPAM DETECTED"
        profile["spam_detected"] += 1

        # If spam but no trigger found, assign fear category
        if not trigger_found:
            profile["fear"] += 1

    else:
        prediction = "SAFE EMAIL"


    # Update total tests
    profile["total_tests"] += 1

    save_profile(profile)

    return jsonify({
        "prediction": prediction,
        "spam_probability": spam_percentage
    })


@app.route("/api/profile_data")
def profile_data():
    return jsonify(load_profile())
# =====================================================
# RUN APPLICATION
# =====================================================

if __name__=="__main__":
    app.run(debug=True)
