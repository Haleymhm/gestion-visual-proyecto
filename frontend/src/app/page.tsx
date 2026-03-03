import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { KanbanBoardView, type KanbanBoard } from "@/components/kanban-board";

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

const fallbackBoard: KanbanBoard = {
  id: "demo-board",
  name: "Team roadmap",
  columns: [],
};

async function fetchBoards(): Promise<ApiBoard[]> {
  const baseUrl =
    process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

  const cookieStore = await cookies();
  const token = cookieStore.get("access_token")?.value;

  const response = await fetch(`${baseUrl}/api/v1/boards`, {
    next: { revalidate: 5 },
    headers: token ? {
      "Authorization": `Bearer ${token}`
    } : {},
  });

  if (response.status === 401) {
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    throw new Error("Failed to load boards");
  }

  const data = (await response.json()) as ApiBoard[];
  return data;
}

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

export default async function Home() {
  let apiBoards: ApiBoard[] = [];

  try {
    apiBoards = await fetchBoards();
  } catch (error: unknown) {
    if (error instanceof Error && error.message === "Unauthorized") {
      redirect("/login");
    }
    // Use fallback board when API is not available
  }

  const selectedBoard =
    apiBoards.length > 0
      ? mapApiBoardToKanban(apiBoards[0])
      : fallbackBoard;

  return <KanbanBoardView board={selectedBoard} />;
}
