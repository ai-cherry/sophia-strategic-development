def test_no_deprecated_imports():
    import pkgutil

    banned = "backend._deprecated"
    for module in pkgutil.walk_packages():
        assert banned not in module.name, f"Deprecated import detected: {module.name}"
