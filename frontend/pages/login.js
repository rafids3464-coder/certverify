/**
 * pages/login.js — User login page.
 * Features: email/password, eye toggle, validation, JWT storage, redirect.
 */

import React, { useState } from "react";
import Link from "next/link";
import Head from "next/head";
import { useRouter } from "next/router";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function LoginPage() {
    const router = useRouter();
    const { login } = useAuth();

    const [form, setForm] = useState({ email: "", password: "" });
    const [showPw, setShowPw] = useState(false);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const validate = () => {
        if (!form.email.includes("@")) return "Please enter a valid email address.";
        if (form.password.length < 6) return "Password must be at least 6 characters.";
        return "";
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const err = validate();
        if (err) { setError(err); return; }

        setLoading(true);
        setError("");
        try {
            const res = await axios.post(`${API_URL}/auth/login`, {
                email: form.email,
                password: form.password,
            });
            login(res.data.access_token);
            router.push("/");
        } catch (e) {
            setError(e.response?.data?.detail || "Login failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const inputStyle = {
        width: "100%",
        padding: "12px 16px",
        background: "var(--bg-elevated)",
        border: "1px solid var(--border-subtle)",
        borderRadius: "var(--radius-sm)",
        color: "var(--text-primary)",
        fontSize: "0.95rem",
        outline: "none",
        transition: "border-color 0.2s",
    };

    return (
        <>
            <Head>
                <title>Login — CertVerify</title>
            </Head>
            <div className="page-wrapper">
                <Navbar />

                <main className="container" style={{ padding: "80px 24px", maxWidth: 440 }}>
                    <div className="card">
                        <div style={{ textAlign: "center", marginBottom: 32 }}>
                            <div style={{ fontSize: "2.5rem", marginBottom: 12 }}>🔑</div>
                            <h1 style={{ fontSize: "1.75rem", marginBottom: 8 }}>Welcome back</h1>
                            <p style={{ fontSize: "0.875rem" }}>
                                Sign in to track your certificate history
                            </p>
                        </div>

                        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                            {/* Email */}
                            <div>
                                <label style={{ display: "block", marginBottom: 6, fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                                    Email address
                                </label>
                                <input
                                    id="login-email"
                                    type="email"
                                    placeholder="you@example.com"
                                    value={form.email}
                                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                                    style={inputStyle}
                                    onFocus={(e) => (e.target.style.borderColor = "var(--accent-cyan)")}
                                    onBlur={(e) => (e.target.style.borderColor = "var(--border-subtle)")}
                                    required
                                />
                            </div>

                            {/* Password */}
                            <div>
                                <label style={{ display: "block", marginBottom: 6, fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                                    Password
                                </label>
                                <div style={{ position: "relative" }}>
                                    <input
                                        id="login-password"
                                        type={showPw ? "text" : "password"}
                                        placeholder="••••••••"
                                        value={form.password}
                                        onChange={(e) => setForm({ ...form, password: e.target.value })}
                                        style={{ ...inputStyle, paddingRight: 44 }}
                                        onFocus={(e) => (e.target.style.borderColor = "var(--accent-cyan)")}
                                        onBlur={(e) => (e.target.style.borderColor = "var(--border-subtle)")}
                                        required
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPw((s) => !s)}
                                        style={{
                                            position: "absolute",
                                            right: 12,
                                            top: "50%",
                                            transform: "translateY(-50%)",
                                            background: "none",
                                            border: "none",
                                            cursor: "pointer",
                                            fontSize: "1rem",
                                            color: "var(--text-muted)",
                                        }}
                                        aria-label="Toggle password visibility"
                                    >
                                        {showPw ? "🙈" : "👁️"}
                                    </button>
                                </div>
                            </div>

                            {/* Error */}
                            {error && (
                                <div style={{
                                    padding: "10px 14px",
                                    background: "rgba(239,68,68,0.1)",
                                    border: "1px solid rgba(239,68,68,0.3)",
                                    borderRadius: "var(--radius-sm)",
                                    color: "var(--accent-red)",
                                    fontSize: "0.85rem",
                                }}>
                                    ⚠️ {error}
                                </div>
                            )}

                            {/* Submit */}
                            <button
                                id="login-submit-btn"
                                type="submit"
                                disabled={loading}
                                className="btn btn-primary"
                                style={{ padding: "14px", marginTop: 8, fontSize: "1rem" }}
                            >
                                {loading ? "Signing in…" : "Sign In →"}
                            </button>
                        </form>

                        <p style={{ textAlign: "center", marginTop: 24, fontSize: "0.875rem", color: "var(--text-muted)" }}>
                            Don&apos;t have an account?{" "}
                            <Link href="/signup" style={{ color: "var(--accent-cyan)" }}>Sign up</Link>
                        </p>
                        <p style={{ textAlign: "center", marginTop: 8, fontSize: "0.8rem" }}>
                            <Link href="/admin/login" style={{ color: "var(--text-muted)" }}>Admin login →</Link>
                        </p>
                    </div>
                </main>
            </div>
        </>
    );
}
