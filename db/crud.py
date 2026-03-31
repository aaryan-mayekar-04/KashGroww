import bcrypt, json
from db.models import get_session, User, Profile, Recommendation

# ════════ USER FUNCTIONS ════════════════════════════════════════
def create_user(name, email, phone, username, plain_password):
    s = get_session()
    try:
        existing = s.query(User).filter_by(username=username).first()
        if existing:
            return existing   # 👈 return instead of error

        hashed = hash_password(plain_password)
        u = User(name=name, email=email, phone=phone,
                 username=username, password=hashed)

        s.add(u)
        s.commit()
        s.refresh(u)
        return u

    except Exception as e:
        s.rollback()
        raise e
    finally:
        s.close()

def get_user(username):
    # Fetch user by username. Returns User object or None.
    s = get_session()
    u = s.query(User).filter_by(username=username).first()
    s.close()
    return u

def email_exists(email):
    # Returns True if this email is already registered
    s = get_session()
    found = s.query(User).filter_by(email=email).first() is not None
    s.close()
    return found

def verify_password(plain, hashed):
    # Returns True if plain password matches stored hash
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def hash_password(plain):
    # Hash a plain password using bcrypt
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_user_by_email(email):
    # Fetch user by email. Returns User object or None.
    s = get_session()
    u = s.query(User).filter_by(email=email).first()
    s.close()
    return u

def reset_password(email, new_password):
    # Reset password for user with given email
    s = get_session()
    try:
        user = s.query(User).filter_by(email=email).first()
        if not user:
            return False, "Email not found"
        
        hashed = hash_password(new_password)
        user.password = hashed
        s.commit()
        return True, "Password reset successfully"
    
    except Exception as e:
        s.rollback()
        return False, f"Error: {str(e)}"
    finally:
        s.close()

# ════════ PROFILE FUNCTIONS ═════════════════════════════════════

def save_profile(user_id, age, gender, no_dependents,
                  income, invest_amount, risk_level, horizon):
    # Upsert: update if profile exists, insert if new
    s = get_session()
    try:
        p = s.query(Profile).filter_by(user_id=user_id).first()
        if p:
            p.age = age; p.gender = gender; p.no_dependents = no_dependents
            p.income = income; p.invest_amount = invest_amount
            p.risk_level = risk_level; p.horizon = horizon
        else:
            p = Profile(user_id=user_id, age=age, gender=gender,
                        no_dependents=no_dependents, income=income,
                        invest_amount=invest_amount,
                        risk_level=risk_level, horizon=horizon)
            s.add(p)
        s.commit()
    except Exception as e:
        s.rollback()
        raise e
    finally:
        s.close()

# ════════ RECOMMENDATION FUNCTIONS ══════════════════════════════

def save_recommendation(user_id, risk_level, plan, blended_return, total_invested):
    # Save a plan as JSON strings in MySQL
    s = get_session()
    try:
        rec = Recommendation(
            user_id      = user_id,
            risk_level   = risk_level,
            plan_json    = json.dumps(plan),
            returns_json = json.dumps({
                'blended_return': blended_return,
                'total_invested': total_invested,
            })
        )
        s.add(rec)
        s.commit()
    except Exception as e:
        s.rollback()
        raise e
    finally:
        s.close()

def get_history(user_id):
    # Fetch all saved plans for a user. Returns list of dicts.
    s = get_session()
    recs = s.query(Recommendation).filter_by(user_id=user_id)             .order_by(Recommendation.created_at).all()
    result = [{
        'id':         r.id,
        'date':       r.created_at,
        'risk_level': r.risk_level,
        'plan':       json.loads(r.plan_json),
        'returns':    json.loads(r.returns_json),
    } for r in recs]
    s.close()
    return result