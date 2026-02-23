/**
 * pages/_app.js — App wrapper with AuthProvider and global CSS.
 */

import "../styles/globals.css";
import { AuthProvider } from "../context/AuthContext";

export default function App({ Component, pageProps }) {
    return (
        <AuthProvider>
            <Component {...pageProps} />
        </AuthProvider>
    );
}
