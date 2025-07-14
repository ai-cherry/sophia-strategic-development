#!/usr/bin/env python3
"""Qdrant vector database"""
    tester = QdrantTester()
    report = await tester.run_all_tests()
    
    # Save report
    with open("qdrant_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to: qdrant_test_report.json")
    
    # Print detailed results
    print("\n📊 DETAILED RESULTS:")
    for component, result in report["test_results"].items():
        if component != "overall":
            status_emoji = "✅" if result["status"] == "success" else "❌"
            print(f"   {status_emoji} {component.upper()}: {result['details']}")
    
    print(f"\n🏆 OVERALL STATUS: {report['summary']['status'].upper()} ({report['summary']['score']}/100)")
    
    if report['summary']['score'] >= 90:
        print("🎉 EXCELLENT: Modern stack is ready for production!")
    elif report['summary']['score'] >= 70:
        print("👍 GOOD: Modern stack is functional with minor issues")
    elif report['summary']['score'] >= 50:
        print("⚠️  FAIR: Modern stack needs attention")
    else:
        print("🚨 POOR: Modern stack requires immediate fixes")

if __name__ == "__main__":
    asyncio.run(main()) 