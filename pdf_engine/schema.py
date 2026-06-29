"""
Content schema validation for the Agent PDF Engine.
"""

from pathlib import Path


def validate_content(content: dict) -> list[str]:
    """
    Validate the content dict against the documented schema.
    Returns a list of human-readable error messages (empty = valid).
    """
    errors = []

    if not isinstance(content, dict):
        return ["Content must be a JSON object (dict)"]

    # ── Required fields ────────────────────────────────────────────────
    if "title" not in content:
        errors.append('Missing required field: "title"')
    elif not isinstance(content["title"], str) or not content["title"].strip():
        errors.append('"title" must be a non-empty string')

    if "sections" not in content:
        errors.append('Missing required field: "sections"')
    elif not isinstance(content["sections"], list):
        errors.append('"sections" must be an array')
    elif len(content["sections"]) == 0:
        errors.append('"sections" must contain at least one section')

    # ── Optional top-level fields ──────────────────────────────────────
    str_fields = {"subtitle", "output", "watermark"}
    for field in str_fields:
        val = content.get(field)
        if val is not None and not isinstance(val, str):
            errors.append(f'"{field}" must be a string (got {type(val).__name__})')

    bool_fields = {"show_toc", "show_cover", "show_footer_date"}
    for field in bool_fields:
        val = content.get(field)
        if val is not None and not isinstance(val, bool):
            errors.append(f'"{field}" must be a boolean (got {type(val).__name__})')

    # page_size
    ps = content.get("page_size")
    if ps is not None:
        if not isinstance(ps, str) or ps not in ("A4", "Letter", "Legal"):
            errors.append('"page_size" must be "A4", "Letter", or "Legal"')

    # orientation
    orient = content.get("orientation")
    if orient is not None:
        if not isinstance(orient, str) or orient not in ("portrait", "landscape"):
            errors.append('"orientation" must be "portrait" or "landscape"')

    # ── Theme validation ───────────────────────────────────────────────
    theme = content.get("theme")
    if theme is not None:
        if not isinstance(theme, dict):
            errors.append('"theme" must be an object')
        else:
            for key in ("primary", "accent", "light", "text", "muted"):
                val = theme.get(key)
                if val is not None:
                    if not isinstance(val, str) or not (
                        val.startswith("#") and len(val) == 7
                    ):
                        errors.append(
                            f'"theme.{key}" must be a hex color like "#RRGGBB"'
                        )

    # ── Meta ───────────────────────────────────────────────────────────
    meta = content.get("meta")
    if meta is not None:
        if not isinstance(meta, dict):
            errors.append('"meta" must be an object')
        else:
            for k, v in meta.items():
                if not isinstance(k, str):
                    errors.append(f'"meta" key must be a string (got {type(k).__name__})')
                if not isinstance(v, str):
                    errors.append(f'"meta.{k}" must be a string')

    # ── Fonts ──────────────────────────────────────────────────────────
    fonts = content.get("fonts")
    if fonts is not None:
        if not isinstance(fonts, dict):
            errors.append('"fonts" must be an object')
        else:
            for role in ("sans", "mono", "serif"):
                cfg = fonts.get(role)
                if cfg is not None:
                    if not isinstance(cfg, dict):
                        errors.append(f'"fonts.{role}" must be an object')
                    else:
                        for variant in ("regular", "bold", "italic", "bold_italic"):
                            val = cfg.get(variant)
                            if val is not None and not isinstance(val, str):
                                errors.append(
                                    f'"fonts.{role}.{variant}" must be a string path'
                                )
                            elif val is not None and not Path(val).exists():
                                errors.append(
                                    f'"fonts.{role}.{variant}" path not found: {val}'
                                )

    # ── header_footer ──────────────────────────────────────────────────
    hf = content.get("header_footer")
    if hf is not None:
        if not isinstance(hf, dict):
            errors.append('"header_footer" must be an object')
        else:
            for zone in ("header", "footer"):
                z = hf.get(zone)
                if z is not None:
                    if not isinstance(z, dict):
                        errors.append(f'"header_footer.{zone}" must be an object')
                    else:
                        if "show" in z and not isinstance(z["show"], bool):
                            errors.append(
                                f'"header_footer.{zone}.show" must be a boolean'
                            )
                        for sf in ("left", "center", "right"):
                            val = z.get(sf)
                            if val is not None and not isinstance(val, str):
                                errors.append(
                                    f'"header_footer.{zone}.{sf}" must be a string'
                                )

    # ── Sections ──────────────────────────────────────────────────────
    sections = content.get("sections")
    if isinstance(sections, list):
        for i, sec in enumerate(sections):
            prefix = f"sections[{i}]"
            if not isinstance(sec, dict):
                errors.append(f"{prefix} must be an object")
                continue

            if "heading" not in sec:
                errors.append(f'{prefix} is missing required field "heading"')
            elif not isinstance(sec["heading"], str) or not sec["heading"].strip():
                errors.append(f'{prefix}."heading" must be a non-empty string')

            for sf in ("body", "highlight", "code", "language", "note"):
                val = sec.get(sf)
                if val is not None and not isinstance(val, str):
                    errors.append(f'{prefix}."{sf}" must be a string')

            if "page_break" in sec and not isinstance(sec["page_break"], bool):
                errors.append(f'{prefix}."page_break" must be a boolean')

            for lf in ("bullets", "ordered_list"):
                val = sec.get(lf)
                if val is not None:
                    if not isinstance(val, list):
                        errors.append(f'{prefix}."{lf}" must be an array')
                    else:
                        for j, item in enumerate(val):
                            if not isinstance(item, str):
                                errors.append(
                                    f'{prefix}."{lf}"[{j}] must be a string'
                                )

            img = sec.get("image")
            if img is not None:
                if not isinstance(img, dict):
                    errors.append(f'{prefix}."image" must be an object')
                else:
                    if "path" not in img:
                        errors.append(f'{prefix}."image" is missing "path"')
                    elif not isinstance(img["path"], str):
                        errors.append(f'{prefix}."image.path" must be a string')
                    elif not Path(img["path"]).exists():
                        errors.append(f'{prefix} "image.path" path not found: {img["path"]}')
                    for nf in ("width", "height"):
                        val = img.get(nf)
                        if val is not None and not isinstance(val, (int, float)):
                            errors.append(
                                f'{prefix}."image.{nf}" must be a number'
                            )
                    if "caption" in img and not isinstance(img["caption"], str):
                        errors.append(f'{prefix}."image.caption" must be a string')

            tbl = sec.get("table")
            if tbl is not None:
                if not isinstance(tbl, dict):
                    errors.append(f'{prefix}."table" must be an object')
                else:
                    headers = tbl.get("headers")
                    if headers is not None:
                        if not isinstance(headers, list):
                            errors.append(f'{prefix}."table.headers" must be an array')
                        else:
                            for j, h in enumerate(headers):
                                if not isinstance(h, str):
                                    errors.append(
                                        f'{prefix}."table.headers"[{j}] must be a string'
                                    )

                    rows = tbl.get("rows")
                    if rows is not None:
                        if not isinstance(rows, list):
                            errors.append(f'{prefix}."table.rows" must be an array')
                        else:
                            for j, row in enumerate(rows):
                                if not isinstance(row, list):
                                    errors.append(
                                        f'{prefix}."table.rows"[{j}] must be an array'
                                    )
                                else:
                                    for k, cell in enumerate(row):
                                        if not isinstance(cell, str):
                                            errors.append(
                                                f'{prefix}."table.rows"[{j}][{k}]'
                                                " must be a string"
                                            )

                    cw = tbl.get("col_widths")
                    if cw is not None:
                        if not isinstance(cw, list):
                            errors.append(
                                f'{prefix}."table.col_widths" must be an array'
                            )
                        else:
                            for j, w in enumerate(cw):
                                if not isinstance(w, (int, float)):
                                    errors.append(
                                        f'{prefix}."table.col_widths"[{j}]'
                                        " must be a number"
                                    )

                    if (
                        isinstance(headers, list)
                        and isinstance(rows, list)
                        and len(rows) > 0
                    ):
                        nh = len(headers)
                        for j, row in enumerate(rows):
                            if isinstance(row, list) and len(row) != nh:
                                errors.append(
                                    f'{prefix}."table.rows"[{j}] has {len(row)} cells'
                                    f" but headers has {nh}"
                                )

    return errors
