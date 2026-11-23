# -*- coding: utf-8 -*-
"""Aplicación SAML de prueba (service provider) del curso MIC_IA_APP_ME_BB.

Muestra todo lo que recibe de Microsoft Entra ID: firma, NameID, claims, condiciones y el XML.
No usar en producción: es una herramienta didáctica para observar y diagnosticar SAML 2.0.

Uso:  python app.py            (lee config.json de esta carpeta)
"""
import base64
import copy
import datetime as dt
import hashlib
import json
import uuid
import zlib
from pathlib import Path
from urllib.parse import urlencode

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from flask import Flask, redirect, request, session, Response, render_template_string
from lxml import etree

BASE = Path(__file__).resolve().parent
CONFIG = json.loads((BASE / "config.json").read_text(encoding="utf-8"))

NS = {
    "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
    "saml": "urn:oasis:names:tc:SAML:2.0:assertion",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
}
ALG_FIRMA = {
    "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256": hashes.SHA256(),
    "http://www.w3.org/2000/09/xmldsig#rsa-sha1": hashes.SHA1(),
}
ALG_DIGEST = {
    "http://www.w3.org/2001/04/xmlenc#sha256": hashlib.sha256,
    "http://www.w3.org/2000/09/xmldsig#sha1": hashlib.sha1,
}
EXC_C14N = "http://www.w3.org/2001/10/xml-exc-c14n#"

app = Flask(__name__)
app.secret_key = CONFIG.get("clave_sesion") or uuid.uuid4().hex
# La respuesta SAML llega con un POST desde login.microsoftonline.com (otro sitio):
# la cookie de sesión necesita SameSite=None y Secure para viajar en ese POST.
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)


# ------------------------------------------------------------------ certificados
def cargar_certificados():
    certs = []
    for ruta in CONFIG.get("certificados_idp", []):
        p = (BASE / ruta)
        if not p.exists():
            certs.append({"archivo": ruta, "error": "no existe"})
            continue
        datos = p.read_bytes()
        try:
            if b"BEGIN CERTIFICATE" in datos:
                c = x509.load_pem_x509_certificate(datos)
            else:
                try:
                    c = x509.load_der_x509_certificate(datos)
                except ValueError:  # Base64 sin encabezados
                    c = x509.load_der_x509_certificate(base64.b64decode(datos))
        except Exception as e:  # noqa: BLE001
            certs.append({"archivo": ruta, "error": str(e)})
            continue
        certs.append({
            "archivo": ruta,
            "cert": c,
            "huella": c.fingerprint(hashes.SHA1()).hex().upper(),
            "vence": c.not_valid_after_utc.strftime("%Y-%m-%d"),
            "sujeto": c.subject.rfc4514_string(),
        })
    return certs


# ------------------------------------------------------------------ firma XML
def c14n(elem, prefijos=None):
    return etree.tostring(elem, method="c14n", exclusive=True, with_comments=False,
                          inclusive_ns_prefixes=prefijos or None)


def verificar_firma(objetivo, certs):
    """Verifica la firma XML (enveloped) que es hija directa de `objetivo`.
    Devuelve (estado, detalle, huella)."""
    firma = objetivo.find("ds:Signature", NS)
    if firma is None:
        return "sin firma", "El elemento no está firmado", None
    si = firma.find("ds:SignedInfo", NS)
    ref = si.find("ds:Reference", NS)
    uri = ref.get("URI", "")
    if uri[1:] != objetivo.get("ID"):
        return "inválida", f"La referencia {uri} no apunta a este elemento", None
    if si.find("ds:CanonicalizationMethod", NS).get("Algorithm") != EXC_C14N:
        return "inválida", "Método de canonicalización no soportado", None
    # 1. Digest del elemento sin su firma
    copia = copy.deepcopy(objetivo)
    copia.remove(copia.find("ds:Signature", NS))
    prefijos = None
    for t in ref.findall("ds:Transforms/ds:Transform", NS):
        inc = t.find("{http://www.w3.org/2001/10/xml-exc-c14n#}InclusiveNamespaces")
        if inc is not None and inc.get("PrefixList"):
            prefijos = inc.get("PrefixList").split()
    alg_d = ref.find("ds:DigestMethod", NS).get("Algorithm")
    if alg_d not in ALG_DIGEST:
        return "inválida", f"Algoritmo de digest no soportado: {alg_d}", None
    digest = base64.b64encode(ALG_DIGEST[alg_d](c14n(copia, prefijos)).digest()).decode()
    esperado = "".join(ref.findtext("ds:DigestValue", namespaces=NS).split())
    if digest != esperado:
        return "inválida", "El digest no coincide: el contenido fue alterado", None
    # 2. Firma de SignedInfo con la clave pública
    alg_f = si.find("ds:SignatureMethod", NS).get("Algorithm")
    if alg_f not in ALG_FIRMA:
        return "inválida", f"Algoritmo de firma no soportado: {alg_f}", None
    valor = base64.b64decode("".join(firma.findtext("ds:SignatureValue", namespaces=NS).split()))
    datos = c14n(si)
    validos = [c for c in certs if "cert" in c]
    for c in validos:
        try:
            c["cert"].public_key().verify(valor, datos, padding.PKCS1v15(), ALG_FIRMA[alg_f])
            alg = "SHA-256" if "sha256" in alg_f else "SHA-1"
            return "válida", f"Firma RSA-{alg} verificada con {c['archivo']}", c["huella"]
        except Exception:  # noqa: BLE001
            continue
    incluido = firma.findtext(".//ds:X509Certificate", namespaces=NS)
    huella = None
    if incluido:
        der = base64.b64decode("".join(incluido.split()))
        huella = hashlib.sha1(der).hexdigest().upper()
    return "inválida", "Ningún certificado de config.json valida la firma (¿se rotó el certificado?)", huella


# ------------------------------------------------------------------ utilidades
def ahora():
    return dt.datetime.now(dt.timezone.utc)


def fecha(texto):
    return dt.datetime.fromisoformat(texto.replace("Z", "+00:00")) if texto else None


def chequeo(nombre, ok, detalle):
    return {"nombre": nombre, "ok": ok, "detalle": detalle}


def analizar_respuesta(xml_bytes, id_solicitud):
    parser = etree.XMLParser(resolve_entities=False, no_network=True, remove_blank_text=False)
    raiz = etree.fromstring(xml_bytes, parser)
    certs = cargar_certificados()
    r = {"chequeos": [], "claims": [], "xml": etree.tostring(raiz, pretty_print=True).decode()}
    tol = dt.timedelta(seconds=CONFIG.get("tolerancia_reloj_segundos", 120))

    # Respuesta
    estado = raiz.find("samlp:Status/samlp:StatusCode", NS)
    codigo = estado.get("Value") if estado is not None else "?"
    r["chequeos"].append(chequeo("Estado de la respuesta", codigo.endswith(":Success"), codigo.split(":")[-1]))
    r["chequeos"].append(chequeo("Destination = ACS", raiz.get("Destination") == CONFIG["acs_url"], raiz.get("Destination")))
    emisor = raiz.findtext("saml:Issuer", namespaces=NS)
    r["chequeos"].append(chequeo("Issuer = Entra ID esperado", emisor == CONFIG["idp_entity_id"], emisor))
    irt = raiz.get("InResponseTo")
    if irt:
        r["flujo"] = "SP-initiated (respuesta a una solicitud de esta aplicación)"
        r["chequeos"].append(chequeo("InResponseTo = ID de la solicitud", irt == id_solicitud, irt))
    else:
        r["flujo"] = "IdP-initiated (iniciado desde Microsoft Entra / My Apps)"

    # Firmas
    est_resp, det_resp, h1 = verificar_firma(raiz, certs)
    assertion = raiz.find("saml:Assertion", NS)
    if assertion is None:
        r["chequeos"].append(chequeo("Assertion presente", False, "No hay assertion (¿cifrada o error?)"))
        return r
    est_as, det_as, h2 = verificar_firma(assertion, certs)
    r["firma_respuesta"] = f"{est_resp}: {det_resp}"
    r["firma_assertion"] = f"{est_as}: {det_as}"
    r["huella"] = h2 or h1
    r["chequeos"].append(chequeo("Firma válida (respuesta o assertion)",
                                 "válida" in (est_resp, est_as) and "inválida" not in (est_resp, est_as),
                                 f"Respuesta: {est_resp} · Assertion: {est_as}"))

    # Assertion
    sujeto = assertion.find("saml:Subject/saml:NameID", NS)
    r["nameid"] = sujeto.text if sujeto is not None else ""
    r["nameid_formato"] = (sujeto.get("Format") or "").split(":")[-1] if sujeto is not None else ""
    cond = assertion.find("saml:Conditions", NS)
    nb, noa = fecha(cond.get("NotBefore")), fecha(cond.get("NotOnOrAfter"))
    t = ahora()
    r["chequeos"].append(chequeo("Vigencia (NotBefore / NotOnOrAfter)", nb - tol <= t <= noa + tol,
                                 f"{cond.get('NotBefore')} → {cond.get('NotOnOrAfter')}"))
    aud = cond.findtext("saml:AudienceRestriction/saml:Audience", namespaces=NS)
    r["chequeos"].append(chequeo("Audience = Entity ID de la app", aud == CONFIG["sp_entity_id"], aud))
    scd = assertion.find("saml:Subject/saml:SubjectConfirmation/saml:SubjectConfirmationData", NS)
    if scd is not None:
        r["chequeos"].append(chequeo("Recipient = ACS", scd.get("Recipient") == CONFIG["acs_url"], scd.get("Recipient")))
    an = assertion.find("saml:AuthnStatement", NS)
    if an is not None:
        r["autenticacion"] = an.get("AuthnInstant")
        r["contexto"] = (an.findtext("saml:AuthnContext/saml:AuthnContextClassRef", namespaces=NS) or "").split(":")[-1]
    for at in assertion.findall("saml:AttributeStatement/saml:Attribute", NS):
        valores = [v.text or "" for v in at.findall("saml:AttributeValue", NS)]
        r["claims"].append({"nombre": at.get("Name"), "valores": valores})
    return r


# ------------------------------------------------------------------ páginas
PLANTILLA = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Aplicación SAML de prueba · Contoso</title>
<style>
 body{font-family:"Neue Haas Grotesk Text Pro",Segoe UI,Arial,sans-serif;margin:24px;color:#262626;max-width:1100px}
 h1{color:#0F3D5C} h2{color:#0F3D5C;border-bottom:3px solid #F5A700;padding-bottom:4px}
 table{border-collapse:collapse;width:100%;margin:8px 0} td,th{border:1px solid #ccc;padding:6px 8px;text-align:left;vertical-align:top}
 th{background:#0F3D5C;color:#fff} .ok{color:#2E7D32;font-weight:bold} .no{color:#C62828;font-weight:bold}
 code,pre{font-family:Consolas,monospace} pre{background:#1e1e1e;color:#e6e6e6;padding:12px;overflow:auto;font-size:12px}
 .boton{background:#0F3D5C;color:#fff;padding:10px 18px;text-decoration:none;border-radius:4px;display:inline-block}
</style></head><body>
<h1>Aplicación SAML de prueba · Portal de Proveedores (Lab)</h1>
{% if r %}
 <h2>Resultado del inicio de sesión</h2>
 <p><b>Flujo:</b> {{ r.flujo }}</p>
 <table><tr><th>Validación</th><th>Resultado</th><th>Detalle</th></tr>
 {% for c in r.chequeos %}<tr><td>{{ c.nombre }}</td><td class="{{ 'ok' if c.ok else 'no' }}">{{ 'OK' if c.ok else 'FALLA' }}</td><td><code>{{ c.detalle }}</code></td></tr>{% endfor %}
 </table>
 {% if r.nameid is defined %}
 <h2>Identidad recibida</h2>
 <table>
  <tr><th>Elemento</th><th>Valor</th></tr>
  <tr><td>NameID</td><td><code>{{ r.nameid }}</code> ({{ r.nameid_formato }})</td></tr>
  <tr><td>Firma de la respuesta</td><td>{{ r.firma_respuesta }}</td></tr>
  <tr><td>Firma de la assertion</td><td>{{ r.firma_assertion }}</td></tr>
  <tr><td>Huella del certificado</td><td><code>{{ r.huella }}</code></td></tr>
  <tr><td>Autenticación</td><td>{{ r.autenticacion }} · {{ r.contexto }}</td></tr>
 </table>
 <h2>Claims recibidos</h2>
 <table><tr><th>Claim (Name)</th><th>Valor(es)</th></tr>
 {% for c in r.claims %}<tr><td><code>{{ c.nombre }}</code></td><td>{{ c.valores|join(', ') }}</td></tr>{% endfor %}
 </table>
 {% endif %}
 <details><summary>Ver el XML completo de la respuesta</summary><pre>{{ r.xml }}</pre></details>
 <p><a class="boton" href="/login">Iniciar sesión de nuevo</a> &nbsp; <a href="/">Inicio</a></p>
{% else %}
 <p>Esta aplicación actúa como <b>service provider</b>. Inicia sesión para ver la assertion que emite Microsoft Entra ID.</p>
 <p><a class="boton" href="/login">Iniciar sesión (SP-initiated)</a> &nbsp; <a href="/metadata">Metadata del SP</a></p>
 <h2>Configuración actual (config.json)</h2>
 <table><tr><th>Parámetro</th><th>Valor</th></tr>
 {% for k, v in cfg.items() %}<tr><td>{{ k }}</td><td><code>{{ v }}</code></td></tr>{% endfor %}
 </table>
 <h2>Certificados de Entra en los que confía la aplicación</h2>
 <table><tr><th>Archivo</th><th>Huella (SHA-1)</th><th>Vence</th></tr>
 {% for c in certs %}<tr><td>{{ c.archivo }}</td><td><code>{{ c.huella or c.error }}</code></td><td>{{ c.vence }}</td></tr>{% endfor %}
 </table>
{% endif %}
</body></html>"""


@app.get("/")
def inicio():
    cfg = {k: v for k, v in CONFIG.items() if k != "clave_sesion"}
    return render_template_string(PLANTILLA, r=None, cfg=cfg, certs=cargar_certificados())


@app.get("/metadata")
def metadata():
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" entityID="{CONFIG['sp_entity_id']}">
  <md:SPSSODescriptor AuthnRequestsSigned="false" WantAssertionsSigned="true"
      protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <md:NameIDFormat>{CONFIG['nameid_formato']}</md:NameIDFormat>
    <md:AssertionConsumerService index="0" isDefault="true"
        Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="{CONFIG['acs_url']}"/>
  </md:SPSSODescriptor>
</md:EntityDescriptor>"""
    return Response(xml, mimetype="application/samlmetadata+xml",
                    headers={"Content-Disposition": "attachment; filename=metadata-sp.xml"})


@app.get("/login")
def login():
    id_sol = "_" + uuid.uuid4().hex
    session["id_solicitud"] = id_sol
    instante = ahora().strftime("%Y-%m-%dT%H:%M:%SZ")
    authn = (f'<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" '
             f'xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="{id_sol}" Version="2.0" '
             f'IssueInstant="{instante}" Destination="{CONFIG["idp_login_url"]}" '
             f'AssertionConsumerServiceURL="{CONFIG["acs_url"]}" '
             f'ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">'
             f'<saml:Issuer>{CONFIG["sp_entity_id"]}</saml:Issuer>'
             f'<samlp:NameIDPolicy Format="{CONFIG["nameid_formato"]}" AllowCreate="true"/>'
             f'</samlp:AuthnRequest>')
    comp = zlib.compressobj(9, zlib.DEFLATED, -15)
    datos = comp.compress(authn.encode()) + comp.flush()
    params = {"SAMLRequest": base64.b64encode(datos).decode(), "RelayState": CONFIG.get("relay_state", "/")}
    (BASE / "ultima_solicitud.xml").write_text(authn, encoding="utf-8")
    return redirect(CONFIG["idp_login_url"] + "?" + urlencode(params))


@app.post(CONFIG.get("ruta_acs", "/saml/acs"))
def acs():
    crudo = request.form.get("SAMLResponse", "")
    if not crudo:
        return "No se recibió SAMLResponse", 400
    xml = base64.b64decode(crudo)
    (BASE / "ultima_respuesta.xml").write_bytes(xml)
    r = analizar_respuesta(xml, session.get("id_solicitud"))
    return render_template_string(PLANTILLA, r=r, cfg={}, certs=[])


if __name__ == "__main__":
    cert = BASE / "certs" / "localhost.pem"
    clave = BASE / "certs" / "localhost-key.pem"
    if not cert.exists():
        raise SystemExit("Falta el certificado HTTPS. Ejecuta primero: python generar_certificado_https.py")
    app.run(host="127.0.0.1", port=CONFIG.get("puerto", 5001), ssl_context=(str(cert), str(clave)))
