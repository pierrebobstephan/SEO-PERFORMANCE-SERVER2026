import unittest

from electri_city_ops.http_probe import extract_page_signals


class HtmlExtractTests(unittest.TestCase):
    def test_extract_page_signals(self) -> None:
        html = """
        <html lang="de">
          <head>
            <title>Startseite</title>
            <meta name="description" content="SEO Beobachtung" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <link rel="canonical" href="https://example.com/" />
          </head>
          <body>
            <h1>Willkommen</h1>
          </body>
        </html>
        """

        signals = extract_page_signals(html)

        self.assertEqual(signals.title, "Startseite")
        self.assertEqual(signals.meta_description, "SEO Beobachtung")
        self.assertEqual(signals.canonical, "https://example.com/")
        self.assertEqual(signals.h1_count, 1)
        self.assertEqual(signals.html_lang, "de")
        self.assertTrue(signals.has_viewport)


if __name__ == "__main__":
    unittest.main()

