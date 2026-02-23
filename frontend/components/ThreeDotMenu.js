/**
 * components/ThreeDotMenu.js — Dropdown context menu (top-right).
 *
 * States:
 *   Logged out  → Login / Sign Up
 *   Logged in   → Profile / Logout
 *   Admin       → Admin Panel / Logout
 */

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import { useAuth } from "../context/AuthContext";

export default function ThreeDotMenu() {
    const { isLoggedIn, isAdmin, user, logout } = useAuth();
    const [open, setOpen] = useState(false);
    const ref = useRef(null);
    const router = useRouter();

    // Close on outside click
    useEffect(() => {
        function handler(e) {
            if (ref.current && !ref.current.contains(e.target)) setOpen(false);
        }
        document.addEventListener("mousedown", handler);
        return () => document.removeEventListener("mousedown", handler);
    }, []);

    const handleLogout = () => {
        logout();
        setOpen(false);
        router.push("/");
    };

    const btnStyle = {
        display: "flex",
        alignItems: "center",
        gap: 10,
        padding: "10px 16px",
        background: "none",
        border: "none",
        color: "var(--text-primary)",
        cursor: "pointer",
        fontSize: "0.875rem",
        width: "100%",
        textAlign: "left",
        borderRadius: 6,
        transition: "background 0.15s",
        textDecoration: "none",
    };

    const hoverFn = (e, enter) => {
        e.currentTarget.style.background = enter ? "var(--bg-elevated)" : "none";
    };

    return (
        <div ref={ref} style={{ position: "relative" }}>
            {/* ⋮ trigger button */}
            <button
                id="three-dot-menu-btn"
                onClick={() => setOpen((o) => !o)}
                aria-label="Account menu"
                style={{
                    width: 40,
                    height: 40,
                    borderRadius: "50%",
                    background: open ? "var(--bg-elevated)" : "transparent",
                    border: "1px solid var(--border-subtle)",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "1.3rem",
                    color: "var(--text-secondary)",
                    transition: "background 0.2s",
                }}
            >
                ⋮
            </button>

            {/* Dropdown */}
            {open && (
                <div
                    style={{
                        position: "absolute",
                        right: 0,
                        top: "calc(100% + 8px)",
                        width: 200,
                        background: "var(--bg-surface)",
                        border: "1px solid var(--border-subtle)",
                        borderRadius: "var(--radius-md)",
                        boxShadow: "var(--shadow-lg)",
                        zIndex: 200,
                        overflow: "hidden",
                        animation: "fadeIn 0.15s ease",
                    }}
                >
                    {/* User info header (if logged in) */}
                    {isLoggedIn && (
                        <div
                            style={{
                                padding: "12px 16px",
                                borderBottom: "1px solid var(--border-subtle)",
                                fontSize: "0.8rem",
                            }}
                        >
                            <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                                {user?.name || "User"}
                            </div>
                            <div style={{ color: "var(--text-muted)", fontSize: "0.72rem" }}>
                                {isAdmin ? "🛡️ Admin" : "👤 User"}
                            </div>
                        </div>
                    )}

                    {/* Menu items */}
                    <div style={{ padding: "6px" }}>
                        {!isLoggedIn && (
                            <>
                                <Link
                                    href="/login"
                                    style={btnStyle}
                                    onClick={() => setOpen(false)}
                                    onMouseEnter={(e) => hoverFn(e, true)}
                                    onMouseLeave={(e) => hoverFn(e, false)}
                                >
                                    🔑 Login
                                </Link>
                                <Link
                                    href="/signup"
                                    style={btnStyle}
                                    onClick={() => setOpen(false)}
                                    onMouseEnter={(e) => hoverFn(e, true)}
                                    onMouseLeave={(e) => hoverFn(e, false)}
                                >
                                    ✍️ Sign Up
                                </Link>
                            </>
                        )}

                        {isLoggedIn && !isAdmin && (
                            <>
                                <Link
                                    href="/history"
                                    style={btnStyle}
                                    onClick={() => setOpen(false)}
                                    onMouseEnter={(e) => hoverFn(e, true)}
                                    onMouseLeave={(e) => hoverFn(e, false)}
                                >
                                    📋 History
                                </Link>
                                <button
                                    style={btnStyle}
                                    onClick={handleLogout}
                                    onMouseEnter={(e) => hoverFn(e, true)}
                                    onMouseLeave={(e) => hoverFn(e, false)}
                                >
                                    🚪 Logout
                                </button>
                            </>
                        )}

                        {isAdmin && (
                            <>
                                <Link
                                    href="/admin"
                                    style={btnStyle}
                                    onClick={() => setOpen(false)}
                                    onMouseEnter={(e) => hoverFn(e, true)}
                                    onMouseLeave={(e) => hoverFn(e, false)}
                                >
                                    🛡️ Admin Panel
                                </Link>
                                <button
                                    style={btnStyle}
                                    onClick={handleLogout}
                                    onMouseEnter={(e) => hoverFn(e, true)}
                                    onMouseLeave={(e) => hoverFn(e, false)}
                                >
                                    🚪 Logout
                                </button>
                            </>
                        )}
                    </div>
                </div>
            )}

            <style jsx global>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-6px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
        </div>
    );
}
