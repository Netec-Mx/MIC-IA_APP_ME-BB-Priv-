# -*- coding: utf-8 -*-
"""Endpoint SCIM 2.0 de prueba del curso MIC_IA_APP_ME_BB.

Implementa lo que usa el servicio de aprovisionamiento de Microsoft Entra:
/Users y /Groups (GET con filtro, POST, PATCH, PUT, DELETE), /ServiceProviderConfig,
/Schemas y /ResourceTypes. Guarda los datos en un archivo JSON y registra cada solicitud.

Variables de entorno:
  SCIM_TOKEN   token portador que debe enviar Entra (obligatorio)
  SCIM_DATOS   ruta del archivo de datos (predeterminado: /home/scim-datos.json en App Service,
               ./scim-datos.json en local)
Páginas de consulta (requieren ?token=<SCIM_TOKEN>):
  /registro    últimas solicitudes recibidas       /cuentas    usuarios y grupos actuales
Uso local:     set SCIM_TOKEN=prueba ; python app.py      (http://localhost:8000/scim/v2)
"""
import datetime as dt
import json
import os
import re
import threading
import uuid
from collections import deque
from pathlib import Path

from flask import Flask, Response, jsonify, request, render_template_string

app = Flask(__name__)
TOKEN = os.environ.get("SCIM_TOKEN", "")
RUTA = Path(os.environ.get("SCIM_DATOS") or ("/home/scim-datos.json" if os.environ.get("WEBSITE_SITE_NAME") else "scim-datos.json"))
BASE = "/scim/v2"
S_USER = "urn:ietf:params:scim:schemas:core:2.0:User"
S_ENT = "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"
S_GROUP = "urn:ietf:params:scim:schemas:core:2.0:Group"
S_LIST = "urn:ietf:params:scim:api:messages:2.0:ListResponse"
S_ERR = "urn:ietf:params:scim:api:messages:2.0:Error"
S_PATCH = "urn:ietf:params:scim:api:messages:2.0:PatchOp"

CANDADO = threading.Lock()
REGISTRO = deque(maxlen=300)


# ------------------------------------------------------------------ almacenamiento
def cargar():
    if RUTA.exists():
        return json.loads(RUTA.read_text(encoding="utf-8"))
    return {"Users": {}, "Groups": {}}


def guardar(db):
    RUTA.write_text(json.dumps(db, ensure_ascii=False, indent=1), encoding="utf-8")


def ahora():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def error(status, detalle, scim_type=None):
    cuerpo = {"schemas": [S_ERR], "status": str(status), "detail": detalle}
    if scim_type:
        cuerpo["scimType"] = scim_type
    return Response(json.dumps(cuerpo, ensure_ascii=False), status=status, mimetype="application/scim+json")


def scim(obj, status=200, location=None):
    r = Response(json.dumps(obj, ensure_ascii=False), status=status, mimetype="application/scim+json")
    if location:
        r.headers["Location"] = location
    return r


# ------------------------------------------------------------------ seguridad y registro
@app.before_request
def autenticar():
    request._inicio = dt.datetime.now()
    if request.path.startswith(BASE):
        if not TOKEN:
            return error(500, "El servidor no tiene configurado SCIM_TOKEN")
        if request.headers.get("Authorization", "") != f"Bearer {TOKEN}":
            return error(401, "Token portador inválido o ausente")
    elif request.path in ("/registro", "/cuentas", "/reiniciar"):
        if not TOKEN or request.args.get("token") != TOKEN:
            return Response("Agrega ?token=<SCIM_TOKEN> a la URL", status=401)


@app.after_request
def registrar(resp):
    if request.path.startswith(BASE):
        cuerpo = request.get_data(as_text=True)
        REGISTRO.appendleft({
            "hora": ahora(), "metodo": request.method,
            "ruta": request.full_path.rstrip("?").replace(BASE, ""),
            "estado": resp.status_code,
            "solicitud": cuerpo[:3000],
            "respuesta": resp.get_data(as_text=True)[:1500] if resp.status_code >= 400 else "",
        })
    return resp


# ------------------------------------------------------------------ utilidades SCIM
def meta(tipo, rid, creado=None):
    return {"resourceType": tipo, "created": creado or ahora(), "lastModified": ahora(),
            "location": f"{request.host_url.rstrip('/')}{BASE}/{tipo}s/{rid}"}


FILTRO = re.compile(r'^\s*([\w.:]+)\s+eq\s+"(.*)"\s*$', re.I)


def filtrar(recursos, filtro):
    if not filtro:
        return list(recursos)
    m = FILTRO.match(filtro)
    if not m:
        raise ValueError("Solo se admite el operador eq: atributo eq \"valor\"")
    attr, valor = m.group(1), m.group(2)
    return [r for r in recursos if str(obtener(r, attr) or "").lower() == valor.lower()]


def obtener(obj, ruta):
    if ruta.startswith(S_ENT + ":"):
        return obj.get(S_ENT, {}).get(ruta[len(S_ENT) + 1:])
    actual = obj
    for parte in ruta.split("."):
        if not isinstance(actual, dict):
            return None
        clave = next((k for k in actual if k.lower() == parte.lower()), None)
        actual = actual.get(clave) if clave else None
    return actual


def lista(recursos):
    recursos = sorted(recursos, key=lambda r: r.get("meta", {}).get("created", ""))
    inicio = max(int(request.args.get("startIndex", 1)), 1)
    cuenta = int(request.args.get("count", 100))
    pagina = recursos[inicio - 1:inicio - 1 + cuenta]
    return scim({"schemas": [S_LIST], "totalResults": len(recursos), "startIndex": inicio,
                 "itemsPerPage": len(pagina), "Resources": pagina})


def a_bool(v):
    if isinstance(v, str):
        return v.strip().lower() == "true"
    return bool(v)


def aplicar_ruta(obj, ruta, valor, op):
    """Aplica add/replace/remove sobre una ruta SCIM simple, anidada, con filtro o de extensión."""
    if ruta.startswith(S_ENT + ":"):
        ext = obj.setdefault(S_ENT, {})
        sub = ruta[len(S_ENT) + 1:]
        if sub == "manager" and isinstance(valor, str):
            valor = {"value": valor}
        if op == "remove":
            ext.pop(sub, None)
        else:
            ext[sub] = valor
        return
    m = re.match(r'^(\w+)\[(\w+)\s+eq\s+"([^"]*)"\]\.?(\w+)?$', ruta, re.I)
    if m:  # emails[type eq "work"].value
        lista_attr, campo, igual, sub = m.groups()
        elementos = obj.setdefault(lista_attr, [])
        elem = next((e for e in elementos if str(e.get(campo, "")).lower() == igual.lower()), None)
        if op == "remove":
            if elem in elementos:
                elementos.remove(elem)
            return
        if elem is None:
            elem = {campo: igual}
            elementos.append(elem)
        if sub:
            elem[sub] = valor
        elif isinstance(valor, dict):
            elem.update(valor)
        return
    partes = ruta.split(".")
    destino = obj
    for p in partes[:-1]:
        destino = destino.setdefault(p, {})
    ultimo = partes[-1]
    if ultimo == "active":
        valor = a_bool(valor)
    if op == "remove":
        destino.pop(ultimo, None)
    elif op == "add" and isinstance(destino.get(ultimo), list) and isinstance(valor, list):
        destino[ultimo].extend(valor)
    else:
        destino[ultimo] = valor


def aplicar_patch(obj, cuerpo, es_grupo=False):
    for op in cuerpo.get("Operations", []):
        tipo = op.get("op", "").lower()
        ruta = op.get("path")
        valor = op.get("value")
        if es_grupo and ruta and ruta.lower().startswith("members"):
            miembros = obj.setdefault("members", [])
            if tipo == "add":
                for v in valor or []:
                    if v["value"] not in [x["value"] for x in miembros]:
                        miembros.append({"value": v["value"]})
            elif tipo == "remove":
                m = re.search(r'value eq "([^"]+)"', ruta)
                quitar = {m.group(1)} if m else {v["value"] for v in (valor or [])}
                if not m and not valor:
                    quitar = {x["value"] for x in miembros}
                obj["members"] = [x for x in miembros if x["value"] not in quitar]
            elif tipo == "replace":
                obj["members"] = [{"value": v["value"]} for v in valor or []]
            continue
        if ruta:
            aplicar_ruta(obj, ruta, valor, tipo)
        elif isinstance(valor, dict):  # operación sin path: {"atributo": valor, ...}
            for k, v in valor.items():
                aplicar_ruta(obj, k, v, tipo)
        else:
            raise ValueError(f"Operación sin path ni objeto de valores: {op}")


# ------------------------------------------------------------------ Users
@app.get(f"{BASE}/Users")
def usuarios_listar():
    try:
        return lista(filtrar(cargar()["Users"].values(), request.args.get("filter")))
    except ValueError as e:
        return error(400, str(e), "invalidFilter")


@app.get(f"{BASE}/Users/<rid>")
def usuario_obtener(rid):
    u = cargar()["Users"].get(rid)
    return scim(u) if u else error(404, f"Usuario {rid} no encontrado")


@app.post(f"{BASE}/Users")
def usuario_crear():
    cuerpo = request.get_json(force=True)
    if not cuerpo.get("userName"):
        return error(400, "userName es obligatorio", "invalidValue")
    with CANDADO:
        db = cargar()
        if any(u["userName"].lower() == cuerpo["userName"].lower() for u in db["Users"].values()):
            return error(409, f"Ya existe un usuario con userName {cuerpo['userName']}", "uniqueness")
        rid = str(uuid.uuid4())
        cuerpo["id"] = rid
        cuerpo["active"] = a_bool(cuerpo.get("active", True))
        cuerpo["meta"] = meta("User", rid)
        db["Users"][rid] = cuerpo
        guardar(db)
    return scim(cuerpo, 201, cuerpo["meta"]["location"])


@app.route(f"{BASE}/Users/<rid>", methods=["PATCH", "PUT"])
def usuario_actualizar(rid):
    cuerpo = request.get_json(force=True)
    with CANDADO:
        db = cargar()
        u = db["Users"].get(rid)
        if not u:
            return error(404, f"Usuario {rid} no encontrado")
        creado = u["meta"]["created"]
        try:
            if request.method == "PUT":
                u = dict(cuerpo, id=rid)
            else:
                aplicar_patch(u, cuerpo)
        except (ValueError, KeyError, TypeError) as e:
            return error(400, str(e), "invalidSyntax")
        u["meta"] = meta("User", rid, creado)
        db["Users"][rid] = u
        guardar(db)
    return scim(u)


@app.delete(f"{BASE}/Users/<rid>")
def usuario_eliminar(rid):
    with CANDADO:
        db = cargar()
        if db["Users"].pop(rid, None) is None:
            return error(404, f"Usuario {rid} no encontrado")
        for g in db["Groups"].values():
            g["members"] = [m for m in g.get("members", []) if m["value"] != rid]
        guardar(db)
    return Response(status=204)


# ------------------------------------------------------------------ Groups
@app.get(f"{BASE}/Groups")
def grupos_listar():
    try:
        recursos = filtrar(cargar()["Groups"].values(), request.args.get("filter"))
    except ValueError as e:
        return error(400, str(e), "invalidFilter")
    if "members" in (request.args.get("excludedAttributes") or ""):
        recursos = [{k: v for k, v in g.items() if k != "members"} for g in recursos]
    return lista(recursos)


@app.get(f"{BASE}/Groups/<rid>")
def grupo_obtener(rid):
    g = cargar()["Groups"].get(rid)
    return scim(g) if g else error(404, f"Grupo {rid} no encontrado")


@app.post(f"{BASE}/Groups")
def grupo_crear():
    cuerpo = request.get_json(force=True)
    with CANDADO:
        db = cargar()
        if any(g["displayName"].lower() == cuerpo.get("displayName", "").lower() for g in db["Groups"].values()):
            return error(409, f"Ya existe el grupo {cuerpo.get('displayName')}", "uniqueness")
        rid = str(uuid.uuid4())
        cuerpo.update(id=rid, members=cuerpo.get("members", []), meta=meta("Group", rid))
        db["Groups"][rid] = cuerpo
        guardar(db)
    return scim(cuerpo, 201, cuerpo["meta"]["location"])


@app.route(f"{BASE}/Groups/<rid>", methods=["PATCH", "PUT"])
def grupo_actualizar(rid):
    cuerpo = request.get_json(force=True)
    with CANDADO:
        db = cargar()
        g = db["Groups"].get(rid)
        if not g:
            return error(404, f"Grupo {rid} no encontrado")
        creado = g["meta"]["created"]
        try:
            if request.method == "PUT":
                g = dict(cuerpo, id=rid)
            else:
                aplicar_patch(g, cuerpo, es_grupo=True)
        except (ValueError, KeyError, TypeError) as e:
            return error(400, str(e), "invalidSyntax")
        g["meta"] = meta("Group", rid, creado)
        db["Groups"][rid] = g
        guardar(db)
    return Response(status=204) if request.method == "PATCH" else scim(g)


@app.delete(f"{BASE}/Groups/<rid>")
def grupo_eliminar(rid):
    with CANDADO:
        db = cargar()
        if db["Groups"].pop(rid, None) is None:
            return error(404, f"Grupo {rid} no encontrado")
        guardar(db)
    return Response(status=204)


# ------------------------------------------------------------------ descubrimiento
@app.get(f"{BASE}/ServiceProviderConfig")
def spc():
    return scim({
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
        "patch": {"supported": True}, "bulk": {"supported": False, "maxOperations": 0, "maxPayloadSize": 0},
        "filter": {"supported": True, "maxResults": 100}, "changePassword": {"supported": False},
        "sort": {"supported": False}, "etag": {"supported": False},
        "authenticationSchemes": [{"type": "oauthbearertoken", "name": "Bearer token",
                                   "description": "Token portador configurado en SCIM_TOKEN"}]})


@app.get(f"{BASE}/ResourceTypes")
def tipos():
    return scim({"schemas": [S_LIST], "totalResults": 2, "Resources": [
        {"id": "User", "name": "User", "endpoint": "/Users", "schema": S_USER,
         "schemaExtensions": [{"schema": S_ENT, "required": False}]},
        {"id": "Group", "name": "Group", "endpoint": "/Groups", "schema": S_GROUP}]})


@app.get(f"{BASE}/Schemas")
def esquemas():
    return scim({"schemas": [S_LIST], "totalResults": 3,
                 "Resources": [{"id": S_USER, "name": "User"}, {"id": S_ENT, "name": "EnterpriseUser"},
                               {"id": S_GROUP, "name": "Group"}]})


# ------------------------------------------------------------------ páginas de consulta
ESTILO = """<style>body{font-family:'Neue Haas Grotesk Text Pro',Segoe UI,Arial,sans-serif;margin:20px;color:#262626}
h1{color:#0F3D5C} table{border-collapse:collapse;width:100%} td,th{border:1px solid #ccc;padding:5px 7px;vertical-align:top;font-size:13px}
th{background:#0F3D5C;color:#fff;text-align:left} pre{font-family:Consolas,monospace;font-size:11px;white-space:pre-wrap;margin:0}
.e2{color:#2E7D32;font-weight:bold}.e4{color:#C62828;font-weight:bold}</style>"""


@app.get("/registro")
def pagina_registro():
    return render_template_string(ESTILO + """<h1>Endpoint SCIM · últimas solicitudes</h1>
<p>Se muestran las {{ r|length }} solicitudes más recientes (la primera es la última). Recarga la página para actualizar.</p>
<table><tr><th>Hora (UTC)</th><th>Método</th><th>Ruta</th><th>Estado</th><th>Cuerpo de la solicitud</th></tr>
{% for x in r %}<tr><td>{{ x.hora }}</td><td>{{ x.metodo }}</td><td><pre>{{ x.ruta }}</pre></td>
<td class="{{ 'e2' if x.estado < 400 else 'e4' }}">{{ x.estado }}</td><td><pre>{{ x.solicitud }}</pre>{% if x.respuesta %}<pre>→ {{ x.respuesta }}</pre>{% endif %}</td></tr>{% endfor %}
</table>""", r=list(REGISTRO))


@app.get("/cuentas")
def pagina_cuentas():
    db = cargar()
    nombres = {u["id"]: u["userName"] for u in db["Users"].values()}
    return render_template_string(ESTILO + """<h1>Endpoint SCIM · cuentas en la aplicación</h1>
<h2>Usuarios ({{ u|length }})</h2><table><tr><th>userName</th><th>displayName</th><th>active</th><th>title</th><th>department</th><th>employeeNumber</th><th>id</th></tr>
{% for x in u %}<tr><td>{{ x.userName }}</td><td>{{ x.displayName }}</td><td>{{ x.active }}</td><td>{{ x.title }}</td>
<td>{{ (x[ent] or {}).department }}</td><td>{{ (x[ent] or {}).employeeNumber }}</td><td><pre>{{ x.id }}</pre></td></tr>{% endfor %}</table>
<h2>Grupos ({{ g|length }})</h2><table><tr><th>displayName</th><th>Miembros</th></tr>
{% for x in g %}<tr><td>{{ x.displayName }}</td><td>{% for m in x.members %}{{ n.get(m.value, m.value) }}<br>{% endfor %}</td></tr>{% endfor %}</table>""",
                                  u=list(db["Users"].values()), g=list(db["Groups"].values()), n=nombres, ent=S_ENT)


@app.post("/reiniciar")
def reiniciar():
    with CANDADO:
        guardar({"Users": {}, "Groups": {}})
        REGISTRO.clear()
    return jsonify(resultado="Datos y registro borrados")


@app.get("/")
def raiz():
    return Response("Endpoint SCIM de prueba. URL base: " + request.host_url.rstrip("/") + BASE, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))
