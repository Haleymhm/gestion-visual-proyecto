import { cookies } from "next/headers";
import { type NextRequest, NextResponse } from "next/server";

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

async function forwardToBackend(
    backendPath: string,
    method: string,
    body?: unknown,
) {
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    const headers: Record<string, string> = {
        "Content-Type": "application/json",
    };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${BACKEND}${backendPath}`, {
        method,
        headers,
        body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    const text = await res.text();
    let json: unknown;
    try {
        json = JSON.parse(text);
    } catch {
        json = { detail: text };
    }

    return NextResponse.json(json, { status: res.status });
}

// POST /api/proxy/boards → create board
export async function POST(req: NextRequest) {
    const body = (await req.json()) as unknown;
    return forwardToBackend("/api/v1/boards", "POST", body);
}

// GET /api/proxy/boards → list boards
export async function GET() {
    return forwardToBackend("/api/v1/boards", "GET");
}
