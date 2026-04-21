import { cache } from "react";
import { readFile } from "fs/promises";
import path from "path";
import { type KnowledgeCard } from "./_components/DisplayKnowledge";
import KnowledgeBrowser, {
  type KnowledgeTypeOption,
} from "./_components/KnowledgeBrowser";

type EnterpriseAttackObject = {
  created?: unknown;
  description?: unknown;
  id?: unknown;
  name?: unknown;
  type?: unknown;
};

type EnterpriseAttackBundle = {
  objects?: EnterpriseAttackObject[];
};

type KnowledgeDataset = {
  objects: KnowledgeCard[];
  typeOptions: KnowledgeTypeOption[];
};

type KnowledgePageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

const PAGE_SIZE = 24;

const getKnowledgeDataset = cache(async (): Promise<KnowledgeDataset> => {
  const filePath = path.join(
    process.cwd(),
    "..",
    "backend",
    "data",
    "enterprise-attack.json",
  );

  const fileContents = await readFile(filePath, "utf8");
  const parsedBundle = JSON.parse(fileContents) as EnterpriseAttackBundle;
  const knowledgeObjects = (parsedBundle.objects ?? []).map((object, index) => ({
    id:
      typeof object.id === "string" && object.id.length > 0
        ? object.id
        : `attack-object-${index}`,
    type:
      typeof object.type === "string" && object.type.length > 0
        ? object.type
        : "Unknown type",
    name:
      typeof object.name === "string" && object.name.length > 0
        ? object.name
        : "Unnamed object",
    description:
      typeof object.description === "string" && object.description.length > 0
        ? object.description
        : "No description available.",
    created:
      typeof object.created === "string" && object.created.length > 0
        ? object.created
        : "Unknown creation date",
  }));

  const typeCounts = new Map<string, number>();

  for (const knowledgeObject of knowledgeObjects) {
    typeCounts.set(
      knowledgeObject.type,
      (typeCounts.get(knowledgeObject.type) ?? 0) + 1,
    );
  }

  const typeOptions = Array.from(typeCounts.entries())
    .sort(([leftType], [rightType]) => leftType.localeCompare(rightType))
    .map(([value, count]) => ({
      value,
      count,
    }));

  return {
    objects: knowledgeObjects,
    typeOptions,
  };
});

function getSingleSearchParam(
  value: string | string[] | undefined,
): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

function parsePageNumber(value: string | undefined) {
  const parsedValue = Number.parseInt(value ?? "", 10);

  if (!Number.isFinite(parsedValue) || parsedValue < 1) {
    return 1;
  }

  return parsedValue;
}

async function KnowledgePage({ searchParams }: KnowledgePageProps) {
  const resolvedSearchParams = await searchParams;
  const requestedType = getSingleSearchParam(resolvedSearchParams.type);
  const requestedPage = parsePageNumber(
    getSingleSearchParam(resolvedSearchParams.page),
  );
  const { objects: knowledgeObjects, typeOptions: knowledgeTypeOptions } =
    await getKnowledgeDataset();

  const selectedType = knowledgeTypeOptions.some(
    (typeOption) => typeOption.value === requestedType,
  )
    ? requestedType ?? null
    : null;

  const filteredKnowledgeObjects =
    selectedType === null
      ? knowledgeObjects
      : knowledgeObjects.filter(
          (knowledgeObject) => knowledgeObject.type === selectedType,
        );

  const totalMatchingObjects = filteredKnowledgeObjects.length;
  const totalPages = Math.max(1, Math.ceil(totalMatchingObjects / PAGE_SIZE));
  const currentPage = Math.min(requestedPage, totalPages);
  const startIndex = (currentPage - 1) * PAGE_SIZE;
  const paginatedObjects = filteredKnowledgeObjects.slice(
    startIndex,
    startIndex + PAGE_SIZE,
  );

  return (
    <div className="min-h-screen bg-zinc-50 px-6 py-10 text-black">
      <div className="mx-auto max-w-7xl">
        <KnowledgeBrowser
          currentPage={currentPage}
          objects={paginatedObjects}
          pageSize={PAGE_SIZE}
          selectedType={selectedType}
          totalMatchingObjects={totalMatchingObjects}
          totalObjects={knowledgeObjects.length}
          totalPages={totalPages}
          typeOptions={knowledgeTypeOptions}
        />
      </div>
    </div>
  );
}

export default KnowledgePage;
