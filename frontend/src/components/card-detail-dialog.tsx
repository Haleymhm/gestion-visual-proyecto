"use client";

import { useEffect, useState } from "react";
import type { KanbanBoard, KanbanCard, Checklist, Comment, Attachment } from "@/components/kanban-board";

type CardActivity = {
  id: number;
  cardId: number;
  type: string;
  payload: string | null;
  createdAt: string;
};

type CardDetailDialogProps = {
  board: KanbanBoard;
  card: KanbanCard | null;
  onClose: () => void;
};

export function CardDetailDialog({ board, card, onClose }: CardDetailDialogProps) {
  const [activity, setActivity] = useState<CardActivity[]>([]);
  const [newComment, setNewComment] = useState("");
  const [newChecklistTitle, setNewChecklistTitle] = useState("");
  const [newItemContents, setNewItemContents] = useState<Record<number, string>>({});

  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

  useEffect(() => {
    if (!card) return;

    const loadActivity = async () => {
      try {
        const response = await fetch(`${baseUrl}/api/v1/activity/cards/${String(card.id)}`);
        if (!response.ok) return;
        const data = (await response.json()) as CardActivity[];
        setActivity(data);
      } catch {
        // Silent fail
      }
    };
    void loadActivity();
  }, [card, baseUrl]);

  if (!card) return null;

  // -- Event Handlers -- //

  const handleAddTag = async (tagId: number) => {
    try {
      await fetch(`${baseUrl}/api/v1/tags/cards/${card.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tagId }),
      });
    } catch (e) { console.error(e); }
  };

  const handleRemoveTag = async (cardTagId: number) => {
    try {
      await fetch(`${baseUrl}/api/v1/tags/cards/${cardTagId}`, { method: "DELETE" });
    } catch (e) { console.error(e); }
  };

  const handleCreateChecklist = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newChecklistTitle.trim()) return;
    try {
      await fetch(`${baseUrl}/api/v1/checklists/cards/${card.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: newChecklistTitle.trim() }),
      });
      setNewChecklistTitle("");
    } catch (e) { console.error(e); }
  };

  const handleAddChecklistItem = async (e: React.FormEvent, checklistId: number) => {
    e.preventDefault();
    const content = newItemContents[checklistId] || "";
    if (!content.trim()) return;
    try {
      await fetch(`${baseUrl}/api/v1/checklists/${checklistId}/items`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: content.trim(), is_completed: false }),
      });
      setNewItemContents(prev => ({ ...prev, [checklistId]: "" }));
    } catch (e) { console.error(e); }
  };

  const handleToggleChecklistItem = async (itemId: number, is_completed: boolean) => {
    try {
      await fetch(`${baseUrl}/api/v1/checklists/items/${itemId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_completed: !is_completed }),
      });
    } catch (e) { console.error(e); }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    try {
      await fetch(`${baseUrl}/api/v1/comments/cards/${card.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: newComment.trim() }),
      });
      setNewComment("");
    } catch (e) { console.error(e); }
  };

  const handleUploadAttachment = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      await fetch(`${baseUrl}/api/v1/attachments/cards/${card.id}`, {
        method: "POST",
        body: formData,
      });
    } catch (e) { console.error(e); }
  };

  const handleDeleteAttachment = async (attachmentId: number) => {
    try {
      await fetch(`${baseUrl}/api/v1/attachments/${attachmentId}`, { method: "DELETE" });
    } catch (e) { console.error(e); }
  }

  // Derived state for available tags not active on the card
  const availableTags = board.tags?.filter(
    (bt) => !card.tags?.some((ct) => ct.tagId === bt.id)
  ) || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4">
      <div className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-2xl border border-slate-800 bg-slate-950 p-5 shadow-2xl custom-scrollbar flex flex-col md:flex-row gap-6">

        <button
          type="button"
          onClick={onClose}
          className="absolute right-3 top-3 rounded-full border border-slate-700 bg-slate-900 px-2 py-0.5 text-xs text-slate-300 hover:border-emerald-500 hover:text-emerald-300 z-10"
        >
          Close
        </button>

        {/* Left Column (Main content) */}
        <div className="flex-1 space-y-6">
          <header>
            <h2 className="text-xl font-semibold leading-snug text-slate-50">
              {card.title}
            </h2>
            <div className="mt-2 flex flex-wrap gap-2">
              {card.tags?.map(ct => (
                <span key={ct.id} className="inline-flex items-center gap-1 rounded bg-slate-900 border px-2 py-1 text-xs font-medium" style={{ borderColor: ct.tag.color, color: ct.tag.color }}>
                  {ct.tag.name}
                  <button onClick={() => handleRemoveTag(ct.id)} className="ml-1 hover:text-red-400">&times;</button>
                </span>
              ))}
              {availableTags.length > 0 && (
                <select
                  onChange={(e) => {
                    if (e.target.value) handleAddTag(Number(e.target.value));
                    e.target.value = "";
                  }}
                  className="bg-slate-900 border border-slate-700 text-slate-300 text-xs rounded px-2 py-1"
                >
                  <option value="">+ Add Tag</option>
                  {availableTags.map(bt => (
                    <option key={bt.id} value={bt.id}>{bt.name}</option>
                  ))}
                </select>
              )}
            </div>
          </header>

          <section>
            <h3 className="mb-2 text-sm font-medium uppercase tracking-wide text-slate-400">Description</h3>
            <p className="rounded-lg border border-slate-800 bg-slate-900/60 p-3 text-sm text-slate-200">
              {card.description ?? "No description yet."}
            </p>
          </section>

          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium uppercase tracking-wide text-slate-400">Checklists</h3>
            </div>
            {card.checklists?.map(cl => {
              const completed = cl.items.filter(i => i.is_completed).length;
              const total = cl.items.length;
              const percent = total === 0 ? 0 : Math.round((completed / total) * 100);
              return (
                <div key={cl.id} className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
                  <h4 className="font-medium text-slate-200 mb-2">{cl.title} <span className="text-xs text-slate-500 ml-2">{percent}%</span></h4>
                  <div className="w-full bg-slate-800 rounded-full h-1.5 mb-3">
                    <div className="bg-emerald-500 h-1.5 rounded-full transition-all duration-300" style={{ width: `${percent}%` }}></div>
                  </div>
                  <ul className="space-y-2 mb-3">
                    {cl.items.map(item => (
                      <li key={item.id} className="flex items-center gap-2 group">
                        <input
                          type="checkbox"
                          checked={item.is_completed}
                          onChange={() => handleToggleChecklistItem(item.id, item.is_completed)}
                          className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-emerald-500 focus:ring-emerald-500 focus:ring-offset-slate-900 cursor-pointer"
                        />
                        <span className={`text-sm ${item.is_completed ? 'line-through text-slate-500' : 'text-slate-300'}`}>
                          {item.content}
                        </span>
                      </li>
                    ))}
                  </ul>
                  <form onSubmit={(e) => handleAddChecklistItem(e, cl.id)} className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Add an item"
                      value={newItemContents[cl.id] || ""}
                      onChange={(e) => setNewItemContents(prev => ({ ...prev, [cl.id]: e.target.value }))}
                      className="flex-1 bg-slate-900 border border-slate-700 text-sm rounded px-3 py-1.5 text-slate-200 placeholder:text-slate-500 focus:border-emerald-500 focus:outline-none"
                    />
                    <button type="submit" className="bg-slate-800 text-slate-300 px-3 py-1.5 rounded text-sm hover:bg-slate-700">Add</button>
                  </form>
                </div>
              );
            })}
            <form onSubmit={handleCreateChecklist} className="flex gap-2">
              <input
                type="text"
                placeholder="New checklist title"
                value={newChecklistTitle}
                onChange={e => setNewChecklistTitle(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-700 text-sm rounded px-3 py-1.5 text-slate-200 placeholder:text-slate-500 focus:border-emerald-500 focus:outline-none"
              />
              <button type="submit" className="bg-slate-800 text-slate-300 px-3 py-1.5 rounded text-sm hover:bg-slate-700">Create</button>
            </form>
          </section>

          <section>
            <h3 className="mb-3 text-sm font-medium uppercase tracking-wide text-slate-400">Comments</h3>
            <div className="space-y-3 mb-4">
              {card.comments?.length === 0 ? (
                <p className="text-sm text-slate-500">No comments yet.</p>
              ) : (
                card.comments?.map(comment => (
                  <div key={comment.id} className="rounded-lg border border-slate-800 bg-slate-900 p-3">
                    <p className="text-sm text-slate-200 whitespace-pre-wrap">{comment.content}</p>
                    <p className="text-[10px] text-slate-500 mt-2">
                      {new Date(comment.createdAt).toLocaleString()}
                    </p>
                  </div>
                ))
              )}
            </div>
            <form onSubmit={handleAddComment} className="mt-2">
              <textarea
                placeholder="Write a comment..."
                value={newComment}
                onChange={e => setNewComment(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-sm rounded-lg px-3 py-2 text-slate-200 placeholder:text-slate-500 focus:border-emerald-500 focus:outline-none min-h-[80px]"
              />
              <button disabled={!newComment.trim()} type="submit" className="mt-2 bg-emerald-600/20 text-emerald-400 border border-emerald-500/50 px-4 py-1.5 rounded-md text-sm font-medium hover:bg-emerald-600/30 disabled:opacity-50">
                Save Comment
              </button>
            </form>
          </section>
        </div>

        {/* Right Column (Sidebar) */}
        <div className="w-full md:w-64 space-y-6 pt-8 md:pt-0">

          <section>
            <h3 className="mb-3 text-sm font-medium uppercase tracking-wide text-slate-400">Attachments</h3>
            <div className="space-y-2 mb-3">
              {card.attachments?.map(att => (
                <div key={att.id} className="flex items-center justify-between rounded bg-slate-900 border border-slate-800 p-2 text-xs text-slate-300">
                  <a href={`${baseUrl}/${att.file_path}`} target="_blank" rel="noopener noreferrer" className="truncate hover:text-emerald-400 max-w-[150px]">
                    {att.file_name}
                  </a>
                  <button onClick={() => handleDeleteAttachment(att.id)} className="text-slate-500 hover:text-red-400">&times;</button>
                </div>
              ))}
            </div>
            <label className="flex cursor-pointer items-center justify-center rounded-md border border-dashed border-slate-600 bg-slate-900/50 py-4 text-xs font-medium text-slate-400 hover:border-emerald-500 hover:text-emerald-400 transition">
              Upload file
              <input type="file" className="hidden" onChange={handleUploadAttachment} />
            </label>
          </section>

          <section>
            <h3 className="mb-3 text-sm font-medium uppercase tracking-wide text-slate-400">Activity</h3>
            <div className="max-h-60 space-y-2 overflow-y-auto rounded-lg border border-slate-800 bg-slate-900/40 p-3 text-[11px] text-slate-300">
              {activity.length === 0 ? (
                <p className="text-slate-500">No activity yet.</p>
              ) : (
                activity.map((item) => (
                  <div key={item.id} className="flex items-start gap-2 rounded-md bg-slate-900/80 p-2">
                    <span className="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />
                    <div>
                      <p className="font-medium text-slate-100">
                        {item.type === "move" ? "Card moved" : item.type}
                      </p>
                      {item.payload ? (
                        <p className="text-slate-400 break-words line-clamp-2">{item.payload}</p>
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

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: #334155;
          border-radius: 10px;
        }
      `}</style>
    </div>
  );
}
