# ============================================================
# app.py — Complete Flask App
# ============================================================

from flask import Flask, render_template, request, redirect, \
                  session, jsonify, make_response
import pickle
import pandas as pd
import secrets
import io
from datetime import datetime, timedelta
from flask_mail import Mail, Message
from database import (
    init_db, create_user, get_user_by_email, get_user_by_id,
    get_user_by_token, verify_user_email, update_user_profile,
    get_all_users, save_prediction, get_user_predictions,
    get_prediction_by_id, get_latest_prediction, delete_prediction,
    get_all_predictions, save_facial_result, get_latest_facial_result,
    save_combined_result, get_user_combined_results,
    get_user_stats, get_admin_stats
)
from facial_tracker import run_facial_tracking

app = Flask(__name__)
app.secret_key = 'autism_prediction_secret_key_2024'

# ============================================================
# EMAIL CONFIG
# ============================================================
app.config['MAIL_SERVER']         = 'smtp.gmail.com'
app.config['MAIL_PORT']           = 587
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USERNAME']       = 'avikdasiitkharagpur@gmail.com'
app.config['MAIL_PASSWORD']       = 'jmklxufbnwupgxxc'
app.config['MAIL_DEFAULT_SENDER'] = ('AutismAI',
                                     'avikdasiitkharagpur@gmail.com')
mail = Mail(app)

reset_tokens = {}

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('columns.pkl', 'rb') as f:
    columns = pickle.load(f)

init_db()
print("App ready!")


# ============================================================
# EMAIL FUNCTIONS
# ============================================================

def send_verification_email(name, email, token):
    link = f"http://127.0.0.1:5000/verify-email/{token}"
    try:
        msg         = Message("Verify Your AutismAI Email ✅",
                              recipients=[email])
        msg.html    = f"""
        <div style="font-family:Segoe UI,sans-serif;max-width:600px;
                    margin:0 auto;background:#0f0f1a;color:#e2e8f0;
                    border-radius:16px;overflow:hidden;">
            <div style="background:linear-gradient(135deg,#7c3aed,#3b82f6);
                        padding:40px;text-align:center;">
                <h1 style="color:white;margin:0;font-size:28px;">🧠 AutismAI</h1>
                <p style="color:rgba(255,255,255,0.85);margin-top:8px;">
                    Email Verification
                </p>
            </div>
            <div style="padding:40px;">
                <h2 style="color:#a78bfa;">Hello, {name}!</h2>
                <p style="color:#94a3b8;line-height:1.8;">
                    Thank you for signing up. Please verify your email
                    address to activate your account.
                </p>
                <div style="text-align:center;margin:32px 0;">
                    <a href="{link}"
                       style="background:linear-gradient(135deg,#7c3aed,#3b82f6);
                              color:white;padding:14px 32px;border-radius:10px;
                              text-decoration:none;font-weight:600;font-size:16px;">
                        ✅ Verify My Email
                    </a>
                </div>
                <div style="background:#1e1e3f;border:1px solid #2d2d5e;
                            border-radius:12px;padding:20px;margin:24px 0;">
                    <p style="color:#94a3b8;margin:0;font-size:14px;">
                        🔗 Or copy this link:<br>
                        <span style="color:#a78bfa;word-break:break-all;">
                            {link}
                        </span>
                    </p>
                </div>
                <p style="color:#94a3b8;font-size:14px;">
                    ⏰ This link expires in <strong>24 hours</strong>.
                </p>
            </div>
            <div style="background:#1a1a2e;padding:20px;text-align:center;
                        border-top:1px solid #2d2d5e;">
                <p style="color:#64748b;font-size:12px;margin:0;">
                    © 2024 AutismAI — College Project
                </p>
            </div>
        </div>"""
        mail.send(msg)
        print(f"Verification email sent to {email}")
    except Exception as e:
        print(f"Verification email error: {e}")


def send_welcome_email(name, email):
    try:
        msg      = Message("Welcome to AutismAI 🧠", recipients=[email])
        msg.html = f"""
        <div style="font-family:Segoe UI,sans-serif;max-width:600px;
                    margin:0 auto;background:#0f0f1a;color:#e2e8f0;
                    border-radius:16px;overflow:hidden;">
            <div style="background:linear-gradient(135deg,#7c3aed,#3b82f6);
                        padding:40px;text-align:center;">
                <h1 style="color:white;margin:0;font-size:28px;">🧠 AutismAI</h1>
            </div>
            <div style="padding:40px;">
                <h2 style="color:#a78bfa;">Welcome, {name}! 🎉</h2>
                <p style="color:#94a3b8;line-height:1.8;">
                    Your email has been verified and your account is now
                    fully active. You can now use all features of AutismAI.
                </p>
                <div style="background:#1e1e3f;border:1px solid #2d2d5e;
                            border-radius:12px;padding:24px;margin:24px 0;">
                    <h3 style="color:#a78bfa;margin-top:0;">
                        What you can do:
                    </h3>
                    <ul style="color:#94a3b8;line-height:2;">
                        <li>✅ Take the AQ-10 autism screening questionnaire</li>
                        <li>🎥 Run the facial behaviour analysis</li>
                        <li>📊 Get combined results with recommendations</li>
                        <li>📄 Download your screening report as PDF</li>
                    </ul>
                </div>
                <div style="text-align:center;margin:32px 0;">
                    <a href="http://127.0.0.1:5000/screen"
                       style="background:linear-gradient(135deg,#7c3aed,#3b82f6);
                              color:white;padding:14px 32px;border-radius:10px;
                              text-decoration:none;font-weight:600;">
                        Start Screening
                    </a>
                </div>
            </div>
            <div style="background:#1a1a2e;padding:20px;text-align:center;
                        border-top:1px solid #2d2d5e;">
                <p style="color:#64748b;font-size:12px;margin:0;">
                    © 2024 AutismAI — College Project
                </p>
            </div>
        </div>"""
        mail.send(msg)
    except Exception as e:
        print(f"Welcome email error: {e}")


def send_reset_email(name, email, token):
    link = f"http://127.0.0.1:5000/reset-password/{token}"
    try:
        msg      = Message("Reset Your AutismAI Password 🔒",
                           recipients=[email])
        msg.html = f"""
        <div style="font-family:Segoe UI,sans-serif;max-width:600px;
                    margin:0 auto;background:#0f0f1a;color:#e2e8f0;
                    border-radius:16px;overflow:hidden;">
            <div style="background:linear-gradient(135deg,#7c3aed,#3b82f6);
                        padding:40px;text-align:center;">
                <h1 style="color:white;margin:0;">🧠 AutismAI</h1>
                <p style="color:rgba(255,255,255,0.85);margin-top:8px;">
                    Password Reset
                </p>
            </div>
            <div style="padding:40px;">
                <h2 style="color:#a78bfa;">Hello, {name}!</h2>
                <p style="color:#94a3b8;line-height:1.8;">
                    Click below to reset your password.
                    This link expires in 15 minutes.
                </p>
                <div style="text-align:center;margin:32px 0;">
                    <a href="{link}"
                       style="background:linear-gradient(135deg,#7c3aed,#3b82f6);
                              color:white;padding:14px 32px;border-radius:10px;
                              text-decoration:none;font-weight:600;">
                        Reset My Password
                    </a>
                </div>
                <p style="color:#64748b;font-size:13px;">
                    If you did not request this, ignore this email.
                </p>
            </div>
        </div>"""
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Reset email error: {e}")
        return False


# ============================================================
# COMBINED SCORE CALCULATOR
# ============================================================

def calculate_combined(aq10_result, aq10_confidence,
                       behavioral_score):
    """
    Combines AQ-10 ML result with facial behavioral score.
    AQ-10 weight: 60% (clinically validated questionnaire)
    Facial weight: 40% (supplementary behavioral data)
    """
    # Convert AQ-10 to a 0-100 score
    # If Autism Detected: risk score = confidence (high = more risk)
    # If No Autism:       risk score = 100 - confidence (low risk)
    if aq10_result == "Autism Detected":
        aq10_risk_score = aq10_confidence
    else:
        aq10_risk_score = 100 - aq10_confidence

    # Facial behavioral score is already 0-100
    # Higher behavioral score = more typical = LOWER risk
    # Convert to risk score
    facial_risk_score = 100 - behavioral_score

    # Combined risk score (higher = more risk)
    combined_risk_score = (aq10_risk_score * 0.60 +
                           facial_risk_score * 0.40)

    # Final combined score (higher = lower risk = better)
    combined_score = round(100 - combined_risk_score, 2)

    # Risk classification
    if combined_score >= 65:
        combined_risk = "Low Risk — Autism Unlikely"
        risk_level    = "low"
    elif combined_score >= 40:
        combined_risk = "Moderate Risk — Further Assessment Recommended"
        risk_level    = "moderate"
    else:
        combined_risk = "High Risk — Professional Consultation Strongly Advised"
        risk_level    = "high"

    return combined_score, combined_risk, risk_level


def get_recommendations(risk_level, aq10_result, behavioral_score):
    """Generate personalized recommendations based on results"""

    dos   = []
    donts = []

    if risk_level == "low":
        dos = [
            "Continue monitoring behaviour and development regularly",
            "Maintain open communication with family members about any changes",
            "Engage in regular social activities and group interactions",
            "Take this screening again in 6 months if you have concerns",
            "Learn more about autism to better support others around you"
        ]
        donts = [
            "Do not ignore any new behavioral changes that develop over time",
            "Do not skip routine developmental checkups with your doctor",
            "Do not rely solely on this screening — it is not a diagnosis",
            "Do not assume a low score means no support is ever needed"
        ]
    elif risk_level == "moderate":
        dos = [
            "Schedule an appointment with a licensed psychologist or psychiatrist",
            "Keep a daily diary of behavioral patterns and social interactions",
            "Discuss your screening results with a trusted healthcare professional",
            "Explore autism support resources and community groups in your area",
            "Consider taking this screening again with facial analysis for comparison",
            "Share these results with a family member or trusted adult"
        ]
        donts = [
            "Do not self-diagnose based on this screening result alone",
            "Do not ignore the recommendation for professional assessment",
            "Do not delay seeking help — early intervention leads to better outcomes",
            "Do not let anxiety about results prevent you from seeking support",
            "Do not share your results publicly without speaking to a professional first"
        ]
    else:
        dos = [
            "Seek an immediate appointment with a qualified autism specialist",
            "Contact your nearest autism assessment center for formal evaluation",
            "Inform a trusted family member or guardian about these results",
            "Document all behavioral patterns and bring notes to your appointment",
            "Reach out to autism support organizations for immediate guidance",
            "Ask your doctor about Applied Behavior Analysis (ABA) therapy options",
            "Connect with local autism support groups for community assistance"
        ]
        donts = [
            "Do not ignore these results — multiple indicators suggest high risk",
            "Do not self-medicate or seek unverified treatments online",
            "Do not delay professional evaluation — early diagnosis is critical",
            "Do not isolate yourself — support from others is essential",
            "Do not assume the worst — many people with ASD lead fulfilling lives",
            "Do not make major life decisions based solely on this screening"
        ]

    return dos, donts


# ============================================================
# HOME
# ============================================================
@app.route('/')
def home():
    return render_template('index.html')


# ============================================================
# SIGN UP
# ============================================================
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name     = request.form['name'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password']

        if len(name) < 2:
            return render_template('signup.html',
                error="Please enter your full name.")
        if len(password) < 6:
            return render_template('signup.html',
                error="Password must be at least 6 characters.")

        # Generate email verification token
        verify_token = secrets.token_urlsafe(32)

        user = create_user(name, email, password, verify_token)
        if user is None:
            return render_template('signup.html',
                error="Email already registered. Please login.")

        # Send verification email
        send_verification_email(name, email, verify_token)

        return render_template('signup.html',
            success="Account created! Please check your email to verify your account before logging in.")

    return render_template('signup.html')


# ============================================================
# VERIFY EMAIL
# ============================================================
@app.route('/verify-email/<token>')
def verify_email(token):
    user = get_user_by_token(token)
    if not user:
        return render_template('verify_email.html',
            status="error",
            message="Invalid or expired verification link.")

    verify_user_email(user['id'])

    # Send welcome email after verification
    send_welcome_email(user['name'], user['email'])

    return render_template('verify_email.html',
        status="success",
        message=f"Email verified successfully! Welcome, {user['name']}!")


# ============================================================
# LOGIN
# ============================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        user     = get_user_by_email(email)

        if user is None or user['password'] != password:
            return render_template('login.html',
                error="Invalid email or password.")

        # Check email verified
        if not user['is_verified']:
            return render_template('login.html',
                error="Please verify your email first. Check your inbox for the verification link.")

        session['user_id']  = user['id']
        session['name']     = user['name']
        session['email']    = user['email']
        session['is_admin'] = bool(user['is_admin'])
        return redirect('/dashboard')

    return render_template('login.html')


# ============================================================
# LOGOUT
# ============================================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ============================================================
# FORGOT PASSWORD
# ============================================================
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        user  = get_user_by_email(email)
        if user:
            token      = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(minutes=15)
            reset_tokens[token] = {
                'email': email, 'expires_at': expires_at
            }
            send_reset_email(user['name'], email, token)
        return render_template('forgot_password.html', success=True)
    return render_template('forgot_password.html', success=False)


# ============================================================
# RESET PASSWORD
# ============================================================
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    token_data = reset_tokens.get(token)

    if not token_data:
        return render_template('reset_password.html',
            error="Invalid or expired link.", token=None)

    if datetime.now() > token_data['expires_at']:
        reset_tokens.pop(token, None)
        return render_template('reset_password.html',
            error="Link expired. Please request a new one.", token=None)

    if request.method == 'POST':
        new_password = request.form['password']
        confirm      = request.form['confirm_password']

        if len(new_password) < 6:
            return render_template('reset_password.html',
                error="Password must be at least 6 characters.", token=token)
        if new_password != confirm:
            return render_template('reset_password.html',
                error="Passwords do not match.", token=token)

        import sqlite3
        conn = sqlite3.connect('autism.db')
        conn.execute('UPDATE users SET password = ? WHERE email = ?',
                     (new_password, token_data['email']))
        conn.commit()
        conn.close()
        reset_tokens.pop(token, None)
        return redirect('/login?reset=success')

    return render_template('reset_password.html', error=None, token=token)


# ============================================================
# DASHBOARD
# ============================================================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    history          = get_user_predictions(session['user_id'])
    stats            = get_user_stats(session['user_id'])
    combined_results = get_user_combined_results(session['user_id'])
    latest_facial    = get_latest_facial_result(session['user_id'])
    latest_pred      = get_latest_prediction(session['user_id'])

    return render_template('dashboard.html',
                           name=session['name'],
                           history=history,
                           stats=stats,
                           combined_results=combined_results,
                           latest_facial=latest_facial,
                           latest_pred=latest_pred)


# ============================================================
# DELETE PREDICTION
# ============================================================
@app.route('/delete/<int:prediction_id>', methods=['POST'])
def delete(prediction_id):
    if 'user_id' not in session:
        return redirect('/login')
    delete_prediction(prediction_id, session['user_id'])
    return redirect('/dashboard')


# ============================================================
# SCREENING FORM
# ============================================================
@app.route('/screen')
def screen():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('screen.html')


# ============================================================
# PREDICT
# ============================================================
@app.route('/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return redirect('/login')

    input_data = {
        'A1_Score':        int(request.form['A1_Score']),
        'A2_Score':        int(request.form['A2_Score']),
        'A3_Score':        int(request.form['A3_Score']),
        'A4_Score':        int(request.form['A4_Score']),
        'A5_Score':        int(request.form['A5_Score']),
        'A6_Score':        int(request.form['A6_Score']),
        'A7_Score':        int(request.form['A7_Score']),
        'A8_Score':        int(request.form['A8_Score']),
        'A9_Score':        int(request.form['A9_Score']),
        'A10_Score':       int(request.form['A10_Score']),
        'age':             int(request.form['age']),
        'gender':          int(request.form['gender']),
        'ethnicity':       int(request.form['ethnicity']),
        'jundice':         int(request.form['jundice']),
        'austim':          int(request.form['austim']),
        'contry_of_res':   int(request.form['contry_of_res']),
        'used_app_before': int(request.form['used_app_before']),
        'relation':        int(request.form['relation']),
    }

    input_df       = pd.DataFrame([input_data])
    input_df       = input_df[columns]
    prediction     = model.predict(input_df)[0]
    probability    = model.predict_proba(input_df)[0]

    result         = "Autism Detected" if prediction == 1 \
                     else "No Autism Detected"
    confidence     = round(max(probability) * 100, 2)
    autism_prob    = round(probability[1] * 100, 2)
    no_autism_prob = round(probability[0] * 100, 2)
    gender_str     = 'Male' if input_data['gender'] == 1 else 'Female'
    answers        = [input_data[f'A{i}_Score'] for i in range(1, 11)]

    prediction_id = save_prediction(
        user_id        = session['user_id'],
        result         = result,
        confidence     = confidence,
        autism_prob    = autism_prob,
        no_autism_prob = no_autism_prob,
        age            = input_data['age'],
        gender         = gender_str,
        answers        = answers
    )

    # Save prediction ID in session for combined result
    session['last_prediction_id']         = prediction_id
    session['last_prediction_result']     = result
    session['last_prediction_confidence'] = confidence

    # Check if facial result exists for combined
    latest_facial = get_latest_facial_result(session['user_id'])

    return render_template('result.html',
                           result=result,
                           confidence=confidence,
                           autism_prob=autism_prob,
                           no_autism_prob=no_autism_prob,
                           prediction=int(prediction),
                           has_facial=latest_facial is not None,
                           prediction_id=prediction_id)


# ============================================================
# FACIAL TRACKING
# ============================================================
@app.route('/facial-tracking')
def facial_tracking():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('facial_tracking.html')


@app.route('/run-tracking', methods=['POST'])
def run_tracking():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"})
    try:
        duration = int(request.form.get('duration', 30))
        results  = run_facial_tracking(duration=duration)

        # Save to database
        facial_id = save_facial_result(session['user_id'], results)
        results['facial_id'] = facial_id

        # Save in session for combined result
        session['last_facial_id']    = facial_id
        session['last_facial_score'] = results['behavioral_score']

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)})


# ============================================================
# COMBINED RESULT
# ============================================================
@app.route('/combined-result')
def combined_result():
    if 'user_id' not in session:
        return redirect('/login')

    # Get latest of both
    latest_pred   = get_latest_prediction(session['user_id'])
    latest_facial = get_latest_facial_result(session['user_id'])

    if not latest_pred or not latest_facial:
        missing = []
        if not latest_pred:
            missing.append("AQ-10 Screening")
        if not latest_facial:
            missing.append("Facial Analysis")
        return render_template('combined_result.html',
                               error=True,
                               missing=missing)

    aq10_result       = latest_pred['result']
    aq10_confidence   = latest_pred['confidence']
    behavioral_score  = latest_facial['behavioral_score']

    combined_score, combined_risk, risk_level = calculate_combined(
        aq10_result, aq10_confidence, behavioral_score
    )

    dos, donts = get_recommendations(
        risk_level, aq10_result, behavioral_score
    )

    # Save combined result
    save_combined_result(
        user_id          = session['user_id'],
        prediction_id    = latest_pred['id'],
        facial_id        = latest_facial['id'],
        aq10_result      = aq10_result,
        aq10_confidence  = aq10_confidence,
        behavioral_score = behavioral_score,
        combined_score   = combined_score,
        combined_risk    = combined_risk,
        risk_level       = risk_level
    )

    return render_template('combined_result.html',
                           error=False,
                           aq10_result=aq10_result,
                           aq10_confidence=aq10_confidence,
                           behavioral_score=behavioral_score,
                           combined_score=combined_score,
                           combined_risk=combined_risk,
                           risk_level=risk_level,
                           dos=dos,
                           donts=donts,
                           latest_pred=latest_pred,
                           latest_facial=latest_facial)


# ============================================================
# PDF REPORT DOWNLOAD
# ============================================================
@app.route('/download-report')
def download_report():
    if 'user_id' not in session:
        return redirect('/login')

    latest_pred   = get_latest_prediction(session['user_id'])
    latest_facial = get_latest_facial_result(session['user_id'])

    if not latest_pred:
        return redirect('/dashboard')

    # Build plain text report
    lines = []
    lines.append("=" * 60)
    lines.append("         AUTISMAI — SCREENING REPORT")
    lines.append("=" * 60)
    lines.append(f"Patient Name   : {session['name']}")
    lines.append(f"Email          : {session['email']}")
    lines.append(f"Report Date    : {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("  AQ-10 SCREENING RESULT")
    lines.append("-" * 60)
    lines.append(f"Result         : {latest_pred['result']}")
    lines.append(f"Confidence     : {latest_pred['confidence']}%")
    lines.append(f"Autism Prob.   : {latest_pred['autism_prob']}%")
    lines.append(f"No Autism Prob.: {latest_pred['no_autism_prob']}%")
    lines.append(f"Age            : {latest_pred['age']}")
    lines.append(f"Gender         : {latest_pred['gender']}")
    lines.append(f"Screening Date : {latest_pred['date']}")
    lines.append("")
    lines.append("  AQ-10 Answers:")
    answers = [latest_pred[f'a{i}'] for i in range(1, 11)]
    for i, ans in enumerate(answers, 1):
        lines.append(f"  Q{i:02d}: {'Yes (1)' if ans == 1 else 'No (0)'}")

    if latest_facial:
        lines.append("")
        lines.append("-" * 60)
        lines.append("  FACIAL BEHAVIOUR ANALYSIS")
        lines.append("-" * 60)
        lines.append(f"Behavioral Score : {latest_facial['behavioral_score']}%")
        lines.append(f"Risk Assessment  : {latest_facial['behavioral_risk']}")
        lines.append(f"Eye Contact      : {latest_facial['eye_contact']}%")
        lines.append(f"Blink Rate       : {latest_facial['blink_rate']} bpm")
        lines.append(f"Head Stability   : {latest_facial['head_movement']}%")
        lines.append(f"Face Presence    : {latest_facial['face_presence']}%")
        lines.append(f"Expression Score : {latest_facial['expression_score']}")
        lines.append(f"Duration         : {latest_facial['duration_seconds']}s")

        # Combined
        combined_score, combined_risk, risk_level = calculate_combined(
            latest_pred['result'],
            latest_pred['confidence'],
            latest_facial['behavioral_score']
        )
        dos, donts = get_recommendations(
            risk_level,
            latest_pred['result'],
            latest_facial['behavioral_score']
        )

        lines.append("")
        lines.append("-" * 60)
        lines.append("  COMBINED ASSESSMENT")
        lines.append("-" * 60)
        lines.append(f"Combined Score : {combined_score}%")
        lines.append(f"Risk Level     : {combined_risk}")
        lines.append("")
        lines.append("  RECOMMENDATIONS — What To Do:")
        for d in dos:
            lines.append(f"  + {d}")
        lines.append("")
        lines.append("  RECOMMENDATIONS — What Not To Do:")
        for d in donts:
            lines.append(f"  - {d}")

    lines.append("")
    lines.append("=" * 60)
    lines.append("DISCLAIMER: This report is generated by an AI screening")
    lines.append("tool and does NOT constitute a medical diagnosis.")
    lines.append("Always consult a qualified healthcare professional.")
    lines.append("=" * 60)

    report_text = "\n".join(lines)

    response = make_response(report_text)
    response.headers['Content-Type']        = 'text/plain'
    response.headers['Content-Disposition'] = \
        f'attachment; filename=AutismAI_Report_{session["name"].replace(" ", "_")}.txt'
    return response


# ============================================================
# PROFILE
# ============================================================
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    user = get_user_by_id(session['user_id'])

    if request.method == 'POST':
        name         = request.form['name'].strip()
        new_password = request.form.get('new_password', '').strip()
        confirm      = request.form.get('confirm_password', '').strip()

        if len(name) < 2:
            return render_template('profile.html', user=user,
                error="Please enter a valid name.")

        if new_password:
            if len(new_password) < 6:
                return render_template('profile.html', user=user,
                    error="Password must be at least 6 characters.")
            if new_password != confirm:
                return render_template('profile.html', user=user,
                    error="Passwords do not match.")
            update_user_profile(session['user_id'], name, new_password)
        else:
            update_user_profile(session['user_id'], name)

        session['name'] = name
        user            = get_user_by_id(session['user_id'])
        return render_template('profile.html', user=user,
            success="Profile updated successfully!")

    return render_template('profile.html', user=user)


# ============================================================
# ADMIN PANEL
# ============================================================
@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect('/login')
    if not session.get('is_admin'):
        return redirect('/dashboard')

    all_users       = get_all_users()
    all_predictions = get_all_predictions()
    stats           = get_admin_stats()

    return render_template('admin.html',
                           all_users=all_users,
                           all_predictions=all_predictions,
                           stats=stats)


@app.route('/admin/make-admin/<int:user_id>', methods=['POST'])
def make_admin(user_id):
    if not session.get('is_admin'):
        return redirect('/dashboard')
    import sqlite3
    conn = sqlite3.connect('autism.db')
    conn.execute('UPDATE users SET is_admin = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')


# ============================================================
# ABOUT & HISTORY
# ============================================================
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/history')
def history():
    return render_template('history.html')

# ============================================================
# GUIDED FLOW — Step by step AQ10 → Face → Combined
# ============================================================

@app.route('/guided-flow')
def guided_flow():
    if 'user_id' not in session:
        return redirect('/login')
    # Always start at step 1
    session.pop('guided_aq10_done', None)
    session.pop('guided_facial_done', None)
    return render_template('guided_flow.html', step=1)


@app.route('/guided-flow/submit-aq10', methods=['POST'])
def guided_submit_aq10():
    if 'user_id' not in session:
        return redirect('/login')

    input_data = {
        'A1_Score':        int(request.form['A1_Score']),
        'A2_Score':        int(request.form['A2_Score']),
        'A3_Score':        int(request.form['A3_Score']),
        'A4_Score':        int(request.form['A4_Score']),
        'A5_Score':        int(request.form['A5_Score']),
        'A6_Score':        int(request.form['A6_Score']),
        'A7_Score':        int(request.form['A7_Score']),
        'A8_Score':        int(request.form['A8_Score']),
        'A9_Score':        int(request.form['A9_Score']),
        'A10_Score':       int(request.form['A10_Score']),
        'age':             int(request.form['age']),
        'gender':          int(request.form['gender']),
        'ethnicity':       int(request.form['ethnicity']),
        'jundice':         int(request.form['jundice']),
        'austim':          int(request.form['austim']),
        'contry_of_res':   int(request.form['contry_of_res']),
        'used_app_before': int(request.form['used_app_before']),
        'relation':        int(request.form['relation']),
    }

    input_df       = pd.DataFrame([input_data])
    input_df       = input_df[columns]
    prediction     = model.predict(input_df)[0]
    probability    = model.predict_proba(input_df)[0]

    result         = "Autism Detected" if prediction == 1 \
                     else "No Autism Detected"
    confidence     = round(max(probability) * 100, 2)
    autism_prob    = round(probability[1] * 100, 2)
    no_autism_prob = round(probability[0] * 100, 2)
    gender_str     = 'Male' if input_data['gender'] == 1 else 'Female'
    answers        = [input_data[f'A{i}_Score'] for i in range(1, 11)]

    prediction_id = save_prediction(
        user_id        = session['user_id'],
        result         = result,
        confidence     = confidence,
        autism_prob    = autism_prob,
        no_autism_prob = no_autism_prob,
        age            = input_data['age'],
        gender         = gender_str,
        answers        = answers
    )

    # Store in session for step 2
    session['guided_aq10_done']       = True
    session['guided_prediction_id']   = prediction_id
    session['guided_aq10_result']     = result
    session['guided_aq10_confidence'] = confidence

    # Go to step 2 — face analysis
    return render_template('guided_flow.html',
                           step=2,
                           aq10_result=result,
                           aq10_confidence=confidence)


@app.route('/guided-flow/combined')
def guided_combined():
    if 'user_id' not in session:
        return redirect('/login')

    if not session.get('guided_aq10_done'):
        return redirect('/guided-flow')

    latest_pred   = get_latest_prediction(session['user_id'])
    latest_facial = get_latest_facial_result(session['user_id'])

    if not latest_pred or not latest_facial:
        return redirect('/guided-flow')

    aq10_result      = latest_pred['result']
    aq10_confidence  = latest_pred['confidence']
    behavioral_score = latest_facial['behavioral_score']

    combined_score, combined_risk, risk_level = calculate_combined(
        aq10_result, aq10_confidence, behavioral_score
    )

    dos, donts = get_recommendations(
        risk_level, aq10_result, behavioral_score
    )

    save_combined_result(
        user_id          = session['user_id'],
        prediction_id    = latest_pred['id'],
        facial_id        = latest_facial['id'],
        aq10_result      = aq10_result,
        aq10_confidence  = aq10_confidence,
        behavioral_score = behavioral_score,
        combined_score   = combined_score,
        combined_risk    = combined_risk,
        risk_level       = risk_level
    )

    # Clear guided session flags
    session.pop('guided_aq10_done', None)

    return render_template('guided_combined.html',
                           aq10_result=aq10_result,
                           aq10_confidence=aq10_confidence,
                           behavioral_score=behavioral_score,
                           combined_score=combined_score,
                           combined_risk=combined_risk,
                           risk_level=risk_level,
                           dos=dos,
                           donts=donts,
                           latest_pred=latest_pred,
                           latest_facial=latest_facial)

# ============================================================
# RUN
# ============================================================
if __name__ == '__main__':
    app.run(debug=True)