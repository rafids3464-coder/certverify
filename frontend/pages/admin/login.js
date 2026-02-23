/**
 * pages/admin/login.js — Separate admin login page.
 */

import React, { useState } from "react";
import Link from "next/link";
import Head from "next/head";
import { useRouter } from "next/router";
import axios from "axios";
import { useAuth } from "../../context/AuthContext";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AdminLoginPage() {
    const router = useRouter();
    const { login } = useAuth();

    const [form, setForm] = useState({ username: "", password: "" });
    const [showPw, setShowPw] = useState(false);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!form.username.trim() || !form.password) { setError("All fields required."); return; }
        setLoading(true); setError("");
        try {
            const res = await axios.post(`${API_URL}/auth/admin/login`, {
                username: form.username.trim(),
                password: form.password,
            });
            login(res.data.access_token);
            router.push("/admin");
        } catch (e) {
            setError(e.response?.data?.detail || "Login failed.");
        } finally {
            setLoading(false);
        }
    };

    const inputStyle = {
        width: "100%", padding: "12px 16px",
        background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)",
        borderRadius: "var(--radius-sm)", color: "var(--text-primary)",
        fontSize: "0.95rem", outline: "none", transition: "border-color 0.2s",
    };

    return (
        <>
            <Head><title>Admin Login — CertVerify</title></Head>
            <div className="page-wrapper" style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 24 }}>
                <div className="card" style={{ width: "100%", maxWidth: 400 }}>
                    <div style={{ textAlign: "center", marginBottom: 28 }}>
                        <div style={{ fontSize: "2.5rem", marginBottom: 10 }}>🛡️</div>
                        <h1 style={{ fontSize: "1.6rem", marginBottom: 6 }}>Admin Portal</h1>
                        <p style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>CertVerify Admin Access</p>
                    </div>

                    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                        <div>
                            <label style={{ display: "block", marginBottom: 6, fontSize: "0.85rem", color: "var(--text-secondary)" }}>Username</label>
                            <input id="admin-username" type="text" placeholder="admin"
                                value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })}
                                style={inputStyle}
                                onFocus={(e) => (e.target.style.borderColor = "var(--accent-cyan)")}
                                onBlur={(e) => (e.target.style.borderColor = "var(--border-subtle)")}
                                required />
                        </div>

                        <div>
                            <label style={{ display: "block", marginBottom: 6, fontSize: "0.85rem", color: "var(--text-secondary)" }}>Password</label>
                            <div style={{ position: "relative" }}>
                                <input id="admin-password" type={showPw ? "text" : "password"} placeholder="••••••••"
                                    value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
                                    style={{ ...inputStyle, paddingRight: 44 }}
                                    onFocus={(e) => (e.target.style.borderColor = "var(--accent-cyan)")}
                                    onBlur={(e) => (e.target.style.borderColor = "var(--border-subtle)")}
                                    required />
                                <button type="button" onClick={() => setShowPw((s) => !s)}
                                    style={{
                                        position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)",
                                        background: "none", border: "none", cursor: "pointer", fontSize: "1rem", color: "var(--text-muted)"
                                    }}>
                                    {showPw ? "🙈" : "👁️"}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <div style={{
                                padding: "10px 14px", background: "rgba(239,68,68,0.1)",
                                border: "1px solid rgba(239,68,68,0.3)", borderRadius: "var(--radius-sm)",
                                color: "var(--accent-red)", fontSize: "0.85rem"
                            }}>
                                ⚠️ {error}
                            </div>
                        )}

                        <button id="admin-login-btn" type="submit" disabled={loading}
                            className="btn btn-primary" style={{ padding: "14px", marginTop: 6, fontSize: "1rem" }}>
                            {loading ? "Verifying…" : "🛡️ Admin Sign In"}
                        </button>
                    </form>

                    <p style={{ textAlign: "center", marginTop: 20, fontSize: "0.8rem" }}>
                        <Link href="/login" style={{ color: "var(--text-muted)" }}>← User login</Link>
                    </p>
                </div>
            </div>
        </>
    );
}
