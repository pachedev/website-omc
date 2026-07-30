/** @odoo-module **/

// Part of Bizople Solutions Pvt. Ltd.
// Licensed under the Bizople Proprietary License v1.0.
// Copyright (C) 2026 Bizople Solutions Pvt. Ltd.

import { fonts } from "@html_editor/utils/fonts";
/**
 * @override
 */
fonts.fontIcons = [
  { base: 'fa', parser: /\.(fa-(?:\w|-)+)::?before/i },
  { base: 'ri', parser: /\.(ri-(?:\w|-)+)::?before/i },
],

  console.log()