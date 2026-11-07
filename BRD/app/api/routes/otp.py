import hashlib
import html
import hmac
import logging
import secrets
import smtplib
import ssl
import uuid
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import formataddr

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.models.otp_challenge import OtpChallenge
from app.schemas.otp import OtpSendRequest, OtpVerifyRequest


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/otp", tags=["Email OTP"])

CHALLENGE_TTL = timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
SESSION_TTL = timedelta(hours=12)
SEND_COOLDOWN = timedelta(seconds=60)
SEND_LIMIT_PER_HOUR = 5
MAX_VERIFY_ATTEMPTS = 5
COOKIE_NAME = "site_otp_session"


def _require_otp_settings():
    missing_settings = [
        name
        for name, value in (
            ("SMTP_HOST", settings.SMTP_HOST),
            ("SMTP_USERNAME", settings.SMTP_USERNAME),
            ("SMTP_PASSWORD", settings.SMTP_PASSWORD),
            ("SMTP_FROM_EMAIL", settings.SMTP_FROM_EMAIL),
            ("SMTP_FROM_NAME", settings.SMTP_FROM_NAME),
        )
        if not value
    ]
    if missing_settings:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Email verification is not configured. Set these backend "
                f"settings: {', '.join(missing_settings)}."
            ),
        )
    if not settings.OTP_SESSION_SECRET or len(settings.OTP_SESSION_SECRET) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "OTP_SESSION_SECRET is missing or shorter than 32 characters. "
                "Set it on the Render backend service without surrounding quotes, then redeploy."
            ),
        )


def _email_hash(email: str) -> str:
    return hmac.new(
        settings.OTP_SESSION_SECRET.encode("utf-8"),
        email.strip().lower().encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _otp_hash(challenge_id: str, otp: str) -> str:
    return hmac.new(
        settings.OTP_SESSION_SECRET.encode("utf-8"),
        f"{challenge_id}:{otp}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _mask_email(email: str) -> str:
    local, domain = email.split("@", 1)
    visible_suffix = local[-1] if len(local) > 1 else ""
    return f"{local[0]}***{visible_suffix}@{domain}"


def _send_otp_email(email: str, otp: str) -> None:
    escaped_otp = html.escape(otp)
    expiry_text = (
        f"{settings.OTP_EXPIRE_MINUTES} minute"
        f"{'s' if settings.OTP_EXPIRE_MINUTES != 1 else ''}"
    )
    message = EmailMessage()
    message["From"] = formataddr(
        (settings.SMTP_FROM_NAME, settings.SMTP_FROM_EMAIL)
    )
    message["To"] = email
    message["Subject"] = "Your Vitae verification code"
    message.set_content(
        f"Your Vitae verification code is {otp}. It expires in {expiry_text}. "
        "If you did not request it, you can ignore this email."
    )
    message.add_alternative(
        "<div style=\"font-family:Arial,sans-serif;line-height:1.6\">"
        "<h2>Verify your email</h2>"
        f"<p>Your Vitae verification code is "
        f"<strong style=\"font-size:24px;letter-spacing:4px\">{escaped_otp}</strong>.</p>"
        f"<p>This code expires in {expiry_text}. If you did not request it, "
        "you can ignore this email.</p></div>",
        subtype="html",
    )

    stage = "connection"
    try:
        context = ssl.create_default_context()
        if settings.SMTP_PORT == 465:
            with smtplib.SMTP_SSL(
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                timeout=12,
                context=context,
            ) as server:
                stage = "authentication"
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                stage = "message delivery"
                server.send_message(message)
        else:
            with smtplib.SMTP(
                settings.SMTP_HOST, settings.SMTP_PORT, timeout=12
            ) as server:
                stage = "EHLO"
                server.ehlo()
                stage = "STARTTLS"
                server.starttls(context=context)
                stage = "EHLO after STARTTLS"
                server.ehlo()
                stage = "authentication"
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                stage = "message delivery"
                server.send_message(message)
    except (OSError, smtplib.SMTPException) as error:
        logger.warning(
            "SMTP email send failed during %s (%s; response code %s)",
            stage,
            type(error).__name__,
            getattr(error, "smtp_code", None),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not send the verification email. Check the SMTP settings and try again.",
        ) from error


def _verified_session_token() -> str:
    now = datetime.utcnow()
    return jwt.encode(
        {
            "purpose": "site_email_verification",
            "iat": now,
            "exp": now + SESSION_TTL,
        },
        settings.OTP_SESSION_SECRET,
        algorithm="HS256",
    )


@router.post("/send")
def send_otp(data: OtpSendRequest, db: Session = Depends(get_db)):
    _require_otp_settings()
    now = datetime.utcnow()
    email = str(data.email).strip().lower()
    email_hash = _email_hash(email)

    db.query(OtpChallenge).filter(
        OtpChallenge.created_at < now - timedelta(hours=24)
    ).delete(synchronize_session=False)

    recent_challenges = (
        db.query(OtpChallenge)
        .filter(
            OtpChallenge.email_hash == email_hash,
            OtpChallenge.created_at >= now - timedelta(hours=1),
        )
        .order_by(OtpChallenge.created_at.desc())
        .all()
    )
    if recent_challenges and now - recent_challenges[0].created_at < SEND_COOLDOWN:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait a minute before requesting another verification code.",
        )
    if len(recent_challenges) >= SEND_LIMIT_PER_HOUR:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Verification request limit reached. Try again in an hour.",
        )

    challenge_id = str(uuid.uuid4())
    otp = f"{secrets.randbelow(1_000_000):06d}"
    _send_otp_email(email, otp)
    db.add(
        OtpChallenge(
            id=challenge_id,
            email_hash=email_hash,
            otp_hash=_otp_hash(challenge_id, otp),
            created_at=now,
            expires_at=now + CHALLENGE_TTL,
            attempts=0,
        )
    )
    db.commit()
    return {
        "challenge_id": challenge_id,
        "email": _mask_email(email),
        "expires_in": int(CHALLENGE_TTL.total_seconds()),
        "resend_after": int(SEND_COOLDOWN.total_seconds()),
    }


@router.post("/verify")
def verify_otp(
    data: OtpVerifyRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    _require_otp_settings()
    challenge = (
        db.query(OtpChallenge)
        .filter(OtpChallenge.id == data.challenge_id)
        .with_for_update()
        .first()
    )
    now = datetime.utcnow()
    if challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OTP request not found.")
    if challenge.verified_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This OTP has already been used.")
    if challenge.expires_at <= now:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="OTP expired. Request a new code.")
    if challenge.attempts >= MAX_VERIFY_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many incorrect codes. Request a new verification code.",
        )

    challenge.attempts += 1
    db.commit()

    if not hmac.compare_digest(challenge.otp_hash, _otp_hash(challenge.id, data.otp)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The OTP is incorrect. Check the code and try again.",
        )

    challenge.verified_at = datetime.utcnow()
    db.commit()
    response.set_cookie(
        key=COOKIE_NAME,
        value=_verified_session_token(),
        max_age=int(SESSION_TTL.total_seconds()),
        httponly=True,
        secure=settings.OTP_COOKIE_SECURE or request.url.scheme == "https",
        samesite="lax",
        path="/",
    )
    return {"verified": True}


@router.get("/status")
def otp_status(request: Request):
    session_token = request.cookies.get(COOKIE_NAME)
    if not session_token or not settings.OTP_SESSION_SECRET:
        return {"verified": False}
    try:
        claims = jwt.decode(
            session_token,
            settings.OTP_SESSION_SECRET,
            algorithms=["HS256"],
        )
    except JWTError:
        return {"verified": False}
    return {"verified": claims.get("purpose") == "site_email_verification"}


@router.post("/logout")
def logout_otp(response: Response):
    response.delete_cookie(
        key=COOKIE_NAME,
        httponly=True,
        secure=settings.OTP_COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
