import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import * as auth from "../services/auth";

export default function Register() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    const submit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        try {
            await auth.register(email, password);
            navigate("/");
        } catch (err: any) {
            setError(err?.message || "Registration failed");
        }
    };

    return (
        <div className="flex items-center justify-center h-screen bg-gray-100 dark:bg-gray-900">
            <form
                onSubmit={submit}
                className="p-6 bg-white rounded shadow-md w-80"
            >
                <h1 className="text-lg font-semibold mb-4">Register</h1>
                {error && (
                    <div className="text-sm text-red-600 mb-2">{error}</div>
                )}
                <label className="block text-sm mb-1">Email</label>
                <input
                    className="w-full p-2 mb-3 border rounded"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <label className="block text-sm mb-1">Password</label>
                <input
                    type="password"
                    className="w-full p-2 mb-4 border rounded"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <div className="flex gap-2">
                    <button
                        type="submit"
                        className="px-3 py-2 bg-emerald-500 text-white rounded"
                    >
                        Create account
                    </button>
                    <button
                        type="button"
                        onClick={() => navigate("/login")}
                        className="px-3 py-2 border rounded"
                    >
                        Back
                    </button>
                </div>
            </form>
        </div>
    );
}
