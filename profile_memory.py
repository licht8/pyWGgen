from memory_profiler import memory_usage
import importlib
import inspect

def profile_function(func, *args, **kwargs):
    """Profiles a function and returns memory usage."""
    def wrapper():
        return func(*args, **kwargs)
    
    # Measure memory usage
    mem_usage = memory_usage(wrapper, interval=0.1, timeout=1)
    return max(mem_usage) - min(mem_usage)

def analyze_module(module_name):
    """Analyzes functions in the specified module."""
    module = importlib.import_module(module_name)
    
    results = []
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if obj.__module__ == module_name:  # Ensure the function belongs to the target module
            try:
                # Profile the function if it has no arguments
                if not inspect.signature(obj).parameters:
                    mem_diff = profile_function(obj)
                    results.append((name, mem_diff))
                else:
                    results.append((name, "⚠️ Requires parameters"))
            except Exception as e:
                results.append((name, f"Error: {e}"))

    # Sort results by memory usage (if numeric) in descending order
    results.sort(key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True)
    return results

def main():
    module_name = input("Enter the module name to analyze: ")
    results = analyze_module(module_name)
    
    print(f"\n{'Function':<30}{'Memory Usage (MB)':<20}")
    print("=" * 50)
    for func, mem in results:
        print(f"{func:<30}{mem:<20}")

if __name__ == "__main__":
    main()
