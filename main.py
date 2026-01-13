from parser import parse_file, collect_functions_and_classes, collect_function_calls
from analyzer import build_call_graph, calculate_risks, generate_report

def main():
    """
    Main function to run the code analyzer.
    """
    # Default file to analyze
    file_path = "sample.py"

    try:
        # Parse the file
        tree = parse_file(file_path)

        # Collect functions, classes, and calls
        counts = collect_functions_and_classes(tree)
        calls = collect_function_calls(tree)

        # Build graph and calculate risks
        graph = build_call_graph(calls)
        risks = calculate_risks(graph)

        # Generate and print report
        report = generate_report(counts, graph, risks)
        print(report)

    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")

if __name__ == "__main__":
    main()
