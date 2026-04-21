export type KnowledgeCard = {
  id: string;
  type: string;
  name: string;
  description: string;
  created: string;
};

type DisplayKnowledgeProps = {
  objects: KnowledgeCard[];
};

function formatCreatedDate(created: string) {
  const parsedDate = new Date(created);

  if (Number.isNaN(parsedDate.getTime())) {
    return created;
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(parsedDate);
}

export default function DisplayKnowledge({
  objects,
}: DisplayKnowledgeProps) {
  return (
    <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4">
      {objects.map((object) => (
        <article
          key={object.id}
          className="flex max-h-80 h-80 flex-col overflow-hidden rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm"
        >
          <span className="w-fit rounded-full bg-zinc-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-zinc-600">
            {object.type}
          </span>

          <h2 className="mt-4 text-lg font-semibold leading-tight text-zinc-950">
            {object.name}
          </h2>

          <p className="mt-3 min-h-0 flex-1 overflow-y-auto break-words pr-1 text-sm leading-6 text-zinc-600">
            {object.description}
          </p>

          <div className="mt-5 border-t border-zinc-200 pt-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-400">
              Created
            </p>
            <p className="mt-1 text-sm text-zinc-500">
              {formatCreatedDate(object.created)}
            </p>
          </div>
        </article>
      ))}
    </div>
  );
}
