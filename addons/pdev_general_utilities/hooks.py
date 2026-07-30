# -*- coding: utf-8 -*-
import base64
import logging
import os

_logger = logging.getLogger(__name__)


def load_default_background_image(env):
    """Post init hook — loads background_login.jpg from static/src/img into web.background.image."""
    image_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "static",
        "src",
        "img",
        "background_login.jpg",
    )
    try:
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("ascii")
        env["web.background.image"].sudo().create(
            {
                "name": "background_login.jpg",
                "image": image_b64,
            }
        )
        _logger.info("pdev_general_utilities: default background image loaded.")
    except Exception:
        _logger.exception("pdev_general_utilities: could not load default background image.")


def remove_system_parameters(env):
    """Uninstall hook — removes all stored config parameters."""
    params = [
        "pdev_general_utilities.credential_border",
        "pdev_general_utilities.credential_element_color",
        "pdev_general_utilities.color",
        "pdev_general_utilities.background",
        "pdev_general_utilities.login_style",
        "pdev_general_utilities.gradient_top_color",
        "pdev_general_utilities.gradient_top_opacity",
        "pdev_general_utilities.gradient_bottom_color",
        "pdev_general_utilities.gradient_bottom_opacity",
        "pdev_general_utilities.credential_opacity",
        "pdev_general_utilities.video",
        "pdev_general_utilities.web_background_image_id",
        "pdev_general_utilities.web_remove_powered_by",
        "pdev_general_utilities.disable_passkey",
    ]
    ir_config = env["ir.config_parameter"].sudo()
    try:
        for key in params:
            record = ir_config.search([("key", "=", key)], limit=1)
            if record:
                record.unlink()
        _logger.info("pdev_general_utilities: system parameters removed.")
    except Exception:
        _logger.exception("pdev_general_utilities: error removing system parameters.")
