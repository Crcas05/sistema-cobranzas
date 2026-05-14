import webbrowser
import urllib.parse

def enviar_whatsapp(nombre, telefono, deuda, atraso):

    mensaje = f"""
Hola {nombre},
tienes una deuda pendiente de S/ {deuda}.
Días de atraso: {atraso}.

Por favor regulariza tu pago.
    """

    mensaje = urllib.parse.quote(mensaje)

    url = f"https://wa.me/{telefono}?text={mensaje}"

    webbrowser.open(url)