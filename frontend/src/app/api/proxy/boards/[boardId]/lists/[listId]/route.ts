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

type Params = { params: Promise<{ boardId: string; listId: string }> };

// POST /api/proxy/boards/[boardId]/lists/[listId]/cards → create card
export async function POST(req: NextRequest, { params }: Params) {
    const { boardId, listId } = await params;
    const body = (await req.json()) as unknown;
    return forwardToBackend(
        `/api/v1/boards/${boardId}/lists/${listId}/cards`,
        "POST",
        body,
    );
}

// DELETE /api/proxy/boards/[boardId]/lists/[listId] → delete list
export async function DELETE(_req: NextRequest, { params }: Params) {
    const { boardId, listId } = await params;
    return forwardToBackend(`/api/v1/boards/${boardId}/lists/${listId}`, "DELETE");
}
