/**
 * pages/signup.js — User registration page.
 * Features: name/email/password, eye toggle, validation, auto-login after signup.
 */

import React, { useState } from "react";
import Link from "next/link";
import Head from "next/head";
import { useRouter } from "next/router";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SignupPage() {
    const router = useRouter();
    const { login } = useAuth();

    const [form, setForm] = useState({ name: "", email: "", password: "" });
    const [showPw, setShowPw] = useState(false);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const validate = () => {
        if (form.name.trim().length < 2) return "Name must be at least 2 characters.";
        if (!form.email.includes("@")) return "Please enter a valid email address.";
        if (form.password.length < 6) return "Password must be at least 6 characters.";
        return "";
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const err = validate();
        if (err) { setError(err); return; }

        setLoading(true); setError("");
        try {
            const res = await axios.post(`${API_URL}/auth/signup`, {
                name: form.name.trim(),
                email: form.email,
                password: form.password,
            });
            login(res.data.access_token);
            router.push("/");
        } catch (e) {
            setError(e.response?.data?.detail || "Sign up failed. Please try again.");
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
    const focus = (e) => (e.target.style.borderColor = "var(--accent-cyan)");
    const unfocus = (e) => (e.target.style.borderColor = "var(--border-subtle)");

    return (
        <>
            <Head><title>Sign Up — CertVerify</title></Head>
            <div className="page-wrapper">
                <Navbar />
                <main className="container" style={{ padding: "80px 24px", maxWidth: 440 }}>
                    <div className="card">
                        <div style={{ textAlign: "center", marginBottom: 32 }}>
                            <div style={{ fontSize: "2.5rem", marginBottom: 12 }}>✍️</div>
                            <h1 style={{ fontSize: "1.75rem", marginBottom: 8 }}>Create account</h1>
                            <p style={{ fontSize: "0.875rem" }}>Free forever. No credit card needed.</p>
                        </div>

                        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                            {/* Name */}
                            <div>
                                <label style={{ display: "block", marginBottom: 6, fontSize: "0.85rem", color: "var(--text-secondary)" }}>Full name</label>
                                <input id="signup-name" type="text" placeholder="Aarav Sharma"
                                    value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                                    style={inputStyle} onFocus={focus} onBlur={unfocus} required />
                            </div>

                            {/* Email */}
                            <div>
                                <label style={{ display: "block", marginBottom: 6, fontSize: "0.85rem", color: "var(--text-secondary)" }}>Email address</label>
                                <input id="signup-email" type="email" placeholder="you@example.com"
                                    value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
                                    style={inputStyle} onFocus={focus} onBlur={unfocus} required />
                            </div>

                            {/* Password */}
                            <div>
                                <label style={{ display: "block", marginBottom: 6, fontSize: "0.85rem", color: "var(--text-secondary)" }}>Password</label>
                                <div style={{ position: "relative" }}>
                                    <input id="signup-password" type={showPw ? "text" : "password"} placeholder="Min. 6 characters"
                                        value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
                                        style={{ ...inputStyle, paddingRight: 44 }} onFocus={focus} onBlur={unfocus} required />
                                    <button type="button" onClick={() => setShowPw((s) => !s)}
                                        style={{
                                            position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)",
                                            background: "none", border: "none", cursor: "pointer", fontSize: "1rem", color: "var(--text-muted)"
                                        }}
                                        aria-label="Toggle password">
                                        {showPw ? "🙈" : "👁️"}
                                    </button>
                                </div>
                            </div>

                            {/* Error */}
                            {error && (
                                <div style={{
                                    padding: "10px 14px", background: "rgba(239,68,68,0.1)",
                                    border: "1px solid rgba(239,68,68,0.3)", borderRadius: "var(--radius-sm)",
                                    color: "var(--accent-red)", fontSize: "0.85rem"
                                }}>
                                    ⚠️ {error}
                                </div>
                            )}

                            <button id="signup-submit-btn" type="submit" disabled={loading}
                                className="btn btn-primary" style={{ padding: "14px", marginTop: 8, fontSize: "1rem" }}>
                                {loading ? "Creating account…" : "Create Account →"}
                            </button>
                        </form>

                        <p style={{ textAlign: "center", marginTop: 24, fontSize: "0.875rem", color: "var(--text-muted)" }}>
                            Already have an account?{" "}
                            <Link href="/login" style={{ color: "var(--accent-cyan)" }}>Sign in</Link>
                        </p>
                    </div>
                </main>
            </div>
        </>
    );
}
