from contextlib import _RedirectStream, redirect_stderr, redirect_stdout
from unittest.mock import patch

import os
import tempfile
import unittest

import brittle

URL = [
    "https://github.com/_123",
    "https://github.com",
    "https://microsoft.com",
    "https://nginx.org/404"
]

class CheckAndPrintTest(unittest.IsolatedAsyncioTestCase):
    @patch('brittle.check')
    async def test_check_and_print(self, check):
        expected = [
            "https://github.com/_123",
            "https://nginx.org/404"
        ]

        check.return_value = expected.copy()

        config = brittle.Config()

        with tempfile.NamedTemporaryFile("w+", encoding="utf-8") as output:
            await brittle.check_and_print(URL, output, config)
            output.flush()
            output.seek(0)
            actual = output.read()
            self.assertEqual(actual, "\n".join(expected) + "\n")

class MainTest(unittest.TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as input:
            input.write("\n".join(URL))
        self.input = input

    def tearDown(self):
        os.unlink(self.input.name)

    @patch('brittle.check_and_print')
    def test_urls_arg(self, check_and_print):
        args = [self.input.name]
        brittle.main(args)

        check_and_print.assert_called_once()

        urls = check_and_print.call_args.args[0]

        self.assertEqual(urls, URL)

    @patch('brittle.check')
    def test_output_option(self, check):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as output:
            pass

        expected = [
            "https://github.com/_123",
            "https://nginx.org/404"
        ]

        check.return_value = expected.copy()

        args = [self.input.name, "--output", output.name]
        brittle.main(args)

        check.assert_called_once()

        with open(output.name, "r", encoding="utf-8") as result:
            self.assertEqual(result.read(), "\n".join(expected) + "\n")

        os.unlink(output.name)

    @patch('brittle.check_and_print')
    def test_delay_option(self, check_and_print):
        delay = "1.7"
        args = [self.input.name, "--delay", delay]
        brittle.main(args)

        check_and_print.assert_called_once()

        config = check_and_print.call_args.args[2]

        self.assertEqual(config.delay, 1.7)

    @patch('brittle.check_and_print')
    def test_timeout_option(self, check_and_print):
        timeout = "0"
        args = [self.input.name, "--timeout", timeout]
        brittle.main(args)

        check_and_print.assert_called_once()

        config = check_and_print.call_args.args[2]

        self.assertEqual(config.timeout, 0)

        check_and_print.reset_mock()

        timeout = "5"
        args = [self.input.name, "--timeout", timeout]
        brittle.main(args)

        check_and_print.assert_called_once()

        config = check_and_print.call_args.args[2]

        self.assertEqual(config.timeout, 5000)

    @patch('brittle.check_and_print')
    def test_workers_option(self, check_and_print):
        workers = "0"
        args = [self.input.name, "--workers", workers]

        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as stderr:
            with redirect_stderr(stderr), self.assertRaises(SystemExit):
                brittle.main(args)

        check_and_print.assert_not_called()

        check_and_print.reset_mock()

        workers = "10"
        args = [self.input.name, "--workers", workers]
        brittle.main(args)

        check_and_print.assert_called_once()

        config = check_and_print.call_args.args[2]

        self.assertEqual(config.workers, 10)

        check_and_print.reset_mock()

        workers = "-15"
        args = [self.input.name, "--workers", workers]
        brittle.main(args)

        check_and_print.assert_called_once()

        config = check_and_print.call_args.args[2]

        self.assertEqual(config.workers, 15)

    @patch('brittle.check_and_print')
    def test_proxy_option(self, check_and_print):
        args = [self.input.name]
        brittle.main(args)

        check_and_print.assert_called_once()

        config = check_and_print.call_args.args[2]

        self.assertEqual(config.proxy, None)

        check_and_print.reset_mock()

        proxy = "socks5://localhost:1080"
        args = [self.input.name, "--proxy", proxy]
        brittle.main(args)

        check_and_print.assert_called_once()

        config = check_and_print.call_args.args[2]

        self.assertEqual(config.proxy, {"server": proxy})

    @patch('brittle.check_and_print')
    def test_proxy_user_option(self, check_and_print):
        proxy_user = "root:12345"
        args = [self.input.name, "--proxy-user", proxy_user]
        brittle.main(args)

        check_and_print.assert_called_once()

        config = check_and_print.call_args.args[2]

        self.assertEqual(config.proxy, None)

        check_and_print.reset_mock()

        proxy = "socks5://localhost:1080"
        args = [self.input.name, "--proxy", proxy, "--proxy-user", proxy_user]
        brittle.main(args)

        check_and_print.assert_called_once()

        config = check_and_print.call_args.args[2]

        self.assertEqual(config.proxy, {"server": proxy, "username": "root", "password": "12345"})

        check_and_print.reset_mock()

        args = [self.input.name, "--proxy", proxy, "--proxy-user", "whoami"]

        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as stderr:
            with redirect_stderr(stderr), self.assertRaises(SystemExit):
                brittle.main(args)

        check_and_print.assert_not_called()

    @patch('brittle.check_and_print')
    def test_headful_flag(self, check_and_print):
        args = [self.input.name]
        brittle.main(args)

        check_and_print.assert_called_once()

        config = check_and_print.call_args.args[2]

        self.assertEqual(config.headless, True)

        check_and_print.reset_mock()

        args = [self.input.name, "--headful"]
        brittle.main(args)

        check_and_print.assert_called_once()

        config = check_and_print.call_args.args[2]

        self.assertEqual(config.headless, False)

    @patch('brittle.check_and_print')
    def test_verbose_flag(self, check_and_print):
        args = [self.input.name]
        brittle.main(args)

        check_and_print.assert_called_once()

        config = check_and_print.call_args.args[2]

        self.assertEqual(config.verbose, False)

        check_and_print.reset_mock()

        args = [self.input.name, "--verbose"]
        brittle.main(args)

        check_and_print.assert_called_once()

        config = check_and_print.call_args.args[2]

        self.assertEqual(config.verbose, True)

class IoTest(unittest.TestCase):
    @patch('brittle.check')
    def test_input_output(self, check):

        expected = [
            "https://github.com/_123",
            "https://nginx.org/404"
        ]
        check.return_value = expected.copy()

        with (tempfile.NamedTemporaryFile("w+", encoding="utf-8") as stdin,
              tempfile.NamedTemporaryFile("w+", encoding="utf-8") as stdout):
            stdin.write("\n".join(URL))
            stdin.flush()
            stdin.seek(0)

            with redirect_stdin(stdin), redirect_stdout(stdout):
                brittle.main([])

            check.assert_called_once()

            urls = check.call_args.args[0]

            stdout.flush()
            stdout.seek(0)
            result = stdout.read()

            self.assertEqual(urls, URL)
            self.assertEqual(result, "\n".join(expected) + "\n")

class redirect_stdin(_RedirectStream):
    _stream = "stdin"
