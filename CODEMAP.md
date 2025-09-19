# Project Structure

```
├── .pytest_cache/
│   ├── CACHEDIR.TAG
│   ├── README.md
│   ├── v/
│   │   ├── cache/
│   │   │   ├── lastfailed
│   │   │   ├── nodeids
├── CODEMAP.md
├── MASTER_FILE.md
├── README.md
├── TASKS.md
├── ai_modules/
│   ├── __init__.py
│   ├── credibility.py
│   ├── importance.py
├── config.py
├── database/
│   ├── __init__.py
│   ├── db_models.py
│   ├── init_tables.sql
│   ├── seed_data.sql
├── main.py
├── parsers/
│   ├── __init__.py
│   ├── rss_parser.py
├── requirements.txt
├── tests/
│   ├── __init__.py
│   ├── test_ai_modules.py
│   ├── test_db_content.py
│   ├── test_db_insert.py
│   ├── test_deepl.py
│   ├── test_main.py
│   ├── test_openai.py
│   ├── test_supabase.py
├── tools/
│   ├── fix_old_news.py
│   ├── repo_map.py
│   ├── show_news.py
├── venv/
│   ├── bin/
│   │   ├── Activate.ps1
│   │   ├── activate
│   │   ├── activate.csh
│   │   ├── activate.fish
│   │   ├── deepl
│   │   ├── distro
│   │   ├── dotenv
│   │   ├── flask
│   │   ├── httpx
│   │   ├── normalizer
│   │   ├── openai
│   │   ├── pip
│   │   ├── pip3
│   │   ├── pip3.11
│   │   ├── py.test
│   │   ├── pygmentize
│   │   ├── pytest
│   │   ├── python
│   │   ├── python3
│   │   ├── python3.11
│   │   ├── tqdm
│   │   ├── websockets
│   ├── include/
│   │   ├── python3.11/
│   ├── lib/
│   │   ├── python3.11/
│   │   │   ├── site-packages/
│   │   │   │   ├── MarkupSafe-3.0.2.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE.txt
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── PyJWT-2.10.1.dist-info/
│   │   │   │   │   ├── AUTHORS.rst
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── StrEnum-0.4.15.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── _cffi_backend.cpython-311-darwin.so
│   │   │   │   ├── _distutils_hack/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── override.py
│   │   │   │   ├── _pytest/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _argcomplete.py
│   │   │   │   │   ├── _code/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── code.py
│   │   │   │   │   │   ├── source.py
│   │   │   │   │   ├── _io/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── pprint.py
│   │   │   │   │   │   ├── saferepr.py
│   │   │   │   │   │   ├── terminalwriter.py
│   │   │   │   │   │   ├── wcwidth.py
│   │   │   │   │   ├── _py/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── error.py
│   │   │   │   │   │   ├── path.py
│   │   │   │   │   ├── _version.py
│   │   │   │   │   ├── assertion/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── rewrite.py
│   │   │   │   │   │   ├── truncate.py
│   │   │   │   │   │   ├── util.py
│   │   │   │   │   ├── cacheprovider.py
│   │   │   │   │   ├── capture.py
│   │   │   │   │   ├── compat.py
│   │   │   │   │   ├── config/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── argparsing.py
│   │   │   │   │   │   ├── compat.py
│   │   │   │   │   │   ├── exceptions.py
│   │   │   │   │   │   ├── findpaths.py
│   │   │   │   │   ├── debugging.py
│   │   │   │   │   ├── deprecated.py
│   │   │   │   │   ├── doctest.py
│   │   │   │   │   ├── faulthandler.py
│   │   │   │   │   ├── fixtures.py
│   │   │   │   │   ├── freeze_support.py
│   │   │   │   │   ├── helpconfig.py
│   │   │   │   │   ├── hookspec.py
│   │   │   │   │   ├── junitxml.py
│   │   │   │   │   ├── legacypath.py
│   │   │   │   │   ├── logging.py
│   │   │   │   │   ├── main.py
│   │   │   │   │   ├── mark/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── expression.py
│   │   │   │   │   │   ├── structures.py
│   │   │   │   │   ├── monkeypatch.py
│   │   │   │   │   ├── nodes.py
│   │   │   │   │   ├── outcomes.py
│   │   │   │   │   ├── pastebin.py
│   │   │   │   │   ├── pathlib.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── pytester.py
│   │   │   │   │   ├── pytester_assertions.py
│   │   │   │   │   ├── python.py
│   │   │   │   │   ├── python_api.py
│   │   │   │   │   ├── raises.py
│   │   │   │   │   ├── recwarn.py
│   │   │   │   │   ├── reports.py
│   │   │   │   │   ├── runner.py
│   │   │   │   │   ├── scope.py
│   │   │   │   │   ├── setuponly.py
│   │   │   │   │   ├── setupplan.py
│   │   │   │   │   ├── skipping.py
│   │   │   │   │   ├── stash.py
│   │   │   │   │   ├── stepwise.py
│   │   │   │   │   ├── terminal.py
│   │   │   │   │   ├── threadexception.py
│   │   │   │   │   ├── timing.py
│   │   │   │   │   ├── tmpdir.py
│   │   │   │   │   ├── tracemalloc.py
│   │   │   │   │   ├── unittest.py
│   │   │   │   │   ├── unraisableexception.py
│   │   │   │   │   ├── warning_types.py
│   │   │   │   │   ├── warnings.py
│   │   │   │   ├── annotated_types/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── test_cases.py
│   │   │   │   ├── annotated_types-0.7.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   ├── anyio/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _backends/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _asyncio.py
│   │   │   │   │   │   ├── _trio.py
│   │   │   │   │   ├── _core/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _asyncio_selector_thread.py
│   │   │   │   │   │   ├── _contextmanagers.py
│   │   │   │   │   │   ├── _eventloop.py
│   │   │   │   │   │   ├── _exceptions.py
│   │   │   │   │   │   ├── _fileio.py
│   │   │   │   │   │   ├── _resources.py
│   │   │   │   │   │   ├── _signals.py
│   │   │   │   │   │   ├── _sockets.py
│   │   │   │   │   │   ├── _streams.py
│   │   │   │   │   │   ├── _subprocesses.py
│   │   │   │   │   │   ├── _synchronization.py
│   │   │   │   │   │   ├── _tasks.py
│   │   │   │   │   │   ├── _tempfile.py
│   │   │   │   │   │   ├── _testing.py
│   │   │   │   │   │   ├── _typedattr.py
│   │   │   │   │   ├── abc/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _eventloop.py
│   │   │   │   │   │   ├── _resources.py
│   │   │   │   │   │   ├── _sockets.py
│   │   │   │   │   │   ├── _streams.py
│   │   │   │   │   │   ├── _subprocesses.py
│   │   │   │   │   │   ├── _tasks.py
│   │   │   │   │   │   ├── _testing.py
│   │   │   │   │   ├── from_thread.py
│   │   │   │   │   ├── lowlevel.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── pytest_plugin.py
│   │   │   │   │   ├── streams/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── buffered.py
│   │   │   │   │   │   ├── file.py
│   │   │   │   │   │   ├── memory.py
│   │   │   │   │   │   ├── stapled.py
│   │   │   │   │   │   ├── text.py
│   │   │   │   │   │   ├── tls.py
│   │   │   │   │   ├── to_interpreter.py
│   │   │   │   │   ├── to_process.py
│   │   │   │   │   ├── to_thread.py
│   │   │   │   ├── anyio-4.10.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── beautifulsoup4-4.13.5.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── REQUESTED
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── AUTHORS
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   ├── blinker/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _utilities.py
│   │   │   │   │   ├── base.py
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── blinker-1.9.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE.txt
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   ├── bs4/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _deprecation.py
│   │   │   │   │   ├── _typing.py
│   │   │   │   │   ├── _warnings.py
│   │   │   │   │   ├── builder/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _html5lib.py
│   │   │   │   │   │   ├── _htmlparser.py
│   │   │   │   │   │   ├── _lxml.py
│   │   │   │   │   ├── css.py
│   │   │   │   │   ├── dammit.py
│   │   │   │   │   ├── diagnose.py
│   │   │   │   │   ├── element.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── filter.py
│   │   │   │   │   ├── formatter.py
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── certifi/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __main__.py
│   │   │   │   │   ├── cacert.pem
│   │   │   │   │   ├── core.py
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── certifi-2025.8.3.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── cffi/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _cffi_errors.h
│   │   │   │   │   ├── _cffi_include.h
│   │   │   │   │   ├── _embedding.h
│   │   │   │   │   ├── _imp_emulation.py
│   │   │   │   │   ├── _shimmed_dist_utils.py
│   │   │   │   │   ├── api.py
│   │   │   │   │   ├── backend_ctypes.py
│   │   │   │   │   ├── cffi_opcode.py
│   │   │   │   │   ├── commontypes.py
│   │   │   │   │   ├── cparser.py
│   │   │   │   │   ├── error.py
│   │   │   │   │   ├── ffiplatform.py
│   │   │   │   │   ├── lock.py
│   │   │   │   │   ├── model.py
│   │   │   │   │   ├── parse_c_type.h
│   │   │   │   │   ├── pkgconfig.py
│   │   │   │   │   ├── recompiler.py
│   │   │   │   │   ├── setuptools_ext.py
│   │   │   │   │   ├── vengine_cpy.py
│   │   │   │   │   ├── vengine_gen.py
│   │   │   │   │   ├── verifier.py
│   │   │   │   ├── cffi-2.0.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── AUTHORS
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── charset_normalizer/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __main__.py
│   │   │   │   │   ├── api.py
│   │   │   │   │   ├── cd.py
│   │   │   │   │   ├── cli/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── __main__.py
│   │   │   │   │   ├── constant.py
│   │   │   │   │   ├── legacy.py
│   │   │   │   │   ├── md.cpython-311-darwin.so
│   │   │   │   │   ├── md.py
│   │   │   │   │   ├── md__mypyc.cpython-311-darwin.so
│   │   │   │   │   ├── models.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── version.py
│   │   │   │   ├── charset_normalizer-3.4.3.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── click/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _compat.py
│   │   │   │   │   ├── _termui_impl.py
│   │   │   │   │   ├── _textwrap.py
│   │   │   │   │   ├── _winconsole.py
│   │   │   │   │   ├── core.py
│   │   │   │   │   ├── decorators.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── formatting.py
│   │   │   │   │   ├── globals.py
│   │   │   │   │   ├── parser.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── shell_completion.py
│   │   │   │   │   ├── termui.py
│   │   │   │   │   ├── testing.py
│   │   │   │   │   ├── types.py
│   │   │   │   │   ├── utils.py
│   │   │   │   ├── click-8.2.1.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE.txt
│   │   │   │   ├── cryptography/
│   │   │   │   │   ├── __about__.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── fernet.py
│   │   │   │   │   ├── hazmat/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _oid.py
│   │   │   │   │   │   ├── asn1/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── asn1.py
│   │   │   │   │   │   ├── backends/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── openssl/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── backend.py
│   │   │   │   │   │   ├── bindings/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _rust/
│   │   │   │   │   │   │   │   ├── __init__.pyi
│   │   │   │   │   │   │   │   ├── _openssl.pyi
│   │   │   │   │   │   │   │   ├── asn1.pyi
│   │   │   │   │   │   │   │   ├── declarative_asn1.pyi
│   │   │   │   │   │   │   │   ├── exceptions.pyi
│   │   │   │   │   │   │   │   ├── ocsp.pyi
│   │   │   │   │   │   │   │   ├── openssl/
│   │   │   │   │   │   │   │   │   ├── __init__.pyi
│   │   │   │   │   │   │   │   │   ├── aead.pyi
│   │   │   │   │   │   │   │   │   ├── ciphers.pyi
│   │   │   │   │   │   │   │   │   ├── cmac.pyi
│   │   │   │   │   │   │   │   │   ├── dh.pyi
│   │   │   │   │   │   │   │   │   ├── dsa.pyi
│   │   │   │   │   │   │   │   │   ├── ec.pyi
│   │   │   │   │   │   │   │   │   ├── ed25519.pyi
│   │   │   │   │   │   │   │   │   ├── ed448.pyi
│   │   │   │   │   │   │   │   │   ├── hashes.pyi
│   │   │   │   │   │   │   │   │   ├── hmac.pyi
│   │   │   │   │   │   │   │   │   ├── kdf.pyi
│   │   │   │   │   │   │   │   │   ├── keys.pyi
│   │   │   │   │   │   │   │   │   ├── poly1305.pyi
│   │   │   │   │   │   │   │   │   ├── rsa.pyi
│   │   │   │   │   │   │   │   │   ├── x25519.pyi
│   │   │   │   │   │   │   │   │   ├── x448.pyi
│   │   │   │   │   │   │   │   ├── pkcs12.pyi
│   │   │   │   │   │   │   │   ├── pkcs7.pyi
│   │   │   │   │   │   │   │   ├── test_support.pyi
│   │   │   │   │   │   │   │   ├── x509.pyi
│   │   │   │   │   │   │   ├── _rust.abi3.so
│   │   │   │   │   │   │   ├── openssl/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── _conditional.py
│   │   │   │   │   │   │   │   ├── binding.py
│   │   │   │   │   │   ├── decrepit/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── ciphers/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── algorithms.py
│   │   │   │   │   │   ├── primitives/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _asymmetric.py
│   │   │   │   │   │   │   ├── _cipheralgorithm.py
│   │   │   │   │   │   │   ├── _serialization.py
│   │   │   │   │   │   │   ├── asymmetric/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── dh.py
│   │   │   │   │   │   │   │   ├── dsa.py
│   │   │   │   │   │   │   │   ├── ec.py
│   │   │   │   │   │   │   │   ├── ed25519.py
│   │   │   │   │   │   │   │   ├── ed448.py
│   │   │   │   │   │   │   │   ├── padding.py
│   │   │   │   │   │   │   │   ├── rsa.py
│   │   │   │   │   │   │   │   ├── types.py
│   │   │   │   │   │   │   │   ├── utils.py
│   │   │   │   │   │   │   │   ├── x25519.py
│   │   │   │   │   │   │   │   ├── x448.py
│   │   │   │   │   │   │   ├── ciphers/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── aead.py
│   │   │   │   │   │   │   │   ├── algorithms.py
│   │   │   │   │   │   │   │   ├── base.py
│   │   │   │   │   │   │   │   ├── modes.py
│   │   │   │   │   │   │   ├── cmac.py
│   │   │   │   │   │   │   ├── constant_time.py
│   │   │   │   │   │   │   ├── hashes.py
│   │   │   │   │   │   │   ├── hmac.py
│   │   │   │   │   │   │   ├── kdf/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── argon2.py
│   │   │   │   │   │   │   │   ├── concatkdf.py
│   │   │   │   │   │   │   │   ├── hkdf.py
│   │   │   │   │   │   │   │   ├── kbkdf.py
│   │   │   │   │   │   │   │   ├── pbkdf2.py
│   │   │   │   │   │   │   │   ├── scrypt.py
│   │   │   │   │   │   │   │   ├── x963kdf.py
│   │   │   │   │   │   │   ├── keywrap.py
│   │   │   │   │   │   │   ├── padding.py
│   │   │   │   │   │   │   ├── poly1305.py
│   │   │   │   │   │   │   ├── serialization/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── base.py
│   │   │   │   │   │   │   │   ├── pkcs12.py
│   │   │   │   │   │   │   │   ├── pkcs7.py
│   │   │   │   │   │   │   │   ├── ssh.py
│   │   │   │   │   │   │   ├── twofactor/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── hotp.py
│   │   │   │   │   │   │   │   ├── totp.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── x509/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── base.py
│   │   │   │   │   │   ├── certificate_transparency.py
│   │   │   │   │   │   ├── extensions.py
│   │   │   │   │   │   ├── general_name.py
│   │   │   │   │   │   ├── name.py
│   │   │   │   │   │   ├── ocsp.py
│   │   │   │   │   │   ├── oid.py
│   │   │   │   │   │   ├── verification.py
│   │   │   │   ├── cryptography-46.0.1.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   ├── LICENSE.APACHE
│   │   │   │   │   │   ├── LICENSE.BSD
│   │   │   │   ├── dateutil/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _common.py
│   │   │   │   │   ├── _version.py
│   │   │   │   │   ├── easter.py
│   │   │   │   │   ├── parser/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _parser.py
│   │   │   │   │   │   ├── isoparser.py
│   │   │   │   │   ├── relativedelta.py
│   │   │   │   │   ├── rrule.py
│   │   │   │   │   ├── tz/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _common.py
│   │   │   │   │   │   ├── _factories.py
│   │   │   │   │   │   ├── tz.py
│   │   │   │   │   │   ├── win.py
│   │   │   │   │   ├── tzwin.py
│   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── zoneinfo/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── dateutil-zoneinfo.tar.gz
│   │   │   │   │   │   ├── rebuild.py
│   │   │   │   ├── deepl/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __main__.py
│   │   │   │   │   ├── api_data.py
│   │   │   │   │   ├── deepl_client.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── http_client.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── translator.py
│   │   │   │   │   ├── util.py
│   │   │   │   │   ├── version.py
│   │   │   │   ├── deepl-1.22.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── REQUESTED
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   ├── deprecation-2.1.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── deprecation.py
│   │   │   │   ├── distro/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __main__.py
│   │   │   │   │   ├── distro.py
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── distro-1.9.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── distutils-precedence.pth
│   │   │   │   ├── dotenv/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __main__.py
│   │   │   │   │   ├── cli.py
│   │   │   │   │   ├── ipython.py
│   │   │   │   │   ├── main.py
│   │   │   │   │   ├── parser.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── variables.py
│   │   │   │   │   ├── version.py
│   │   │   │   ├── feedparser/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── api.py
│   │   │   │   │   ├── datetimes/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── asctime.py
│   │   │   │   │   │   ├── greek.py
│   │   │   │   │   │   ├── hungarian.py
│   │   │   │   │   │   ├── iso8601.py
│   │   │   │   │   │   ├── korean.py
│   │   │   │   │   │   ├── perforce.py
│   │   │   │   │   │   ├── rfc822.py
│   │   │   │   │   │   ├── w3dtf.py
│   │   │   │   │   ├── encodings.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── html.py
│   │   │   │   │   ├── http.py
│   │   │   │   │   ├── mixin.py
│   │   │   │   │   ├── namespaces/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _base.py
│   │   │   │   │   │   ├── admin.py
│   │   │   │   │   │   ├── cc.py
│   │   │   │   │   │   ├── dc.py
│   │   │   │   │   │   ├── georss.py
│   │   │   │   │   │   ├── itunes.py
│   │   │   │   │   │   ├── mediarss.py
│   │   │   │   │   │   ├── psc.py
│   │   │   │   │   ├── parsers/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── loose.py
│   │   │   │   │   │   ├── strict.py
│   │   │   │   │   ├── sanitizer.py
│   │   │   │   │   ├── sgml.py
│   │   │   │   │   ├── urls.py
│   │   │   │   │   ├── util.py
│   │   │   │   ├── feedparser-6.0.12.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── REQUESTED
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── flask/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __main__.py
│   │   │   │   │   ├── app.py
│   │   │   │   │   ├── blueprints.py
│   │   │   │   │   ├── cli.py
│   │   │   │   │   ├── config.py
│   │   │   │   │   ├── ctx.py
│   │   │   │   │   ├── debughelpers.py
│   │   │   │   │   ├── globals.py
│   │   │   │   │   ├── helpers.py
│   │   │   │   │   ├── json/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── provider.py
│   │   │   │   │   │   ├── tag.py
│   │   │   │   │   ├── logging.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── sansio/
│   │   │   │   │   │   ├── README.md
│   │   │   │   │   │   ├── app.py
│   │   │   │   │   │   ├── blueprints.py
│   │   │   │   │   │   ├── scaffold.py
│   │   │   │   │   ├── sessions.py
│   │   │   │   │   ├── signals.py
│   │   │   │   │   ├── templating.py
│   │   │   │   │   ├── testing.py
│   │   │   │   │   ├── typing.py
│   │   │   │   │   ├── views.py
│   │   │   │   │   ├── wrappers.py
│   │   │   │   ├── flask-3.1.2.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── REQUESTED
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE.txt
│   │   │   │   ├── h11/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _abnf.py
│   │   │   │   │   ├── _connection.py
│   │   │   │   │   ├── _events.py
│   │   │   │   │   ├── _headers.py
│   │   │   │   │   ├── _readers.py
│   │   │   │   │   ├── _receivebuffer.py
│   │   │   │   │   ├── _state.py
│   │   │   │   │   ├── _util.py
│   │   │   │   │   ├── _version.py
│   │   │   │   │   ├── _writers.py
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── h11-0.16.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE.txt
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── h2/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── config.py
│   │   │   │   │   ├── connection.py
│   │   │   │   │   ├── errors.py
│   │   │   │   │   ├── events.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── frame_buffer.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── settings.py
│   │   │   │   │   ├── stream.py
│   │   │   │   │   ├── utilities.py
│   │   │   │   │   ├── windows.py
│   │   │   │   ├── h2-4.3.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── hpack/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── hpack.py
│   │   │   │   │   ├── huffman.py
│   │   │   │   │   ├── huffman_constants.py
│   │   │   │   │   ├── huffman_table.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── struct.py
│   │   │   │   │   ├── table.py
│   │   │   │   ├── hpack-4.1.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── httpcore/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _api.py
│   │   │   │   │   ├── _async/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── connection.py
│   │   │   │   │   │   ├── connection_pool.py
│   │   │   │   │   │   ├── http11.py
│   │   │   │   │   │   ├── http2.py
│   │   │   │   │   │   ├── http_proxy.py
│   │   │   │   │   │   ├── interfaces.py
│   │   │   │   │   │   ├── socks_proxy.py
│   │   │   │   │   ├── _backends/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── anyio.py
│   │   │   │   │   │   ├── auto.py
│   │   │   │   │   │   ├── base.py
│   │   │   │   │   │   ├── mock.py
│   │   │   │   │   │   ├── sync.py
│   │   │   │   │   │   ├── trio.py
│   │   │   │   │   ├── _exceptions.py
│   │   │   │   │   ├── _models.py
│   │   │   │   │   ├── _ssl.py
│   │   │   │   │   ├── _sync/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── connection.py
│   │   │   │   │   │   ├── connection_pool.py
│   │   │   │   │   │   ├── http11.py
│   │   │   │   │   │   ├── http2.py
│   │   │   │   │   │   ├── http_proxy.py
│   │   │   │   │   │   ├── interfaces.py
│   │   │   │   │   │   ├── socks_proxy.py
│   │   │   │   │   ├── _synchronization.py
│   │   │   │   │   ├── _trace.py
│   │   │   │   │   ├── _utils.py
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── httpcore-1.0.9.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE.md
│   │   │   │   ├── httpx/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __version__.py
│   │   │   │   │   ├── _api.py
│   │   │   │   │   ├── _auth.py
│   │   │   │   │   ├── _client.py
│   │   │   │   │   ├── _config.py
│   │   │   │   │   ├── _content.py
│   │   │   │   │   ├── _decoders.py
│   │   │   │   │   ├── _exceptions.py
│   │   │   │   │   ├── _main.py
│   │   │   │   │   ├── _models.py
│   │   │   │   │   ├── _multipart.py
│   │   │   │   │   ├── _status_codes.py
│   │   │   │   │   ├── _transports/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── asgi.py
│   │   │   │   │   │   ├── base.py
│   │   │   │   │   │   ├── default.py
│   │   │   │   │   │   ├── mock.py
│   │   │   │   │   │   ├── wsgi.py
│   │   │   │   │   ├── _types.py
│   │   │   │   │   ├── _urlparse.py
│   │   │   │   │   ├── _urls.py
│   │   │   │   │   ├── _utils.py
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── httpx-0.28.1.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE.md
│   │   │   │   ├── hyperframe/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── flags.py
│   │   │   │   │   ├── frame.py
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── hyperframe-6.1.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── idna/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── codec.py
│   │   │   │   │   ├── compat.py
│   │   │   │   │   ├── core.py
│   │   │   │   │   ├── idnadata.py
│   │   │   │   │   ├── intranges.py
│   │   │   │   │   ├── package_data.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── uts46data.py
│   │   │   │   ├── idna-3.10.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE.md
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   ├── iniconfig/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _parse.py
│   │   │   │   │   ├── _version.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── iniconfig-2.1.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   ├── itsdangerous/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _json.py
│   │   │   │   │   ├── encoding.py
│   │   │   │   │   ├── exc.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── serializer.py
│   │   │   │   │   ├── signer.py
│   │   │   │   │   ├── timed.py
│   │   │   │   │   ├── url_safe.py
│   │   │   │   ├── itsdangerous-2.2.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE.txt
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   ├── jinja2/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _identifier.py
│   │   │   │   │   ├── async_utils.py
│   │   │   │   │   ├── bccache.py
│   │   │   │   │   ├── compiler.py
│   │   │   │   │   ├── constants.py
│   │   │   │   │   ├── debug.py
│   │   │   │   │   ├── defaults.py
│   │   │   │   │   ├── environment.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── ext.py
│   │   │   │   │   ├── filters.py
│   │   │   │   │   ├── idtracking.py
│   │   │   │   │   ├── lexer.py
│   │   │   │   │   ├── loaders.py
│   │   │   │   │   ├── meta.py
│   │   │   │   │   ├── nativetypes.py
│   │   │   │   │   ├── nodes.py
│   │   │   │   │   ├── optimizer.py
│   │   │   │   │   ├── parser.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── runtime.py
│   │   │   │   │   ├── sandbox.py
│   │   │   │   │   ├── tests.py
│   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── visitor.py
│   │   │   │   ├── jinja2-3.1.6.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE.txt
│   │   │   │   ├── jiter/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __init__.pyi
│   │   │   │   │   ├── jiter.cpython-311-darwin.so
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── jiter-0.11.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   ├── jwt/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── algorithms.py
│   │   │   │   │   ├── api_jwk.py
│   │   │   │   │   ├── api_jws.py
│   │   │   │   │   ├── api_jwt.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── help.py
│   │   │   │   │   ├── jwk_set_cache.py
│   │   │   │   │   ├── jwks_client.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── types.py
│   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── warnings.py
│   │   │   │   ├── markupsafe/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _native.py
│   │   │   │   │   ├── _speedups.c
│   │   │   │   │   ├── _speedups.cpython-311-darwin.so
│   │   │   │   │   ├── _speedups.pyi
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── openai/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __main__.py
│   │   │   │   │   ├── _base_client.py
│   │   │   │   │   ├── _client.py
│   │   │   │   │   ├── _compat.py
│   │   │   │   │   ├── _constants.py
│   │   │   │   │   ├── _exceptions.py
│   │   │   │   │   ├── _extras/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _common.py
│   │   │   │   │   │   ├── numpy_proxy.py
│   │   │   │   │   │   ├── pandas_proxy.py
│   │   │   │   │   │   ├── sounddevice_proxy.py
│   │   │   │   │   ├── _files.py
│   │   │   │   │   ├── _legacy_response.py
│   │   │   │   │   ├── _models.py
│   │   │   │   │   ├── _module_client.py
│   │   │   │   │   ├── _qs.py
│   │   │   │   │   ├── _resource.py
│   │   │   │   │   ├── _response.py
│   │   │   │   │   ├── _streaming.py
│   │   │   │   │   ├── _types.py
│   │   │   │   │   ├── _utils/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _compat.py
│   │   │   │   │   │   ├── _datetime_parse.py
│   │   │   │   │   │   ├── _logs.py
│   │   │   │   │   │   ├── _proxy.py
│   │   │   │   │   │   ├── _reflection.py
│   │   │   │   │   │   ├── _resources_proxy.py
│   │   │   │   │   │   ├── _streams.py
│   │   │   │   │   │   ├── _sync.py
│   │   │   │   │   │   ├── _transform.py
│   │   │   │   │   │   ├── _typing.py
│   │   │   │   │   │   ├── _utils.py
│   │   │   │   │   ├── _version.py
│   │   │   │   │   ├── cli/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _api/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _main.py
│   │   │   │   │   │   │   ├── audio.py
│   │   │   │   │   │   │   ├── chat/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── completions.py
│   │   │   │   │   │   │   ├── completions.py
│   │   │   │   │   │   │   ├── files.py
│   │   │   │   │   │   │   ├── fine_tuning/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── jobs.py
│   │   │   │   │   │   │   ├── image.py
│   │   │   │   │   │   │   ├── models.py
│   │   │   │   │   │   ├── _cli.py
│   │   │   │   │   │   ├── _errors.py
│   │   │   │   │   │   ├── _models.py
│   │   │   │   │   │   ├── _progress.py
│   │   │   │   │   │   ├── _tools/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _main.py
│   │   │   │   │   │   │   ├── fine_tunes.py
│   │   │   │   │   │   │   ├── migrate.py
│   │   │   │   │   │   ├── _utils.py
│   │   │   │   │   ├── helpers/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── local_audio_player.py
│   │   │   │   │   │   ├── microphone.py
│   │   │   │   │   ├── lib/
│   │   │   │   │   │   ├── .keep
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _old_api.py
│   │   │   │   │   │   ├── _parsing/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _completions.py
│   │   │   │   │   │   │   ├── _responses.py
│   │   │   │   │   │   ├── _pydantic.py
│   │   │   │   │   │   ├── _tools.py
│   │   │   │   │   │   ├── _validators.py
│   │   │   │   │   │   ├── azure.py
│   │   │   │   │   │   ├── streaming/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _assistants.py
│   │   │   │   │   │   │   ├── _deltas.py
│   │   │   │   │   │   │   ├── chat/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── _completions.py
│   │   │   │   │   │   │   │   ├── _events.py
│   │   │   │   │   │   │   │   ├── _types.py
│   │   │   │   │   │   │   ├── responses/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── _events.py
│   │   │   │   │   │   │   │   ├── _responses.py
│   │   │   │   │   │   │   │   ├── _types.py
│   │   │   │   │   ├── pagination.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── resources/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── audio/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── audio.py
│   │   │   │   │   │   │   ├── speech.py
│   │   │   │   │   │   │   ├── transcriptions.py
│   │   │   │   │   │   │   ├── translations.py
│   │   │   │   │   │   ├── batches.py
│   │   │   │   │   │   ├── beta/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── assistants.py
│   │   │   │   │   │   │   ├── beta.py
│   │   │   │   │   │   │   ├── realtime/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── realtime.py
│   │   │   │   │   │   │   │   ├── sessions.py
│   │   │   │   │   │   │   │   ├── transcription_sessions.py
│   │   │   │   │   │   │   ├── threads/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── messages.py
│   │   │   │   │   │   │   │   ├── runs/
│   │   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   │   ├── runs.py
│   │   │   │   │   │   │   │   │   ├── steps.py
│   │   │   │   │   │   │   │   ├── threads.py
│   │   │   │   │   │   ├── chat/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── chat.py
│   │   │   │   │   │   │   ├── completions/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── completions.py
│   │   │   │   │   │   │   │   ├── messages.py
│   │   │   │   │   │   ├── completions.py
│   │   │   │   │   │   ├── containers/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── containers.py
│   │   │   │   │   │   │   ├── files/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── content.py
│   │   │   │   │   │   │   │   ├── files.py
│   │   │   │   │   │   ├── conversations/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── conversations.py
│   │   │   │   │   │   │   ├── items.py
│   │   │   │   │   │   ├── embeddings.py
│   │   │   │   │   │   ├── evals/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── evals.py
│   │   │   │   │   │   │   ├── runs/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── output_items.py
│   │   │   │   │   │   │   │   ├── runs.py
│   │   │   │   │   │   ├── files.py
│   │   │   │   │   │   ├── fine_tuning/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── alpha/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── alpha.py
│   │   │   │   │   │   │   │   ├── graders.py
│   │   │   │   │   │   │   ├── checkpoints/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── checkpoints.py
│   │   │   │   │   │   │   │   ├── permissions.py
│   │   │   │   │   │   │   ├── fine_tuning.py
│   │   │   │   │   │   │   ├── jobs/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── checkpoints.py
│   │   │   │   │   │   │   │   ├── jobs.py
│   │   │   │   │   │   ├── images.py
│   │   │   │   │   │   ├── models.py
│   │   │   │   │   │   ├── moderations.py
│   │   │   │   │   │   ├── realtime/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── client_secrets.py
│   │   │   │   │   │   │   ├── realtime.py
│   │   │   │   │   │   ├── responses/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── input_items.py
│   │   │   │   │   │   │   ├── responses.py
│   │   │   │   │   │   ├── uploads/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── parts.py
│   │   │   │   │   │   │   ├── uploads.py
│   │   │   │   │   │   ├── vector_stores/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── file_batches.py
│   │   │   │   │   │   │   ├── files.py
│   │   │   │   │   │   │   ├── vector_stores.py
│   │   │   │   │   │   ├── webhooks.py
│   │   │   │   │   ├── types/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── audio/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── speech_create_params.py
│   │   │   │   │   │   │   ├── speech_model.py
│   │   │   │   │   │   │   ├── transcription.py
│   │   │   │   │   │   │   ├── transcription_create_params.py
│   │   │   │   │   │   │   ├── transcription_create_response.py
│   │   │   │   │   │   │   ├── transcription_include.py
│   │   │   │   │   │   │   ├── transcription_segment.py
│   │   │   │   │   │   │   ├── transcription_stream_event.py
│   │   │   │   │   │   │   ├── transcription_text_delta_event.py
│   │   │   │   │   │   │   ├── transcription_text_done_event.py
│   │   │   │   │   │   │   ├── transcription_verbose.py
│   │   │   │   │   │   │   ├── transcription_word.py
│   │   │   │   │   │   │   ├── translation.py
│   │   │   │   │   │   │   ├── translation_create_params.py
│   │   │   │   │   │   │   ├── translation_create_response.py
│   │   │   │   │   │   │   ├── translation_verbose.py
│   │   │   │   │   │   ├── audio_model.py
│   │   │   │   │   │   ├── audio_response_format.py
│   │   │   │   │   │   ├── auto_file_chunking_strategy_param.py
│   │   │   │   │   │   ├── batch.py
│   │   │   │   │   │   ├── batch_create_params.py
│   │   │   │   │   │   ├── batch_error.py
│   │   │   │   │   │   ├── batch_list_params.py
│   │   │   │   │   │   ├── batch_request_counts.py
│   │   │   │   │   │   ├── beta/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── assistant.py
│   │   │   │   │   │   │   ├── assistant_create_params.py
│   │   │   │   │   │   │   ├── assistant_deleted.py
│   │   │   │   │   │   │   ├── assistant_list_params.py
│   │   │   │   │   │   │   ├── assistant_response_format_option.py
│   │   │   │   │   │   │   ├── assistant_response_format_option_param.py
│   │   │   │   │   │   │   ├── assistant_stream_event.py
│   │   │   │   │   │   │   ├── assistant_tool.py
│   │   │   │   │   │   │   ├── assistant_tool_choice.py
│   │   │   │   │   │   │   ├── assistant_tool_choice_function.py
│   │   │   │   │   │   │   ├── assistant_tool_choice_function_param.py
│   │   │   │   │   │   │   ├── assistant_tool_choice_option.py
│   │   │   │   │   │   │   ├── assistant_tool_choice_option_param.py
│   │   │   │   │   │   │   ├── assistant_tool_choice_param.py
│   │   │   │   │   │   │   ├── assistant_tool_param.py
│   │   │   │   │   │   │   ├── assistant_update_params.py
│   │   │   │   │   │   │   ├── chat/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── code_interpreter_tool.py
│   │   │   │   │   │   │   ├── code_interpreter_tool_param.py
│   │   │   │   │   │   │   ├── file_search_tool.py
│   │   │   │   │   │   │   ├── file_search_tool_param.py
│   │   │   │   │   │   │   ├── function_tool.py
│   │   │   │   │   │   │   ├── function_tool_param.py
│   │   │   │   │   │   │   ├── realtime/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── conversation_created_event.py
│   │   │   │   │   │   │   │   ├── conversation_item.py
│   │   │   │   │   │   │   │   ├── conversation_item_content.py
│   │   │   │   │   │   │   │   ├── conversation_item_content_param.py
│   │   │   │   │   │   │   │   ├── conversation_item_create_event.py
│   │   │   │   │   │   │   │   ├── conversation_item_create_event_param.py
│   │   │   │   │   │   │   │   ├── conversation_item_created_event.py
│   │   │   │   │   │   │   │   ├── conversation_item_delete_event.py
│   │   │   │   │   │   │   │   ├── conversation_item_delete_event_param.py
│   │   │   │   │   │   │   │   ├── conversation_item_deleted_event.py
│   │   │   │   │   │   │   │   ├── conversation_item_input_audio_transcription_completed_event.py
│   │   │   │   │   │   │   │   ├── conversation_item_input_audio_transcription_delta_event.py
│   │   │   │   │   │   │   │   ├── conversation_item_input_audio_transcription_failed_event.py
│   │   │   │   │   │   │   │   ├── conversation_item_param.py
│   │   │   │   │   │   │   │   ├── conversation_item_retrieve_event.py
│   │   │   │   │   │   │   │   ├── conversation_item_retrieve_event_param.py
│   │   │   │   │   │   │   │   ├── conversation_item_truncate_event.py
│   │   │   │   │   │   │   │   ├── conversation_item_truncate_event_param.py
│   │   │   │   │   │   │   │   ├── conversation_item_truncated_event.py
│   │   │   │   │   │   │   │   ├── conversation_item_with_reference.py
│   │   │   │   │   │   │   │   ├── conversation_item_with_reference_param.py
│   │   │   │   │   │   │   │   ├── error_event.py
│   │   │   │   │   │   │   │   ├── input_audio_buffer_append_event.py
│   │   │   │   │   │   │   │   ├── input_audio_buffer_append_event_param.py
│   │   │   │   │   │   │   │   ├── input_audio_buffer_clear_event.py
│   │   │   │   │   │   │   │   ├── input_audio_buffer_clear_event_param.py
│   │   │   │   │   │   │   │   ├── input_audio_buffer_cleared_event.py
│   │   │   │   │   │   │   │   ├── input_audio_buffer_commit_event.py
│   │   │   │   │   │   │   │   ├── input_audio_buffer_commit_event_param.py
│   │   │   │   │   │   │   │   ├── input_audio_buffer_committed_event.py
│   │   │   │   │   │   │   │   ├── input_audio_buffer_speech_started_event.py
│   │   │   │   │   │   │   │   ├── input_audio_buffer_speech_stopped_event.py
│   │   │   │   │   │   │   │   ├── rate_limits_updated_event.py
│   │   │   │   │   │   │   │   ├── realtime_client_event.py
│   │   │   │   │   │   │   │   ├── realtime_client_event_param.py
│   │   │   │   │   │   │   │   ├── realtime_connect_params.py
│   │   │   │   │   │   │   │   ├── realtime_response.py
│   │   │   │   │   │   │   │   ├── realtime_response_status.py
│   │   │   │   │   │   │   │   ├── realtime_response_usage.py
│   │   │   │   │   │   │   │   ├── realtime_server_event.py
│   │   │   │   │   │   │   │   ├── response_audio_delta_event.py
│   │   │   │   │   │   │   │   ├── response_audio_done_event.py
│   │   │   │   │   │   │   │   ├── response_audio_transcript_delta_event.py
│   │   │   │   │   │   │   │   ├── response_audio_transcript_done_event.py
│   │   │   │   │   │   │   │   ├── response_cancel_event.py
│   │   │   │   │   │   │   │   ├── response_cancel_event_param.py
│   │   │   │   │   │   │   │   ├── response_content_part_added_event.py
│   │   │   │   │   │   │   │   ├── response_content_part_done_event.py
│   │   │   │   │   │   │   │   ├── response_create_event.py
│   │   │   │   │   │   │   │   ├── response_create_event_param.py
│   │   │   │   │   │   │   │   ├── response_created_event.py
│   │   │   │   │   │   │   │   ├── response_done_event.py
│   │   │   │   │   │   │   │   ├── response_function_call_arguments_delta_event.py
│   │   │   │   │   │   │   │   ├── response_function_call_arguments_done_event.py
│   │   │   │   │   │   │   │   ├── response_output_item_added_event.py
│   │   │   │   │   │   │   │   ├── response_output_item_done_event.py
│   │   │   │   │   │   │   │   ├── response_text_delta_event.py
│   │   │   │   │   │   │   │   ├── response_text_done_event.py
│   │   │   │   │   │   │   │   ├── session.py
│   │   │   │   │   │   │   │   ├── session_create_params.py
│   │   │   │   │   │   │   │   ├── session_create_response.py
│   │   │   │   │   │   │   │   ├── session_created_event.py
│   │   │   │   │   │   │   │   ├── session_update_event.py
│   │   │   │   │   │   │   │   ├── session_update_event_param.py
│   │   │   │   │   │   │   │   ├── session_updated_event.py
│   │   │   │   │   │   │   │   ├── transcription_session.py
│   │   │   │   │   │   │   │   ├── transcription_session_create_params.py
│   │   │   │   │   │   │   │   ├── transcription_session_update.py
│   │   │   │   │   │   │   │   ├── transcription_session_update_param.py
│   │   │   │   │   │   │   │   ├── transcription_session_updated_event.py
│   │   │   │   │   │   │   ├── thread.py
│   │   │   │   │   │   │   ├── thread_create_and_run_params.py
│   │   │   │   │   │   │   ├── thread_create_params.py
│   │   │   │   │   │   │   ├── thread_deleted.py
│   │   │   │   │   │   │   ├── thread_update_params.py
│   │   │   │   │   │   │   ├── threads/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── annotation.py
│   │   │   │   │   │   │   │   ├── annotation_delta.py
│   │   │   │   │   │   │   │   ├── file_citation_annotation.py
│   │   │   │   │   │   │   │   ├── file_citation_delta_annotation.py
│   │   │   │   │   │   │   │   ├── file_path_annotation.py
│   │   │   │   │   │   │   │   ├── file_path_delta_annotation.py
│   │   │   │   │   │   │   │   ├── image_file.py
│   │   │   │   │   │   │   │   ├── image_file_content_block.py
│   │   │   │   │   │   │   │   ├── image_file_content_block_param.py
│   │   │   │   │   │   │   │   ├── image_file_delta.py
│   │   │   │   │   │   │   │   ├── image_file_delta_block.py
│   │   │   │   │   │   │   │   ├── image_file_param.py
│   │   │   │   │   │   │   │   ├── image_url.py
│   │   │   │   │   │   │   │   ├── image_url_content_block.py
│   │   │   │   │   │   │   │   ├── image_url_content_block_param.py
│   │   │   │   │   │   │   │   ├── image_url_delta.py
│   │   │   │   │   │   │   │   ├── image_url_delta_block.py
│   │   │   │   │   │   │   │   ├── image_url_param.py
│   │   │   │   │   │   │   │   ├── message.py
│   │   │   │   │   │   │   │   ├── message_content.py
│   │   │   │   │   │   │   │   ├── message_content_delta.py
│   │   │   │   │   │   │   │   ├── message_content_part_param.py
│   │   │   │   │   │   │   │   ├── message_create_params.py
│   │   │   │   │   │   │   │   ├── message_deleted.py
│   │   │   │   │   │   │   │   ├── message_delta.py
│   │   │   │   │   │   │   │   ├── message_delta_event.py
│   │   │   │   │   │   │   │   ├── message_list_params.py
│   │   │   │   │   │   │   │   ├── message_update_params.py
│   │   │   │   │   │   │   │   ├── refusal_content_block.py
│   │   │   │   │   │   │   │   ├── refusal_delta_block.py
│   │   │   │   │   │   │   │   ├── required_action_function_tool_call.py
│   │   │   │   │   │   │   │   ├── run.py
│   │   │   │   │   │   │   │   ├── run_create_params.py
│   │   │   │   │   │   │   │   ├── run_list_params.py
│   │   │   │   │   │   │   │   ├── run_status.py
│   │   │   │   │   │   │   │   ├── run_submit_tool_outputs_params.py
│   │   │   │   │   │   │   │   ├── run_update_params.py
│   │   │   │   │   │   │   │   ├── runs/
│   │   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   │   ├── code_interpreter_logs.py
│   │   │   │   │   │   │   │   │   ├── code_interpreter_output_image.py
│   │   │   │   │   │   │   │   │   ├── code_interpreter_tool_call.py
│   │   │   │   │   │   │   │   │   ├── code_interpreter_tool_call_delta.py
│   │   │   │   │   │   │   │   │   ├── file_search_tool_call.py
│   │   │   │   │   │   │   │   │   ├── file_search_tool_call_delta.py
│   │   │   │   │   │   │   │   │   ├── function_tool_call.py
│   │   │   │   │   │   │   │   │   ├── function_tool_call_delta.py
│   │   │   │   │   │   │   │   │   ├── message_creation_step_details.py
│   │   │   │   │   │   │   │   │   ├── run_step.py
│   │   │   │   │   │   │   │   │   ├── run_step_delta.py
│   │   │   │   │   │   │   │   │   ├── run_step_delta_event.py
│   │   │   │   │   │   │   │   │   ├── run_step_delta_message_delta.py
│   │   │   │   │   │   │   │   │   ├── run_step_include.py
│   │   │   │   │   │   │   │   │   ├── step_list_params.py
│   │   │   │   │   │   │   │   │   ├── step_retrieve_params.py
│   │   │   │   │   │   │   │   │   ├── tool_call.py
│   │   │   │   │   │   │   │   │   ├── tool_call_delta.py
│   │   │   │   │   │   │   │   │   ├── tool_call_delta_object.py
│   │   │   │   │   │   │   │   │   ├── tool_calls_step_details.py
│   │   │   │   │   │   │   │   ├── text.py
│   │   │   │   │   │   │   │   ├── text_content_block.py
│   │   │   │   │   │   │   │   ├── text_content_block_param.py
│   │   │   │   │   │   │   │   ├── text_delta.py
│   │   │   │   │   │   │   │   ├── text_delta_block.py
│   │   │   │   │   │   ├── chat/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── chat_completion.py
│   │   │   │   │   │   │   ├── chat_completion_allowed_tool_choice_param.py
│   │   │   │   │   │   │   ├── chat_completion_allowed_tools_param.py
│   │   │   │   │   │   │   ├── chat_completion_assistant_message_param.py
│   │   │   │   │   │   │   ├── chat_completion_audio.py
│   │   │   │   │   │   │   ├── chat_completion_audio_param.py
│   │   │   │   │   │   │   ├── chat_completion_chunk.py
│   │   │   │   │   │   │   ├── chat_completion_content_part_image.py
│   │   │   │   │   │   │   ├── chat_completion_content_part_image_param.py
│   │   │   │   │   │   │   ├── chat_completion_content_part_input_audio_param.py
│   │   │   │   │   │   │   ├── chat_completion_content_part_param.py
│   │   │   │   │   │   │   ├── chat_completion_content_part_refusal_param.py
│   │   │   │   │   │   │   ├── chat_completion_content_part_text.py
│   │   │   │   │   │   │   ├── chat_completion_content_part_text_param.py
│   │   │   │   │   │   │   ├── chat_completion_custom_tool_param.py
│   │   │   │   │   │   │   ├── chat_completion_deleted.py
│   │   │   │   │   │   │   ├── chat_completion_developer_message_param.py
│   │   │   │   │   │   │   ├── chat_completion_function_call_option_param.py
│   │   │   │   │   │   │   ├── chat_completion_function_message_param.py
│   │   │   │   │   │   │   ├── chat_completion_function_tool.py
│   │   │   │   │   │   │   ├── chat_completion_function_tool_param.py
│   │   │   │   │   │   │   ├── chat_completion_message.py
│   │   │   │   │   │   │   ├── chat_completion_message_custom_tool_call.py
│   │   │   │   │   │   │   ├── chat_completion_message_custom_tool_call_param.py
│   │   │   │   │   │   │   ├── chat_completion_message_function_tool_call.py
│   │   │   │   │   │   │   ├── chat_completion_message_function_tool_call_param.py
│   │   │   │   │   │   │   ├── chat_completion_message_param.py
│   │   │   │   │   │   │   ├── chat_completion_message_tool_call.py
│   │   │   │   │   │   │   ├── chat_completion_message_tool_call_param.py
│   │   │   │   │   │   │   ├── chat_completion_message_tool_call_union_param.py
│   │   │   │   │   │   │   ├── chat_completion_modality.py
│   │   │   │   │   │   │   ├── chat_completion_named_tool_choice_custom_param.py
│   │   │   │   │   │   │   ├── chat_completion_named_tool_choice_param.py
│   │   │   │   │   │   │   ├── chat_completion_prediction_content_param.py
│   │   │   │   │   │   │   ├── chat_completion_reasoning_effort.py
│   │   │   │   │   │   │   ├── chat_completion_role.py
│   │   │   │   │   │   │   ├── chat_completion_store_message.py
│   │   │   │   │   │   │   ├── chat_completion_stream_options_param.py
│   │   │   │   │   │   │   ├── chat_completion_system_message_param.py
│   │   │   │   │   │   │   ├── chat_completion_token_logprob.py
│   │   │   │   │   │   │   ├── chat_completion_tool_choice_option_param.py
│   │   │   │   │   │   │   ├── chat_completion_tool_message_param.py
│   │   │   │   │   │   │   ├── chat_completion_tool_param.py
│   │   │   │   │   │   │   ├── chat_completion_tool_union_param.py
│   │   │   │   │   │   │   ├── chat_completion_user_message_param.py
│   │   │   │   │   │   │   ├── completion_create_params.py
│   │   │   │   │   │   │   ├── completion_list_params.py
│   │   │   │   │   │   │   ├── completion_update_params.py
│   │   │   │   │   │   │   ├── completions/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── message_list_params.py
│   │   │   │   │   │   │   ├── parsed_chat_completion.py
│   │   │   │   │   │   │   ├── parsed_function_tool_call.py
│   │   │   │   │   │   ├── chat_model.py
│   │   │   │   │   │   ├── completion.py
│   │   │   │   │   │   ├── completion_choice.py
│   │   │   │   │   │   ├── completion_create_params.py
│   │   │   │   │   │   ├── completion_usage.py
│   │   │   │   │   │   ├── container_create_params.py
│   │   │   │   │   │   ├── container_create_response.py
│   │   │   │   │   │   ├── container_list_params.py
│   │   │   │   │   │   ├── container_list_response.py
│   │   │   │   │   │   ├── container_retrieve_response.py
│   │   │   │   │   │   ├── containers/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── file_create_params.py
│   │   │   │   │   │   │   ├── file_create_response.py
│   │   │   │   │   │   │   ├── file_list_params.py
│   │   │   │   │   │   │   ├── file_list_response.py
│   │   │   │   │   │   │   ├── file_retrieve_response.py
│   │   │   │   │   │   │   ├── files/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── conversations/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── computer_screenshot_content.py
│   │   │   │   │   │   │   ├── conversation.py
│   │   │   │   │   │   │   ├── conversation_create_params.py
│   │   │   │   │   │   │   ├── conversation_deleted_resource.py
│   │   │   │   │   │   │   ├── conversation_item.py
│   │   │   │   │   │   │   ├── conversation_item_list.py
│   │   │   │   │   │   │   ├── conversation_update_params.py
│   │   │   │   │   │   │   ├── input_file_content.py
│   │   │   │   │   │   │   ├── input_file_content_param.py
│   │   │   │   │   │   │   ├── input_image_content.py
│   │   │   │   │   │   │   ├── input_image_content_param.py
│   │   │   │   │   │   │   ├── input_text_content.py
│   │   │   │   │   │   │   ├── input_text_content_param.py
│   │   │   │   │   │   │   ├── item_create_params.py
│   │   │   │   │   │   │   ├── item_list_params.py
│   │   │   │   │   │   │   ├── item_retrieve_params.py
│   │   │   │   │   │   │   ├── message.py
│   │   │   │   │   │   │   ├── output_text_content.py
│   │   │   │   │   │   │   ├── output_text_content_param.py
│   │   │   │   │   │   │   ├── refusal_content.py
│   │   │   │   │   │   │   ├── refusal_content_param.py
│   │   │   │   │   │   │   ├── summary_text_content.py
│   │   │   │   │   │   │   ├── text_content.py
│   │   │   │   │   │   ├── create_embedding_response.py
│   │   │   │   │   │   ├── embedding.py
│   │   │   │   │   │   ├── embedding_create_params.py
│   │   │   │   │   │   ├── embedding_model.py
│   │   │   │   │   │   ├── eval_create_params.py
│   │   │   │   │   │   ├── eval_create_response.py
│   │   │   │   │   │   ├── eval_custom_data_source_config.py
│   │   │   │   │   │   ├── eval_delete_response.py
│   │   │   │   │   │   ├── eval_list_params.py
│   │   │   │   │   │   ├── eval_list_response.py
│   │   │   │   │   │   ├── eval_retrieve_response.py
│   │   │   │   │   │   ├── eval_stored_completions_data_source_config.py
│   │   │   │   │   │   ├── eval_update_params.py
│   │   │   │   │   │   ├── eval_update_response.py
│   │   │   │   │   │   ├── evals/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── create_eval_completions_run_data_source.py
│   │   │   │   │   │   │   ├── create_eval_completions_run_data_source_param.py
│   │   │   │   │   │   │   ├── create_eval_jsonl_run_data_source.py
│   │   │   │   │   │   │   ├── create_eval_jsonl_run_data_source_param.py
│   │   │   │   │   │   │   ├── eval_api_error.py
│   │   │   │   │   │   │   ├── run_cancel_response.py
│   │   │   │   │   │   │   ├── run_create_params.py
│   │   │   │   │   │   │   ├── run_create_response.py
│   │   │   │   │   │   │   ├── run_delete_response.py
│   │   │   │   │   │   │   ├── run_list_params.py
│   │   │   │   │   │   │   ├── run_list_response.py
│   │   │   │   │   │   │   ├── run_retrieve_response.py
│   │   │   │   │   │   │   ├── runs/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── output_item_list_params.py
│   │   │   │   │   │   │   │   ├── output_item_list_response.py
│   │   │   │   │   │   │   │   ├── output_item_retrieve_response.py
│   │   │   │   │   │   ├── file_chunking_strategy.py
│   │   │   │   │   │   ├── file_chunking_strategy_param.py
│   │   │   │   │   │   ├── file_content.py
│   │   │   │   │   │   ├── file_create_params.py
│   │   │   │   │   │   ├── file_deleted.py
│   │   │   │   │   │   ├── file_list_params.py
│   │   │   │   │   │   ├── file_object.py
│   │   │   │   │   │   ├── file_purpose.py
│   │   │   │   │   │   ├── fine_tuning/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── alpha/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── grader_run_params.py
│   │   │   │   │   │   │   │   ├── grader_run_response.py
│   │   │   │   │   │   │   │   ├── grader_validate_params.py
│   │   │   │   │   │   │   │   ├── grader_validate_response.py
│   │   │   │   │   │   │   ├── checkpoints/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── permission_create_params.py
│   │   │   │   │   │   │   │   ├── permission_create_response.py
│   │   │   │   │   │   │   │   ├── permission_delete_response.py
│   │   │   │   │   │   │   │   ├── permission_retrieve_params.py
│   │   │   │   │   │   │   │   ├── permission_retrieve_response.py
│   │   │   │   │   │   │   ├── dpo_hyperparameters.py
│   │   │   │   │   │   │   ├── dpo_hyperparameters_param.py
│   │   │   │   │   │   │   ├── dpo_method.py
│   │   │   │   │   │   │   ├── dpo_method_param.py
│   │   │   │   │   │   │   ├── fine_tuning_job.py
│   │   │   │   │   │   │   ├── fine_tuning_job_event.py
│   │   │   │   │   │   │   ├── fine_tuning_job_integration.py
│   │   │   │   │   │   │   ├── fine_tuning_job_wandb_integration.py
│   │   │   │   │   │   │   ├── fine_tuning_job_wandb_integration_object.py
│   │   │   │   │   │   │   ├── job_create_params.py
│   │   │   │   │   │   │   ├── job_list_events_params.py
│   │   │   │   │   │   │   ├── job_list_params.py
│   │   │   │   │   │   │   ├── jobs/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── checkpoint_list_params.py
│   │   │   │   │   │   │   │   ├── fine_tuning_job_checkpoint.py
│   │   │   │   │   │   │   ├── reinforcement_hyperparameters.py
│   │   │   │   │   │   │   ├── reinforcement_hyperparameters_param.py
│   │   │   │   │   │   │   ├── reinforcement_method.py
│   │   │   │   │   │   │   ├── reinforcement_method_param.py
│   │   │   │   │   │   │   ├── supervised_hyperparameters.py
│   │   │   │   │   │   │   ├── supervised_hyperparameters_param.py
│   │   │   │   │   │   │   ├── supervised_method.py
│   │   │   │   │   │   │   ├── supervised_method_param.py
│   │   │   │   │   │   ├── graders/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── label_model_grader.py
│   │   │   │   │   │   │   ├── label_model_grader_param.py
│   │   │   │   │   │   │   ├── multi_grader.py
│   │   │   │   │   │   │   ├── multi_grader_param.py
│   │   │   │   │   │   │   ├── python_grader.py
│   │   │   │   │   │   │   ├── python_grader_param.py
│   │   │   │   │   │   │   ├── score_model_grader.py
│   │   │   │   │   │   │   ├── score_model_grader_param.py
│   │   │   │   │   │   │   ├── string_check_grader.py
│   │   │   │   │   │   │   ├── string_check_grader_param.py
│   │   │   │   │   │   │   ├── text_similarity_grader.py
│   │   │   │   │   │   │   ├── text_similarity_grader_param.py
│   │   │   │   │   │   ├── image.py
│   │   │   │   │   │   ├── image_create_variation_params.py
│   │   │   │   │   │   ├── image_edit_completed_event.py
│   │   │   │   │   │   ├── image_edit_params.py
│   │   │   │   │   │   ├── image_edit_partial_image_event.py
│   │   │   │   │   │   ├── image_edit_stream_event.py
│   │   │   │   │   │   ├── image_gen_completed_event.py
│   │   │   │   │   │   ├── image_gen_partial_image_event.py
│   │   │   │   │   │   ├── image_gen_stream_event.py
│   │   │   │   │   │   ├── image_generate_params.py
│   │   │   │   │   │   ├── image_model.py
│   │   │   │   │   │   ├── images_response.py
│   │   │   │   │   │   ├── model.py
│   │   │   │   │   │   ├── model_deleted.py
│   │   │   │   │   │   ├── moderation.py
│   │   │   │   │   │   ├── moderation_create_params.py
│   │   │   │   │   │   ├── moderation_create_response.py
│   │   │   │   │   │   ├── moderation_image_url_input_param.py
│   │   │   │   │   │   ├── moderation_model.py
│   │   │   │   │   │   ├── moderation_multi_modal_input_param.py
│   │   │   │   │   │   ├── moderation_text_input_param.py
│   │   │   │   │   │   ├── other_file_chunking_strategy_object.py
│   │   │   │   │   │   ├── realtime/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── audio_transcription.py
│   │   │   │   │   │   │   ├── audio_transcription_param.py
│   │   │   │   │   │   │   ├── client_secret_create_params.py
│   │   │   │   │   │   │   ├── client_secret_create_response.py
│   │   │   │   │   │   │   ├── conversation_created_event.py
│   │   │   │   │   │   │   ├── conversation_item.py
│   │   │   │   │   │   │   ├── conversation_item_added.py
│   │   │   │   │   │   │   ├── conversation_item_create_event.py
│   │   │   │   │   │   │   ├── conversation_item_create_event_param.py
│   │   │   │   │   │   │   ├── conversation_item_created_event.py
│   │   │   │   │   │   │   ├── conversation_item_delete_event.py
│   │   │   │   │   │   │   ├── conversation_item_delete_event_param.py
│   │   │   │   │   │   │   ├── conversation_item_deleted_event.py
│   │   │   │   │   │   │   ├── conversation_item_done.py
│   │   │   │   │   │   │   ├── conversation_item_input_audio_transcription_completed_event.py
│   │   │   │   │   │   │   ├── conversation_item_input_audio_transcription_delta_event.py
│   │   │   │   │   │   │   ├── conversation_item_input_audio_transcription_failed_event.py
│   │   │   │   │   │   │   ├── conversation_item_input_audio_transcription_segment.py
│   │   │   │   │   │   │   ├── conversation_item_param.py
│   │   │   │   │   │   │   ├── conversation_item_retrieve_event.py
│   │   │   │   │   │   │   ├── conversation_item_retrieve_event_param.py
│   │   │   │   │   │   │   ├── conversation_item_truncate_event.py
│   │   │   │   │   │   │   ├── conversation_item_truncate_event_param.py
│   │   │   │   │   │   │   ├── conversation_item_truncated_event.py
│   │   │   │   │   │   │   ├── input_audio_buffer_append_event.py
│   │   │   │   │   │   │   ├── input_audio_buffer_append_event_param.py
│   │   │   │   │   │   │   ├── input_audio_buffer_clear_event.py
│   │   │   │   │   │   │   ├── input_audio_buffer_clear_event_param.py
│   │   │   │   │   │   │   ├── input_audio_buffer_cleared_event.py
│   │   │   │   │   │   │   ├── input_audio_buffer_commit_event.py
│   │   │   │   │   │   │   ├── input_audio_buffer_commit_event_param.py
│   │   │   │   │   │   │   ├── input_audio_buffer_committed_event.py
│   │   │   │   │   │   │   ├── input_audio_buffer_speech_started_event.py
│   │   │   │   │   │   │   ├── input_audio_buffer_speech_stopped_event.py
│   │   │   │   │   │   │   ├── input_audio_buffer_timeout_triggered.py
│   │   │   │   │   │   │   ├── log_prob_properties.py
│   │   │   │   │   │   │   ├── mcp_list_tools_completed.py
│   │   │   │   │   │   │   ├── mcp_list_tools_failed.py
│   │   │   │   │   │   │   ├── mcp_list_tools_in_progress.py
│   │   │   │   │   │   │   ├── noise_reduction_type.py
│   │   │   │   │   │   │   ├── output_audio_buffer_clear_event.py
│   │   │   │   │   │   │   ├── output_audio_buffer_clear_event_param.py
│   │   │   │   │   │   │   ├── rate_limits_updated_event.py
│   │   │   │   │   │   │   ├── realtime_audio_config.py
│   │   │   │   │   │   │   ├── realtime_audio_config_input.py
│   │   │   │   │   │   │   ├── realtime_audio_config_input_param.py
│   │   │   │   │   │   │   ├── realtime_audio_config_output.py
│   │   │   │   │   │   │   ├── realtime_audio_config_output_param.py
│   │   │   │   │   │   │   ├── realtime_audio_config_param.py
│   │   │   │   │   │   │   ├── realtime_audio_formats.py
│   │   │   │   │   │   │   ├── realtime_audio_formats_param.py
│   │   │   │   │   │   │   ├── realtime_audio_input_turn_detection.py
│   │   │   │   │   │   │   ├── realtime_audio_input_turn_detection_param.py
│   │   │   │   │   │   │   ├── realtime_client_event.py
│   │   │   │   │   │   │   ├── realtime_client_event_param.py
│   │   │   │   │   │   │   ├── realtime_connect_params.py
│   │   │   │   │   │   │   ├── realtime_conversation_item_assistant_message.py
│   │   │   │   │   │   │   ├── realtime_conversation_item_assistant_message_param.py
│   │   │   │   │   │   │   ├── realtime_conversation_item_function_call.py
│   │   │   │   │   │   │   ├── realtime_conversation_item_function_call_output.py
│   │   │   │   │   │   │   ├── realtime_conversation_item_function_call_output_param.py
│   │   │   │   │   │   │   ├── realtime_conversation_item_function_call_param.py
│   │   │   │   │   │   │   ├── realtime_conversation_item_system_message.py
│   │   │   │   │   │   │   ├── realtime_conversation_item_system_message_param.py
│   │   │   │   │   │   │   ├── realtime_conversation_item_user_message.py
│   │   │   │   │   │   │   ├── realtime_conversation_item_user_message_param.py
│   │   │   │   │   │   │   ├── realtime_error.py
│   │   │   │   │   │   │   ├── realtime_error_event.py
│   │   │   │   │   │   │   ├── realtime_function_tool.py
│   │   │   │   │   │   │   ├── realtime_function_tool_param.py
│   │   │   │   │   │   │   ├── realtime_mcp_approval_request.py
│   │   │   │   │   │   │   ├── realtime_mcp_approval_request_param.py
│   │   │   │   │   │   │   ├── realtime_mcp_approval_response.py
│   │   │   │   │   │   │   ├── realtime_mcp_approval_response_param.py
│   │   │   │   │   │   │   ├── realtime_mcp_list_tools.py
│   │   │   │   │   │   │   ├── realtime_mcp_list_tools_param.py
│   │   │   │   │   │   │   ├── realtime_mcp_protocol_error.py
│   │   │   │   │   │   │   ├── realtime_mcp_protocol_error_param.py
│   │   │   │   │   │   │   ├── realtime_mcp_tool_call.py
│   │   │   │   │   │   │   ├── realtime_mcp_tool_call_param.py
│   │   │   │   │   │   │   ├── realtime_mcp_tool_execution_error.py
│   │   │   │   │   │   │   ├── realtime_mcp_tool_execution_error_param.py
│   │   │   │   │   │   │   ├── realtime_mcphttp_error.py
│   │   │   │   │   │   │   ├── realtime_mcphttp_error_param.py
│   │   │   │   │   │   │   ├── realtime_response.py
│   │   │   │   │   │   │   ├── realtime_response_create_audio_output.py
│   │   │   │   │   │   │   ├── realtime_response_create_audio_output_param.py
│   │   │   │   │   │   │   ├── realtime_response_create_mcp_tool.py
│   │   │   │   │   │   │   ├── realtime_response_create_mcp_tool_param.py
│   │   │   │   │   │   │   ├── realtime_response_create_params.py
│   │   │   │   │   │   │   ├── realtime_response_create_params_param.py
│   │   │   │   │   │   │   ├── realtime_response_status.py
│   │   │   │   │   │   │   ├── realtime_response_usage.py
│   │   │   │   │   │   │   ├── realtime_response_usage_input_token_details.py
│   │   │   │   │   │   │   ├── realtime_response_usage_output_token_details.py
│   │   │   │   │   │   │   ├── realtime_server_event.py
│   │   │   │   │   │   │   ├── realtime_session_client_secret.py
│   │   │   │   │   │   │   ├── realtime_session_create_request.py
│   │   │   │   │   │   │   ├── realtime_session_create_request_param.py
│   │   │   │   │   │   │   ├── realtime_session_create_response.py
│   │   │   │   │   │   │   ├── realtime_tool_choice_config.py
│   │   │   │   │   │   │   ├── realtime_tool_choice_config_param.py
│   │   │   │   │   │   │   ├── realtime_tools_config.py
│   │   │   │   │   │   │   ├── realtime_tools_config_param.py
│   │   │   │   │   │   │   ├── realtime_tools_config_union.py
│   │   │   │   │   │   │   ├── realtime_tools_config_union_param.py
│   │   │   │   │   │   │   ├── realtime_tracing_config.py
│   │   │   │   │   │   │   ├── realtime_tracing_config_param.py
│   │   │   │   │   │   │   ├── realtime_transcription_session_audio.py
│   │   │   │   │   │   │   ├── realtime_transcription_session_audio_input.py
│   │   │   │   │   │   │   ├── realtime_transcription_session_audio_input_param.py
│   │   │   │   │   │   │   ├── realtime_transcription_session_audio_input_turn_detection.py
│   │   │   │   │   │   │   ├── realtime_transcription_session_audio_input_turn_detection_param.py
│   │   │   │   │   │   │   ├── realtime_transcription_session_audio_param.py
│   │   │   │   │   │   │   ├── realtime_transcription_session_create_request.py
│   │   │   │   │   │   │   ├── realtime_transcription_session_create_request_param.py
│   │   │   │   │   │   │   ├── realtime_transcription_session_create_response.py
│   │   │   │   │   │   │   ├── realtime_transcription_session_turn_detection.py
│   │   │   │   │   │   │   ├── realtime_truncation.py
│   │   │   │   │   │   │   ├── realtime_truncation_param.py
│   │   │   │   │   │   │   ├── realtime_truncation_retention_ratio.py
│   │   │   │   │   │   │   ├── realtime_truncation_retention_ratio_param.py
│   │   │   │   │   │   │   ├── response_audio_delta_event.py
│   │   │   │   │   │   │   ├── response_audio_done_event.py
│   │   │   │   │   │   │   ├── response_audio_transcript_delta_event.py
│   │   │   │   │   │   │   ├── response_audio_transcript_done_event.py
│   │   │   │   │   │   │   ├── response_cancel_event.py
│   │   │   │   │   │   │   ├── response_cancel_event_param.py
│   │   │   │   │   │   │   ├── response_content_part_added_event.py
│   │   │   │   │   │   │   ├── response_content_part_done_event.py
│   │   │   │   │   │   │   ├── response_create_event.py
│   │   │   │   │   │   │   ├── response_create_event_param.py
│   │   │   │   │   │   │   ├── response_created_event.py
│   │   │   │   │   │   │   ├── response_done_event.py
│   │   │   │   │   │   │   ├── response_function_call_arguments_delta_event.py
│   │   │   │   │   │   │   ├── response_function_call_arguments_done_event.py
│   │   │   │   │   │   │   ├── response_mcp_call_arguments_delta.py
│   │   │   │   │   │   │   ├── response_mcp_call_arguments_done.py
│   │   │   │   │   │   │   ├── response_mcp_call_completed.py
│   │   │   │   │   │   │   ├── response_mcp_call_failed.py
│   │   │   │   │   │   │   ├── response_mcp_call_in_progress.py
│   │   │   │   │   │   │   ├── response_output_item_added_event.py
│   │   │   │   │   │   │   ├── response_output_item_done_event.py
│   │   │   │   │   │   │   ├── response_text_delta_event.py
│   │   │   │   │   │   │   ├── response_text_done_event.py
│   │   │   │   │   │   │   ├── session_created_event.py
│   │   │   │   │   │   │   ├── session_update_event.py
│   │   │   │   │   │   │   ├── session_update_event_param.py
│   │   │   │   │   │   │   ├── session_updated_event.py
│   │   │   │   │   │   ├── responses/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── computer_tool.py
│   │   │   │   │   │   │   ├── computer_tool_param.py
│   │   │   │   │   │   │   ├── custom_tool.py
│   │   │   │   │   │   │   ├── custom_tool_param.py
│   │   │   │   │   │   │   ├── easy_input_message.py
│   │   │   │   │   │   │   ├── easy_input_message_param.py
│   │   │   │   │   │   │   ├── file_search_tool.py
│   │   │   │   │   │   │   ├── file_search_tool_param.py
│   │   │   │   │   │   │   ├── function_tool.py
│   │   │   │   │   │   │   ├── function_tool_param.py
│   │   │   │   │   │   │   ├── input_item_list_params.py
│   │   │   │   │   │   │   ├── parsed_response.py
│   │   │   │   │   │   │   ├── response.py
│   │   │   │   │   │   │   ├── response_audio_delta_event.py
│   │   │   │   │   │   │   ├── response_audio_done_event.py
│   │   │   │   │   │   │   ├── response_audio_transcript_delta_event.py
│   │   │   │   │   │   │   ├── response_audio_transcript_done_event.py
│   │   │   │   │   │   │   ├── response_code_interpreter_call_code_delta_event.py
│   │   │   │   │   │   │   ├── response_code_interpreter_call_code_done_event.py
│   │   │   │   │   │   │   ├── response_code_interpreter_call_completed_event.py
│   │   │   │   │   │   │   ├── response_code_interpreter_call_in_progress_event.py
│   │   │   │   │   │   │   ├── response_code_interpreter_call_interpreting_event.py
│   │   │   │   │   │   │   ├── response_code_interpreter_tool_call.py
│   │   │   │   │   │   │   ├── response_code_interpreter_tool_call_param.py
│   │   │   │   │   │   │   ├── response_completed_event.py
│   │   │   │   │   │   │   ├── response_computer_tool_call.py
│   │   │   │   │   │   │   ├── response_computer_tool_call_output_item.py
│   │   │   │   │   │   │   ├── response_computer_tool_call_output_screenshot.py
│   │   │   │   │   │   │   ├── response_computer_tool_call_output_screenshot_param.py
│   │   │   │   │   │   │   ├── response_computer_tool_call_param.py
│   │   │   │   │   │   │   ├── response_content_part_added_event.py
│   │   │   │   │   │   │   ├── response_content_part_done_event.py
│   │   │   │   │   │   │   ├── response_conversation_param.py
│   │   │   │   │   │   │   ├── response_create_params.py
│   │   │   │   │   │   │   ├── response_created_event.py
│   │   │   │   │   │   │   ├── response_custom_tool_call.py
│   │   │   │   │   │   │   ├── response_custom_tool_call_input_delta_event.py
│   │   │   │   │   │   │   ├── response_custom_tool_call_input_done_event.py
│   │   │   │   │   │   │   ├── response_custom_tool_call_output.py
│   │   │   │   │   │   │   ├── response_custom_tool_call_output_param.py
│   │   │   │   │   │   │   ├── response_custom_tool_call_param.py
│   │   │   │   │   │   │   ├── response_error.py
│   │   │   │   │   │   │   ├── response_error_event.py
│   │   │   │   │   │   │   ├── response_failed_event.py
│   │   │   │   │   │   │   ├── response_file_search_call_completed_event.py
│   │   │   │   │   │   │   ├── response_file_search_call_in_progress_event.py
│   │   │   │   │   │   │   ├── response_file_search_call_searching_event.py
│   │   │   │   │   │   │   ├── response_file_search_tool_call.py
│   │   │   │   │   │   │   ├── response_file_search_tool_call_param.py
│   │   │   │   │   │   │   ├── response_format_text_config.py
│   │   │   │   │   │   │   ├── response_format_text_config_param.py
│   │   │   │   │   │   │   ├── response_format_text_json_schema_config.py
│   │   │   │   │   │   │   ├── response_format_text_json_schema_config_param.py
│   │   │   │   │   │   │   ├── response_function_call_arguments_delta_event.py
│   │   │   │   │   │   │   ├── response_function_call_arguments_done_event.py
│   │   │   │   │   │   │   ├── response_function_tool_call.py
│   │   │   │   │   │   │   ├── response_function_tool_call_item.py
│   │   │   │   │   │   │   ├── response_function_tool_call_output_item.py
│   │   │   │   │   │   │   ├── response_function_tool_call_param.py
│   │   │   │   │   │   │   ├── response_function_web_search.py
│   │   │   │   │   │   │   ├── response_function_web_search_param.py
│   │   │   │   │   │   │   ├── response_image_gen_call_completed_event.py
│   │   │   │   │   │   │   ├── response_image_gen_call_generating_event.py
│   │   │   │   │   │   │   ├── response_image_gen_call_in_progress_event.py
│   │   │   │   │   │   │   ├── response_image_gen_call_partial_image_event.py
│   │   │   │   │   │   │   ├── response_in_progress_event.py
│   │   │   │   │   │   │   ├── response_includable.py
│   │   │   │   │   │   │   ├── response_incomplete_event.py
│   │   │   │   │   │   │   ├── response_input_audio.py
│   │   │   │   │   │   │   ├── response_input_audio_param.py
│   │   │   │   │   │   │   ├── response_input_content.py
│   │   │   │   │   │   │   ├── response_input_content_param.py
│   │   │   │   │   │   │   ├── response_input_file.py
│   │   │   │   │   │   │   ├── response_input_file_param.py
│   │   │   │   │   │   │   ├── response_input_image.py
│   │   │   │   │   │   │   ├── response_input_image_param.py
│   │   │   │   │   │   │   ├── response_input_item.py
│   │   │   │   │   │   │   ├── response_input_item_param.py
│   │   │   │   │   │   │   ├── response_input_message_content_list.py
│   │   │   │   │   │   │   ├── response_input_message_content_list_param.py
│   │   │   │   │   │   │   ├── response_input_message_item.py
│   │   │   │   │   │   │   ├── response_input_param.py
│   │   │   │   │   │   │   ├── response_input_text.py
│   │   │   │   │   │   │   ├── response_input_text_param.py
│   │   │   │   │   │   │   ├── response_item.py
│   │   │   │   │   │   │   ├── response_item_list.py
│   │   │   │   │   │   │   ├── response_mcp_call_arguments_delta_event.py
│   │   │   │   │   │   │   ├── response_mcp_call_arguments_done_event.py
│   │   │   │   │   │   │   ├── response_mcp_call_completed_event.py
│   │   │   │   │   │   │   ├── response_mcp_call_failed_event.py
│   │   │   │   │   │   │   ├── response_mcp_call_in_progress_event.py
│   │   │   │   │   │   │   ├── response_mcp_list_tools_completed_event.py
│   │   │   │   │   │   │   ├── response_mcp_list_tools_failed_event.py
│   │   │   │   │   │   │   ├── response_mcp_list_tools_in_progress_event.py
│   │   │   │   │   │   │   ├── response_output_item.py
│   │   │   │   │   │   │   ├── response_output_item_added_event.py
│   │   │   │   │   │   │   ├── response_output_item_done_event.py
│   │   │   │   │   │   │   ├── response_output_message.py
│   │   │   │   │   │   │   ├── response_output_message_param.py
│   │   │   │   │   │   │   ├── response_output_refusal.py
│   │   │   │   │   │   │   ├── response_output_refusal_param.py
│   │   │   │   │   │   │   ├── response_output_text.py
│   │   │   │   │   │   │   ├── response_output_text_annotation_added_event.py
│   │   │   │   │   │   │   ├── response_output_text_param.py
│   │   │   │   │   │   │   ├── response_prompt.py
│   │   │   │   │   │   │   ├── response_prompt_param.py
│   │   │   │   │   │   │   ├── response_queued_event.py
│   │   │   │   │   │   │   ├── response_reasoning_item.py
│   │   │   │   │   │   │   ├── response_reasoning_item_param.py
│   │   │   │   │   │   │   ├── response_reasoning_summary_part_added_event.py
│   │   │   │   │   │   │   ├── response_reasoning_summary_part_done_event.py
│   │   │   │   │   │   │   ├── response_reasoning_summary_text_delta_event.py
│   │   │   │   │   │   │   ├── response_reasoning_summary_text_done_event.py
│   │   │   │   │   │   │   ├── response_reasoning_text_delta_event.py
│   │   │   │   │   │   │   ├── response_reasoning_text_done_event.py
│   │   │   │   │   │   │   ├── response_refusal_delta_event.py
│   │   │   │   │   │   │   ├── response_refusal_done_event.py
│   │   │   │   │   │   │   ├── response_retrieve_params.py
│   │   │   │   │   │   │   ├── response_status.py
│   │   │   │   │   │   │   ├── response_stream_event.py
│   │   │   │   │   │   │   ├── response_text_config.py
│   │   │   │   │   │   │   ├── response_text_config_param.py
│   │   │   │   │   │   │   ├── response_text_delta_event.py
│   │   │   │   │   │   │   ├── response_text_done_event.py
│   │   │   │   │   │   │   ├── response_usage.py
│   │   │   │   │   │   │   ├── response_web_search_call_completed_event.py
│   │   │   │   │   │   │   ├── response_web_search_call_in_progress_event.py
│   │   │   │   │   │   │   ├── response_web_search_call_searching_event.py
│   │   │   │   │   │   │   ├── tool.py
│   │   │   │   │   │   │   ├── tool_choice_allowed.py
│   │   │   │   │   │   │   ├── tool_choice_allowed_param.py
│   │   │   │   │   │   │   ├── tool_choice_custom.py
│   │   │   │   │   │   │   ├── tool_choice_custom_param.py
│   │   │   │   │   │   │   ├── tool_choice_function.py
│   │   │   │   │   │   │   ├── tool_choice_function_param.py
│   │   │   │   │   │   │   ├── tool_choice_mcp.py
│   │   │   │   │   │   │   ├── tool_choice_mcp_param.py
│   │   │   │   │   │   │   ├── tool_choice_options.py
│   │   │   │   │   │   │   ├── tool_choice_types.py
│   │   │   │   │   │   │   ├── tool_choice_types_param.py
│   │   │   │   │   │   │   ├── tool_param.py
│   │   │   │   │   │   │   ├── web_search_preview_tool.py
│   │   │   │   │   │   │   ├── web_search_preview_tool_param.py
│   │   │   │   │   │   │   ├── web_search_tool.py
│   │   │   │   │   │   │   ├── web_search_tool_param.py
│   │   │   │   │   │   ├── shared/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── all_models.py
│   │   │   │   │   │   │   ├── chat_model.py
│   │   │   │   │   │   │   ├── comparison_filter.py
│   │   │   │   │   │   │   ├── compound_filter.py
│   │   │   │   │   │   │   ├── custom_tool_input_format.py
│   │   │   │   │   │   │   ├── error_object.py
│   │   │   │   │   │   │   ├── function_definition.py
│   │   │   │   │   │   │   ├── function_parameters.py
│   │   │   │   │   │   │   ├── metadata.py
│   │   │   │   │   │   │   ├── reasoning.py
│   │   │   │   │   │   │   ├── reasoning_effort.py
│   │   │   │   │   │   │   ├── response_format_json_object.py
│   │   │   │   │   │   │   ├── response_format_json_schema.py
│   │   │   │   │   │   │   ├── response_format_text.py
│   │   │   │   │   │   │   ├── response_format_text_grammar.py
│   │   │   │   │   │   │   ├── response_format_text_python.py
│   │   │   │   │   │   │   ├── responses_model.py
│   │   │   │   │   │   ├── shared_params/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── chat_model.py
│   │   │   │   │   │   │   ├── comparison_filter.py
│   │   │   │   │   │   │   ├── compound_filter.py
│   │   │   │   │   │   │   ├── custom_tool_input_format.py
│   │   │   │   │   │   │   ├── function_definition.py
│   │   │   │   │   │   │   ├── function_parameters.py
│   │   │   │   │   │   │   ├── metadata.py
│   │   │   │   │   │   │   ├── reasoning.py
│   │   │   │   │   │   │   ├── reasoning_effort.py
│   │   │   │   │   │   │   ├── response_format_json_object.py
│   │   │   │   │   │   │   ├── response_format_json_schema.py
│   │   │   │   │   │   │   ├── response_format_text.py
│   │   │   │   │   │   │   ├── responses_model.py
│   │   │   │   │   │   ├── static_file_chunking_strategy.py
│   │   │   │   │   │   ├── static_file_chunking_strategy_object.py
│   │   │   │   │   │   ├── static_file_chunking_strategy_object_param.py
│   │   │   │   │   │   ├── static_file_chunking_strategy_param.py
│   │   │   │   │   │   ├── upload.py
│   │   │   │   │   │   ├── upload_complete_params.py
│   │   │   │   │   │   ├── upload_create_params.py
│   │   │   │   │   │   ├── uploads/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── part_create_params.py
│   │   │   │   │   │   │   ├── upload_part.py
│   │   │   │   │   │   ├── vector_store.py
│   │   │   │   │   │   ├── vector_store_create_params.py
│   │   │   │   │   │   ├── vector_store_deleted.py
│   │   │   │   │   │   ├── vector_store_list_params.py
│   │   │   │   │   │   ├── vector_store_search_params.py
│   │   │   │   │   │   ├── vector_store_search_response.py
│   │   │   │   │   │   ├── vector_store_update_params.py
│   │   │   │   │   │   ├── vector_stores/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── file_batch_create_params.py
│   │   │   │   │   │   │   ├── file_batch_list_files_params.py
│   │   │   │   │   │   │   ├── file_content_response.py
│   │   │   │   │   │   │   ├── file_create_params.py
│   │   │   │   │   │   │   ├── file_list_params.py
│   │   │   │   │   │   │   ├── file_update_params.py
│   │   │   │   │   │   │   ├── vector_store_file.py
│   │   │   │   │   │   │   ├── vector_store_file_batch.py
│   │   │   │   │   │   │   ├── vector_store_file_deleted.py
│   │   │   │   │   │   ├── webhooks/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── batch_cancelled_webhook_event.py
│   │   │   │   │   │   │   ├── batch_completed_webhook_event.py
│   │   │   │   │   │   │   ├── batch_expired_webhook_event.py
│   │   │   │   │   │   │   ├── batch_failed_webhook_event.py
│   │   │   │   │   │   │   ├── eval_run_canceled_webhook_event.py
│   │   │   │   │   │   │   ├── eval_run_failed_webhook_event.py
│   │   │   │   │   │   │   ├── eval_run_succeeded_webhook_event.py
│   │   │   │   │   │   │   ├── fine_tuning_job_cancelled_webhook_event.py
│   │   │   │   │   │   │   ├── fine_tuning_job_failed_webhook_event.py
│   │   │   │   │   │   │   ├── fine_tuning_job_succeeded_webhook_event.py
│   │   │   │   │   │   │   ├── realtime_call_incoming_webhook_event.py
│   │   │   │   │   │   │   ├── response_cancelled_webhook_event.py
│   │   │   │   │   │   │   ├── response_completed_webhook_event.py
│   │   │   │   │   │   │   ├── response_failed_webhook_event.py
│   │   │   │   │   │   │   ├── response_incomplete_webhook_event.py
│   │   │   │   │   │   │   ├── unwrap_webhook_event.py
│   │   │   │   │   │   ├── websocket_connection_options.py
│   │   │   │   │   ├── version.py
│   │   │   │   ├── openai-1.108.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── REQUESTED
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   ├── packaging/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _elffile.py
│   │   │   │   │   ├── _manylinux.py
│   │   │   │   │   ├── _musllinux.py
│   │   │   │   │   ├── _parser.py
│   │   │   │   │   ├── _structures.py
│   │   │   │   │   ├── _tokenizer.py
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _spdx.py
│   │   │   │   │   ├── markers.py
│   │   │   │   │   ├── metadata.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── requirements.py
│   │   │   │   │   ├── specifiers.py
│   │   │   │   │   ├── tags.py
│   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── version.py
│   │   │   │   ├── packaging-25.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   ├── LICENSE.APACHE
│   │   │   │   │   │   ├── LICENSE.BSD
│   │   │   │   ├── pip/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __main__.py
│   │   │   │   │   ├── __pip-runner__.py
│   │   │   │   │   ├── _internal/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── build_env.py
│   │   │   │   │   │   ├── cache.py
│   │   │   │   │   │   ├── cli/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── autocompletion.py
│   │   │   │   │   │   │   ├── base_command.py
│   │   │   │   │   │   │   ├── cmdoptions.py
│   │   │   │   │   │   │   ├── command_context.py
│   │   │   │   │   │   │   ├── index_command.py
│   │   │   │   │   │   │   ├── main.py
│   │   │   │   │   │   │   ├── main_parser.py
│   │   │   │   │   │   │   ├── parser.py
│   │   │   │   │   │   │   ├── progress_bars.py
│   │   │   │   │   │   │   ├── req_command.py
│   │   │   │   │   │   │   ├── spinners.py
│   │   │   │   │   │   │   ├── status_codes.py
│   │   │   │   │   │   ├── commands/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── cache.py
│   │   │   │   │   │   │   ├── check.py
│   │   │   │   │   │   │   ├── completion.py
│   │   │   │   │   │   │   ├── configuration.py
│   │   │   │   │   │   │   ├── debug.py
│   │   │   │   │   │   │   ├── download.py
│   │   │   │   │   │   │   ├── freeze.py
│   │   │   │   │   │   │   ├── hash.py
│   │   │   │   │   │   │   ├── help.py
│   │   │   │   │   │   │   ├── index.py
│   │   │   │   │   │   │   ├── inspect.py
│   │   │   │   │   │   │   ├── install.py
│   │   │   │   │   │   │   ├── list.py
│   │   │   │   │   │   │   ├── lock.py
│   │   │   │   │   │   │   ├── search.py
│   │   │   │   │   │   │   ├── show.py
│   │   │   │   │   │   │   ├── uninstall.py
│   │   │   │   │   │   │   ├── wheel.py
│   │   │   │   │   │   ├── configuration.py
│   │   │   │   │   │   ├── distributions/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── base.py
│   │   │   │   │   │   │   ├── installed.py
│   │   │   │   │   │   │   ├── sdist.py
│   │   │   │   │   │   │   ├── wheel.py
│   │   │   │   │   │   ├── exceptions.py
│   │   │   │   │   │   ├── index/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── collector.py
│   │   │   │   │   │   │   ├── package_finder.py
│   │   │   │   │   │   │   ├── sources.py
│   │   │   │   │   │   ├── locations/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _distutils.py
│   │   │   │   │   │   │   ├── _sysconfig.py
│   │   │   │   │   │   │   ├── base.py
│   │   │   │   │   │   ├── main.py
│   │   │   │   │   │   ├── metadata/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _json.py
│   │   │   │   │   │   │   ├── base.py
│   │   │   │   │   │   │   ├── importlib/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── _compat.py
│   │   │   │   │   │   │   │   ├── _dists.py
│   │   │   │   │   │   │   │   ├── _envs.py
│   │   │   │   │   │   │   ├── pkg_resources.py
│   │   │   │   │   │   ├── models/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── candidate.py
│   │   │   │   │   │   │   ├── direct_url.py
│   │   │   │   │   │   │   ├── format_control.py
│   │   │   │   │   │   │   ├── index.py
│   │   │   │   │   │   │   ├── installation_report.py
│   │   │   │   │   │   │   ├── link.py
│   │   │   │   │   │   │   ├── pylock.py
│   │   │   │   │   │   │   ├── scheme.py
│   │   │   │   │   │   │   ├── search_scope.py
│   │   │   │   │   │   │   ├── selection_prefs.py
│   │   │   │   │   │   │   ├── target_python.py
│   │   │   │   │   │   │   ├── wheel.py
│   │   │   │   │   │   ├── network/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── auth.py
│   │   │   │   │   │   │   ├── cache.py
│   │   │   │   │   │   │   ├── download.py
│   │   │   │   │   │   │   ├── lazy_wheel.py
│   │   │   │   │   │   │   ├── session.py
│   │   │   │   │   │   │   ├── utils.py
│   │   │   │   │   │   │   ├── xmlrpc.py
│   │   │   │   │   │   ├── operations/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── build/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── build_tracker.py
│   │   │   │   │   │   │   │   ├── metadata.py
│   │   │   │   │   │   │   │   ├── metadata_editable.py
│   │   │   │   │   │   │   │   ├── metadata_legacy.py
│   │   │   │   │   │   │   │   ├── wheel.py
│   │   │   │   │   │   │   │   ├── wheel_editable.py
│   │   │   │   │   │   │   │   ├── wheel_legacy.py
│   │   │   │   │   │   │   ├── check.py
│   │   │   │   │   │   │   ├── freeze.py
│   │   │   │   │   │   │   ├── install/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── editable_legacy.py
│   │   │   │   │   │   │   │   ├── wheel.py
│   │   │   │   │   │   │   ├── prepare.py
│   │   │   │   │   │   ├── pyproject.py
│   │   │   │   │   │   ├── req/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── constructors.py
│   │   │   │   │   │   │   ├── req_dependency_group.py
│   │   │   │   │   │   │   ├── req_file.py
│   │   │   │   │   │   │   ├── req_install.py
│   │   │   │   │   │   │   ├── req_set.py
│   │   │   │   │   │   │   ├── req_uninstall.py
│   │   │   │   │   │   ├── resolution/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── base.py
│   │   │   │   │   │   │   ├── legacy/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── resolver.py
│   │   │   │   │   │   │   ├── resolvelib/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── base.py
│   │   │   │   │   │   │   │   ├── candidates.py
│   │   │   │   │   │   │   │   ├── factory.py
│   │   │   │   │   │   │   │   ├── found_candidates.py
│   │   │   │   │   │   │   │   ├── provider.py
│   │   │   │   │   │   │   │   ├── reporter.py
│   │   │   │   │   │   │   │   ├── requirements.py
│   │   │   │   │   │   │   │   ├── resolver.py
│   │   │   │   │   │   ├── self_outdated_check.py
│   │   │   │   │   │   ├── vcs/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── bazaar.py
│   │   │   │   │   │   │   ├── git.py
│   │   │   │   │   │   │   ├── mercurial.py
│   │   │   │   │   │   │   ├── subversion.py
│   │   │   │   │   │   │   ├── versioncontrol.py
│   │   │   │   │   │   ├── wheel_builder.py
│   │   │   │   │   ├── _vendor/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── cachecontrol/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _cmd.py
│   │   │   │   │   │   │   ├── adapter.py
│   │   │   │   │   │   │   ├── cache.py
│   │   │   │   │   │   │   ├── caches/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── file_cache.py
│   │   │   │   │   │   │   │   ├── redis_cache.py
│   │   │   │   │   │   │   ├── controller.py
│   │   │   │   │   │   │   ├── filewrapper.py
│   │   │   │   │   │   │   ├── heuristics.py
│   │   │   │   │   │   │   ├── py.typed
│   │   │   │   │   │   │   ├── serialize.py
│   │   │   │   │   │   │   ├── wrapper.py
│   │   │   │   │   │   ├── certifi/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── __main__.py
│   │   │   │   │   │   │   ├── cacert.pem
│   │   │   │   │   │   │   ├── core.py
│   │   │   │   │   │   │   ├── py.typed
│   │   │   │   │   │   ├── dependency_groups/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── __main__.py
│   │   │   │   │   │   │   ├── _implementation.py
│   │   │   │   │   │   │   ├── _lint_dependency_groups.py
│   │   │   │   │   │   │   ├── _pip_wrapper.py
│   │   │   │   │   │   │   ├── _toml_compat.py
│   │   │   │   │   │   │   ├── py.typed
│   │   │   │   │   │   ├── distlib/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── compat.py
│   │   │   │   │   │   │   ├── resources.py
│   │   │   │   │   │   │   ├── scripts.py
│   │   │   │   │   │   │   ├── t32.exe
│   │   │   │   │   │   │   ├── t64-arm.exe
│   │   │   │   │   │   │   ├── t64.exe
│   │   │   │   │   │   │   ├── util.py
│   │   │   │   │   │   │   ├── w32.exe
│   │   │   │   │   │   │   ├── w64-arm.exe
│   │   │   │   │   │   │   ├── w64.exe
│   │   │   │   │   │   ├── distro/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── __main__.py
│   │   │   │   │   │   │   ├── distro.py
│   │   │   │   │   │   │   ├── py.typed
│   │   │   │   │   │   ├── idna/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── codec.py
│   │   │   │   │   │   │   ├── compat.py
│   │   │   │   │   │   │   ├── core.py
│   │   │   │   │   │   │   ├── idnadata.py
│   │   │   │   │   │   │   ├── intranges.py
│   │   │   │   │   │   │   ├── package_data.py
│   │   │   │   │   │   │   ├── py.typed
│   │   │   │   │   │   │   ├── uts46data.py
│   │   │   │   │   │   ├── msgpack/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── exceptions.py
│   │   │   │   │   │   │   ├── ext.py
│   │   │   │   │   │   │   ├── fallback.py
│   │   │   │   │   │   ├── packaging/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _elffile.py
│   │   │   │   │   │   │   ├── _manylinux.py
│   │   │   │   │   │   │   ├── _musllinux.py
│   │   │   │   │   │   │   ├── _parser.py
│   │   │   │   │   │   │   ├── _structures.py
│   │   │   │   │   │   │   ├── _tokenizer.py
│   │   │   │   │   │   │   ├── licenses/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── _spdx.py
│   │   │   │   │   │   │   ├── markers.py
│   │   │   │   │   │   │   ├── metadata.py
│   │   │   │   │   │   │   ├── py.typed
│   │   │   │   │   │   │   ├── requirements.py
│   │   │   │   │   │   │   ├── specifiers.py
│   │   │   │   │   │   │   ├── tags.py
│   │   │   │   │   │   │   ├── utils.py
│   │   │   │   │   │   │   ├── version.py
│   │   │   │   │   │   ├── pkg_resources/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── platformdirs/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── __main__.py
│   │   │   │   │   │   │   ├── android.py
│   │   │   │   │   │   │   ├── api.py
│   │   │   │   │   │   │   ├── macos.py
│   │   │   │   │   │   │   ├── py.typed
│   │   │   │   │   │   │   ├── unix.py
│   │   │   │   │   │   │   ├── version.py
│   │   │   │   │   │   │   ├── windows.py
│   │   │   │   │   │   ├── pygments/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── __main__.py
│   │   │   │   │   │   │   ├── console.py
│   │   │   │   │   │   │   ├── filter.py
│   │   │   │   │   │   │   ├── filters/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── formatter.py
│   │   │   │   │   │   │   ├── formatters/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── _mapping.py
│   │   │   │   │   │   │   ├── lexer.py
│   │   │   │   │   │   │   ├── lexers/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── _mapping.py
│   │   │   │   │   │   │   │   ├── python.py
│   │   │   │   │   │   │   ├── modeline.py
│   │   │   │   │   │   │   ├── plugin.py
│   │   │   │   │   │   │   ├── regexopt.py
│   │   │   │   │   │   │   ├── scanner.py
│   │   │   │   │   │   │   ├── sphinxext.py
│   │   │   │   │   │   │   ├── style.py
│   │   │   │   │   │   │   ├── styles/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── _mapping.py
│   │   │   │   │   │   │   ├── token.py
│   │   │   │   │   │   │   ├── unistring.py
│   │   │   │   │   │   │   ├── util.py
│   │   │   │   │   │   ├── pyproject_hooks/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _impl.py
│   │   │   │   │   │   │   ├── _in_process/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── _in_process.py
│   │   │   │   │   │   │   ├── py.typed
│   │   │   │   │   │   ├── requests/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── __version__.py
│   │   │   │   │   │   │   ├── _internal_utils.py
│   │   │   │   │   │   │   ├── adapters.py
│   │   │   │   │   │   │   ├── api.py
│   │   │   │   │   │   │   ├── auth.py
│   │   │   │   │   │   │   ├── certs.py
│   │   │   │   │   │   │   ├── compat.py
│   │   │   │   │   │   │   ├── cookies.py
│   │   │   │   │   │   │   ├── exceptions.py
│   │   │   │   │   │   │   ├── help.py
│   │   │   │   │   │   │   ├── hooks.py
│   │   │   │   │   │   │   ├── models.py
│   │   │   │   │   │   │   ├── packages.py
│   │   │   │   │   │   │   ├── sessions.py
│   │   │   │   │   │   │   ├── status_codes.py
│   │   │   │   │   │   │   ├── structures.py
│   │   │   │   │   │   │   ├── utils.py
│   │   │   │   │   │   ├── resolvelib/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── providers.py
│   │   │   │   │   │   │   ├── py.typed
│   │   │   │   │   │   │   ├── reporters.py
│   │   │   │   │   │   │   ├── resolvers/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── abstract.py
│   │   │   │   │   │   │   │   ├── criterion.py
│   │   │   │   │   │   │   │   ├── exceptions.py
│   │   │   │   │   │   │   │   ├── resolution.py
│   │   │   │   │   │   │   ├── structs.py
│   │   │   │   │   │   ├── rich/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── __main__.py
│   │   │   │   │   │   │   ├── _cell_widths.py
│   │   │   │   │   │   │   ├── _emoji_codes.py
│   │   │   │   │   │   │   ├── _emoji_replace.py
│   │   │   │   │   │   │   ├── _export_format.py
│   │   │   │   │   │   │   ├── _extension.py
│   │   │   │   │   │   │   ├── _fileno.py
│   │   │   │   │   │   │   ├── _inspect.py
│   │   │   │   │   │   │   ├── _log_render.py
│   │   │   │   │   │   │   ├── _loop.py
│   │   │   │   │   │   │   ├── _null_file.py
│   │   │   │   │   │   │   ├── _palettes.py
│   │   │   │   │   │   │   ├── _pick.py
│   │   │   │   │   │   │   ├── _ratio.py
│   │   │   │   │   │   │   ├── _spinners.py
│   │   │   │   │   │   │   ├── _stack.py
│   │   │   │   │   │   │   ├── _timer.py
│   │   │   │   │   │   │   ├── _win32_console.py
│   │   │   │   │   │   │   ├── _windows.py
│   │   │   │   │   │   │   ├── _windows_renderer.py
│   │   │   │   │   │   │   ├── _wrap.py
│   │   │   │   │   │   │   ├── abc.py
│   │   │   │   │   │   │   ├── align.py
│   │   │   │   │   │   │   ├── ansi.py
│   │   │   │   │   │   │   ├── bar.py
│   │   │   │   │   │   │   ├── box.py
│   │   │   │   │   │   │   ├── cells.py
│   │   │   │   │   │   │   ├── color.py
│   │   │   │   │   │   │   ├── color_triplet.py
│   │   │   │   │   │   │   ├── columns.py
│   │   │   │   │   │   │   ├── console.py
│   │   │   │   │   │   │   ├── constrain.py
│   │   │   │   │   │   │   ├── containers.py
│   │   │   │   │   │   │   ├── control.py
│   │   │   │   │   │   │   ├── default_styles.py
│   │   │   │   │   │   │   ├── diagnose.py
│   │   │   │   │   │   │   ├── emoji.py
│   │   │   │   │   │   │   ├── errors.py
│   │   │   │   │   │   │   ├── file_proxy.py
│   │   │   │   │   │   │   ├── filesize.py
│   │   │   │   │   │   │   ├── highlighter.py
│   │   │   │   │   │   │   ├── json.py
│   │   │   │   │   │   │   ├── jupyter.py
│   │   │   │   │   │   │   ├── layout.py
│   │   │   │   │   │   │   ├── live.py
│   │   │   │   │   │   │   ├── live_render.py
│   │   │   │   │   │   │   ├── logging.py
│   │   │   │   │   │   │   ├── markup.py
│   │   │   │   │   │   │   ├── measure.py
│   │   │   │   │   │   │   ├── padding.py
│   │   │   │   │   │   │   ├── pager.py
│   │   │   │   │   │   │   ├── palette.py
│   │   │   │   │   │   │   ├── panel.py
│   │   │   │   │   │   │   ├── pretty.py
│   │   │   │   │   │   │   ├── progress.py
│   │   │   │   │   │   │   ├── progress_bar.py
│   │   │   │   │   │   │   ├── prompt.py
│   │   │   │   │   │   │   ├── protocol.py
│   │   │   │   │   │   │   ├── py.typed
│   │   │   │   │   │   │   ├── region.py
│   │   │   │   │   │   │   ├── repr.py
│   │   │   │   │   │   │   ├── rule.py
│   │   │   │   │   │   │   ├── scope.py
│   │   │   │   │   │   │   ├── screen.py
│   │   │   │   │   │   │   ├── segment.py
│   │   │   │   │   │   │   ├── spinner.py
│   │   │   │   │   │   │   ├── status.py
│   │   │   │   │   │   │   ├── style.py
│   │   │   │   │   │   │   ├── styled.py
│   │   │   │   │   │   │   ├── syntax.py
│   │   │   │   │   │   │   ├── table.py
│   │   │   │   │   │   │   ├── terminal_theme.py
│   │   │   │   │   │   │   ├── text.py
│   │   │   │   │   │   │   ├── theme.py
│   │   │   │   │   │   │   ├── themes.py
│   │   │   │   │   │   │   ├── traceback.py
│   │   │   │   │   │   │   ├── tree.py
│   │   │   │   │   │   ├── tomli/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _parser.py
│   │   │   │   │   │   │   ├── _re.py
│   │   │   │   │   │   │   ├── _types.py
│   │   │   │   │   │   │   ├── py.typed
│   │   │   │   │   │   ├── tomli_w/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _writer.py
│   │   │   │   │   │   │   ├── py.typed
│   │   │   │   │   │   ├── truststore/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _api.py
│   │   │   │   │   │   │   ├── _macos.py
│   │   │   │   │   │   │   ├── _openssl.py
│   │   │   │   │   │   │   ├── _ssl_constants.py
│   │   │   │   │   │   │   ├── _windows.py
│   │   │   │   │   │   │   ├── py.typed
│   │   │   │   │   │   ├── urllib3/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _collections.py
│   │   │   │   │   │   │   ├── _version.py
│   │   │   │   │   │   │   ├── connection.py
│   │   │   │   │   │   │   ├── connectionpool.py
│   │   │   │   │   │   │   ├── contrib/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── _appengine_environ.py
│   │   │   │   │   │   │   │   ├── _securetransport/
│   │   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   │   ├── bindings.py
│   │   │   │   │   │   │   │   │   ├── low_level.py
│   │   │   │   │   │   │   │   ├── appengine.py
│   │   │   │   │   │   │   │   ├── ntlmpool.py
│   │   │   │   │   │   │   │   ├── pyopenssl.py
│   │   │   │   │   │   │   │   ├── securetransport.py
│   │   │   │   │   │   │   │   ├── socks.py
│   │   │   │   │   │   │   ├── exceptions.py
│   │   │   │   │   │   │   ├── fields.py
│   │   │   │   │   │   │   ├── filepost.py
│   │   │   │   │   │   │   ├── packages/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── backports/
│   │   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   │   ├── makefile.py
│   │   │   │   │   │   │   │   │   ├── weakref_finalize.py
│   │   │   │   │   │   │   │   ├── six.py
│   │   │   │   │   │   │   ├── poolmanager.py
│   │   │   │   │   │   │   ├── request.py
│   │   │   │   │   │   │   ├── response.py
│   │   │   │   │   │   │   ├── util/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   │   ├── connection.py
│   │   │   │   │   │   │   │   ├── proxy.py
│   │   │   │   │   │   │   │   ├── queue.py
│   │   │   │   │   │   │   │   ├── request.py
│   │   │   │   │   │   │   │   ├── response.py
│   │   │   │   │   │   │   │   ├── retry.py
│   │   │   │   │   │   │   │   ├── ssl_.py
│   │   │   │   │   │   │   │   ├── ssl_match_hostname.py
│   │   │   │   │   │   │   │   ├── ssltransport.py
│   │   │   │   │   │   │   │   ├── timeout.py
│   │   │   │   │   │   │   │   ├── url.py
│   │   │   │   │   │   │   │   ├── wait.py
│   │   │   │   │   │   ├── vendor.txt
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── pip-25.2.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── REQUESTED
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── AUTHORS.txt
│   │   │   │   │   │   ├── LICENSE.txt
│   │   │   │   │   │   ├── src/
│   │   │   │   │   │   │   ├── pip/
│   │   │   │   │   │   │   │   ├── _vendor/
│   │   │   │   │   │   │   │   │   ├── cachecontrol/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE.txt
│   │   │   │   │   │   │   │   │   ├── certifi/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   │   │   │   ├── dependency_groups/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE.txt
│   │   │   │   │   │   │   │   │   ├── distlib/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE.txt
│   │   │   │   │   │   │   │   │   ├── distro/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   │   │   │   ├── idna/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE.md
│   │   │   │   │   │   │   │   │   ├── msgpack/
│   │   │   │   │   │   │   │   │   │   ├── COPYING
│   │   │   │   │   │   │   │   │   ├── packaging/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   │   │   │   │   ├── LICENSE.APACHE
│   │   │   │   │   │   │   │   │   │   ├── LICENSE.BSD
│   │   │   │   │   │   │   │   │   ├── pkg_resources/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   │   │   │   ├── platformdirs/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   │   │   │   ├── pygments/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   │   │   │   ├── pyproject_hooks/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   │   │   │   ├── requests/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   │   │   │   ├── resolvelib/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   │   │   │   ├── rich/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   │   │   │   ├── tomli/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   │   │   │   │   ├── LICENSE-HEADER
│   │   │   │   │   │   │   │   │   ├── tomli_w/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   │   │   │   ├── truststore/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   │   │   │   │   ├── urllib3/
│   │   │   │   │   │   │   │   │   │   ├── LICENSE.txt
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── pkg_resources/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _vendor/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── appdirs.py
│   │   │   │   │   │   ├── importlib_resources/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _adapters.py
│   │   │   │   │   │   │   ├── _common.py
│   │   │   │   │   │   │   ├── _compat.py
│   │   │   │   │   │   │   ├── _itertools.py
│   │   │   │   │   │   │   ├── _legacy.py
│   │   │   │   │   │   │   ├── abc.py
│   │   │   │   │   │   │   ├── readers.py
│   │   │   │   │   │   │   ├── simple.py
│   │   │   │   │   │   ├── jaraco/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── context.py
│   │   │   │   │   │   │   ├── functools.py
│   │   │   │   │   │   │   ├── text/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── more_itertools/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── more.py
│   │   │   │   │   │   │   ├── recipes.py
│   │   │   │   │   │   ├── packaging/
│   │   │   │   │   │   │   ├── __about__.py
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _manylinux.py
│   │   │   │   │   │   │   ├── _musllinux.py
│   │   │   │   │   │   │   ├── _structures.py
│   │   │   │   │   │   │   ├── markers.py
│   │   │   │   │   │   │   ├── requirements.py
│   │   │   │   │   │   │   ├── specifiers.py
│   │   │   │   │   │   │   ├── tags.py
│   │   │   │   │   │   │   ├── utils.py
│   │   │   │   │   │   │   ├── version.py
│   │   │   │   │   │   ├── pyparsing/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── actions.py
│   │   │   │   │   │   │   ├── common.py
│   │   │   │   │   │   │   ├── core.py
│   │   │   │   │   │   │   ├── diagram/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── exceptions.py
│   │   │   │   │   │   │   ├── helpers.py
│   │   │   │   │   │   │   ├── results.py
│   │   │   │   │   │   │   ├── testing.py
│   │   │   │   │   │   │   ├── unicode.py
│   │   │   │   │   │   │   ├── util.py
│   │   │   │   │   │   ├── zipp.py
│   │   │   │   │   ├── extern/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   ├── pluggy/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _callers.py
│   │   │   │   │   ├── _hooks.py
│   │   │   │   │   ├── _manager.py
│   │   │   │   │   ├── _result.py
│   │   │   │   │   ├── _tracing.py
│   │   │   │   │   ├── _version.py
│   │   │   │   │   ├── _warnings.py
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── pluggy-1.6.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── postgrest/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _async/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── client.py
│   │   │   │   │   │   ├── request_builder.py
│   │   │   │   │   ├── _sync/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── client.py
│   │   │   │   │   │   ├── request_builder.py
│   │   │   │   │   ├── base_client.py
│   │   │   │   │   ├── base_request_builder.py
│   │   │   │   │   ├── constants.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── types.py
│   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── version.py
│   │   │   │   ├── postgrest-2.19.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   ├── py.py
│   │   │   │   ├── pycparser/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _ast_gen.py
│   │   │   │   │   ├── _build_tables.py
│   │   │   │   │   ├── _c_ast.cfg
│   │   │   │   │   ├── ast_transforms.py
│   │   │   │   │   ├── c_ast.py
│   │   │   │   │   ├── c_generator.py
│   │   │   │   │   ├── c_lexer.py
│   │   │   │   │   ├── c_parser.py
│   │   │   │   │   ├── lextab.py
│   │   │   │   │   ├── ply/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── cpp.py
│   │   │   │   │   │   ├── ctokens.py
│   │   │   │   │   │   ├── lex.py
│   │   │   │   │   │   ├── yacc.py
│   │   │   │   │   │   ├── ygen.py
│   │   │   │   │   ├── plyparser.py
│   │   │   │   │   ├── yacctab.py
│   │   │   │   ├── pycparser-2.23.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── pydantic/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _internal/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _config.py
│   │   │   │   │   │   ├── _core_metadata.py
│   │   │   │   │   │   ├── _core_utils.py
│   │   │   │   │   │   ├── _dataclasses.py
│   │   │   │   │   │   ├── _decorators.py
│   │   │   │   │   │   ├── _decorators_v1.py
│   │   │   │   │   │   ├── _discriminated_union.py
│   │   │   │   │   │   ├── _docs_extraction.py
│   │   │   │   │   │   ├── _fields.py
│   │   │   │   │   │   ├── _forward_ref.py
│   │   │   │   │   │   ├── _generate_schema.py
│   │   │   │   │   │   ├── _generics.py
│   │   │   │   │   │   ├── _git.py
│   │   │   │   │   │   ├── _import_utils.py
│   │   │   │   │   │   ├── _internal_dataclass.py
│   │   │   │   │   │   ├── _known_annotated_metadata.py
│   │   │   │   │   │   ├── _mock_val_ser.py
│   │   │   │   │   │   ├── _model_construction.py
│   │   │   │   │   │   ├── _namespace_utils.py
│   │   │   │   │   │   ├── _repr.py
│   │   │   │   │   │   ├── _schema_gather.py
│   │   │   │   │   │   ├── _schema_generation_shared.py
│   │   │   │   │   │   ├── _serializers.py
│   │   │   │   │   │   ├── _signature.py
│   │   │   │   │   │   ├── _typing_extra.py
│   │   │   │   │   │   ├── _utils.py
│   │   │   │   │   │   ├── _validate_call.py
│   │   │   │   │   │   ├── _validators.py
│   │   │   │   │   ├── _migration.py
│   │   │   │   │   ├── alias_generators.py
│   │   │   │   │   ├── aliases.py
│   │   │   │   │   ├── annotated_handlers.py
│   │   │   │   │   ├── class_validators.py
│   │   │   │   │   ├── color.py
│   │   │   │   │   ├── config.py
│   │   │   │   │   ├── dataclasses.py
│   │   │   │   │   ├── datetime_parse.py
│   │   │   │   │   ├── decorator.py
│   │   │   │   │   ├── deprecated/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── class_validators.py
│   │   │   │   │   │   ├── config.py
│   │   │   │   │   │   ├── copy_internals.py
│   │   │   │   │   │   ├── decorator.py
│   │   │   │   │   │   ├── json.py
│   │   │   │   │   │   ├── parse.py
│   │   │   │   │   │   ├── tools.py
│   │   │   │   │   ├── env_settings.py
│   │   │   │   │   ├── error_wrappers.py
│   │   │   │   │   ├── errors.py
│   │   │   │   │   ├── experimental/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── arguments_schema.py
│   │   │   │   │   │   ├── pipeline.py
│   │   │   │   │   ├── fields.py
│   │   │   │   │   ├── functional_serializers.py
│   │   │   │   │   ├── functional_validators.py
│   │   │   │   │   ├── generics.py
│   │   │   │   │   ├── json.py
│   │   │   │   │   ├── json_schema.py
│   │   │   │   │   ├── main.py
│   │   │   │   │   ├── mypy.py
│   │   │   │   │   ├── networks.py
│   │   │   │   │   ├── parse.py
│   │   │   │   │   ├── plugin/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _loader.py
│   │   │   │   │   │   ├── _schema_validator.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── root_model.py
│   │   │   │   │   ├── schema.py
│   │   │   │   │   ├── tools.py
│   │   │   │   │   ├── type_adapter.py
│   │   │   │   │   ├── types.py
│   │   │   │   │   ├── typing.py
│   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── v1/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _hypothesis_plugin.py
│   │   │   │   │   │   ├── annotated_types.py
│   │   │   │   │   │   ├── class_validators.py
│   │   │   │   │   │   ├── color.py
│   │   │   │   │   │   ├── config.py
│   │   │   │   │   │   ├── dataclasses.py
│   │   │   │   │   │   ├── datetime_parse.py
│   │   │   │   │   │   ├── decorator.py
│   │   │   │   │   │   ├── env_settings.py
│   │   │   │   │   │   ├── error_wrappers.py
│   │   │   │   │   │   ├── errors.py
│   │   │   │   │   │   ├── fields.py
│   │   │   │   │   │   ├── generics.py
│   │   │   │   │   │   ├── json.py
│   │   │   │   │   │   ├── main.py
│   │   │   │   │   │   ├── mypy.py
│   │   │   │   │   │   ├── networks.py
│   │   │   │   │   │   ├── parse.py
│   │   │   │   │   │   ├── py.typed
│   │   │   │   │   │   ├── schema.py
│   │   │   │   │   │   ├── tools.py
│   │   │   │   │   │   ├── types.py
│   │   │   │   │   │   ├── typing.py
│   │   │   │   │   │   ├── utils.py
│   │   │   │   │   │   ├── validators.py
│   │   │   │   │   │   ├── version.py
│   │   │   │   │   ├── validate_call_decorator.py
│   │   │   │   │   ├── validators.py
│   │   │   │   │   ├── version.py
│   │   │   │   │   ├── warnings.py
│   │   │   │   ├── pydantic-2.11.9.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   ├── pydantic_core/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _pydantic_core.cpython-311-darwin.so
│   │   │   │   │   ├── _pydantic_core.pyi
│   │   │   │   │   ├── core_schema.py
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── pydantic_core-2.33.2.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   ├── pygments/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __main__.py
│   │   │   │   │   ├── cmdline.py
│   │   │   │   │   ├── console.py
│   │   │   │   │   ├── filter.py
│   │   │   │   │   ├── filters/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── formatter.py
│   │   │   │   │   ├── formatters/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _mapping.py
│   │   │   │   │   │   ├── bbcode.py
│   │   │   │   │   │   ├── groff.py
│   │   │   │   │   │   ├── html.py
│   │   │   │   │   │   ├── img.py
│   │   │   │   │   │   ├── irc.py
│   │   │   │   │   │   ├── latex.py
│   │   │   │   │   │   ├── other.py
│   │   │   │   │   │   ├── pangomarkup.py
│   │   │   │   │   │   ├── rtf.py
│   │   │   │   │   │   ├── svg.py
│   │   │   │   │   │   ├── terminal.py
│   │   │   │   │   │   ├── terminal256.py
│   │   │   │   │   ├── lexer.py
│   │   │   │   │   ├── lexers/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _ada_builtins.py
│   │   │   │   │   │   ├── _asy_builtins.py
│   │   │   │   │   │   ├── _cl_builtins.py
│   │   │   │   │   │   ├── _cocoa_builtins.py
│   │   │   │   │   │   ├── _csound_builtins.py
│   │   │   │   │   │   ├── _css_builtins.py
│   │   │   │   │   │   ├── _googlesql_builtins.py
│   │   │   │   │   │   ├── _julia_builtins.py
│   │   │   │   │   │   ├── _lasso_builtins.py
│   │   │   │   │   │   ├── _lilypond_builtins.py
│   │   │   │   │   │   ├── _lua_builtins.py
│   │   │   │   │   │   ├── _luau_builtins.py
│   │   │   │   │   │   ├── _mapping.py
│   │   │   │   │   │   ├── _mql_builtins.py
│   │   │   │   │   │   ├── _mysql_builtins.py
│   │   │   │   │   │   ├── _openedge_builtins.py
│   │   │   │   │   │   ├── _php_builtins.py
│   │   │   │   │   │   ├── _postgres_builtins.py
│   │   │   │   │   │   ├── _qlik_builtins.py
│   │   │   │   │   │   ├── _scheme_builtins.py
│   │   │   │   │   │   ├── _scilab_builtins.py
│   │   │   │   │   │   ├── _sourcemod_builtins.py
│   │   │   │   │   │   ├── _sql_builtins.py
│   │   │   │   │   │   ├── _stan_builtins.py
│   │   │   │   │   │   ├── _stata_builtins.py
│   │   │   │   │   │   ├── _tsql_builtins.py
│   │   │   │   │   │   ├── _usd_builtins.py
│   │   │   │   │   │   ├── _vbscript_builtins.py
│   │   │   │   │   │   ├── _vim_builtins.py
│   │   │   │   │   │   ├── actionscript.py
│   │   │   │   │   │   ├── ada.py
│   │   │   │   │   │   ├── agile.py
│   │   │   │   │   │   ├── algebra.py
│   │   │   │   │   │   ├── ambient.py
│   │   │   │   │   │   ├── amdgpu.py
│   │   │   │   │   │   ├── ampl.py
│   │   │   │   │   │   ├── apdlexer.py
│   │   │   │   │   │   ├── apl.py
│   │   │   │   │   │   ├── archetype.py
│   │   │   │   │   │   ├── arrow.py
│   │   │   │   │   │   ├── arturo.py
│   │   │   │   │   │   ├── asc.py
│   │   │   │   │   │   ├── asm.py
│   │   │   │   │   │   ├── asn1.py
│   │   │   │   │   │   ├── automation.py
│   │   │   │   │   │   ├── bare.py
│   │   │   │   │   │   ├── basic.py
│   │   │   │   │   │   ├── bdd.py
│   │   │   │   │   │   ├── berry.py
│   │   │   │   │   │   ├── bibtex.py
│   │   │   │   │   │   ├── blueprint.py
│   │   │   │   │   │   ├── boa.py
│   │   │   │   │   │   ├── bqn.py
│   │   │   │   │   │   ├── business.py
│   │   │   │   │   │   ├── c_cpp.py
│   │   │   │   │   │   ├── c_like.py
│   │   │   │   │   │   ├── capnproto.py
│   │   │   │   │   │   ├── carbon.py
│   │   │   │   │   │   ├── cddl.py
│   │   │   │   │   │   ├── chapel.py
│   │   │   │   │   │   ├── clean.py
│   │   │   │   │   │   ├── codeql.py
│   │   │   │   │   │   ├── comal.py
│   │   │   │   │   │   ├── compiled.py
│   │   │   │   │   │   ├── configs.py
│   │   │   │   │   │   ├── console.py
│   │   │   │   │   │   ├── cplint.py
│   │   │   │   │   │   ├── crystal.py
│   │   │   │   │   │   ├── csound.py
│   │   │   │   │   │   ├── css.py
│   │   │   │   │   │   ├── d.py
│   │   │   │   │   │   ├── dalvik.py
│   │   │   │   │   │   ├── data.py
│   │   │   │   │   │   ├── dax.py
│   │   │   │   │   │   ├── devicetree.py
│   │   │   │   │   │   ├── diff.py
│   │   │   │   │   │   ├── dns.py
│   │   │   │   │   │   ├── dotnet.py
│   │   │   │   │   │   ├── dsls.py
│   │   │   │   │   │   ├── dylan.py
│   │   │   │   │   │   ├── ecl.py
│   │   │   │   │   │   ├── eiffel.py
│   │   │   │   │   │   ├── elm.py
│   │   │   │   │   │   ├── elpi.py
│   │   │   │   │   │   ├── email.py
│   │   │   │   │   │   ├── erlang.py
│   │   │   │   │   │   ├── esoteric.py
│   │   │   │   │   │   ├── ezhil.py
│   │   │   │   │   │   ├── factor.py
│   │   │   │   │   │   ├── fantom.py
│   │   │   │   │   │   ├── felix.py
│   │   │   │   │   │   ├── fift.py
│   │   │   │   │   │   ├── floscript.py
│   │   │   │   │   │   ├── forth.py
│   │   │   │   │   │   ├── fortran.py
│   │   │   │   │   │   ├── foxpro.py
│   │   │   │   │   │   ├── freefem.py
│   │   │   │   │   │   ├── func.py
│   │   │   │   │   │   ├── functional.py
│   │   │   │   │   │   ├── futhark.py
│   │   │   │   │   │   ├── gcodelexer.py
│   │   │   │   │   │   ├── gdscript.py
│   │   │   │   │   │   ├── gleam.py
│   │   │   │   │   │   ├── go.py
│   │   │   │   │   │   ├── grammar_notation.py
│   │   │   │   │   │   ├── graph.py
│   │   │   │   │   │   ├── graphics.py
│   │   │   │   │   │   ├── graphql.py
│   │   │   │   │   │   ├── graphviz.py
│   │   │   │   │   │   ├── gsql.py
│   │   │   │   │   │   ├── hare.py
│   │   │   │   │   │   ├── haskell.py
│   │   │   │   │   │   ├── haxe.py
│   │   │   │   │   │   ├── hdl.py
│   │   │   │   │   │   ├── hexdump.py
│   │   │   │   │   │   ├── html.py
│   │   │   │   │   │   ├── idl.py
│   │   │   │   │   │   ├── igor.py
│   │   │   │   │   │   ├── inferno.py
│   │   │   │   │   │   ├── installers.py
│   │   │   │   │   │   ├── int_fiction.py
│   │   │   │   │   │   ├── iolang.py
│   │   │   │   │   │   ├── j.py
│   │   │   │   │   │   ├── javascript.py
│   │   │   │   │   │   ├── jmespath.py
│   │   │   │   │   │   ├── jslt.py
│   │   │   │   │   │   ├── json5.py
│   │   │   │   │   │   ├── jsonnet.py
│   │   │   │   │   │   ├── jsx.py
│   │   │   │   │   │   ├── julia.py
│   │   │   │   │   │   ├── jvm.py
│   │   │   │   │   │   ├── kuin.py
│   │   │   │   │   │   ├── kusto.py
│   │   │   │   │   │   ├── ldap.py
│   │   │   │   │   │   ├── lean.py
│   │   │   │   │   │   ├── lilypond.py
│   │   │   │   │   │   ├── lisp.py
│   │   │   │   │   │   ├── macaulay2.py
│   │   │   │   │   │   ├── make.py
│   │   │   │   │   │   ├── maple.py
│   │   │   │   │   │   ├── markup.py
│   │   │   │   │   │   ├── math.py
│   │   │   │   │   │   ├── matlab.py
│   │   │   │   │   │   ├── maxima.py
│   │   │   │   │   │   ├── meson.py
│   │   │   │   │   │   ├── mime.py
│   │   │   │   │   │   ├── minecraft.py
│   │   │   │   │   │   ├── mips.py
│   │   │   │   │   │   ├── ml.py
│   │   │   │   │   │   ├── modeling.py
│   │   │   │   │   │   ├── modula2.py
│   │   │   │   │   │   ├── mojo.py
│   │   │   │   │   │   ├── monte.py
│   │   │   │   │   │   ├── mosel.py
│   │   │   │   │   │   ├── ncl.py
│   │   │   │   │   │   ├── nimrod.py
│   │   │   │   │   │   ├── nit.py
│   │   │   │   │   │   ├── nix.py
│   │   │   │   │   │   ├── numbair.py
│   │   │   │   │   │   ├── oberon.py
│   │   │   │   │   │   ├── objective.py
│   │   │   │   │   │   ├── ooc.py
│   │   │   │   │   │   ├── openscad.py
│   │   │   │   │   │   ├── other.py
│   │   │   │   │   │   ├── parasail.py
│   │   │   │   │   │   ├── parsers.py
│   │   │   │   │   │   ├── pascal.py
│   │   │   │   │   │   ├── pawn.py
│   │   │   │   │   │   ├── pddl.py
│   │   │   │   │   │   ├── perl.py
│   │   │   │   │   │   ├── phix.py
│   │   │   │   │   │   ├── php.py
│   │   │   │   │   │   ├── pointless.py
│   │   │   │   │   │   ├── pony.py
│   │   │   │   │   │   ├── praat.py
│   │   │   │   │   │   ├── procfile.py
│   │   │   │   │   │   ├── prolog.py
│   │   │   │   │   │   ├── promql.py
│   │   │   │   │   │   ├── prql.py
│   │   │   │   │   │   ├── ptx.py
│   │   │   │   │   │   ├── python.py
│   │   │   │   │   │   ├── q.py
│   │   │   │   │   │   ├── qlik.py
│   │   │   │   │   │   ├── qvt.py
│   │   │   │   │   │   ├── r.py
│   │   │   │   │   │   ├── rdf.py
│   │   │   │   │   │   ├── rebol.py
│   │   │   │   │   │   ├── rego.py
│   │   │   │   │   │   ├── resource.py
│   │   │   │   │   │   ├── ride.py
│   │   │   │   │   │   ├── rita.py
│   │   │   │   │   │   ├── rnc.py
│   │   │   │   │   │   ├── roboconf.py
│   │   │   │   │   │   ├── robotframework.py
│   │   │   │   │   │   ├── ruby.py
│   │   │   │   │   │   ├── rust.py
│   │   │   │   │   │   ├── sas.py
│   │   │   │   │   │   ├── savi.py
│   │   │   │   │   │   ├── scdoc.py
│   │   │   │   │   │   ├── scripting.py
│   │   │   │   │   │   ├── sgf.py
│   │   │   │   │   │   ├── shell.py
│   │   │   │   │   │   ├── sieve.py
│   │   │   │   │   │   ├── slash.py
│   │   │   │   │   │   ├── smalltalk.py
│   │   │   │   │   │   ├── smithy.py
│   │   │   │   │   │   ├── smv.py
│   │   │   │   │   │   ├── snobol.py
│   │   │   │   │   │   ├── solidity.py
│   │   │   │   │   │   ├── soong.py
│   │   │   │   │   │   ├── sophia.py
│   │   │   │   │   │   ├── special.py
│   │   │   │   │   │   ├── spice.py
│   │   │   │   │   │   ├── sql.py
│   │   │   │   │   │   ├── srcinfo.py
│   │   │   │   │   │   ├── stata.py
│   │   │   │   │   │   ├── supercollider.py
│   │   │   │   │   │   ├── tablegen.py
│   │   │   │   │   │   ├── tact.py
│   │   │   │   │   │   ├── tal.py
│   │   │   │   │   │   ├── tcl.py
│   │   │   │   │   │   ├── teal.py
│   │   │   │   │   │   ├── templates.py
│   │   │   │   │   │   ├── teraterm.py
│   │   │   │   │   │   ├── testing.py
│   │   │   │   │   │   ├── text.py
│   │   │   │   │   │   ├── textedit.py
│   │   │   │   │   │   ├── textfmts.py
│   │   │   │   │   │   ├── theorem.py
│   │   │   │   │   │   ├── thingsdb.py
│   │   │   │   │   │   ├── tlb.py
│   │   │   │   │   │   ├── tls.py
│   │   │   │   │   │   ├── tnt.py
│   │   │   │   │   │   ├── trafficscript.py
│   │   │   │   │   │   ├── typoscript.py
│   │   │   │   │   │   ├── typst.py
│   │   │   │   │   │   ├── ul4.py
│   │   │   │   │   │   ├── unicon.py
│   │   │   │   │   │   ├── urbi.py
│   │   │   │   │   │   ├── usd.py
│   │   │   │   │   │   ├── varnish.py
│   │   │   │   │   │   ├── verification.py
│   │   │   │   │   │   ├── verifpal.py
│   │   │   │   │   │   ├── vip.py
│   │   │   │   │   │   ├── vyper.py
│   │   │   │   │   │   ├── web.py
│   │   │   │   │   │   ├── webassembly.py
│   │   │   │   │   │   ├── webidl.py
│   │   │   │   │   │   ├── webmisc.py
│   │   │   │   │   │   ├── wgsl.py
│   │   │   │   │   │   ├── whiley.py
│   │   │   │   │   │   ├── wowtoc.py
│   │   │   │   │   │   ├── wren.py
│   │   │   │   │   │   ├── x10.py
│   │   │   │   │   │   ├── xorg.py
│   │   │   │   │   │   ├── yang.py
│   │   │   │   │   │   ├── yara.py
│   │   │   │   │   │   ├── zig.py
│   │   │   │   │   ├── modeline.py
│   │   │   │   │   ├── plugin.py
│   │   │   │   │   ├── regexopt.py
│   │   │   │   │   ├── scanner.py
│   │   │   │   │   ├── sphinxext.py
│   │   │   │   │   ├── style.py
│   │   │   │   │   ├── styles/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _mapping.py
│   │   │   │   │   │   ├── abap.py
│   │   │   │   │   │   ├── algol.py
│   │   │   │   │   │   ├── algol_nu.py
│   │   │   │   │   │   ├── arduino.py
│   │   │   │   │   │   ├── autumn.py
│   │   │   │   │   │   ├── borland.py
│   │   │   │   │   │   ├── bw.py
│   │   │   │   │   │   ├── coffee.py
│   │   │   │   │   │   ├── colorful.py
│   │   │   │   │   │   ├── default.py
│   │   │   │   │   │   ├── dracula.py
│   │   │   │   │   │   ├── emacs.py
│   │   │   │   │   │   ├── friendly.py
│   │   │   │   │   │   ├── friendly_grayscale.py
│   │   │   │   │   │   ├── fruity.py
│   │   │   │   │   │   ├── gh_dark.py
│   │   │   │   │   │   ├── gruvbox.py
│   │   │   │   │   │   ├── igor.py
│   │   │   │   │   │   ├── inkpot.py
│   │   │   │   │   │   ├── lightbulb.py
│   │   │   │   │   │   ├── lilypond.py
│   │   │   │   │   │   ├── lovelace.py
│   │   │   │   │   │   ├── manni.py
│   │   │   │   │   │   ├── material.py
│   │   │   │   │   │   ├── monokai.py
│   │   │   │   │   │   ├── murphy.py
│   │   │   │   │   │   ├── native.py
│   │   │   │   │   │   ├── nord.py
│   │   │   │   │   │   ├── onedark.py
│   │   │   │   │   │   ├── paraiso_dark.py
│   │   │   │   │   │   ├── paraiso_light.py
│   │   │   │   │   │   ├── pastie.py
│   │   │   │   │   │   ├── perldoc.py
│   │   │   │   │   │   ├── rainbow_dash.py
│   │   │   │   │   │   ├── rrt.py
│   │   │   │   │   │   ├── sas.py
│   │   │   │   │   │   ├── solarized.py
│   │   │   │   │   │   ├── staroffice.py
│   │   │   │   │   │   ├── stata_dark.py
│   │   │   │   │   │   ├── stata_light.py
│   │   │   │   │   │   ├── tango.py
│   │   │   │   │   │   ├── trac.py
│   │   │   │   │   │   ├── vim.py
│   │   │   │   │   │   ├── vs.py
│   │   │   │   │   │   ├── xcode.py
│   │   │   │   │   │   ├── zenburn.py
│   │   │   │   │   ├── token.py
│   │   │   │   │   ├── unistring.py
│   │   │   │   │   ├── util.py
│   │   │   │   ├── pygments-2.19.2.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── AUTHORS
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   ├── pytest/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __main__.py
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── pytest-8.4.2.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── REQUESTED
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── AUTHORS
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── python_dateutil-2.9.0.post0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── REQUESTED
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── top_level.txt
│   │   │   │   │   ├── zip-safe
│   │   │   │   ├── python_dotenv-1.1.1.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── REQUESTED
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── realtime/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _async/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── channel.py
│   │   │   │   │   │   ├── client.py
│   │   │   │   │   │   ├── presence.py
│   │   │   │   │   │   ├── push.py
│   │   │   │   │   │   ├── timer.py
│   │   │   │   │   ├── _sync/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── channel.py
│   │   │   │   │   │   ├── client.py
│   │   │   │   │   │   ├── presence.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── message.py
│   │   │   │   │   ├── transformers.py
│   │   │   │   │   ├── types.py
│   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── version.py
│   │   │   │   ├── realtime-2.19.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   ├── requests/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __version__.py
│   │   │   │   │   ├── _internal_utils.py
│   │   │   │   │   ├── adapters.py
│   │   │   │   │   ├── api.py
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── certs.py
│   │   │   │   │   ├── compat.py
│   │   │   │   │   ├── cookies.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── help.py
│   │   │   │   │   ├── hooks.py
│   │   │   │   │   ├── models.py
│   │   │   │   │   ├── packages.py
│   │   │   │   │   ├── sessions.py
│   │   │   │   │   ├── status_codes.py
│   │   │   │   │   ├── structures.py
│   │   │   │   │   ├── utils.py
│   │   │   │   ├── requests-2.32.5.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── REQUESTED
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── setuptools/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _deprecation_warning.py
│   │   │   │   │   ├── _distutils/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _collections.py
│   │   │   │   │   │   ├── _functools.py
│   │   │   │   │   │   ├── _macos_compat.py
│   │   │   │   │   │   ├── _msvccompiler.py
│   │   │   │   │   │   ├── archive_util.py
│   │   │   │   │   │   ├── bcppcompiler.py
│   │   │   │   │   │   ├── ccompiler.py
│   │   │   │   │   │   ├── cmd.py
│   │   │   │   │   │   ├── command/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _framework_compat.py
│   │   │   │   │   │   │   ├── bdist.py
│   │   │   │   │   │   │   ├── bdist_dumb.py
│   │   │   │   │   │   │   ├── bdist_rpm.py
│   │   │   │   │   │   │   ├── build.py
│   │   │   │   │   │   │   ├── build_clib.py
│   │   │   │   │   │   │   ├── build_ext.py
│   │   │   │   │   │   │   ├── build_py.py
│   │   │   │   │   │   │   ├── build_scripts.py
│   │   │   │   │   │   │   ├── check.py
│   │   │   │   │   │   │   ├── clean.py
│   │   │   │   │   │   │   ├── config.py
│   │   │   │   │   │   │   ├── install.py
│   │   │   │   │   │   │   ├── install_data.py
│   │   │   │   │   │   │   ├── install_egg_info.py
│   │   │   │   │   │   │   ├── install_headers.py
│   │   │   │   │   │   │   ├── install_lib.py
│   │   │   │   │   │   │   ├── install_scripts.py
│   │   │   │   │   │   │   ├── py37compat.py
│   │   │   │   │   │   │   ├── register.py
│   │   │   │   │   │   │   ├── sdist.py
│   │   │   │   │   │   │   ├── upload.py
│   │   │   │   │   │   ├── config.py
│   │   │   │   │   │   ├── core.py
│   │   │   │   │   │   ├── cygwinccompiler.py
│   │   │   │   │   │   ├── debug.py
│   │   │   │   │   │   ├── dep_util.py
│   │   │   │   │   │   ├── dir_util.py
│   │   │   │   │   │   ├── dist.py
│   │   │   │   │   │   ├── errors.py
│   │   │   │   │   │   ├── extension.py
│   │   │   │   │   │   ├── fancy_getopt.py
│   │   │   │   │   │   ├── file_util.py
│   │   │   │   │   │   ├── filelist.py
│   │   │   │   │   │   ├── log.py
│   │   │   │   │   │   ├── msvc9compiler.py
│   │   │   │   │   │   ├── msvccompiler.py
│   │   │   │   │   │   ├── py38compat.py
│   │   │   │   │   │   ├── py39compat.py
│   │   │   │   │   │   ├── spawn.py
│   │   │   │   │   │   ├── sysconfig.py
│   │   │   │   │   │   ├── text_file.py
│   │   │   │   │   │   ├── unixccompiler.py
│   │   │   │   │   │   ├── util.py
│   │   │   │   │   │   ├── version.py
│   │   │   │   │   │   ├── versionpredicate.py
│   │   │   │   │   ├── _entry_points.py
│   │   │   │   │   ├── _imp.py
│   │   │   │   │   ├── _importlib.py
│   │   │   │   │   ├── _itertools.py
│   │   │   │   │   ├── _path.py
│   │   │   │   │   ├── _reqs.py
│   │   │   │   │   ├── _vendor/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── importlib_metadata/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _adapters.py
│   │   │   │   │   │   │   ├── _collections.py
│   │   │   │   │   │   │   ├── _compat.py
│   │   │   │   │   │   │   ├── _functools.py
│   │   │   │   │   │   │   ├── _itertools.py
│   │   │   │   │   │   │   ├── _meta.py
│   │   │   │   │   │   │   ├── _text.py
│   │   │   │   │   │   ├── importlib_resources/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _adapters.py
│   │   │   │   │   │   │   ├── _common.py
│   │   │   │   │   │   │   ├── _compat.py
│   │   │   │   │   │   │   ├── _itertools.py
│   │   │   │   │   │   │   ├── _legacy.py
│   │   │   │   │   │   │   ├── abc.py
│   │   │   │   │   │   │   ├── readers.py
│   │   │   │   │   │   │   ├── simple.py
│   │   │   │   │   │   ├── jaraco/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── context.py
│   │   │   │   │   │   │   ├── functools.py
│   │   │   │   │   │   │   ├── text/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── more_itertools/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── more.py
│   │   │   │   │   │   │   ├── recipes.py
│   │   │   │   │   │   ├── ordered_set.py
│   │   │   │   │   │   ├── packaging/
│   │   │   │   │   │   │   ├── __about__.py
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _manylinux.py
│   │   │   │   │   │   │   ├── _musllinux.py
│   │   │   │   │   │   │   ├── _structures.py
│   │   │   │   │   │   │   ├── markers.py
│   │   │   │   │   │   │   ├── requirements.py
│   │   │   │   │   │   │   ├── specifiers.py
│   │   │   │   │   │   │   ├── tags.py
│   │   │   │   │   │   │   ├── utils.py
│   │   │   │   │   │   │   ├── version.py
│   │   │   │   │   │   ├── pyparsing/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── actions.py
│   │   │   │   │   │   │   ├── common.py
│   │   │   │   │   │   │   ├── core.py
│   │   │   │   │   │   │   ├── diagram/
│   │   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── exceptions.py
│   │   │   │   │   │   │   ├── helpers.py
│   │   │   │   │   │   │   ├── results.py
│   │   │   │   │   │   │   ├── testing.py
│   │   │   │   │   │   │   ├── unicode.py
│   │   │   │   │   │   │   ├── util.py
│   │   │   │   │   │   ├── tomli/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── _parser.py
│   │   │   │   │   │   │   ├── _re.py
│   │   │   │   │   │   │   ├── _types.py
│   │   │   │   │   │   ├── typing_extensions.py
│   │   │   │   │   │   ├── zipp.py
│   │   │   │   │   ├── archive_util.py
│   │   │   │   │   ├── build_meta.py
│   │   │   │   │   ├── cli-32.exe
│   │   │   │   │   ├── cli-64.exe
│   │   │   │   │   ├── cli-arm64.exe
│   │   │   │   │   ├── cli.exe
│   │   │   │   │   ├── command/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── alias.py
│   │   │   │   │   │   ├── bdist_egg.py
│   │   │   │   │   │   ├── bdist_rpm.py
│   │   │   │   │   │   ├── build.py
│   │   │   │   │   │   ├── build_clib.py
│   │   │   │   │   │   ├── build_ext.py
│   │   │   │   │   │   ├── build_py.py
│   │   │   │   │   │   ├── develop.py
│   │   │   │   │   │   ├── dist_info.py
│   │   │   │   │   │   ├── easy_install.py
│   │   │   │   │   │   ├── editable_wheel.py
│   │   │   │   │   │   ├── egg_info.py
│   │   │   │   │   │   ├── install.py
│   │   │   │   │   │   ├── install_egg_info.py
│   │   │   │   │   │   ├── install_lib.py
│   │   │   │   │   │   ├── install_scripts.py
│   │   │   │   │   │   ├── launcher manifest.xml
│   │   │   │   │   │   ├── py36compat.py
│   │   │   │   │   │   ├── register.py
│   │   │   │   │   │   ├── rotate.py
│   │   │   │   │   │   ├── saveopts.py
│   │   │   │   │   │   ├── sdist.py
│   │   │   │   │   │   ├── setopt.py
│   │   │   │   │   │   ├── test.py
│   │   │   │   │   │   ├── upload.py
│   │   │   │   │   │   ├── upload_docs.py
│   │   │   │   │   ├── config/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── _apply_pyprojecttoml.py
│   │   │   │   │   │   ├── _validate_pyproject/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── error_reporting.py
│   │   │   │   │   │   │   ├── extra_validations.py
│   │   │   │   │   │   │   ├── fastjsonschema_exceptions.py
│   │   │   │   │   │   │   ├── fastjsonschema_validations.py
│   │   │   │   │   │   │   ├── formats.py
│   │   │   │   │   │   ├── expand.py
│   │   │   │   │   │   ├── pyprojecttoml.py
│   │   │   │   │   │   ├── setupcfg.py
│   │   │   │   │   ├── dep_util.py
│   │   │   │   │   ├── depends.py
│   │   │   │   │   ├── discovery.py
│   │   │   │   │   ├── dist.py
│   │   │   │   │   ├── errors.py
│   │   │   │   │   ├── extension.py
│   │   │   │   │   ├── extern/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── glob.py
│   │   │   │   │   ├── gui-32.exe
│   │   │   │   │   ├── gui-64.exe
│   │   │   │   │   ├── gui-arm64.exe
│   │   │   │   │   ├── gui.exe
│   │   │   │   │   ├── installer.py
│   │   │   │   │   ├── launch.py
│   │   │   │   │   ├── logging.py
│   │   │   │   │   ├── monkey.py
│   │   │   │   │   ├── msvc.py
│   │   │   │   │   ├── namespaces.py
│   │   │   │   │   ├── package_index.py
│   │   │   │   │   ├── py34compat.py
│   │   │   │   │   ├── sandbox.py
│   │   │   │   │   ├── script (dev).tmpl
│   │   │   │   │   ├── script.tmpl
│   │   │   │   │   ├── unicode_utils.py
│   │   │   │   │   ├── version.py
│   │   │   │   │   ├── wheel.py
│   │   │   │   │   ├── windows_support.py
│   │   │   │   ├── setuptools-65.5.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── REQUESTED
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── sgmllib.py
│   │   │   │   ├── sgmllib3k-1.0.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── six-1.17.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── six.py
│   │   │   │   ├── sniffio/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _impl.py
│   │   │   │   │   ├── _tests/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── test_sniffio.py
│   │   │   │   │   ├── _version.py
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── sniffio-1.3.1.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── LICENSE.APACHE2
│   │   │   │   │   ├── LICENSE.MIT
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── soupsieve/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __meta__.py
│   │   │   │   │   ├── css_match.py
│   │   │   │   │   ├── css_parser.py
│   │   │   │   │   ├── css_types.py
│   │   │   │   │   ├── pretty.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── util.py
│   │   │   │   ├── soupsieve-2.8.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE.md
│   │   │   │   ├── storage3/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _async/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── bucket.py
│   │   │   │   │   │   ├── client.py
│   │   │   │   │   │   ├── file_api.py
│   │   │   │   │   ├── _sync/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── bucket.py
│   │   │   │   │   │   ├── client.py
│   │   │   │   │   │   ├── file_api.py
│   │   │   │   │   ├── constants.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── types.py
│   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── version.py
│   │   │   │   ├── storage3-2.19.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   ├── strenum/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __init__.pyi
│   │   │   │   │   ├── _name_mangler.py
│   │   │   │   │   ├── _name_mangler.pyi
│   │   │   │   │   ├── _version.py
│   │   │   │   │   ├── mixins.py
│   │   │   │   │   ├── mixins.pyi
│   │   │   │   │   ├── py.typed
│   │   │   │   ├── supabase/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _async/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── auth_client.py
│   │   │   │   │   │   ├── client.py
│   │   │   │   │   ├── _sync/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── auth_client.py
│   │   │   │   │   │   ├── client.py
│   │   │   │   │   ├── client.py
│   │   │   │   │   ├── lib/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── client_options.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── types.py
│   │   │   │   │   ├── version.py
│   │   │   │   ├── supabase-2.19.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── REQUESTED
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   ├── supabase_auth/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _async/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── gotrue_admin_api.py
│   │   │   │   │   │   ├── gotrue_admin_mfa_api.py
│   │   │   │   │   │   ├── gotrue_base_api.py
│   │   │   │   │   │   ├── gotrue_client.py
│   │   │   │   │   │   ├── gotrue_mfa_api.py
│   │   │   │   │   │   ├── storage.py
│   │   │   │   │   ├── _sync/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── gotrue_admin_api.py
│   │   │   │   │   │   ├── gotrue_admin_mfa_api.py
│   │   │   │   │   │   ├── gotrue_base_api.py
│   │   │   │   │   │   ├── gotrue_client.py
│   │   │   │   │   │   ├── gotrue_mfa_api.py
│   │   │   │   │   │   ├── storage.py
│   │   │   │   │   ├── constants.py
│   │   │   │   │   ├── errors.py
│   │   │   │   │   ├── helpers.py
│   │   │   │   │   ├── http_clients.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── timer.py
│   │   │   │   │   ├── types.py
│   │   │   │   │   ├── version.py
│   │   │   │   ├── supabase_auth-2.19.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   ├── supabase_functions/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _async/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── functions_client.py
│   │   │   │   │   ├── _sync/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── functions_client.py
│   │   │   │   │   ├── errors.py
│   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── version.py
│   │   │   │   ├── supabase_functions-2.19.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   ├── tqdm/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __main__.py
│   │   │   │   │   ├── _dist_ver.py
│   │   │   │   │   ├── _main.py
│   │   │   │   │   ├── _monitor.py
│   │   │   │   │   ├── _tqdm.py
│   │   │   │   │   ├── _tqdm_gui.py
│   │   │   │   │   ├── _tqdm_notebook.py
│   │   │   │   │   ├── _tqdm_pandas.py
│   │   │   │   │   ├── _utils.py
│   │   │   │   │   ├── asyncio.py
│   │   │   │   │   ├── auto.py
│   │   │   │   │   ├── autonotebook.py
│   │   │   │   │   ├── cli.py
│   │   │   │   │   ├── completion.sh
│   │   │   │   │   ├── contrib/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── bells.py
│   │   │   │   │   │   ├── concurrent.py
│   │   │   │   │   │   ├── discord.py
│   │   │   │   │   │   ├── itertools.py
│   │   │   │   │   │   ├── logging.py
│   │   │   │   │   │   ├── slack.py
│   │   │   │   │   │   ├── telegram.py
│   │   │   │   │   │   ├── utils_worker.py
│   │   │   │   │   ├── dask.py
│   │   │   │   │   ├── gui.py
│   │   │   │   │   ├── keras.py
│   │   │   │   │   ├── notebook.py
│   │   │   │   │   ├── rich.py
│   │   │   │   │   ├── std.py
│   │   │   │   │   ├── tk.py
│   │   │   │   │   ├── tqdm.1
│   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── version.py
│   │   │   │   ├── tqdm-4.67.1.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENCE
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── typing_extensions-4.15.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   ├── typing_extensions.py
│   │   │   │   ├── typing_inspection/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── introspection.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── typing_objects.py
│   │   │   │   │   ├── typing_objects.pyi
│   │   │   │   ├── typing_inspection-0.4.1.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE
│   │   │   │   ├── urllib3/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _base_connection.py
│   │   │   │   │   ├── _collections.py
│   │   │   │   │   ├── _request_methods.py
│   │   │   │   │   ├── _version.py
│   │   │   │   │   ├── connection.py
│   │   │   │   │   ├── connectionpool.py
│   │   │   │   │   ├── contrib/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── emscripten/
│   │   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   │   ├── connection.py
│   │   │   │   │   │   │   ├── emscripten_fetch_worker.js
│   │   │   │   │   │   │   ├── fetch.py
│   │   │   │   │   │   │   ├── request.py
│   │   │   │   │   │   │   ├── response.py
│   │   │   │   │   │   ├── pyopenssl.py
│   │   │   │   │   │   ├── socks.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── fields.py
│   │   │   │   │   ├── filepost.py
│   │   │   │   │   ├── http2/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── connection.py
│   │   │   │   │   │   ├── probe.py
│   │   │   │   │   ├── poolmanager.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── response.py
│   │   │   │   │   ├── util/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── connection.py
│   │   │   │   │   │   ├── proxy.py
│   │   │   │   │   │   ├── request.py
│   │   │   │   │   │   ├── response.py
│   │   │   │   │   │   ├── retry.py
│   │   │   │   │   │   ├── ssl_.py
│   │   │   │   │   │   ├── ssl_match_hostname.py
│   │   │   │   │   │   ├── ssltransport.py
│   │   │   │   │   │   ├── timeout.py
│   │   │   │   │   │   ├── url.py
│   │   │   │   │   │   ├── util.py
│   │   │   │   │   │   ├── wait.py
│   │   │   │   ├── urllib3-2.5.0.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── licenses/
│   │   │   │   │   │   ├── LICENSE.txt
│   │   │   │   ├── websockets/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── __main__.py
│   │   │   │   │   ├── asyncio/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── async_timeout.py
│   │   │   │   │   │   ├── client.py
│   │   │   │   │   │   ├── compatibility.py
│   │   │   │   │   │   ├── connection.py
│   │   │   │   │   │   ├── messages.py
│   │   │   │   │   │   ├── router.py
│   │   │   │   │   │   ├── server.py
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── cli.py
│   │   │   │   │   ├── client.py
│   │   │   │   │   ├── connection.py
│   │   │   │   │   ├── datastructures.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── extensions/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── base.py
│   │   │   │   │   │   ├── permessage_deflate.py
│   │   │   │   │   ├── frames.py
│   │   │   │   │   ├── headers.py
│   │   │   │   │   ├── http.py
│   │   │   │   │   ├── http11.py
│   │   │   │   │   ├── imports.py
│   │   │   │   │   ├── legacy/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── auth.py
│   │   │   │   │   │   ├── client.py
│   │   │   │   │   │   ├── exceptions.py
│   │   │   │   │   │   ├── framing.py
│   │   │   │   │   │   ├── handshake.py
│   │   │   │   │   │   ├── http.py
│   │   │   │   │   │   ├── protocol.py
│   │   │   │   │   │   ├── server.py
│   │   │   │   │   ├── protocol.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── server.py
│   │   │   │   │   ├── speedups.c
│   │   │   │   │   ├── speedups.cpython-311-darwin.so
│   │   │   │   │   ├── speedups.pyi
│   │   │   │   │   ├── streams.py
│   │   │   │   │   ├── sync/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── client.py
│   │   │   │   │   │   ├── connection.py
│   │   │   │   │   │   ├── messages.py
│   │   │   │   │   │   ├── router.py
│   │   │   │   │   │   ├── server.py
│   │   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── typing.py
│   │   │   │   │   ├── uri.py
│   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── version.py
│   │   │   │   ├── websockets-15.0.1.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   │   │   │   │   ├── entry_points.txt
│   │   │   │   │   ├── top_level.txt
│   │   │   │   ├── werkzeug/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── _internal.py
│   │   │   │   │   ├── _reloader.py
│   │   │   │   │   ├── datastructures/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── accept.py
│   │   │   │   │   │   ├── auth.py
│   │   │   │   │   │   ├── cache_control.py
│   │   │   │   │   │   ├── csp.py
│   │   │   │   │   │   ├── etag.py
│   │   │   │   │   │   ├── file_storage.py
│   │   │   │   │   │   ├── headers.py
│   │   │   │   │   │   ├── mixins.py
│   │   │   │   │   │   ├── range.py
│   │   │   │   │   │   ├── structures.py
│   │   │   │   │   ├── debug/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── console.py
│   │   │   │   │   │   ├── repr.py
│   │   │   │   │   │   ├── shared/
│   │   │   │   │   │   │   ├── ICON_LICENSE.md
│   │   │   │   │   │   │   ├── console.png
│   │   │   │   │   │   │   ├── debugger.js
│   │   │   │   │   │   │   ├── less.png
│   │   │   │   │   │   │   ├── more.png
│   │   │   │   │   │   │   ├── style.css
│   │   │   │   │   │   ├── tbtools.py
│   │   │   │   │   ├── exceptions.py
│   │   │   │   │   ├── formparser.py
│   │   │   │   │   ├── http.py
│   │   │   │   │   ├── local.py
│   │   │   │   │   ├── middleware/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── dispatcher.py
│   │   │   │   │   │   ├── http_proxy.py
│   │   │   │   │   │   ├── lint.py
│   │   │   │   │   │   ├── profiler.py
│   │   │   │   │   │   ├── proxy_fix.py
│   │   │   │   │   │   ├── shared_data.py
│   │   │   │   │   ├── py.typed
│   │   │   │   │   ├── routing/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── converters.py
│   │   │   │   │   │   ├── exceptions.py
│   │   │   │   │   │   ├── map.py
│   │   │   │   │   │   ├── matcher.py
│   │   │   │   │   │   ├── rules.py
│   │   │   │   │   ├── sansio/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── http.py
│   │   │   │   │   │   ├── multipart.py
│   │   │   │   │   │   ├── request.py
│   │   │   │   │   │   ├── response.py
│   │   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── security.py
│   │   │   │   │   ├── serving.py
│   │   │   │   │   ├── test.py
│   │   │   │   │   ├── testapp.py
│   │   │   │   │   ├── urls.py
│   │   │   │   │   ├── user_agent.py
│   │   │   │   │   ├── utils.py
│   │   │   │   │   ├── wrappers/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── request.py
│   │   │   │   │   │   ├── response.py
│   │   │   │   │   ├── wsgi.py
│   │   │   │   ├── werkzeug-3.1.3.dist-info/
│   │   │   │   │   ├── INSTALLER
│   │   │   │   │   ├── LICENSE.txt
│   │   │   │   │   ├── METADATA
│   │   │   │   │   ├── RECORD
│   │   │   │   │   ├── WHEEL
│   ├── pyvenv.cfg
├── webapp.py
```
