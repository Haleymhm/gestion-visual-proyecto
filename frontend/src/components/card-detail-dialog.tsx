"use client";

import { useEffect, useState } from "react";

import type { KanbanCard } from "@/components/kanban-board";

type CardActivity = {
  id: number;
  cardId: number;
  type: string;
  payload: string | null;
  createdAt: string;
};

type CardDetailDialogProps = {
  card: KanbanCard | null;
  onClose: () => void;
};

export function CardDetailDialog({ card, onClose }: CardDetailDialogProps) {
  const [activity, setActivity] = useState<CardActivity[]>([]);

  useEffect(() => {
    if (!card) return;

    const loadActivity = async () => {
      const baseUrl =
        process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
      try {
        const response = await fetch(
          `${baseUrl}/api/v1/activity/cards/${String(card.id)}`,
        );
        if (!response.ok) return;
        const data = (await response.json()) as CardActivity[];
        setActivity(data);
      } catch {
        // Silent fail for now
      }
    };

    void loadActivity();
  }, [card]);

  if (!card) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4">
      <div className="relative w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-950 p-5 shadow-2xl">
        <button
          type="button"
          onClick={onClose}
          className="absolute right-3 top-3 rounded-full border border-slate-700 bg-slate-900 px-2 py-0.5 text-xs text-slate-300 hover:border-emerald-500 hover:text-emerald-300"
        >
          Close
        </button>

        <h2 className="mb-3 text-base font-semibold leading-snug text-slate-50">
          {card.title}
        </h2>

        <section className="mb-4 space-y-2">
          <h3 className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Description
          </h3>
          <p className="rounded-lg border border-slate-800 bg-slate-900/60 p-3 text-xs text-slate-200">
            {card.description ?? "No description yet."}
          </p>
        </section>

        <section className="space-y-2">
          <h3 className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Activity
          </h3>
          <div className="max-h-48 space-y-2 overflow-y-auto rounded-lg border border-slate-800 bg-slate-900/40 p-3 text-[11px] text-slate-300">
            {activity.length === 0 ? (
              <p className="text-slate-500">No activity yet.</p>
            ) : (
              activity.map((item) => (
                <div
                  key={item.id}
                  className="flex items-start gap-2 rounded-md bg-slate-900/80 p-2"
                >
                  <span className="mt-0.5 h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  <div>
                    <p className="font-medium text-slate-100">
                      {item.type === "move"
                        ? "Card moved"
                        : item.type}
                    </p>
                    {item.payload ? (
                      <p className="text-slate-400">{item.payload}</p>
                    ) : null}
                    <p className="text-[10px] text-slate-500">
                      {new Date(item.createdAt).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

