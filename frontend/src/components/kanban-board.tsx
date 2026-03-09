"use client";

import { useEffect, useRef, useState } from "react";
import {
  DragDropContext,
  Draggable,
  Droppable,
  type DropResult,
} from "@hello-pangea/dnd";
import { CardDetailDialog } from "@/components/card-detail-dialog";
import { ManageTagsDialog } from "@/components/manage-tags-dialog";

export type BoardTag = {
  id: number;
  boardId: number;
  name: string;
  color: string;
};

export type CardTag = {
  id: number;
  cardId: number;
  tagId: number;
  tag: BoardTag;
};

export type ChecklistItem = {
  id: number;
  checklistId: number;
  content: string;
  is_completed: boolean;
};

export type Checklist = {
  id: number;
  cardId: number;
  title: string;
  items: ChecklistItem[];
};

export type Comment = {
  id: number;
  cardId: number;
  content: string;
  createdAt: string;
  userId: number | null;
};

export type Attachment = {
  id: number;
  cardId: number;
  file_name: string;
  file_path: string;
  uploadedAt: string;
};

export type KanbanCard = {
  id: number | string;
  title: string;
  description?: string | null;
  labels?: string[];
  dueDate?: string | null;
  checklists?: Checklist[];
  comments?: Comment[];
  attachments?: Attachment[];
  tags?: CardTag[];
};

export type KanbanColumn = {
  id: number | string;
  title: string;
  position?: number;
  cards: KanbanCard[];
};

export type KanbanBoard = {
  id: number | string;
  name: string;
  createdAt?: string;
  columns: KanbanColumn[];
  tags?: BoardTag[];
};

type KanbanBoardProps = {
  boards: KanbanBoard[];
};

type ApiCard = {
  id: number;
  title: string;
  description: string | null;
  labels: string[];
  dueDate: string | null;
  position: number;
  listId: number;
  checklists: Checklist[];
  comments: Comment[];
  attachments: Attachment[];
  tags: CardTag[];
};

type ApiList = {
  id: number;
  title: string;
  position: number;
  boardId: number;
  cards: ApiCard[];
};

type ApiBoard = {
  id: number;
  name: string;
  createdAt: string;
  lists: ApiList[];
  tags: BoardTag[];
};

function mapApiBoardToKanban(board: ApiBoard): KanbanBoard {
  return {
    id: board.id,
    name: board.name,
    createdAt: board.createdAt,
    tags: board.tags,
    columns: board.lists
      .slice()
      .sort((a, b) => a.position - b.position)
      .map((list) => ({
        id: list.id,
        title: list.title,
        position: list.position,
        cards: list.cards
          .slice()
          .sort((a, b) => a.position - b.position)
          .map((card) => ({
            id: card.id,
            title: card.title,
            description: card.description,
            labels: card.labels,
            dueDate: card.dueDate,
            checklists: (card.checklists ?? []).map((cl) => ({
              ...cl,
              items: cl.items ?? [],
            })),
            comments: card.comments,
            attachments: card.attachments,
            tags: card.tags,
          })),
      })),
  };
}

/** All mutating requests go through our Next.js proxy so the httpOnly token is attached server-side. */
async function proxyFetch(path: string, method: string, body?: unknown): Promise<Response> {
  return fetch(`/api/proxy${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}

// ─── New Board Modal ──────────────────────────────────────────────────────────

type NewBoardModalProps = {
  onClose: () => void;
  onCreated: (board: KanbanBoard) => void;
};

function NewBoardModal({ onClose, onCreated }: NewBoardModalProps) {
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await proxyFetch("/boards", "POST", { name: name.trim() });
      if (!res.ok) throw new Error("Error al crear el tablero");
      const data = (await res.json()) as ApiBoard;
      onCreated(mapApiBoardToKanban(data));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-sm rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="mb-4 text-base font-semibold text-slate-50">
          Nuevo tablero
        </h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <input
            ref={inputRef}
            type="text"
            placeholder="Nombre del tablero"
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={255}
            className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-emerald-500"
          />
          {error && <p className="text-xs text-red-400">{error}</p>}
          <div className="flex gap-2 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-xs font-medium text-slate-300 transition hover:border-slate-500"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading || !name.trim()}
              className="rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-50"
            >
              {loading ? "Creando..." : "Crear tablero"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Inline Add Column Form ───────────────────────────────────────────────────

type AddColumnFormProps = {
  boardId: number | string;
  onCreated: (board: KanbanBoard) => void;
};

function AddColumnForm({ boardId, onCreated }: AddColumnFormProps) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setLoading(true);
    try {
      const res = await proxyFetch(`/boards/${String(boardId)}`, "POST", { name: title.trim() });
      if (!res.ok) throw new Error("Error");
      const data = (await res.json()) as ApiBoard;
      onCreated(mapApiBoardToKanban(data));
      setTitle("");
      setOpen(false);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="flex h-min w-64 shrink-0 items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-900/40 px-3 py-3 text-sm font-medium text-slate-300 transition hover:border-emerald-500 hover:text-emerald-300"
      >
        + Agregar columna
      </button>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex w-64 shrink-0 flex-col gap-2 rounded-xl border border-emerald-700 bg-slate-900/60 p-3 shadow-sm"
    >
      <input
        ref={inputRef}
        type="text"
        placeholder="Título de la columna"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        maxLength={255}
        className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-xs text-slate-100 placeholder-slate-500 outline-none focus:border-emerald-500"
      />
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={loading || !title.trim()}
          className="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-50"
        >
          {loading ? "..." : "Agregar"}
        </button>
        <button
          type="button"
          onClick={() => { setOpen(false); setTitle(""); }}
          className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200"
        >
          Cancelar
        </button>
      </div>
    </form>
  );
}

// ─── Inline Add Card Form ─────────────────────────────────────────────────────

type AddCardFormProps = {
  boardId: number | string;
  listId: number | string;
  onCreated: (board: KanbanBoard) => void;
};

function AddCardForm({ boardId, listId, onCreated }: AddCardFormProps) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await proxyFetch(
        `/boards/${String(boardId)}/lists/${String(listId)}`,
        "POST",
        { title: title.trim(), description: null },
      );
      if (!res.ok) {
        const data = await res.json().catch(() => ({})) as { detail?: string };
        throw new Error(data.detail ?? `Error ${res.status}`);
      }
      const data = (await res.json()) as ApiBoard;
      onCreated(mapApiBoardToKanban(data));
      setTitle("");
      setOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear la tarjeta");
    } finally {
      setLoading(false);
    }
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="mt-2 w-full rounded-md border border-dashed border-slate-700 px-2 py-1 text-left text-[11px] font-medium text-slate-300 transition hover:border-emerald-500 hover:text-emerald-300"
      >
        + Agregar tarjeta
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="mt-2 flex flex-col gap-2">
      <textarea
        ref={inputRef}
        placeholder="Título de la tarjeta"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        rows={2}
        maxLength={255}
        className="w-full resize-none rounded-lg border border-slate-700 bg-slate-800 px-2 py-1.5 text-xs text-slate-100 placeholder-slate-500 outline-none focus:border-emerald-500"
      />
      {error && <p className="text-[10px] text-red-400">{error}</p>}
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={loading || !title.trim()}
          className="rounded-lg bg-emerald-600 px-3 py-1 text-[11px] font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-50"
        >
          {loading ? "..." : "Agregar"}
        </button>
        <button
          type="button"
          onClick={() => { setOpen(false); setTitle(""); setError(null); }}
          className="rounded-lg border border-slate-700 px-3 py-1 text-[11px] text-slate-400 hover:text-slate-200"
        >
          Cancelar
        </button>
      </div>
    </form>
  );
}

// ─── Main board view ──────────────────────────────────────────────────────────

export function KanbanBoardView({ boards }: KanbanBoardProps) {
  const [allBoards, setAllBoards] = useState<KanbanBoard[]>(boards);
  const [activeId, setActiveId] = useState<number | string>(
    boards[0]?.id ?? "demo-board",
  );
  const state = allBoards.find((b) => b.id === activeId) ?? allBoards[0] ?? {
    id: "demo-board",
    name: "Sin tableros",
    columns: [],
  };

  // Helper: update a single board in the allBoards list
  const upsertBoard = (updated: KanbanBoard) => {
    setAllBoards((prev) => {
      const idx = prev.findIndex((b) => b.id === updated.id);
      if (idx === -1) return [...prev, updated];
      const copy = [...prev];
      copy[idx] = updated;
      return copy;
    });
  };

  const [selectedCardId, setSelectedCardId] = useState<string | null>(null);
  const [isManageTagsOpen, setIsManageTagsOpen] = useState(false);
  const [isNewBoardOpen, setIsNewBoardOpen] = useState(false);
  const [isBoardMenuOpen, setIsBoardMenuOpen] = useState(false);

  useEffect(() => {
    if (state.id === "demo-board") return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
    const wsUrl = apiUrl.replace(/^http/, "ws");
    const websocket = new WebSocket(
      `${wsUrl}/ws/boards/${String(state.id)}`,
    );

    websocket.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as ApiBoard;
        upsertBoard(mapApiBoardToKanban(data));
      } catch {
        // Ignore malformed messages
      }
    };

    return () => {
      websocket.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.id]);

  const persistMove = async (
    cardId: string,
    sourceListId: string,
    destListId: string,
    destIndex: number,
  ) => {
    const payload = {
      cardId: Number(cardId),
      sourceListId: Number(sourceListId),
      destListId: Number(destListId),
      destIndex,
    };
    try {
      const res = await proxyFetch(
        `/boards/${String(state.id)}/move-card`,
        "POST",
        payload,
      );
      if (!res.ok) {
        const data = (await res.json().catch(() => ({}))) as { detail?: string };
        console.error("[move-card] Backend error:", res.status, data.detail ?? data);
      }
    } catch (e) {
      console.error("[move-card] Request failed:", e);
    }
  };

  const handleDragEnd = (result: DropResult) => {
    const { destination, source, draggableId } = result;

    if (!destination) return;

    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    setState((prev) => {
      const columnsCopy = prev.columns.map((col) => ({
        ...col,
        cards: [...col.cards],
      }));

      const sourceColumnIndex = columnsCopy.findIndex(
        (col) => String(col.id) === source.droppableId,
      );
      const destColumnIndex = columnsCopy.findIndex(
        (col) => String(col.id) === destination.droppableId,
      );

      if (sourceColumnIndex === -1 || destColumnIndex === -1) {
        return prev;
      }

      const sourceColumn = columnsCopy[sourceColumnIndex];
      const destColumn = columnsCopy[destColumnIndex];

      const [moved] = sourceColumn.cards.splice(source.index, 1);
      if (!moved || String(moved.id) !== draggableId) {
        sourceColumn.cards.splice(source.index, 0, moved);
        return prev;
      }

      destColumn.cards.splice(destination.index, 0, moved);

      void persistMove(
        draggableId,
        source.droppableId,
        destination.droppableId,
        destination.index,
      );

      return {
        ...prev,
        columns: columnsCopy,
      };
    });
  };

  // For drag-end we need to mutate the active board inside allBoards
  const setState = (updater: (prev: KanbanBoard) => KanbanBoard) => {
    setAllBoards((prev) => {
      const idx = prev.findIndex((b) => b.id === activeId);
      if (idx === -1) return prev;
      const copy = [...prev];
      copy[idx] = updater(copy[idx]!);
      return copy;
    });
  };

  const selectedCard: KanbanCard | null =
    selectedCardId == null
      ? null
      : (() => {
        for (const column of state.columns) {
          const match = column.cards.find(
            (card) => String(card.id) === selectedCardId,
          );
          if (match) return match;
        }
        return null;
      })();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <header className="border-b border-slate-800 bg-slate-950/60 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-emerald-500 text-sm font-bold text-slate-950">
              KV
            </div>
            <div>
              <p className="text-sm font-semibold tracking-tight">
                Kanban Visual
              </p>
              <p className="text-xs text-slate-400">
                Visual workflow management for teams
              </p>
            </div>
          </div>

          {/* Board switcher */}
          <div className="relative hidden md:flex items-center gap-1">
            {allBoards.map((b) => (
              <button
                key={b.id}
                onClick={() => { setActiveId(b.id); setSelectedCardId(null); }}
                className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${b.id === state.id
                  ? "bg-emerald-600 text-white shadow"
                  : "border border-slate-700 bg-slate-900 text-slate-300 hover:border-emerald-500 hover:text-emerald-300"
                  }`}
              >
                {b.name}
              </button>
            ))}
          </div>

          {/* Board switcher (mobile dropdown) */}
          <div className="relative md:hidden">
            <button
              onClick={() => setIsBoardMenuOpen((o) => !o)}
              className="rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-200"
            >
              {state.name} ▾
            </button>
            {isBoardMenuOpen && (
              <div className="absolute right-0 z-50 mt-1 w-48 rounded-xl border border-slate-700 bg-slate-900 p-1 shadow-xl">
                {allBoards.map((b) => (
                  <button
                    key={b.id}
                    onClick={() => { setActiveId(b.id); setSelectedCardId(null); setIsBoardMenuOpen(false); }}
                    className={`w-full rounded-lg px-3 py-2 text-left text-xs font-medium transition ${b.id === state.id
                      ? "bg-emerald-600/20 text-emerald-300"
                      : "text-slate-300 hover:bg-slate-800"
                      }`}
                  >
                    {b.name}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsManageTagsOpen(true)}
              className="rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-200 shadow-sm transition hover:border-emerald-500 hover:text-emerald-300"
            >
              Manage Tags
            </button>
            <button
              onClick={() => setIsNewBoardOpen(true)}
              className="rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-200 shadow-sm transition hover:border-emerald-500 hover:text-emerald-300"
            >
              Nuevo tablero
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-6">
        <section className="flex items-center justify-between gap-2">
          <div className="space-y-1">
            <h1 className="text-lg font-semibold tracking-tight md:text-xl">
              {state.name}
            </h1>
            <p className="text-xs text-slate-400 md:text-sm">
              Arrastra tarjetas entre columnas para reorganizar tu trabajo.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="hidden text-xs text-slate-400 md:inline">
              Synced workspace
            </span>
            <div className="flex -space-x-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-full border border-slate-900 bg-slate-700 text-[10px] font-semibold">
                AB
              </div>
              <div className="flex h-7 w-7 items-center justify-center rounded-full border border-slate-900 bg-slate-700 text-[10px] font-semibold">
                CD
              </div>
              <div className="flex h-7 w-7 items-center justify-center rounded-full border border-slate-900 bg-slate-700 text-[10px] font-semibold">
                +3
              </div>
            </div>
          </div>
        </section>

        <DragDropContext onDragEnd={handleDragEnd}>
          <section className="flex gap-4 overflow-x-auto pb-4">
            {state.columns.map((column) => (
              <Droppable droppableId={String(column.id)} key={column.id}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className="flex w-64 shrink-0 flex-col rounded-xl border border-slate-800 bg-slate-900/60 p-3 shadow-sm"
                  >
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <h2 className="text-sm font-medium tracking-tight">
                        {column.title}
                      </h2>
                      <span className="rounded-full bg-slate-800 px-2 py-0.5 text-[10px] font-medium text-slate-300">
                        {column.cards.length}
                      </span>
                    </div>
                    <div
                      className={`space-y-2 ${snapshot.isDraggingOver ? "bg-slate-900/60" : ""
                        }`}
                    >
                      {column.cards.map((card, index) => (
                        <Draggable
                          key={card.id}
                          draggableId={String(card.id)}
                          index={index}
                        >
                          {(dragProvided, dragSnapshot) => (
                            <article
                              ref={dragProvided.innerRef}
                              {...dragProvided.draggableProps}
                              {...dragProvided.dragHandleProps}
                              onClick={() =>
                                setSelectedCardId(String(card.id))
                              }
                              className={`group cursor-pointer rounded-lg border border-slate-800 bg-slate-900/80 p-3 text-xs shadow-sm transition hover:border-emerald-500 hover:bg-slate-900 ${dragSnapshot.isDragging
                                ? "border-emerald-400 shadow-lg"
                                : ""
                                }`}
                            >
                              <header className="mb-1 flex items-start justify-between gap-2">
                                <h3 className="text-xs font-semibold leading-snug text-slate-50">
                                  {card.title}
                                </h3>
                              </header>
                              {card.description ? (
                                <p className="mb-2 line-clamp-2 text-[11px] text-slate-400">
                                  {card.description}
                                </p>
                              ) : null}
                              <footer className="flex flex-wrap items-center gap-1.5 mt-2">
                                {card.tags?.map((cardTag) => (
                                  <span
                                    key={cardTag.id}
                                    style={{ backgroundColor: cardTag.tag.color + "33", color: cardTag.tag.color, borderColor: cardTag.tag.color }}
                                    className="rounded-full border px-2 py-0.5 text-[10px] font-medium"
                                  >
                                    {cardTag.tag.name}
                                  </span>
                                ))}
                                {card.labels?.map((label) => (
                                  <span
                                    key={label}
                                    className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-300"
                                  >
                                    {label}
                                  </span>
                                ))}
                                {card.checklists && card.checklists.length > 0 && (
                                  <span className="flex items-center gap-1 rounded bg-slate-800/80 px-1.5 py-0.5 text-[10px] font-medium text-slate-300">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
                                    {card.checklists.reduce((acc, c) => acc + (c.items ?? []).filter(i => i.is_completed).length, 0)}/
                                    {card.checklists.reduce((acc, c) => acc + (c.items ?? []).length, 0)}
                                  </span>
                                )}
                                {card.comments && card.comments.length > 0 && (
                                  <span className="flex items-center gap-1 rounded bg-slate-800/80 px-1.5 py-0.5 text-[10px] font-medium text-slate-300">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                                    {card.comments.length}
                                  </span>
                                )}
                                {card.attachments && card.attachments.length > 0 && (
                                  <span className="flex items-center gap-1 rounded bg-slate-800/80 px-1.5 py-0.5 text-[10px] font-medium text-slate-300">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
                                    {card.attachments.length}
                                  </span>
                                )}
                                {card.dueDate ? (
                                  <span className="ml-auto flex items-center gap-1 rounded-full bg-slate-800 px-2 py-0.5 text-[10px] text-slate-300">
                                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                                    {card.dueDate}
                                  </span>
                                ) : null}
                              </footer>
                            </article>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>

                    {/* Add card form */}
                    <AddCardForm
                      boardId={state.id}
                      listId={column.id}
                      onCreated={(updatedBoard) => upsertBoard(updatedBoard)}
                    />
                  </div>
                )}
              </Droppable>
            ))}

            <AddColumnForm
              boardId={state.id}
              onCreated={(updatedBoard) => upsertBoard(updatedBoard)}
            />
          </section>
        </DragDropContext>
      </main>

      <CardDetailDialog
        board={state}
        card={selectedCard}
        onClose={() => setSelectedCardId(null)}
        onCardUpdate={(updatedCard) => {
          const updatedBoard: KanbanBoard = {
            ...state,
            columns: state.columns.map((col) => ({
              ...col,
              cards: col.cards.map((c) =>
                String(c.id) === String(updatedCard.id) ? updatedCard : c
              ),
            })),
          };
          upsertBoard(updatedBoard);
        }}
      />

      {isManageTagsOpen && (
        <ManageTagsDialog board={state} onClose={() => setIsManageTagsOpen(false)} />
      )}

      {isNewBoardOpen && (
        <NewBoardModal
          onClose={() => setIsNewBoardOpen(false)}
          onCreated={(newBoard) => {
            upsertBoard(newBoard);
            setActiveId(newBoard.id);
            setIsNewBoardOpen(false);
          }}
        />
      )}
    </div>
  );
}
