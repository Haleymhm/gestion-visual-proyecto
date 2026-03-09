"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export async function login(prevState: unknown, formData: FormData) {
    const email = formData.get("email");
    const password = formData.get("password");

    if (!email || !password) {
        return { error: "Email and password are required" };
    }

    const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
            username: email.toString(),
            password: password.toString(),
        }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return { error: errorData.detail || "Invalid credentials" };
    }

    const data = await response.json();
    const token = data.access_token;

    const cookieStore = await cookies();
    cookieStore.set("access_token", token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        path: "/",
        maxAge: 60 * 60 * 24 * 7, // 7 days
    });

    redirect("/");
}

export async function register(prevState: unknown, formData: FormData) {
    const email = formData.get("email");
    const password = formData.get("password");
    const fullName = formData.get("fullName");

    if (!email || !password || !fullName) {
        return { error: "All fields are required" };
    }

    const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            email: email.toString(),
            password: password.toString(),
            fullName: fullName.toString(),
        }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return { error: errorData.detail || "Registration failed" };
    }

    // Auto login after registration
    return login(prevState, formData);
}

export async function logout() {
    const cookieStore = await cookies();
    cookieStore.delete("access_token");
    redirect("/login");
}

export async function getToken() {
    const cookieStore = await cookies();
    return cookieStore.get("access_token")?.value;
}
