/**
 * pages/admin/index.js — Admin Dashboard.
 * Features: metrics, all uploads, users list, disable user, retrain button, log tail.
 * Requires admin JWT.
 */

import React, { useEffect, useState, useCallback } from "react";
import Head from "next/head";
import { useRouter } from "next/router";
import axios from "axios";
import { useAuth } from "../../context/AuthContext";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function MetricCard({ icon, label, value, color }) {
    return (
        <div className="card" style={{ textAlign: "center", padding: "24px 20px" }}>
            <div style={{ fontSize: "2rem", marginBottom: 8 }}>{icon}</div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: "1.6rem", fontWeight: 800, color: color || "var(--accent-cyan)", fontFamily: "'JetBrains Mono',monospace" }}>{value}</div>
        </div>
    );
}

function SectionHeader({ children }) {
    return (
        <h2 style={{
            fontSize: "1rem", color: "var(--text-secondary)", textTransform: "uppercase",
            letterSpacing: "0.08em", borderBottom: "1px solid var(--border-subtle)", paddingBottom: 10, marginBottom: 16
        }}>
            {children}
        </h2>
    );
}

export default function AdminDashboard() {
    const { isAdmin, token } = useAuth();
    const router = useRouter();

    const [metrics, setMetrics] = useState(null);
    const [uploads, setUploads] = useState([]);
    const [users, setUsers] = useState([]);
    const [logs, setLogs] = useState([]);
    const [retrain, setRetrain] = useState(false);
    const [retrainMsg, setRetrainMsg] = useState("");
    const [tab, setTab] = useState("overview");

    const authH = { headers: { Authorization: `Bearer ${token}` } };

    const load = useCallback(async () => {
        if (!isAdmin) { router.replace("/admin/login"); return; }
        try {
            const [m, u, us] = await Promise.all([
                axios.get(`${API_URL}/admin/metrics`, authH),
                axios.get(`${API_URL}/admin/uploads?limit=100`, authH),
                axios.get(`${API_URL}/admin/users`, authH),
            ]);
            setMetrics(m.data);
            setUploads(u.data.results || []);
            setUsers(us.data.users || []);
        } catch (e) {
            if (e.response?.status === 403) router.replace("/admin/login");
        }
    }, [isAdmin, token]);          // eslint-disable-line

    useEffect(() => { load(); }, [load]);

    const handleDelete = async (id) => {
        if (!window.confirm("Delete this record?")) return;
        await axios.delete(`${API_URL}/admin/upload/${id}`, authH);
        setUploads((u) => u.filter((r) => r._id !== id));
    };

    const handleDisable = async (email) => {
        if (!window.confirm(`Disable account ${email}?`)) return;
        await axios.post(`${API_URL}/admin/disable-user`, { email }, authH);
        setUsers((u) => u.map((usr) => usr.email === email ? { ...usr, disabled: true } : usr));
    };

    const handleRetrain = async () => {
        setRetrain(true); setRetrainMsg("");
        try {
            const res = await axios.post(`${API_URL}/admin/retrain`, {}, authH);
            setRetrainMsg(res.data.message);
            // Poll logs after 2s
            setTimeout(async () => {
                const l = await axios.get(`${API_URL}/admin/logs?lines=50`, authH);
                setLogs(l.data.lines || []);
            }, 2000);
        } catch (e) {
            setRetrainMsg(e.response?.data?.detail || "Failed to start retraining.");
        } finally {
            setRetrain(false);
        }
    };

    const tabBtnStyle = (active) => ({
        padding: "8px 18px",
        borderRadius: "var(--radius-sm)",
        background: active ? "var(--accent-cyan)" : "var(--bg-elevated)",
        border: "none",
        color: active ? "#000" : "var(--text-secondary)",
        cursor: "pointer",
        fontWeight: active ? 700 : 400,
        fontSize: "0.85rem",
        transition: "all 0.2s",
    });

    if (!isAdmin) return null;

    return (
        <>
            <Head><title>Admin Dashboard — CertVerify</title></Head>
            <div className="page-wrapper">

                {/* Admin top bar */}
                <div style={{ background: "var(--bg-surface)", borderBottom: "1px solid var(--border-subtle)", padding: "0 24px" }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", maxWidth: 1200, margin: "0 auto", height: 60 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                            <span style={{ fontSize: "1.4rem" }}>🛡️</span>
                            <span style={{ fontWeight: 700, fontSize: "1rem" }}>CertVerify Admin</span>
                        </div>
                        <button onClick={() => { const { logout } = require("../../context/AuthContext"); router.push("/"); }}
                            className="btn btn-secondary" style={{ padding: "6px 14px", fontSize: "0.8rem" }}>
                            ← Back to site
                        </button>
                    </div>
                </div>

                <main style={{ maxWidth: 1200, margin: "0 auto", padding: "32px 24px 80px" }}>

                    {/* Tab nav */}
                    <div style={{ display: "flex", gap: 8, marginBottom: 28, flexWrap: "wrap" }}>
                        {[["overview", "📊 Overview"], ["uploads", "📁 Uploads"], ["users", "👤 Users"], ["retrain", "🔁 Retrain"]].map(([id, label]) => (
                            <button key={id} style={tabBtnStyle(tab === id)} onClick={() => setTab(id)}>{label}</button>
                        ))}
                    </div>

                    {/* ── Overview ────────────────────────────────────────────────────── */}
                    {tab === "overview" && metrics && (
                        <>
                            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 16, marginBottom: 32 }}>
                                <MetricCard icon="📁" label="Total Images" value={metrics.dataset.total.toLocaleString()} />
                                <MetricCard icon="✅" label="Real (train)" value={metrics.dataset.train_real.toLocaleString()} color="var(--accent-green)" />
                                <MetricCard icon="❌" label="Fake (train)" value={metrics.dataset.train_fake.toLocaleString()} color="var(--accent-red)" />
                                <MetricCard icon="🧠" label="Model" value={metrics.model.exists ? `${metrics.model.size_mb} MB` : "Missing"} color={metrics.model.exists ? "var(--accent-cyan)" : "var(--accent-red)"} />
                                <MetricCard icon="📤" label="Uploads" value={uploads.length} />
                                <MetricCard icon="👤" label="Users" value={users.length} />
                            </div>

                            <SectionHeader>Recent Uploads</SectionHeader>
                            <div style={{ overflowX: "auto" }}>
                                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.82rem" }}>
                                    <thead>
                                        <tr style={{ background: "var(--bg-elevated)", color: "var(--text-muted)" }}>
                                            {["File", "Prediction", "Confidence", "CNN", "CLIP", "ELA", "User", "Date", ""].map((h) => (
                                                <th key={h} style={{ padding: "10px 12px", textAlign: "left", fontWeight: 600 }}>{h}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {uploads.slice(0, 10).map((r) => (
                                            <tr key={r._id} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                                                <td style={{ padding: "10px 12px", maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{r.filename}</td>
                                                <td style={{ padding: "10px 12px" }}>
                                                    <span className={`badge ${r.prediction === "REAL" ? "badge-real" : "badge-fake"}`} style={{ fontSize: "0.7rem" }}>{r.prediction}</span>
                                                </td>
                                                <td style={{ padding: "10px 12px" }}>{r.confidence?.toFixed(1)}%</td>
                                                <td style={{ padding: "10px 12px" }}>{((r.cnn_score ?? 0) * 100).toFixed(0)}%</td>
                                                <td style={{ padding: "10px 12px" }}>{((r.clip_score ?? 0) * 100).toFixed(0)}%</td>
                                                <td style={{ padding: "10px 12px" }}>{((r.tamper_score ?? 0) * 100).toFixed(0)}%</td>
                                                <td style={{ padding: "10px 12px", color: "var(--text-muted)" }}>{r.user_email || "anon"}</td>
                                                <td style={{ padding: "10px 12px", color: "var(--text-muted)", whiteSpace: "nowrap" }}>
                                                    {r.timestamp ? new Date(r.timestamp).toLocaleDateString() : "—"}
                                                </td>
                                                <td style={{ padding: "10px 12px" }}>
                                                    <button onClick={() => handleDelete(r._id)}
                                                        style={{ background: "none", border: "none", cursor: "pointer", color: "var(--accent-red)", fontSize: "1rem" }}
                                                        title="Delete">🗑️</button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </>
                    )}

                    {/* ── Uploads tab ──────────────────────────────────────────────────── */}
                    {tab === "uploads" && (
                        <>
                            <SectionHeader>All Certificate Uploads ({uploads.length})</SectionHeader>
                            <div style={{ overflowX: "auto" }}>
                                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.82rem" }}>
                                    <thead>
                                        <tr style={{ background: "var(--bg-elevated)", color: "var(--text-muted)" }}>
                                            {["File", "Result", "Conf.", "User", "Date", "Del"].map((h) => (
                                                <th key={h} style={{ padding: "10px 12px", textAlign: "left", fontWeight: 600 }}>{h}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {uploads.map((r) => (
                                            <tr key={r._id} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                                                <td style={{ padding: "10px 12px", maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{r.filename}</td>
                                                <td style={{ padding: "10px 12px" }}>
                                                    <span className={`badge ${r.prediction === "REAL" ? "badge-real" : "badge-fake"}`} style={{ fontSize: "0.7rem" }}>{r.prediction}</span>
                                                </td>
                                                <td style={{ padding: "10px 12px" }}>{r.confidence?.toFixed(1)}%</td>
                                                <td style={{ padding: "10px 12px", color: "var(--text-muted)" }}>{r.user_email || "anon"}</td>
                                                <td style={{ padding: "10px 12px", color: "var(--text-muted)", whiteSpace: "nowrap" }}>
                                                    {r.timestamp ? new Date(r.timestamp).toLocaleDateString() : "—"}
                                                </td>
                                                <td style={{ padding: "10px 12px" }}>
                                                    <button onClick={() => handleDelete(r._id)}
                                                        style={{ background: "none", border: "none", cursor: "pointer", color: "var(--accent-red)" }}>🗑️</button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </>
                    )}

                    {/* ── Users tab ────────────────────────────────────────────────────── */}
                    {tab === "users" && (
                        <>
                            <SectionHeader>Registered Users ({users.length})</SectionHeader>
                            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                                {users.map((u, i) => (
                                    <div key={i} style={{
                                        display: "flex", justifyContent: "space-between", alignItems: "center",
                                        padding: "14px 18px", background: "var(--bg-surface)", border: "1px solid var(--border-subtle)",
                                        borderRadius: "var(--radius-sm)"
                                    }}>
                                        <div>
                                            <div style={{ fontWeight: 600 }}>{u.name}</div>
                                            <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>{u.email}</div>
                                        </div>
                                        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                                            {u.disabled && <span className="badge badge-fake" style={{ fontSize: "0.7rem" }}>Disabled</span>}
                                            {!u.disabled && (
                                                <button onClick={() => handleDisable(u.email)}
                                                    className="btn btn-secondary" style={{ padding: "6px 12px", fontSize: "0.8rem", color: "var(--accent-red)" }}>
                                                    Disable
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                ))}
                                {users.length === 0 && <p style={{ color: "var(--text-muted)" }}>No users registered yet.</p>}
                            </div>
                        </>
                    )}

                    {/* ── Retrain tab ───────────────────────────────────────────────────── */}
                    {tab === "retrain" && (
                        <>
                            <SectionHeader>Model Retraining</SectionHeader>
                            <div className="card" style={{ padding: 28, marginBottom: 24 }}>
                                <p style={{ marginBottom: 20 }}>
                                    Trigger a full retraining run. The ML container will regenerate the dataset and retrain
                                    EfficientNet-B0 (~45–90 min on RTX 4060). Existing <code>model.pth</code> will be replaced when complete.
                                </p>
                                <button
                                    id="retrain-btn"
                                    onClick={handleRetrain}
                                    disabled={retrain}
                                    className="btn btn-primary"
                                    style={{ padding: "12px 28px" }}
                                >
                                    {retrain ? "Starting…" : "🔁 Start Retraining"}
                                </button>
                                {retrainMsg && (
                                    <div style={{
                                        marginTop: 16, padding: "12px 16px", background: "rgba(0,212,255,0.08)",
                                        border: "1px solid rgba(0,212,255,0.2)", borderRadius: "var(--radius-sm)", fontSize: "0.875rem"
                                    }}>
                                        {retrainMsg}
                                    </div>
                                )}
                            </div>

                            {logs.length > 0 && (
                                <>
                                    <SectionHeader>Recent Log Output</SectionHeader>
                                    <pre style={{
                                        background: "var(--bg-elevated)", borderRadius: "var(--radius-sm)",
                                        padding: 16, fontSize: "0.72rem", fontFamily: "'JetBrains Mono',monospace",
                                        maxHeight: 360, overflowY: "auto", color: "var(--text-secondary)", whiteSpace: "pre-wrap"
                                    }}>
                                        {logs.join("\n")}
                                    </pre>
                                </>
                            )}
                        </>
                    )}

                </main>
            </div>
        </>
    );
}
