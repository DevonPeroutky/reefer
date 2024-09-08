from fasthtml.common import Script, Link, Meta, Style

flowurl = "https://cdn.jsdelivr.net/npm/flowbite@2.4.1/dist"

custom_script = Script(
    """

    document.addEventListener('DOMContentLoaded', function() {
        console.log("Adding htmx event listeners");
        document.body.addEventListener('htmx:configRequest', function(evt) {
            evt.detail.headers['HX-Debug'] = 'true';
        });

        document.body.addEventListener("htmx:beforeSwap", (event) => {
            console.log("HTMX beforeSwap event fired:", event.detail);
            // event.detail.shouldSwap = true;
        });

        document.body.addEventListener("htmx:afterSwap", (event) => {
            console.log("HTMX afterSwap event fired:", event.detail);
        });

        document.body.addEventListener("htmx:swapError", (event) => {
            console.log("HTMX swapError event fired:", event.detail);
        });

        document.body.addEventListener('htmx:afterSwap', (event) => {
            // console.log('Chunk received and swapped into the DOM:', event);

            // Access the target element and the swapped content
            const chunkContent = event.detail.elt; // The element that received the chunk

            // Run your custom JavaScript here upon each chunk received
            reinitializeFlowbiteOnNewModals(chunkContent);
        });

        function reinitializeFlowbiteOnNewModals(chunkContent) {

            // Check if the chunk contains an element with a specific data attribute, e.g., data-flowbite-init
            const flowbiteElement = chunkContent.querySelector('[data-modal-target]');

            // Call initFlowbite if the element with the data attribute is found
            if (flowbiteElement) {

                const start = performance.now();
                initFlowbite();
                const end = performance.now();
                console.log('!!!!!!!!!!!!! Flowbite re-initialized in ' + (end - start) + ' milliseconds.');
            }
        }

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
