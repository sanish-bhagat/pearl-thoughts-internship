import inspect

def build_call_graph(calls):
    """
    Builds a call graph from the collected calls.
    Args:
        calls (dict): {caller: [callees]}
    Returns:
        dict: Same as input, cleaned up (remove duplicates, self-calls if any)
    """
    graph = {}
    for caller, callees in calls.items():
        # Remove duplicates and self-calls
        unique_callees = list(set(callees))
        if caller in unique_callees:
            unique_callees.remove(caller)
        graph[caller] = unique_callees
    return graph

def calculate_risks(graph):
    """
    Calculates risk for each function based on incoming dependencies (number of functions that call it).
    Higher number means higher risk, as changing it affects more callers.
    Args:
        graph (dict): {func: [callees]}
    Returns:
        dict: {func: risk_score}
    """
    # Build reverse graph: {callee: [callers]}
    reverse = {}
    for caller, callees in graph.items():
        for callee in callees:
            if callee not in reverse:
                reverse[callee] = []
    
            reverse[callee].append(caller)
    
    # Risk is number of callers
    risks = {}
    for func in graph.keys():
        risks[func] = len(reverse.get(func, []))
    return risks

def generate_report(counts, graph, risks):
    """
    Generates a plain text summary report.
    Args:
        counts (dict): {'functions': list of dicts, 'classes': [...]}
        graph (dict): {caller: [callees]}
        risks (dict): {func: risk}
    Returns:
        str: The report text.
    """
    report = []
    report.append("Code Analysis Summary")
    report.append("=" * 30)

    fn_cnt = len(counts['functions'])
    report.append(f"Total Functions: {fn_cnt}")
    for func_dict in counts['functions']:
        report.append(f"  - {func_dict['name']}")

    report.append("")

    cl_cnt = len(counts['classes'])
    report.append(f"Total Classes: {cl_cnt}")
    for cls in counts['classes']:
        report.append(f"  - {cls}")

    report.append("")

    report.append("Call Relationships (Who calls what):")
    for caller, callees in graph.items():
        if callees:
            report.append(f"  {caller} calls: {', '.join(callees)}")
        else:

            report.append(f"  {caller} calls nothing")

    report.append("")

    report.append("Risk Assessment (based on incoming dependencies):")
    # Sort by risk descending
    sorted_risks = sorted(risks.items(), key=lambda x: x[1], reverse=True)
    for func, risk in sorted_risks:
        report.append(f"  {func}: Risk {risk} (called by {risk} functions)")

    report.append("")
    # Most risky function details
    if sorted_risks:
        most_risky = sorted_risks[0][0]
        # Find doc
        doc = ""
        for func_dict in counts['functions']:
            if func_dict['name'] == most_risky:
                doc = func_dict['doc']
                break
        report.append(f"Most Risky Function: {most_risky}")
        report.append(f"Description: {doc}")
        # Build reverse graph
        reverse = {}
        for caller, callees in graph.items():
            for callee in callees:
                if callee not in reverse:
                    reverse[callee] = []
                reverse[callee].append(caller)
        callers = reverse.get(most_risky, [])
        if callers:
            report.append(f"Callers at risk if changed: {', '.join(callers)}")
            # Add descriptions
            for caller in callers:
                doc = ""
                for func_dict in counts['functions']:
                    if func_dict['name'] == caller:
                        doc = func_dict['doc']
                        break
                
                report.append("")
                report.append(f"*{caller} description: {doc}")
    
        else:
            report.append("Callers at risk if changed: None")

    return "\n".join(report)
