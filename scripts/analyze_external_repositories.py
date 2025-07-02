import os
import json
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_repo_summary(repo_path: Path) -> str:
    """
    Creates a summary from the first few lines of a README.md file.
    """
    readme_path = repo_path / "README.md"
    if not readme_path.exists():
        return "No README.md found."
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            # Join the first 5 non-empty lines for a concise summary
            summary = " ".join(lines[:5])
            return summary
    except Exception as e:
        logging.warning(f"Could not read README for {repo_path.name}: {e}")
        return "Could not read README."

def calculate_relevance(repo_content: str, query_keywords: list[str]) -> int:
    """
    Calculates a simple relevance score based on keyword matching.
    """
    score = 0
    repo_content_lower = repo_content.lower()
    for keyword in query_keywords:
        # Higher score for keyword appearing in the content
        score += repo_content_lower.count(keyword.lower())
    return score

def analyze_repositories(query: str) -> list[dict]:
    """
    Analyzes external repositories to find patterns relevant to a query.
    """
    base_path = Path(__file__).parent.parent / "external"
    if not base_path.exists():
        logging.error(f"External repositories directory not found at: {base_path}")
        return []

    query_keywords = query.lower().split()
    recommendations = []

    logging.info(f"Analyzing repositories in {base_path} for query: '{query}'")

    for repo_dir in base_path.iterdir():
        if repo_dir.is_dir() and not repo_dir.name.startswith('.'):
            summary = get_repo_summary(repo_dir)
            
            # Combine repo name and summary for relevance check
            searchable_content = f"{repo_dir.name.replace('_', ' ')} {summary}"
            
            relevance_score = calculate_relevance(searchable_content, query_keywords)
            
            # Only include repos that have some relevance
            if relevance_score > 0:
                recommendations.append({
                    "repository": repo_dir.name,
                    "path": str(repo_dir.relative_to(base_path.parent)),
                    "summary": summary,
                    "relevance_score": relevance_score,
                    "recommendation": f"Consider using '{repo_dir.name}' for tasks related to '{query}'."
                })

    # Sort recommendations by relevance score, descending
    recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    logging.info(f"Found {len(recommendations)} relevant repositories.")
    return recommendations

def main():
    """
    Main function to run the analysis from the command line.
    """
    parser = argparse.ArgumentParser(description="Analyze external repositories for relevant patterns.")
    parser.add_argument("query", type=str, help="The natural language query describing the desired pattern (e.g., 'browser automation test').")
    args = parser.parse_args()
    
    results = analyze_repositories(args.query)
    
    # Print results as a JSON object to be captured by N8N or other scripts
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
