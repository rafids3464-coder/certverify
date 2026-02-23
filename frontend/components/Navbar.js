/**
 * components/Navbar.js — Updated navbar with About/History links and 3-dot menu.
 * Upload button removed from nav bar (stays as hero CTA on home page).
 */

import React from "react";
import Link from "next/link";
import { useAuth } from "../context/AuthContext";
import ThreeDotMenu from "./ThreeDotMenu";

export default function Navbar() {
    const { isLoggedIn } = useAuth();

    return (
        <nav className="navbar">
            <div className="navbar-inner">
                {/* Logo */}
                <Link href="/" className="navbar-logo">
                    <div className="logo-icon">🔏</div>
                    <span>CertVerify</span>
                </Link>

                {/* Centre nav links */}
                <ul className="navbar-links">
                    <li><Link href="/">Home</Link></li>
                    <li><Link href="/about">About</Link></li>
                    {isLoggedIn && <li><Link href="/history">History</Link></li>}
                </ul>

                {/* Right: 3-dot menu */}
                <ThreeDotMenu />
            </div>
        </nav>
    );
}
