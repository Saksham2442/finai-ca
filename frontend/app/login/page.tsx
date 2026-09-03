"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";
import { saveToken } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const result = await login(email, password);
      saveToken(result.access_token, result.email);
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-paper flex items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <p className="text-xs uppercase tracking-widest text-ink/50 font-body mb-3">
          Financial Ratio Analysis
        </p>
        <h1 className="font-display text-3xl text-ink mb-8">Log in</h1>

        <form onSubmit={handleSubmit} className="space-y-5">
          <label className="block">
            <span className="text-sm text-ink/70 font-body">Email</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full bg-transparent py-2 font-body text-ink outline-none border-b border-rule focus:border-ink transition-colors"
            />
          </label>
          <label className="block">
            <span className="text-sm text-ink/70 font-body">Password</span>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full bg-transparent py-2 font-body text-ink outline-none border-b border-rule focus:border-ink transition-colors"
            />
          </label>

          {error && (
            <p className="text-sm text-concern font-body">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-ink text-paper px-6 py-3 font-body text-sm tracking-wide hover:bg-accent transition-colors disabled:opacity-50"
          >
            {loading ? "Logging in…" : "Log in"}
          </button>
        </form>

        <p className="text-sm text-ink/60 font-body mt-6">
          Don't have an account? <a href="/signup" className="text-ink underline underline-offset-4">Sign up</a>
        </p>
      </div>
    </main>
  );
}
