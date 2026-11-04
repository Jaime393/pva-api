# pva-api

API de demostración y decodificación, sin despacho de acciones. Los valores históricos Phi se presentan como constantes declaradas, no como mediciones actuales o evidencia científica.

```bash
python3 app.py
python3 app.py --serve --host 127.0.0.1 --port 8003
python3 -m unittest discover -s tests -v
```

El modo predeterminado describe capacidades y no levanta un servidor. La implementación usa `http.server`, no FastAPI/uvicorn; no se atribuyen dos runtimes inexistentes.

`POST /api/micelio` comprueba el checksum interno y, si se envía, el externo. Un SHA-256 no es firma autenticada ni autorización: el resultado siempre indica `authentication_performed=false`, `authorization_granted=false` y `capability_executed=false`.

El léxico conserva etiquetas históricas, incluidas acciones que requerirían permisos. Decodificarlas nunca ejecuta instrucciones, crea logs en otro repositorio ni concede esos permisos.

`/api/ki` y `/api/falsador` evalúan fórmulas/reglas ilustrativas con entradas finitas; no validan conciencia, experiencia ni teorías físicas. `/api/publish` devuelve 410 en lugar de inventar una transacción o DOI.

Los tests HTTP usan solo loopback temporal. No se hizo despliegue ni llamada a modelos o proveedores externos, y la API no implementa autenticación de producción.
