# -*- coding: utf-8 -*-
"""Tienda en línea de Contoso (aplicación web OIDC de ejemplo) para Microsoft Entra External ID.

Usa MSAL para Python con el flujo de código de autorización (con PKCE) y muestra los claims
del ID token que emite el external tenant.

Uso:  python app.py      (lee config.json; abre http://localhost:5002)
"""
import json
import uuid
from pathlib import Path
from urllib.parse import urlencode

import msal
from flask import Flask, redirect, render_template_string, request, session, url_for

BASE = Path(__file__).resolve().parent
CONFIG = json.loads((BASE / "config.json").read_text(encoding="utf-8"))

app = Flask(__name__)
app.secret_key = CONFIG.get("clave_sesion") or uuid.uuid4().hex
app.config.update(SESSION_COOKIE_SAMESITE="Lax")


def cliente():
    return msal.ConfidentialClientApplication(
        CONFIG["client_id"], authority=CONFIG["authority"], client_credential=CONFIG["client_secret"])


PLANTILLA = """<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Tienda en línea · Contoso</title>
<style>body{font-family:'Neue Haas Grotesk Text Pro',Segoe UI,Arial,sans-serif;margin:24px;color:#262626;max-width:1000px}
h1{color:#0F3D5C} h2{color:#0F3D5C;border-bottom:3px solid #F5A700;padding-bottom:4px}
table{border-collapse:collapse;width:100%} td,th{border:1px solid #ccc;padding:6px 8px;text-align:left}
th{background:#0F3D5C;color:#fff} code{font-family:Consolas,monospace} .err{color:#C62828;font-weight:bold}
.boton{background:#0F3D5C;color:#fff;padding:10px 18px;text-decoration:none;border-radius:4px;display:inline-block}</style>
</head><body><h1>Tienda en línea · Contoso</h1>
{% if error %}<p class="err">{{ error }}</p><p><code>{{ detalle }}</code></p>{% endif %}
{% if claims %}
 <p>Hola, <b>{{ claims.get('name') or claims.get('given_name') or claims.get('email') or 'cliente' }}</b>. Iniciaste sesión con
 <b>{{ claims.get('idp', 'una cuenta local del external tenant') }}</b>.</p>
 <h2>Claims del ID token</h2>
 <table><tr><th>Claim</th><th>Valor</th><th>Significado</th></tr>
 {% for k, v in claims.items() %}<tr><td><code>{{ k }}</code></td><td><code>{{ v }}</code></td><td>{{ ayuda.get(k, '') }}</td></tr>{% endfor %}
 </table>
 <p><a class="boton" href="/logout">Cerrar sesión</a></p>
{% else %}
 <p>Regístrate o inicia sesión para comprar. La autenticación la realiza Microsoft Entra External ID.</p>
 <p><a class="boton" href="/login">Registrarse o iniciar sesión</a></p>
 <p>Authority: <code>{{ authority }}</code></p>
{% endif %}</body></html>"""

AYUDA = {
    "iss": "Emisor: el external tenant", "aud": "Audiencia: el client_id de esta aplicación",
    "sub": "Identificador del usuario para esta aplicación", "oid": "Object ID del usuario en el external tenant",
    "tid": "ID del tenant", "idp": "Proveedor con el que se autenticó (si no es una cuenta local)",
    "email": "Correo del usuario", "name": "Nombre para mostrar", "given_name": "Nombre",
    "family_name": "Apellido", "preferred_username": "Nombre de inicio de sesión",
    "nonce": "Valor de un solo uso que valida MSAL", "iat": "Emitido (epoch)", "exp": "Expira (epoch)",
    "nbf": "Válido desde (epoch)", "ver": "Versión del token", "auth_time": "Momento de la autenticación",
}


@app.get("/")
def inicio():
    return render_template_string(PLANTILLA, claims=session.get("claims"), ayuda=AYUDA,
                                  authority=CONFIG["authority"], error=None)


@app.get("/login")
def login():
    flujo = cliente().initiate_auth_code_flow(scopes=[], redirect_uri=CONFIG["redirect_uri"])
    session["flujo"] = flujo
    return redirect(flujo["auth_uri"])


@app.get("/getAToken")
def callback():
    try:
        resultado = cliente().acquire_token_by_auth_code_flow(session.get("flujo", {}), request.args)
    except ValueError as e:  # estado o flujo no coinciden (p. ej., la sesión expiró)
        return render_template_string(PLANTILLA, claims=None, error="Flujo inválido", detalle=str(e),
                                      authority=CONFIG["authority"], ayuda=AYUDA)
    if "error" in resultado:
        return render_template_string(PLANTILLA, claims=None, error=resultado.get("error"),
                                      detalle=resultado.get("error_description"),
                                      authority=CONFIG["authority"], ayuda=AYUDA)
    session["claims"] = resultado.get("id_token_claims", {})
    return redirect(url_for("inicio"))


@app.get("/logout")
def logout():
    session.clear()
    destino = CONFIG["authority"].rstrip("/") + "/oauth2/v2.0/logout?" + urlencode(
        {"post_logout_redirect_uri": CONFIG["post_logout_redirect_uri"]})
    return redirect(destino)


if __name__ == "__main__":
    app.run(host="localhost", port=CONFIG.get("puerto", 5002))
