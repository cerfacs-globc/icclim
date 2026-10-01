from icclim._core.model.index_config import (
    CompletenessPolicy,
    resolve_legacy_completeness_policy,
)


def test_strict_policy_has_stable_provenance() -> None:
    policy = resolve_legacy_completeness_policy(
        allow_missing_periods=False,
        missing_method="any",
        missing_options=None,
    )

    assert policy.name == "strict"
    assert policy.method == "any"
    assert policy.options == {}
    assert policy.metadata() == {
        "completeness_policy": "strict",
        "completeness_method": "xclim:any",
        "completeness_options": "{}",
    }


def test_none_policy_disables_masking() -> None:
    policy = resolve_legacy_completeness_policy(
        allow_missing_periods=True,
        missing_method="any",
        missing_options=None,
    )

    assert not policy.is_applied
    assert policy.metadata()["completeness_policy"] == "none"
    assert policy.metadata()["completeness_method"] == "not_applied"


def test_named_method_and_options_are_preserved_for_future_profiles() -> None:
    options = {"n": 350}

    policy = resolve_legacy_completeness_policy(
        allow_missing_periods=False,
        missing_method="at_least_n",
        missing_options=options,
    )
    options["n"] = 1

    assert policy.name == "at_least_n"
    assert policy.method == "at_least_n"
    assert policy.options == {"n": 350}
    assert policy.metadata()["completeness_options"] == '{"n": 350}'


def test_policy_reference_and_version_are_available_for_fair_provenance() -> None:
    policy = CompletenessPolicy(
        name="ecad",
        method="at_least_n",
        options={"n": 350},
        reference="ECA&D ATBD section 5.1",
        version="2023",
    )

    assert policy.metadata()["completeness_reference"] == "ECA&D ATBD section 5.1"
    assert policy.metadata()["completeness_policy_version"] == "2023"
