 

# pylint: disable=unused-argument

import json

from platformio.commands import platform as cli_platform
from platformio.package.exception import UnknownPackageError


def test_search_json_output(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cli_platform.platform_search, ["arduino", "--json-output"]
    )
    validate_cliresult(result)
    search_result = json.loads(result.output)
    assert isinstance(search_result, list)
    assert search_result
    platforms = [item["name"] for item in search_result]
    assert "atmelsam" in platforms


def test_search_raw_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cli_platform.platform_search, ["arduino"])
    validate_cliresult(result)
    assert "teensy" in result.output


def test_install_unknown_version(clirunner):
    result = clirunner.invoke(cli_platform.platform_install, ["atmelavr@99.99.99"])
    assert result.exit_code != 0
    assert isinstance(result.exception, UnknownPackageError)


def test_install_unknown_from_registry(clirunner):
    result = clirunner.invoke(cli_platform.platform_install, ["unknown-platform"])
    assert result.exit_code != 0
    assert isinstance(result.exception, UnknownPackageError)


# def test_install_incompatbile(clirunner, validate_cliresult, isolated_pio_core):
#     result = clirunner.invoke(
#         cli_platform.platform_install, ["atmelavr@1.2.0", "--skip-default-package"],
#     )
#     assert result.exit_code != 0
#     assert isinstance(result.exception, IncompatiblePlatform)


def test_install_core_3_dev_platform(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cli_platform.platform_install,
        ["atmelavr@1.2.0", "--skip-default-package"],
    )
    assert result.exit_code == 0


def test_install_known_version(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cli_platform.platform_install,
        ["atmelavr@2.0.0", "--skip-default-package", "--with-package", "tool-avrdude"],
    )
    validate_cliresult(result)
    assert "atmelavr @ 2.0.0" in result.output
    assert "Installing tool-avrdude @" in result.output
    assert len(isolated_pio_core.join("packages").listdir()) == 1


def test_install_from_vcs(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cli_platform.platform_install,
        [
            "https://github.com/platformio/platform-espressif8266.git",
            "--skip-default-package",
        ],
    )
    validate_cliresult(result)
    assert "espressif8266" in result.output
    assert len(isolated_pio_core.join("packages").listdir()) == 1


def test_list_json_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cli_platform.platform_list, ["--json-output"])
    validate_cliresult(result)
    list_result = json.loads(result.output)
    assert isinstance(list_result, list)
    assert list_result
    platforms = [item["name"] for item in list_result]
    assert set(["atmelavr", "espressif8266"]) == set(platforms)


def test_list_raw_output(clirunner, validate_cliresult):
    result = clirunner.invoke(cli_platform.platform_list)
    validate_cliresult(result)
    assert all(s in result.output for s in ("atmelavr", "espressif8266"))


def test_update_check(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cli_platform.platform_update, ["--dry-run", "--json-output"]
    )
    validate_cliresult(result)
    output = json.loads(result.output)
    assert len(output) == 1
    assert output[0]["name"] == "atmelavr"
    assert len(isolated_pio_core.join("packages").listdir()) == 1


def test_update_raw(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(cli_platform.platform_update)
    validate_cliresult(result)
    assert "Removing atmelavr @ 2.0.0" in result.output
    assert "Platform Manager: Installing platformio/atmelavr @" in result.output
    assert len(isolated_pio_core.join("packages").listdir()) == 2


def test_uninstall(clirunner, validate_cliresult, isolated_pio_core):
    result = clirunner.invoke(
        cli_platform.platform_uninstall, ["atmelavr@1.2.0", "atmelavr", "espressif8266"]
    )
    validate_cliresult(result)
    assert not isolated_pio_core.join("platforms").listdir()
