import os

from coolfig.providers import (
    DictConfig,
    EnvConfig,
    EnvDirConfig,
    FallbackProvider,
    NOT_PROVIDED,
)


def test_dictconfig():
    conf = DictConfig(
        {"TEST": "value", "PREFIX_ONE": "foo", "PREFIX_TWO": "bar"}
    )
    assert conf.get("FOO") is NOT_PROVIDED
    assert dict(conf.iterprefixed("NOPREFIX_")) == {}
    assert conf.get("TEST") == "value"
    assert dict(conf.iterprefixed("PREFIX_")) == {
        "PREFIX_ONE": "foo",
        "PREFIX_TWO": "bar",
    }


def test_envconfig():
    conf = EnvConfig()
    assert isinstance(conf, DictConfig)
    assert conf._conf_dict is os.environ


def test_envdirconfig(tmpdir):
    tmpdir.join("TEST").write("value")
    tmpdir.join("PREFIX_ONE").write("foo")
    tmpdir.join("PREFIX_TWO").write("bar")

    conf = EnvDirConfig(str(tmpdir))
    assert conf.get("FOO") is NOT_PROVIDED
    assert dict(conf.iterprefixed("NOPREFIX_")) == {}
    assert conf.get("TEST") == "value"
    assert dict(conf.iterprefixed("PREFIX_")) == {
        "PREFIX_ONE": "foo",
        "PREFIX_TWO": "bar",
    }


def test_envdirconfig_nodir():
    conf = EnvDirConfig("/non-existing-coolfig-directory")
    assert conf.get("FOO") is NOT_PROVIDED
    assert dict(conf.iterprefixed("PREFIX_")) == {}


def test_fallbackprovider():
    conf = FallbackProvider(
        [
            DictConfig(
                {"TEST1": "value", "PREFIX_ONE": "foo", "PREFIX_TWO": "bar"}
            ),
            DictConfig(
                {
                    "TEST1": "wrongvalue",
                    "TEST2": "rightvalue",
                    "PREFIX_ONE": "wrongfoo",
                    "PREFIX_THREE": "rightbar",
                }
            ),
        ]
    )

    assert conf.get("FOO") is NOT_PROVIDED
    assert dict(conf.iterprefixed("NOPREFIX_")) == {}
    assert conf.get('TEST1') == 'value'
    assert conf.get('TEST2') == 'rightvalue'
    assert dict(conf.iterprefixed("PREFIX_")) == {
        'PREFIX_ONE': 'foo',
        'PREFIX_TWO': 'bar',
        'PREFIX_THREE': 'rightbar',
    }
