const API_BASE = "/api/v1";

class ApiClient {
    getToken() {
        return localStorage.getItem("access_token");
    }

    setTokens(accessToken, refreshToken) {
        localStorage.setItem("access_token", accessToken);
        localStorage.setItem("refresh_token", refreshToken);
    }

    clearTokens() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
    }

    async request(endpoint, method = "GET", body = null, isMultipart = false) {
        const url = `${API_BASE}${endpoint}`;
        const headers = {};

        const token = this.getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        let options = { method, headers };

        if (body) {
            if (isMultipart) {
                // Fetch library handles boundary strings dynamically
                options.body = body;
            } else {
                headers["Content-Type"] = "application/json";
                options.body = JSON.stringify(body);
            }
        }

        try {
            const response = await fetch(url, options);

            if (response.status === 401) {
                // Unauthorized token could be expired. Try to refresh
                const refreshed = await this.tryTokenRefresh();
                if (refreshed) {
                    // Retry original call
                    headers["Authorization"] = `Bearer ${this.getToken()}`;
                    const retryResponse = await fetch(url, options);
                    return await this.handleResponse(retryResponse);
                } else {
                    if (this.getToken()) {
                        this.clearTokens();
                        window.dispatchEvent(new CustomEvent("unauthorized-endpoint-event"));
                    }
                    return null;
                }
            }

            return await this.handleResponse(response);
        } catch (error) {
            console.error(`API Call failed [${method} ${endpoint}]:`, error);
            throw error;
        }
    }

    async handleResponse(response) {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/octet-stream")) {
             return await response.blob(); 
        }

        let data;
        try {
            data = await response.json();
        } catch (e) {
            data = { detail: "Parsing error. Server returned non-json data." };
        }

        if (!response.ok) {
            const message = data.detail || "System request failed template details.";
            throw new Error(typeof message === "string" ? message : JSON.stringify(message));
        }

        return data;
    }

    async tryTokenRefresh() {
        const refresh = localStorage.getItem("refresh_token");
        if (!refresh) return false;

        try {
            const response = await fetch(`${API_BASE}/auth/refresh?refresh_token=${refresh}`, {
                method: "POST"
            });
            if (response.ok) {
                const credentialBytes = await response.json();
                this.setTokens(credentialBytes.access_token, credentialBytes.refresh_token);
                return true;
            }
        } catch (e) {
            console.error("Token refresh action collapsed:", e);
        }
        return false;
    }
}

const api = new ApiClient();
window.api = api;  // Expose to window scope
