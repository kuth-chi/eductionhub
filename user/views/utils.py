from jwcrypto import jwt, jwk
from django.conf import settings
import os

def load_key(file_path):
    with open(file_path, 'rb') as f:
        return f.read()

def generate_jwt(payload):
    private_key = load_key(settings.JWT_PRIVATE_KEY_PATH)
    key = jwk.JWK.from_pem(private_key)
    token = jwt.JWT(header={'alg': 'RS256'}, claims=payload)
    token.make_signed_token(key)
    return token.serialize()

def verify_jwt(token):
    public_key = load_key(settings.JWT_PUBLIC_KEY_PATH)
    key = jwk.JWK.from_pem(public_key)
    jwt_token = jwt.JWT(jwt=token, key=key)
    return jwt_token.claims
