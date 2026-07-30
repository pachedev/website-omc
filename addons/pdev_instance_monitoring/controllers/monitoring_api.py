# -*- coding: utf-8 -*-
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class InstanceMonitoringController(http.Controller):

    @http.route(
        "/pdev/instance/monitoring",
        type="http",
        auth="public",
        methods=["GET", "POST"],
        csrf=False,
        save_session=False,
    )
    def instance_monitoring(self, **kwargs):
        """Endpoint de monitoreo para Uptime Kuma.

        Autenticación: encabezado ``X-API-KEY``, parámetro ``api_key`` (query
        string o formulario) o cuerpo JSON ``{"api_key": "..."}``.
        Responde 200 con la información del servidor si la clave es válida,
        401 en caso contrario.
        """
        api_key = request.httprequest.headers.get("X-API-KEY") or kwargs.get("api_key")

        # Permitir api_key dentro de un cuerpo JSON.
        if not api_key and request.httprequest.data:
            try:
                body = json.loads(request.httprequest.data.decode("utf-8"))
                api_key = body.get("api_key") or (body.get("params") or {}).get("api_key")
            except (ValueError, AttributeError):
                api_key = None

        if not api_key:
            return self._json_response({"status": "error", "message": "Missing API key"}, 401)

        config = (
            request.env["pdev.instance.monitoring"]
            .sudo()
            .search([("api_key", "=", api_key)], limit=1)
        )
        if not config:
            return self._json_response({"status": "error", "message": "Invalid API key"}, 401)

        return self._json_response(config.get_server_info(), 200)

    def _json_response(self, payload, status):
        return request.make_json_response(
            payload,
            status=status,
            headers=[("Cache-Control", "no-cache")],
        )
