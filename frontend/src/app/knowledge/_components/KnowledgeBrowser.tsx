import Link from "next/link";
import DisplayKnowledge, { type KnowledgeCard } from "./DisplayKnowledge";

export type KnowledgeTypeOption = {
  count: number;
  value: string;
};

type KnowledgeBrowserProps = {
  currentPage: number;
  objects: KnowledgeCard[];
  pageSize: number;
  selectedType: string | null;
  totalMatchingObjects: number;
  totalObjects: number;
  totalPages: number;
  typeOptions: KnowledgeTypeOption[];
};

function getKnowledgeHref(page: number, selectedType: string | null) {
  const searchParams = new URLSearchParams();

  if (page > 1) {
    searchParams.set("page", String(page));
  }

  if (selectedType !== null) {
    searchParams.set("type", selectedType);
  }

  const queryString = searchParams.toString();

  return queryString.length > 0 ? `/knowledge?${queryString}` : "/knowledge";
}

function getVisiblePages(currentPage: number, totalPages: number) {
  const visiblePages = new Set<number>([1, totalPages]);

  for (
    let pageNumber = currentPage - 1;
    pageNumber <= currentPage + 1;
    pageNumber += 1
  ) {
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      visiblePages.add(pageNumber);
    }
  }

  return Array.from(visiblePages).sort(
    (leftPage, rightPage) => leftPage - rightPage,
  );
}

export default function KnowledgeBrowser({
  currentPage,
  objects,
  pageSize,
  selectedType,
  totalMatchingObjects,
  totalObjects,
  totalPages,
  typeOptions,
}: KnowledgeBrowserProps) {
  const rangeStart =
    totalMatchingObjects === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const rangeEnd = Math.min(currentPage * pageSize, totalMatchingObjects);
  const visiblePages = getVisiblePages(currentPage, totalPages);

  const filterSummary =
    selectedType === null
      ? `Showing ${rangeStart.toLocaleString()}-${rangeEnd.toLocaleString()} of ${totalObjects.toLocaleString()} objects from enterprise attack data.`
      : `Showing ${rangeStart.toLocaleString()}-${rangeEnd.toLocaleString()} of ${totalMatchingObjects.toLocaleString()} ${selectedType} objects.`;

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">
            ATT&amp;CK Knowledge
          </h1>
          <p className="text-sm text-zinc-600">{filterSummary}</p>
        </div>

        <details className="relative self-start">
          <summary className="list-none rounded-xl border border-zinc-200 bg-white px-4 py-2 text-sm font-medium text-zinc-700 shadow-sm transition-colors hover:cursor-pointer hover:border-zinc-300 hover:bg-zinc-100">
            {selectedType === null ? "Filter by type" : `Type: ${selectedType}`}
          </summary>

          <div className="absolute right-0 top-full z-20 mt-2 flex w-72 flex-col overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-xl">
            <Link
              href={getKnowledgeHref(1, null)}
              className="flex items-center justify-between border-b border-zinc-100 px-4 py-3 text-left text-sm text-zinc-700 transition-colors hover:bg-zinc-50"
            >
              <span>All types</span>
              <span className="text-xs text-zinc-400">
                {totalObjects.toLocaleString()}
              </span>
            </Link>

            <div className="max-h-80 overflow-y-auto">
              {typeOptions.map((typeOption) => (
                <Link
                  key={typeOption.value}
                  href={getKnowledgeHref(1, typeOption.value)}
                  className="flex w-full items-center justify-between px-4 py-3 text-left text-sm text-zinc-700 transition-colors hover:bg-zinc-50"
                >
                  <span className="truncate pr-4">{typeOption.value}</span>
                  <span className="shrink-0 text-xs text-zinc-400">
                    {typeOption.count.toLocaleString()}
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </details>
      </div>

      <DisplayKnowledge objects={objects} />

      <div className="flex flex-col gap-4 rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-zinc-600">
          Page {currentPage.toLocaleString()} of {totalPages.toLocaleString()}
        </p>

        <div className="flex flex-wrap items-center gap-2">
          <Link
            href={getKnowledgeHref(Math.max(1, currentPage - 1), selectedType)}
            aria-disabled={currentPage === 1}
            className={`rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
              currentPage === 1
                ? "pointer-events-none border-zinc-200 bg-zinc-100 text-zinc-400"
                : "border-zinc-200 bg-white text-zinc-700 hover:border-zinc-300 hover:bg-zinc-100"
            }`}
          >
            Previous
          </Link>

          {visiblePages.map((pageNumber, index) => {
            const previousPage = visiblePages[index - 1];
            const shouldShowGap =
              previousPage !== undefined && pageNumber - previousPage > 1;

            return (
              <div key={pageNumber} className="flex items-center gap-2">
                {shouldShowGap && (
                  <span className="px-1 text-sm text-zinc-400">...</span>
                )}

                <Link
                  href={getKnowledgeHref(pageNumber, selectedType)}
                  aria-current={pageNumber === currentPage ? "page" : undefined}
                  className={`rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
                    pageNumber === currentPage
                      ? "border-zinc-900 bg-zinc-900 text-white"
                      : "border-zinc-200 bg-white text-zinc-700 hover:border-zinc-300 hover:bg-zinc-100"
                  }`}
                >
                  {pageNumber}
                </Link>
              </div>
            );
          })}

          <Link
            href={getKnowledgeHref(
              Math.min(totalPages, currentPage + 1),
              selectedType,
            )}
            aria-disabled={currentPage === totalPages}
            className={`rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
              currentPage === totalPages
                ? "pointer-events-none border-zinc-200 bg-zinc-100 text-zinc-400"
                : "border-zinc-200 bg-white text-zinc-700 hover:border-zinc-300 hover:bg-zinc-100"
            }`}
          >
            Next
          </Link>
        </div>
      </div>
    </div>
  );
}
