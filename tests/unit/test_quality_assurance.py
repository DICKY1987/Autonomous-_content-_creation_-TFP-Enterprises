import importlib


def test_flags_offensive_terms():
    m = importlib.import_module("src.core.automated_content_system")
    QualityAssuranceModule = getattr(m, "QualityAssuranceModule")

    qa = QualityAssuranceModule()
    report = qa.verify_content({"image_meta": []}, "This text mentions slave labor")

    assert not report.technical_compliance
    assert any("Offensive terms" in issue for issue in report.issues)


def test_flags_unlicensed_images():
    m = importlib.import_module("src.core.automated_content_system")
    QualityAssuranceModule = getattr(m, "QualityAssuranceModule")

    qa = QualityAssuranceModule()
    content = {"image_meta": [{"url": "https://img/0", "licensed": False}]}
    report = qa.verify_content(content, "clean text")

    assert report.copyright_status == "uncertain"
    assert any("Unlicensed images" in issue for issue in report.issues)
