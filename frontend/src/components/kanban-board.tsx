"use client";

import { useEffect, useState } from "react";
import {
  DragDropContext,
  Draggable,
  Droppable,
  type DropResult,
} from "@hello-pangea/dnd";
import { CardDetailDialog } from "@/components/card-detail-dialog";

export type KanbanCard = {
  id: number | string;
  title: string;
  description?: string | null;
  labels?: string[];
  dueDate?: string | null;
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
};

type KanbanBoardProps = {
  board: KanbanBoard;
};

type ApiCard = {
  id: number;
  title: string;
  description: string | null;
  labels: string[];
  dueDate: string | null;
  position: number;
  listId: number;
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
};

function mapApiBoardToKanban(board: ApiBoard): KanbanBoard {
  return {
    id: board.id,
    name: board.name,
    createdAt: board.createdAt,
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
          })),
      })),
  };
}

export function KanbanBoardView({ board }: KanbanBoardProps) {
  const [state, setState] = useState<KanbanBoard>(board);
  const [selectedCardId, setSelectedCardId] = useState<string | null>(
    null,
  );

  useEffect(() => {
    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
    const wsUrl = baseUrl.replace(/^http/, "ws");
    const websocket = new WebSocket(
      `${wsUrl}/ws/boards/${String(board.id)}`,
    );

    websocket.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as ApiBoard;
        setState(mapApiBoardToKanban(data));
      } catch {
        // Ignore malformed messages
      }
    };

    return () => {
      websocket.close();
    };
  }, [board.id]);

  const persistMove = async (
    cardId: string,
    sourceListId: string,
    destListId: string,
    destIndex: number,
  ) => {
    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

    try {
      await fetch(
        `${baseUrl}/api/v1/boards/${String(board.id)}/move-card`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            cardId: Number(cardId),
            sourceListId: Number(sourceListId),
            destListId: Number(destListId),
            destIndex,
          }),
        },
      );
    } catch {
      // In a real app we would surface an error toast and maybe refetch.
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
          <button className="rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-200 shadow-sm transition hover:border-emerald-500 hover:text-emerald-300">
            New board
          </button>
        </div>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-6">
        <section className="flex items-center justify-between gap-2">
          <div className="space-y-1">
            <h1 className="text-lg font-semibold tracking-tight md:text-xl">
              {board.name}
            </h1>
            <p className="text-xs text-slate-400 md:text-sm">
              Drag cards between columns to reorganize your work. This board
              data is coming from the API.
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
                      className={`space-y-2 ${
                        snapshot.isDraggingOver ? "bg-slate-900/60" : ""
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
                              className={`group cursor-pointer rounded-lg border border-slate-800 bg-slate-900/80 p-3 text-xs shadow-sm transition hover:border-emerald-500 hover:bg-slate-900 ${
                                dragSnapshot.isDragging
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
                              <footer className="flex flex-wrap items-center gap-1.5">
                                {card.labels?.map((label) => (
                                  <span
                                    key={label}
                                    className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-300"
                                  >
                                    {label}
                                  </span>
                                ))}
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
                    <button className="mt-2 w-full rounded-md border border-dashed border-slate-700 px-2 py-1 text-left text-[11px] font-medium text-slate-300 transition hover:border-emerald-500 hover:text-emerald-300">
                      + Add card
                    </button>
                  </div>
                )}
              </Droppable>
            ))}

            <button className="flex h-min w-64 shrink-0 items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-900/40 px-3 py-3 text-sm font-medium text-slate-300 transition hover:border-emerald-500 hover:text-emerald-300">
              + Add column
            </button>
          </section>
        </DragDropContext>
      </main>
      <CardDetailDialog
        card={selectedCard}
        onClose={() => setSelectedCardId(null)}
      />
    </div>
  );
}

