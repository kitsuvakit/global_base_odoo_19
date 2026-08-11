/** @odoo-module **/

import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";
import { FormController } from "@web/views/form/form_controller";
import { onMounted, onPatched, onWillUnmount } from "@odoo/owl";

export class FastDispatchFormController extends FormController {
    setup() {
        super.setup();
        this.scanTimeout = null;

        onMounted(() => {
            this.setupFastDispatchScanner();
        });

        onPatched(() => {
            this.setupFastDispatchScanner();
        });

        onWillUnmount(() => {
            if (this.scanTimeout) {
                clearTimeout(this.scanTimeout);
            }
        });
    }

    setupFastDispatchScanner() {
        setTimeout(() => {
            const input = document.querySelector('div[name="search_query"] input, .search_input_autofocus input, input.search_input_autofocus');

            if (input) {
                if (!input.dataset.fastDispatchBound) {
                    input.dataset.fastDispatchBound = "true";

                    // 1. Manejo inmediato al presionar o recibir Enter / Tab de la lectora de código de barras
                    input.addEventListener('keydown', (ev) => {
                        if (ev.key === 'Enter' || ev.key === 'Tab' || ev.keyCode === 13 || ev.keyCode === 9) {
                            ev.preventDefault();
                            ev.stopPropagation();

                            input.dispatchEvent(new Event('change', { bubbles: true }));

                            if (this.scanTimeout) {
                                clearTimeout(this.scanTimeout);
                            }

                            setTimeout(() => {
                                const btn = document.querySelector('button[name="process_scan_input"]');
                                if (btn) {
                                    btn.click();
                                }
                            }, 60);
                        }
                    });

                    // 2. Detección automática por temporizador (por si la lectora no envía Enter)
                    input.addEventListener('input', () => {
                        if (this.scanTimeout) {
                            clearTimeout(this.scanTimeout);
                        }

                        const val = input.value ? input.value.trim() : '';
                        if (val.length >= 3) {
                            this.scanTimeout = setTimeout(() => {
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                const btn = document.querySelector('button[name="process_scan_input"]');
                                if (btn && document.activeElement === input) {
                                    btn.click();
                                }
                            }, 350);
                        }
                    });
                }

                // Mantener el cursor siempre dentro del campo de escaneo
                if (document.activeElement !== input) {
                    input.focus();
                    if (input.value) {
                        input.select();
                    }
                }
            }
        }, 150);
    }
}

export const FastDispatchFormView = {
    ...formView,
    Controller: FastDispatchFormController,
};

registry.category("views").add("fast_dispatch_form", FastDispatchFormView);
