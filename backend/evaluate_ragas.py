import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
from ragas.embeddings import OpenAIEmbeddings
from ragas.llms import llm_factory
from ragas.metrics.collections import (
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
    Faithfulness,
)

from src.rag_pipeline import RAGPipeline


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_INDEX_PATH = BASE_DIR / "data" / "faiss_index.bin"
DEFAULT_METADATA_PATH = BASE_DIR / "data" / "faiss_metadata.json"
DEFAULT_EVAL_PATH = BASE_DIR / "data" / "retrieval_eval_questions.json"
DEFAULT_OUTPUT_PATH = BASE_DIR / "data" / "ragas_eval_results.json"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate Cyber-RAG answers with RAGAS metrics."
    )
    parser.add_argument(
        "--eval-file",
        default=str(DEFAULT_EVAL_PATH),
        help="Path to the JSON evaluation file.",
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
        help="Number of documents to retrieve for each question.",
    )
    parser.add_argument(
        "--generator-model",
        default="gpt-4o-mini",
        help="Generator model name used by the pipeline.",
    )
    parser.add_argument(
        "--evaluator-model",
        default="gpt-4o-mini",
        help="RAGAS evaluator model name.",
    )
    parser.add_argument(
        "--embedding-model",
        default="text-embedding-3-small",
        help="Embedding model used for answer relevancy scoring.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Path to write the detailed evaluation results JSON.",
    )
    return parser.parse_args()


def load_eval_examples(path: str):
    with open(path, "r") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Evaluation file must contain a JSON list.")

    examples = []
    for index, item in enumerate(data, start=1):
        question = item.get("question")
        gold_ids = item.get("gold_technique_ids")
        reference_answer = item.get("reference_answer")

        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"Entry {index} is missing a valid 'question'.")
        if not isinstance(gold_ids, list) or not gold_ids:
            raise ValueError(f"Entry {index} is missing a non-empty 'gold_technique_ids' list.")
        if not isinstance(reference_answer, str) or not reference_answer.strip():
            raise ValueError(f"Entry {index} is missing a valid 'reference_answer'.")

        examples.append(
            {
                "question_id": item.get("question_id", f"q{index:02d}"),
                "question": question.strip(),
                "gold_technique_ids": gold_ids,
                "reference_answer": reference_answer.strip(),
            }
        )

    return examples


def metric_value(result):
    value = getattr(result, "value", result)
    return float(value)


def summarize_scores(results):
    metric_names = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
    summary = {}

    for metric_name in metric_names:
        summary[metric_name] = sum(result[metric_name] for result in results) / len(results)

    return summary


def build_metrics(api_key: str, evaluator_model: str, embedding_model: str):
    async_client = AsyncOpenAI(api_key=api_key)
    evaluator_llm = llm_factory(evaluator_model, client=async_client, temperature=0)
    evaluator_embeddings = OpenAIEmbeddings(client=async_client, model=embedding_model)

    return {
        "faithfulness": Faithfulness(llm=evaluator_llm),
        "answer_relevancy": AnswerRelevancy(
            llm=evaluator_llm,
            embeddings=evaluator_embeddings,
        ),
        "context_precision": ContextPrecision(llm=evaluator_llm),
        "context_recall": ContextRecall(llm=evaluator_llm),
    }


def evaluate_examples(pipeline: RAGPipeline, examples, metrics, top_k: int):
    detailed_results = []

    for example in examples:
        print(
            f"[{example['question_id']}] Generating answer and retrieving context...",
            flush=True,
        )
        run = pipeline.generate_answer_with_context(example["question"], top_k=top_k)
        retrieved_docs = run["retrieved_docs"]
        retrieved_contexts = [
            document["content"]
            for document in retrieved_docs
            if isinstance(document.get("content"), str) and document["content"].strip()
        ]

        if not retrieved_contexts:
            raise ValueError(
                f"No retrieved document content found for question {example['question_id']}."
            )

        answer = run["answer"]
        reference_answer = example["reference_answer"]

        print(f"[{example['question_id']}] Scoring faithfulness...", flush=True)
        faithfulness = metric_value(
            metrics["faithfulness"].score(
                user_input=example["question"],
                response=answer,
                retrieved_contexts=retrieved_contexts,
            )
        )
        print(f"[{example['question_id']}] Scoring answer relevancy...", flush=True)
        answer_relevancy = metric_value(
            metrics["answer_relevancy"].score(
                user_input=example["question"],
                response=answer,
            )
        )
        print(f"[{example['question_id']}] Scoring context precision...", flush=True)
        context_precision = metric_value(
            metrics["context_precision"].score(
                user_input=example["question"],
                reference=reference_answer,
                retrieved_contexts=retrieved_contexts,
            )
        )
        print(f"[{example['question_id']}] Scoring context recall...", flush=True)
        context_recall = metric_value(
            metrics["context_recall"].score(
                user_input=example["question"],
                reference=reference_answer,
                retrieved_contexts=retrieved_contexts,
            )
        )

        detailed_results.append(
            {
                "question_id": example["question_id"],
                "question": example["question"],
                "gold_technique_ids": example["gold_technique_ids"],
                "reference_answer": reference_answer,
                "generated_answer": answer,
                "retrieved_docs": [
                    {
                        "technique_id": document["id"],
                        "name": document["metadata"]["name"],
                    }
                    for document in retrieved_docs
                ],
                "faithfulness": faithfulness,
                "answer_relevancy": answer_relevancy,
                "context_precision": context_precision,
                "context_recall": context_recall,
            }
        )

        print(
            (
                f"[{example['question_id']}] Done "
                f"(faithfulness={faithfulness:.4f}, "
                f"answer_relevancy={answer_relevancy:.4f}, "
                f"context_precision={context_precision:.4f}, "
                f"context_recall={context_recall:.4f})"
            ),
            flush=True,
        )

    return detailed_results


def main():
    args = parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in backend/.env.")

    client = OpenAI(api_key=api_key)
    metrics = build_metrics(api_key, args.evaluator_model, args.embedding_model)
    pipeline = RAGPipeline(
        args.index_path,
        args.metadata_path,
        generation_model=args.generator_model,
    )
    examples = load_eval_examples(args.eval_file)

    results = evaluate_examples(pipeline, examples, metrics, args.top_k)
    summary = summarize_scores(results)

    output_payload = {
        "summary": {
            "num_questions": len(results),
            "top_k": args.top_k,
            "generator_model": args.generator_model,
            "evaluator_model": args.evaluator_model,
            "embedding_model": args.embedding_model,
            **summary,
        },
        "questions": results,
    }

    with open(args.output, "w") as f:
        json.dump(output_payload, f, indent=2)

    print(f"Evaluated {len(results)} questions")
    print(f"Faithfulness: {summary['faithfulness']:.4f}")
    print(f"Answer relevancy: {summary['answer_relevancy']:.4f}")
    print(f"Context precision: {summary['context_precision']:.4f}")
    print(f"Context recall: {summary['context_recall']:.4f}")
    print(f"Detailed results written to: {args.output}")


if __name__ == "__main__":
    main()
