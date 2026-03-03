import Link from "next/link";
import { getToken, logout } from "../app/actions/auth";

export default async function Navbar() {
    const token = await getToken();

    return (
        <nav className="bg-white shadow">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <div className="flex h-16 justify-between">
                    <div className="flex">
                        <div className="flex flex-shrink-0 items-center">
                            <Link href="/" className="text-xl font-bold text-indigo-600">
                                Kanban Visual
                            </Link>
                        </div>
                    </div>
                    <div className="flex items-center space-x-4">
                        {token ? (
                            <form action={logout}>
                                <button
                                    type="submit"
                                    className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                                >
                                    Logout
                                </button>
                            </form>
                        ) : (
                            <Link
                                href="/login"
                                className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                            >
                                Sign in
                            </Link>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}
