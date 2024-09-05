from fasthtml.common import Script, Link, Meta, Style

flowurl = "https://cdn.jsdelivr.net/npm/flowbite@2.4.1/dist"

custom_script = Script(
    """
    document.body.addEventListener('htmx:configRequest', function(evt) {
        evt.detail.headers['HX-Debug'] = '1';
    });
    """
)
custom_styles = Style(
    """
    ol:empty {
        display: none;
    }

    .htmx-indicator {
        display: None;
    }

    .htmx-request .htmx-indicator {
        opacity: 1;
    }

    /* To ensure the htmx-request itself is affected */
    .htmx-request.htmx-indicator {
        opacity: 1;
        display: block;
    }

    """
)
CUSTOM_HDRS = (
    # Flowbite CSS
    Link(href=f"{flowurl}/flowbite.min.css", rel="stylesheet"),
    Meta(name="theme-color", content="#ffffff"),
    # Tailwind CSS
    Script(src="https://cdn.tailwindcss.com"),
    # HTMX
    # Script(src="https://unpkg.com/htmx.org@1.9.12"),
    # Ext
    # Script(src="https://unpkg.com/htmx.ext...chunked-transfer/dist/index.js"),
    Script(
        src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.4.0/transfer-encoding-chunked.js"
    ),
    # Script(
    #     src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.2.0/transfer-encoding-chunked.js"
    # ),
    custom_styles,
    custom_script,
)

FLOWBITE_INCLUDE_SCRIPT = (Script(src=f"{flowurl}/flowbite.min.js"),)
