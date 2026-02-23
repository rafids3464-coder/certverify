/**
 * context/AuthContext.js — Global JWT auth state.
 * Stores token in localStorage, exposes user info and helpers.
 */

import React, { createContext, useContext, useState, useEffect } from "react";

const AuthCtx = createContext(null);

function parseJwt(token) {
    try {
        const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
        return JSON.parse(atob(base64));
    } catch {
        return null;
    }
}

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);   // { name, role, sub, exp }
    const [token, setToken] = useState(null);

    // Rehydrate from localStorage on mount
    useEffect(() => {
        const stored = localStorage.getItem("certverify_token");
        if (stored) {
            const parsed = parseJwt(stored);
            if (parsed && parsed.exp * 1000 > Date.now()) {
                setToken(stored);
                setUser(parsed);
            } else {
                localStorage.removeItem("certverify_token");
            }
        }
    }, []);

    const login = (tokenStr) => {
        const parsed = parseJwt(tokenStr);
        localStorage.setItem("certverify_token", tokenStr);
        setToken(tokenStr);
        setUser(parsed);
    };

    const logout = () => {
        localStorage.removeItem("certverify_token");
        setToken(null);
        setUser(null);
    };

    const isLoggedIn = !!user;
    const isAdmin = user?.role === "admin";

    return (
        <AuthCtx.Provider value={{ user, token, isLoggedIn, isAdmin, login, logout }}>
            {children}
        </AuthCtx.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthCtx);
    if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
    return ctx;
}
