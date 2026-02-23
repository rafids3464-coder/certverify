/**
 * pages/history.js — User upload history page (protected).
 * Shows: thumbnail placeholder, prediction badge, confidence, date.
 */

import React, { useEffect, useState } from "react";
import Link from "next/link";
import Head from "next/head";
import { useRouter } from "next/router";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function HistoryCard({ item }) {
    const isReal = item.prediction === "REAL";
    const date = item.timestamp ? new Date(item.timestamp).toLocaleString() : "—";

    return (
        <div
            style={{
                display: "grid",
                gridTemplateColumns: "80px 1fr auto",
                gap: 16,
                alignItems: "center",
                padding: "16px 20px",
                background: "var(--bg-surface)",
                border: "1px solid var(--border-subtle)",
                borderRadius: "var(--radius-md)",
                transition: "border-color 0.2s",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.borderColor = "var(--border-accent)")}
            onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--border-subtle)")}
        >
            {/* Thumbnail placeholder / heatmap mini */}
            <div
                style={{
                    width: 80,
                    height: 60,
                    borderRadius: "var(--radius-sm)",
                    background: "var(--bg-elevated)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "1.8rem",
                    overflow: "hidden",
                }}
            >
                {item.heatmap_b64 ? (
                    <img
                        src={`data:image/png;base64,${item.heatmap_b64}`}
                        alt="heatmap"
                        style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    />
                ) : (
                    "📄"
                )}
            </div>

            {/* Info */}
            <div>
                <div style={{ fontWeight: 600, fontSize: "0.9rem", marginBottom: 4, wordBreak: "break-all" }}>
                    {item.filename || "Unnamed certificate"}
                </div>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    <span className={`badge ${isReal ? "badge-real" : "badge-fake"}`} style={{ fontSize: "0.72rem" }}>
                        {isReal ? "✓ REAL" : "✗ FAKE"}
                    </span>
                    <span className="badge badge-info" style={{ fontSize: "0.72rem" }}>
                        {item.confidence?.toFixed(1) ?? "—"}% confidence
                    </span>
                </div>
                <div style={{ marginTop: 6, fontSize: "0.75rem", color: "var(--text-muted)" }}>{date}</div>
            </div>

            {/* Score mini-bar */}
            <div style={{ minWidth: 100, fontSize: "0.72rem", color: "var(--text-muted)", textAlign: "right" }}>
                <div>CNN: {((item.cnn_score ?? 0) * 100).toFixed(0)}%</div>
                <div>CLIP: {((item.clip_score ?? 0) * 100).toFixed(0)}%</div>
                <div>ELA: {((item.tamper_score ?? 0) * 100).toFixed(0)}%</div>
            </div>
        </div>
    );
}

export default function HistoryPage() {
    const { isLoggedIn, token } = useAuth();
    const router = useRouter();

    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!isLoggedIn) {
            router.replace("/login");
            return;
        }
        (async () => {
            try {
                const res = await axios.get(`${API_URL}/api/history`, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                setResults(res.data.results || []);
            } catch (e) {
                setError(e.response?.data?.detail || "Failed to load history.");
            } finally {
                setLoading(false);
            }
        })();
    }, [isLoggedIn, router, token]);

    return (
        <>
            <Head><title>History — CertVerify</title></Head>
            <div className="page-wrapper">
                <Navbar />

                <main className="container" style={{ padding: "48px 24px 80px", maxWidth: 860 }}>
                    <div style={{ marginBottom: 36 }}>
                        <h1 style={{ fontSize: "clamp(1.6rem,3vw,2.2rem)", marginBottom: 8 }}>
                            📋 Upload <span className="gradient-text">History</span>
                        </h1>
                        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
                            Your past certificate analyses — newest first.
                        </p>
                    </div>

                    {loading && (
                        <div style={{ display: "flex", justifyContent: "center", padding: 48 }}>
                            <div className="spinner" />
                        </div>
                    )}

                    {error && (
                        <div style={{
                            padding: "14px 18px", background: "rgba(239,68,68,0.1)",
                            border: "1px solid rgba(239,68,68,0.3)", borderRadius: "var(--radius-sm)",
                            color: "var(--accent-red)", fontSize: "0.875rem"
                        }}>
                            ⚠️ {error}
                        </div>
                    )}

                    {!loading && !error && results.length === 0 && (
                        <div className="card" style={{ textAlign: "center", padding: "60px 32px" }}>
                            <div style={{ fontSize: "3rem", marginBottom: 16 }}>📂</div>
                            <h3 style={{ marginBottom: 12 }}>No uploads yet</h3>
                            <p style={{ marginBottom: 24 }}>Upload your first certificate to see results here.</p>
                            <Link href="/upload" className="btn btn-primary">Upload Certificate →</Link>
                        </div>
                    )}

                    {!loading && results.length > 0 && (
                        <>
                            <div style={{ marginBottom: 16, fontSize: "0.85rem", color: "var(--text-muted)" }}>
                                {results.length} record{results.length !== 1 ? "s" : ""}
                            </div>
                            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                                {results.map((r, i) => (
                                    <HistoryCard key={r._id || i} item={r} />
                                ))}
                            </div>
                        </>
                    )}

                    <div style={{ textAlign: "center", marginTop: 40 }}>
                        <Link href="/upload" className="btn btn-secondary">
                            + Analyse Another
                        </Link>
                    </div>
                </main>
            </div>
        </>
    );
}
