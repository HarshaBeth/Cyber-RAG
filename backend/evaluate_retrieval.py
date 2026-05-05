import argparse
import json
from pathlib import Path

import numpy as np

from src.search import SemanticSearcher


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INDEX_PATH = BASE_DIR / "data" / "faiss_index.bin"
DEFAULT_METADATA_PATH = BASE_DIR / "data" / "faiss_metadata.json"
DEFAULT_EVAL_PATH = BASE_DIR / "data" / "retrieval_eval_questions.json"
DEFAULT_OUTPUT_PATH = BASE_DIR / "data" / "retrieval_eval_results.json"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate FAISS retrieval with Recall@1, Recall@5, and MRR."
    )
    parser.add_argument(
        "--eval-file",
        default=str(DEFAULT_EVAL_PATH),
        help="Path to a JSON file containing evaluation questions and gold technique IDs.",
    )
    parser.add_argument(
        "--index-path",
        default=str(DEFAULT_INDEX_PATH),
        help="Path to the FAISS index file.",
    )
    parser.add_argument(
        "--metadata-path",
        default=str(DEFAULT_METADATA_PATH),
        help="Path to the FAISS metadata JSON file.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of documents to retrieve per question. Must be at least 5.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Path to write the detailed evaluation results JSON.",
    )
    args = parser.parse_args()

    if args.top_k < 5:
        parser.error("--top-k must be at least 5 to compute Recall@5.")

    return args


def load_eval_examples(path: str):
    with open(path, "r") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Evaluation file must contain a JSON list.")

    examples = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Entry {index} must be a JSON object.")

        question = item.get("question")
        gold_ids = item.get("gold_technique_ids")

        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"Entry {index} is missing a valid 'question'.")

        if not isinstance(gold_ids, list) or not gold_ids:
            raise ValueError(f"Entry {index} is missing a non-empty 'gold_technique_ids' list.")

        if not all(isinstance(gold_id, str) and gold_id.strip() for gold_id in gold_ids):
            raise ValueError(f"Entry {index} contains an invalid gold technique ID.")

        examples.append(
            {
                "question_id": item.get("question_id", f"q{index:02d}"),
                "question": question.strip(),
                "gold_technique_ids": gold_ids,
            }
        )

    return examples


def retrieve_ranked_results(searcher: SemanticSearcher, question: str, top_k: int):
    query_vector = searcher.embed_query(question)
    query_vector = np.expand_dims(query_vector, axis=0)

    distances, indices = searcher.index.search(query_vector, top_k)

    ranked_results = []
    for rank, idx in enumerate(indices[0], start=1):
        if idx < 0 or idx >= len(searcher.metadata):
            continue

        metadata = searcher.metadata[idx]
        ranked_results.append(
            {
                "rank": rank,
                "technique_id": metadata["id"],
                "name": metadata["metadata"]["name"],
                "distance": float(distances[0][rank - 1]),
            }
        )

    return ranked_results


def first_relevant_rank(ranked_results, gold_technique_ids):
    gold_set = set(gold_technique_ids)

    for result in ranked_results:
        if result["technique_id"] in gold_set:
            return result["rank"]

    return None


def evaluate(searcher: SemanticSearcher, examples, top_k: int):
    detailed_results = []
    recall_at_1_total = 0.0
    recall_at_5_total = 0.0
    reciprocal_rank_total = 0.0

    for example in examples:
        ranked_results = retrieve_ranked_results(searcher, example["question"], top_k)
        relevant_rank = first_relevant_rank(ranked_results, example["gold_technique_ids"])

        recall_at_1 = 1.0 if relevant_rank == 1 else 0.0
        recall_at_5 = 1.0 if relevant_rank is not None and relevant_rank <= 5 else 0.0
        reciprocal_rank = 0.0 if relevant_rank is None else 1.0 / relevant_rank

        recall_at_1_total += recall_at_1
        recall_at_5_total += recall_at_5
        reciprocal_rank_total += reciprocal_rank

        detailed_results.append(
            {
                "question_id": example["question_id"],
                "question": example["question"],
                "gold_technique_ids": example["gold_technique_ids"],
                "first_relevant_rank": relevant_rank,
                "recall_at_1": recall_at_1,
                "recall_at_5": recall_at_5,
                "reciprocal_rank": reciprocal_rank,
                "retrieved_top_k": ranked_results,
            }
        )

    total_questions = len(examples)
    summary = {
        "num_questions": total_questions,
        "top_k": top_k,
        "recall_at_1": recall_at_1_total / total_questions,
        "recall_at_5": recall_at_5_total / total_questions,
        "mrr": reciprocal_rank_total / total_questions,
    }

    return summary, detailed_results


def main():
    args = parse_args()

    examples = load_eval_examples(args.eval_file)
    searcher = SemanticSearcher(args.index_path, args.metadata_path)

    summary, detailed_results = evaluate(searcher, examples, args.top_k)

    output_payload = {
        "summary": summary,
        "questions": detailed_results,
    }

    with open(args.output, "w") as f:
        json.dump(output_payload, f, indent=2)

    print(f"Evaluated {summary['num_questions']} questions")
    print(f"Recall@1: {summary['recall_at_1']:.4f}")
    print(f"Recall@5: {summary['recall_at_5']:.4f}")
    print(f"MRR: {summary['mrr']:.4f}")
    print(f"Detailed results written to: {args.output}")


if __name__ == "__main__":
    main()
