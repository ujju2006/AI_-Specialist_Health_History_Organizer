class EmergencyCardManager {
    async updateEmergencyCard() {
        try {
            const contacts = await api.request("/emergency", "GET");
            const user = auth.getCurrentUser() || {};

            let blood = "O Positive (O+)";
            if (contacts && contacts.length > 0 && contacts[0].blood_group) {
                blood = contacts[0].blood_group;
            }

            const nameEl = document.getElementById("em-card-patient-name");
            if (nameEl) nameEl.innerText = `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.email || "Patient Profile";

            const bloodEl = document.getElementById("em-card-blood-group");
            if (bloodEl) bloodEl.innerText = blood;

            const container = document.getElementById("emergency-contacts-list-target");
            if (container) {
                container.innerHTML = "";
                if (!contacts || contacts.length === 0) {
                    container.innerHTML = '<tr><td colspan="5" class="text-secondary" style="text-align: center;">No emergency contacts registered yet.</td></tr>';
                } else {
                    contacts.forEach(c => {
                        const tr = document.createElement("tr");
                        tr.innerHTML = `
                            <td class="font-semibold">${c.name}</td>
                            <td>${c.relationship || "--"}</td>
                            <td>${c.phone_number || "--"}</td>
                            <td><span class="status-badge normal">${c.blood_group || "--"}</span></td>
                            <td class="text-secondary">${c.notes || "--"}</td>
                        `;
                        container.appendChild(tr);
                    });
                }
            }

            const qrCanvas = document.getElementById("qr-code-canvas-target");
            if (qrCanvas && typeof QRCode !== 'undefined') {
                const payload = `EMERGENCY MEDICAL PROFILE\n` +
                                `Patient: ${user.first_name || ""} ${user.last_name || ""}\n` +
                                `Blood Group: ${blood}\n`;
                QRCode.toCanvas(qrCanvas, payload, { width: 90, margin: 1 }, function (error) {
                    if (error) console.error("QR Code rendering failed:", error);
                });
            }

        } catch (error) {
            console.warn("Failed to load emergency data:", error);
        }
        if (window.lucide) lucide.createIcons();
    }
}

const emergency = new EmergencyCardManager();
window.emergency = emergency;
