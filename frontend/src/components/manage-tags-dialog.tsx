"use client";

import { useState } from "react";
import type { KanbanBoard } from "@/components/kanban-board";

type ManageTagsDialogProps = {
    board: KanbanBoard;
    onClose: () => void;
};

export function ManageTagsDialog({ board, onClose }: ManageTagsDialogProps) {
    const [name, setName] = useState("");
    const [color, setColor] = useState("#10b981");

    const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

    const handleCreateTag = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!name.trim()) return;
        try {
            await fetch(`${baseUrl}/api/v1/tags/boards/${board.id}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: name.trim(), color }),
            });
            setName("");
        } catch {
            // Ignore
        }
    };

    const handleDeleteTag = async (tagId: number) => {
        try {
            await fetch(`${baseUrl}/api/v1/tags/boards/${tagId}`, { method: "DELETE" });
        } catch {
            // Ignore
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4">
            <div className="relative w-full max-w-sm rounded-2xl border border-slate-800 bg-slate-950 p-5 shadow-2xl">
                <button
                    type="button"
                    onClick={onClose}
                    className="absolute right-3 top-3 rounded-full border border-slate-700 bg-slate-900 px-2 py-0.5 text-xs text-slate-300 hover:border-emerald-500 hover:text-emerald-300"
                >
                    Close
                </button>

                <h2 className="mb-4 text-base font-semibold leading-snug text-slate-50">
                    Manage Board Tags
                </h2>

                <ul className="mb-5 space-y-2">
                    {(!board.tags || board.tags.length === 0) && (
                        <p className="text-xs text-slate-500">No tags configured yet.</p>
                    )}
                    {board.tags?.map((tag) => (
                        <li key={tag.id} className="flex items-center justify-between rounded-md border border-slate-800 bg-slate-900/60 px-3 py-2">
                            <span className="flex items-center gap-2 text-sm text-slate-200">
                                <span className="h-3 w-3 rounded-full" style={{ backgroundColor: tag.color }}></span>
                                {tag.name}
                            </span>
                            <button onClick={() => handleDeleteTag(tag.id)} className="text-slate-500 hover:text-red-400 text-sm">
                                &times;
                            </button>
                        </li>
                    ))}
                </ul>

                <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">Add New Tag</h3>
                <form onSubmit={handleCreateTag} className="space-y-3">
                    <input
                        type="text"
                        placeholder="Tag name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200 placeholder:text-slate-500 focus:border-emerald-500 focus:outline-none"
                        required
                    />
                    <div className="flex items-center gap-3">
                        <input
                            type="color"
                            value={color}
                            onChange={(e) => setColor(e.target.value)}
                            className="h-8 w-14 cursor-pointer rounded border-0 bg-transparent"
                        />
                        <button
                            type="submit"
                            className="flex-1 rounded-md bg-emerald-600/20 py-2 text-sm font-medium text-emerald-400 border border-emerald-500/50 hover:bg-emerald-600/30"
                        >
                            Create Tag
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
