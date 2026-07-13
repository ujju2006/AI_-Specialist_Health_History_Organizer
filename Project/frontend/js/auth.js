class AuthManager {
    async login(email, password) {
        try {
            const response = await fetch("/api/v1/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    username: email,
                    password: password
                })
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || "Authentication failed");
            }

            api.setTokens(data.access_token, data.refresh_token);
            await this.loadCurrentUser();
            return true;
        } catch (error) {
            console.error("Login verification failed:", error);
            throw error;
        }
    }

    async register(email, password, firstName, lastName, dob, gender) {
        const payload = {
            email,
            password,
            first_name: firstName,
            last_name: lastName,
            date_of_birth: dob,
            gender
        };

        const data = await api.request("/auth/register", "POST", payload);
        return data;
    }

    logout() {
        api.clearTokens();
        sessionStorage.removeItem("current_user");
        window.dispatchEvent(new CustomEvent("session-terminated-event"));
    }

    async loadCurrentUser() {
        try {
            const user = await api.request("/auth/me", "GET");
            sessionStorage.setItem("current_user", JSON.stringify(user));
            return user;
        } catch (e) {
            this.logout();
            return null;
        }
    }

    getCurrentUser() {
        const user = sessionStorage.getItem("current_user");
        return user ? JSON.parse(user) : null;
    }

    isAuthenticated() {
        return !!api.getToken() && !!this.getCurrentUser();
    }
}

const auth = new AuthManager();
window.auth = auth;
