/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ProductBarcodeScannerAction extends Component {
    static template = "product_barcode_scanner_mobile.ScannerActionTemplate";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            searchTerm: "",
            product: null,
            loading: false,
            error: null,
            cameraActive: false,
        });

        this.videoStream = null;
        this.barcodeDetector = null;
        this.scanInterval = null;

        if ("BarcodeDetector" in window) {
            this.barcodeDetector = new BarcodeDetector({
                formats: ["ean_13", "code_128", "code_39", "qr_code", "upc_a", "upc_e", "ean_8"],
            });
        }
    }

    playScanBeep() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = "sine";
            osc.frequency.setValueAtTime(1400, ctx.currentTime);
            gain.gain.setValueAtTime(0.15, ctx.currentTime);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.12);
        } catch (e) {}
    }

    triggerHaptic() {
        if ("vibrate" in navigator) {
            navigator.vibrate([40, 30, 40]);
        }
    }

    async onSearch() {
        if (!this.state.searchTerm) return;
        this.state.loading = true;
        this.state.error = null;
        try {
            const res = await this.orm.call(
                "product.product",
                "search_product_for_scanner",
                [this.state.searchTerm]
            );
            if (res.success) {
                this.playScanBeep();
                this.triggerHaptic();
                this.state.product = res.product;
            } else {
                this.state.error = res.message;
                this.state.product = null;
            }
        } catch (err) {
            this.state.error = "Error de conexión al consultar el producto.";
        } finally {
            this.state.loading = false;
        }
    }

    async toggleCamera() {
        if (this.state.cameraActive) {
            this.stopCamera();
        } else {
            try {
                this.videoStream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: { ideal: "environment" } },
                });
                this.state.cameraActive = true;
                setTimeout(() => {
                    const video = document.getElementById("owl_video_feed");
                    if (video) {
                        video.srcObject = this.videoStream;
                        this.startCameraScan(video);
                    }
                }, 100);
            } catch (e) {
                this.notification.add("No se pudo acceder a la cámara del dispositivo.", { type: "danger" });
            }
        }
    }

    stopCamera() {
        if (this.scanInterval) clearInterval(this.scanInterval);
        if (this.videoStream) {
            this.videoStream.getTracks().forEach((t) => t.stop());
            this.videoStream = null;
        }
        this.state.cameraActive = false;
    }

    startCameraScan(videoElem) {
        if (!this.barcodeDetector) return;
        this.scanInterval = setInterval(async () => {
            try {
                const barcodes = await this.barcodeDetector.detect(videoElem);
                if (barcodes.length > 0) {
                    const code = barcodes[0].rawValue;
                    this.state.searchTerm = code;
                    this.stopCamera();
                    this.onSearch();
                }
            } catch (e) {}
        }, 250);
    }

    copySpecs() {
        if (!this.state.product) return;
        const p = this.state.product;
        const text = `📦 ${p.name}
🏷️ SKU: ${p.default_code} | Barcode: ${p.barcode}
🏷️ Marca: ${p.product_brand}
🚗 Vehículo: ${p.brand_car}
📍 Ubicación: ${p.location}
💰 Precio: ${p.formatted_price}
📦 Stock: ${p.qty_available} u`;

        navigator.clipboard.writeText(text).then(() => {
            this.notification.add("Ficha copiada al portapapeles", { type: "success" });
        });
    }

    scanNext() {
        this.state.searchTerm = "";
        this.state.product = null;
        this.state.error = null;
    }
}

registry.category("actions").add("product_barcode_scanner_mobile.scanner_action", ProductBarcodeScannerAction);
