import { cookies } from "next/headers";
import { type NextRequest, NextResponse } from "next/server";

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

type Params = { params: Promise<{ path: string[] }> };

/**
 * Catch-all proxy for activity, tags, checklists, comments, attachments.
 * Forwards requests to the backend with the auth token from the httpOnly cookie.
 */
export async function GET(req: NextRequest, { params }: Params) {
    return forward(req, "GET", params);
}

export async function POST(req: NextRequest, { params }: Params) {
    return forward(req, "POST", params);
}

export async function PATCH(req: NextRequest, { params }: Params) {
    return forward(req, "PATCH", params);
}

export async function DELETE(req: NextRequest, { params }: Params) {
    return forward(req, "DELETE", params);
}

async function forward(
    req: NextRequest,
    method: string,
    params: Params["params"],
) {
    const { path } = await params;
    const backendPath = `/api/v1/${path.join("/")}`;

    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const contentType = req.headers.get("content-type") ?? "";
    const isFormData = contentType.includes("multipart/form-data");

    let body: string | ArrayBuffer | undefined;
    if (method !== "GET" && method !== "DELETE") {
        if (isFormData) {
            body = await req.arrayBuffer();
            const boundary = contentType.match(/boundary=(.+)/)?.[1]?.trim();
            if (boundary) {
                headers["Content-Type"] = `multipart/form-data; boundary=${boundary}`;
            }
        } else {
            const json = (await req.json()) as unknown;
            body = JSON.stringify(json);
            headers["Content-Type"] = "application/json";
        }
    }

    const res = await fetch(`${BACKEND}${backendPath}`, {
        method,
        headers,
        body,
    });

    if (res.status === 204) {
        return new NextResponse(null, { status: 204 });
    }

    const text = await res.text();
    let json: unknown;
    try {
        json = JSON.parse(text);
    } catch {
        json = { detail: text };
    }

    return NextResponse.json(json, { status: res.status });
}
